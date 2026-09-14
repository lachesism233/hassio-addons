import json
import logging
import os
import signal
import sys
import threading
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from capture import build_sources
from scheduler import Scheduler
from web import serve

LOGGER = logging.getLogger("main")

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"
DEFAULT_OPTIONS_PATH = "/data/options.json"
DEFAULT_MEDIA_ROOT = "/share/timelapse"


def load_options():
    candidates = []
    custom = os.environ.get("TIMELAPSE_OPTIONS")
    if custom:
        candidates.append(Path(custom))
    candidates.append(Path(DEFAULT_OPTIONS_PATH))
    candidates.append(Path(__file__).resolve().with_name("options.json"))

    for path in candidates:
        if path.is_file():
            with path.open("r", encoding="utf-8") as handle:
                return json.load(handle), path
    return {}, None


def supervisor_timezone():
    token = os.environ.get("SUPERVISOR_TOKEN", "")
    if not token:
        return None

    request = urllib.request.Request(
        "http://supervisor/supervisor/info",
        headers={"Authorization": f"Bearer {token}"},
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            payload = json.load(response)
    except Exception as exc:
        LOGGER.warning("could not read the timezone from supervisor: %s", exc)
        return None

    return payload.get("data", {}).get("timezone") or None


def resolve_timezone(options):
    name = str(options.get("timezone") or "").strip()
    if not name:
        name = supervisor_timezone() or ""
    if name:
        try:
            from zoneinfo import ZoneInfo

            return name, ZoneInfo(name)
        except Exception as exc:
            LOGGER.warning("unknown timezone '%s' (%s), falling back to local time", name, exc)

    local = datetime.now().astimezone().tzinfo or timezone.utc
    return str(local), local


def main():
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, stream=sys.stdout)

    options, options_path = load_options()
    if options_path is None:
        LOGGER.warning("no options file found, using built-in defaults")
    else:
        LOGGER.info("loaded options from %s", options_path)

    tz_name, tzinfo = resolve_timezone(options)
    media_root = str(options.get("media_root") or DEFAULT_MEDIA_ROOT)
    sources = build_sources(options.get("captures"), media_root, LOGGER)
    if not sources:
        LOGGER.warning("no capture sources configured, add them in the app configuration")

    stop_event = threading.Event()

    def request_stop(signum, frame):
        LOGGER.info("received signal %s, shutting down", signum)
        stop_event.set()

    if threading.current_thread() is threading.main_thread():
        signal.signal(signal.SIGTERM, request_stop)
        signal.signal(signal.SIGINT, request_stop)

    scheduler = Scheduler(sources, tzinfo, stop_event)

    web_thread = threading.Thread(
        target=serve, args=(media_root, sources, stop_event, scheduler), name="web", daemon=True
    )
    web_thread.start()

    scheduler.start()

    LOGGER.info(
        "延时摄影 started: timezone=%s media_root=%s sources=%d",
        tz_name,
        media_root,
        len(sources),
    )

    try:
        while not stop_event.wait(1):
            pass
    finally:
        LOGGER.info("延时摄影 stopped")


if __name__ == "__main__":
    main()
