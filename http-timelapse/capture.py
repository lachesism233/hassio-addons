import logging
import os
import re
import urllib.request
from dataclasses import dataclass
from pathlib import Path

LOGGER = logging.getLogger("capture")

TIME_RE = re.compile(r"^([01]?\d|2[0-3]):([0-5]\d)$")
JPEG_SOI = b"\xff\xd8\xff"
JPEG_EOI = b"\xff\xd9"


class CaptureError(Exception):
    pass


@dataclass
class Source:
    name: str
    url: str
    directory: Path
    times: list
    interval_minutes: int = 0
    retries: int = 3
    retry_wait: int = 5
    timeout: int = 10
    min_size: int = 1024
    keep_days: int = 0

    def describe(self):
        times = ",".join(self.times) if self.times else "-"
        interval = f"{self.interval_minutes}m" if self.interval_minutes > 0 else "-"
        keep = f"{self.keep_days}d" if self.keep_days > 0 else "forever"
        return (
            f"{self.name}: times={times} interval={interval} dir={self.directory} "
            f"retries={self.retries} retry_wait={self.retry_wait}s timeout={self.timeout}s "
            f"min_size={self.min_size}B keep={keep}"
        )


def pick(config, key, default):
    value = config.get(key)
    return default if value is None else value


def as_int(config, key, default):
    value = pick(config, key, default)
    try:
        return int(value)
    except (TypeError, ValueError):
        LOGGER.warning("invalid value for '%s': %r, using %s", key, value, default)
        return default


def sanitize_name(name):
    cleaned = re.sub(r'[\\/:*?"<>|\x00-\x1f]+', "_", name).strip().strip(".")
    return cleaned or "capture"


def build_sources(raw_captures, media_root, logger=None):
    logger = logger or LOGGER
    sources = []
    seen = set()
    if not isinstance(raw_captures, list):
        return sources

    for index, raw in enumerate(raw_captures, start=1):
        if not isinstance(raw, dict):
            logger.warning("captures[%d] is not a mapping, skipped", index)
            continue

        name = str(pick(raw, "name", "")).strip()
        url = str(pick(raw, "url", "")).strip()
        if not name or not url:
            logger.error("captures[%d] needs both 'name' and 'url', skipped", index)
            continue

        base = name
        suffix = 2
        while name in seen:
            name = f"{base}-{suffix}"
            suffix += 1
        seen.add(name)

        times_raw = pick(raw, "times", []) or []
        if isinstance(times_raw, str):
            times_raw = [times_raw]
        times = []
        for value in times_raw:
            text = str(value).strip()
            match = TIME_RE.match(text)
            if not match:
                logger.warning("%s: invalid time '%s' ignored (expected HH:MM)", name, text)
                continue
            times.append(f"{int(match.group(1)):02d}:{match.group(2)}")
        times = sorted(set(times))

        interval = max(0, as_int(raw, "interval_minutes", 0))

        directory = str(pick(raw, "directory", "") or "").strip()
        if directory:
            directory_path = Path(directory)
            if not directory_path.is_absolute():
                directory_path = Path(media_root) / directory_path
        else:
            directory_path = Path(media_root) / sanitize_name(name)

        source = Source(
            name=name,
            url=url,
            directory=directory_path,
            times=times,
            interval_minutes=interval,
            retries=max(0, as_int(raw, "retries", 3)),
            retry_wait=max(1, as_int(raw, "retry_wait", 5)),
            timeout=max(1, as_int(raw, "timeout", 10)),
            min_size=max(0, as_int(raw, "min_size", 1024)),
            keep_days=max(0, as_int(raw, "keep_days", 0)),
        )
        if not source.times and source.interval_minutes <= 0:
            logger.warning("%s has no daily times and no interval, it will never capture", name)
        sources.append(source)

    return sources


def fetch_image(source):
    request = urllib.request.Request(source.url, headers={"User-Agent": "http-timelapse/0.2"})
    with urllib.request.urlopen(request, timeout=source.timeout) as response:
        status = getattr(response, "status", None) or response.getcode()
        data = response.read()
    if status != 200:
        raise CaptureError(f"unexpected HTTP status {status}")
    if not data:
        raise CaptureError("empty response body")
    return data


def validate_image(data, min_size):
    if len(data) < min_size:
        return f"image too small ({len(data)} < {min_size} bytes)"
    if not data.startswith(JPEG_SOI):
        return "response is not a JPEG image"
    if not data.endswith(JPEG_EOI):
        LOGGER.warning("JPEG is missing the EOI marker (%d bytes), accepting anyway", len(data))
    return None


def save_image(source, data, now):
    source.directory.mkdir(parents=True, exist_ok=True)
    stamp = now.strftime("%Y%m%d_%H%M%S")
    path = source.directory / f"{stamp}.jpg"
    counter = 1
    while path.exists():
        path = source.directory / f"{stamp}-{counter}.jpg"
        counter += 1

    tmp_path = path.with_name(path.name + ".tmp")
    tmp_path.write_bytes(data)
    os.replace(tmp_path, path)

    latest = source.directory / "latest.jpg"
    latest_tmp = source.directory / "latest.jpg.tmp"
    latest_tmp.write_bytes(data)
    os.replace(latest_tmp, latest)

    return path


def capture_source(source, now, stop_event, logger=None):
    logger = logger or LOGGER
    attempts = max(1, 1 + int(source.retries))

    for attempt in range(1, attempts + 1):
        try:
            data = fetch_image(source)
            problem = validate_image(data, source.min_size)
            if problem:
                raise CaptureError(problem)
            path = save_image(source, data, now)
            logger.info(
                "%s saved %s (%d bytes, attempt %d/%d)",
                source.name,
                path,
                len(data),
                attempt,
                attempts,
            )
            return path
        except Exception as exc:
            if attempt >= attempts:
                logger.error("%s capture failed after %d attempt(s): %s", source.name, attempt, exc)
                return None
            logger.warning(
                "%s attempt %d/%d failed: %s; retrying in %ds",
                source.name,
                attempt,
                attempts,
                exc,
                source.retry_wait,
            )
            if stop_event is not None and stop_event.wait(source.retry_wait):
                logger.warning("%s capture aborted (shutting down)", source.name)
                return None
    return None


def cleanup_source(source, now, logger=None):
    logger = logger or LOGGER
    if source.keep_days <= 0:
        return 0

    cutoff = now.timestamp() - source.keep_days * 86400
    removed = 0
    for path in source.directory.glob("*.jpg"):
        if path.name == "latest.jpg":
            continue
        try:
            if path.stat().st_mtime < cutoff:
                path.unlink()
                removed += 1
        except OSError as exc:
            logger.warning("%s cleanup failed for %s: %s", source.name, path, exc)

    if removed:
        logger.info(
            "%s cleanup removed %d file(s) older than %d day(s)",
            source.name,
            removed,
            source.keep_days,
        )
    return removed
