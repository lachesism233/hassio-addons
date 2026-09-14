import json
import logging
import os
import urllib.request
from pathlib import Path

from capture import TIME_RE

LOGGER = logging.getLogger("settings")

SUPERVISOR_URL = "http://supervisor"


class SettingsError(Exception):
    pass


def normalize_time(value):
    match = TIME_RE.match(str(value).strip())
    if not match:
        raise SettingsError(f"invalid time '{value}' (expected HH:MM)")
    return f"{int(match.group(1)):02d}:{match.group(2)}"


class SettingsManager:
    def __init__(self, options, options_path=None):
        self.options = options if isinstance(options, dict) else {}
        self.options_path = Path(options_path) if options_path else None

    @property
    def token(self):
        return os.environ.get("SUPERVISOR_TOKEN", "")

    def update_times(self, times_by_source):
        if not isinstance(times_by_source, dict) or not times_by_source:
            raise SettingsError("no times supplied")

        captures = self.options.get("captures")
        if not isinstance(captures, list) or not captures:
            raise SettingsError("no capture sources configured")

        known = {}
        for item in captures:
            if isinstance(item, dict):
                known[str(item.get("name", ""))] = item

        for name, values in times_by_source.items():
            if name not in known:
                raise SettingsError(f"unknown source: {name}")
            if not isinstance(values, list):
                raise SettingsError(f"{name}: times must be a list")
            cleaned = sorted({normalize_time(value) for value in values})
            known[name]["times"] = cleaned
            LOGGER.info("%s: times updated to %s", name, ",".join(cleaned) or "-")

        self._persist()

    def _post(self, path, payload=None):
        headers = {"Authorization": f"Bearer {self.token}"}
        body = None
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(
            f"{SUPERVISOR_URL}{path}", data=body, headers=headers, method="POST"
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read()
        return json.loads(raw) if raw else {}

    def _persist(self):
        if self.token:
            try:
                self._post("/addons/self/options", {"options": self.options})
            except Exception as exc:
                raise SettingsError(f"supervisor rejected the update: {exc}") from exc
            return

        if self.options_path is None:
            raise SettingsError("no supervisor token and no options file available")
        LOGGER.warning(
            "SUPERVISOR_TOKEN is missing, writing options directly to %s", self.options_path
        )
        self.options_path.write_text(
            json.dumps(self.options, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    def restart(self):
        if not self.token:
            LOGGER.warning("SUPERVISOR_TOKEN is missing, restart the app manually")
            return False
        try:
            self._post("/addons/self/restart")
        except Exception as exc:
            LOGGER.warning("restart request failed: %s", exc)
            return False
        LOGGER.info("restart requested from supervisor")
        return True
