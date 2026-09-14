import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, time as dtime

from capture import capture_source, cleanup_source

LOGGER = logging.getLogger("scheduler")

TICK_SECONDS = 5
CLEANUP_AFTER = dtime(3, 0)
MAX_WORKERS = 8


class Scheduler(threading.Thread):
    def __init__(self, sources, tzinfo, stop_event):
        super().__init__(name="scheduler", daemon=True)
        self.sources = sources
        self.tzinfo = tzinfo
        self.stop_event = stop_event
        self._executor = ThreadPoolExecutor(max_workers=MAX_WORKERS, thread_name_prefix="capture")
        self._lock = threading.Lock()
        self._busy = set()
        self._fired = set()
        self._slots = {}
        self._cleanup_date = None

    @staticmethod
    def _slot(now, source):
        return int(now.timestamp()) // (source.interval_minutes * 60)

    def run(self):
        now = datetime.now(self.tzinfo)
        for source in self.sources:
            if source.interval_minutes > 0:
                self._slots[source.name] = self._slot(now, source)
            LOGGER.info("source ready -> %s", source.describe())

        LOGGER.info("scheduler started, ticking every %ss", TICK_SECONDS)
        while not self.stop_event.is_set():
            try:
                self._tick(datetime.now(self.tzinfo))
            except Exception:
                LOGGER.exception("scheduler tick failed")
            self.stop_event.wait(TICK_SECONDS)

        self._executor.shutdown(wait=False)
        LOGGER.info("scheduler stopped")

    def _tick(self, now):
        day = now.strftime("%Y-%m-%d")
        current = now.strftime("%H:%M")

        if self._fired and not any(key[0] == day for key in self._fired):
            self._fired.clear()

        for source in self.sources:
            reasons = []
            if current in source.times:
                key = (day, source.name, current)
                if key not in self._fired:
                    self._fired.add(key)
                    reasons.append(f"time {current}")
            if source.interval_minutes > 0:
                slot = self._slot(now, source)
                if self._slots.get(source.name) != slot:
                    self._slots[source.name] = slot
                    reasons.append(f"interval {source.interval_minutes}m")
            if reasons:
                self._submit(source, reasons)

        self._maybe_cleanup(now)

    def _submit(self, source, reasons):
        with self._lock:
            if source.name in self._busy:
                LOGGER.warning(
                    "%s is still busy, trigger skipped: %s", source.name, ", ".join(reasons)
                )
                return
            self._busy.add(source.name)
        self._executor.submit(self._run, source, reasons)

    def _run(self, source, reasons):
        try:
            LOGGER.info("%s capture triggered (%s)", source.name, ", ".join(reasons))
            capture_source(source, datetime.now(self.tzinfo), self.stop_event, LOGGER)
        except Exception:
            LOGGER.exception("%s capture crashed", source.name)
        finally:
            with self._lock:
                self._busy.discard(source.name)

    def _maybe_cleanup(self, now):
        day = now.strftime("%Y-%m-%d")
        if now.time() < CLEANUP_AFTER or self._cleanup_date == day:
            return
        self._cleanup_date = day
        for source in self.sources:
            if source.keep_days > 0:
                self._executor.submit(cleanup_source, source, now, LOGGER)
