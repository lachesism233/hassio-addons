import html
import json
import logging
import os
import socketserver
import threading
from concurrent.futures import TimeoutError as FutureTimeoutError
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from settings import SettingsError

LOGGER = logging.getLogger("web")

PORT = 8099

SHARED_STYLE = """
:root { color-scheme: light dark; }
body { font-family: system-ui, sans-serif; margin: 0; padding: 24px; background: #f4f4f4; }
header { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; }
h1 { font-size: 1.4rem; margin: 0; }
button, a.button-link { font: inherit; padding: 6px 14px; border: 0; border-radius: 8px; background: #03a9f4; color: #fff; cursor: pointer; text-decoration: none; }
button:disabled { opacity: .5; cursor: wait; }
button.secondary, a.button-link.secondary { background: #78909c; }
input[type=time] { font: inherit; padding: 6px 10px; border-radius: 8px; border: 1px solid #bbb; background: #fff; color: #111; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
.card { background: #fff; border-radius: 12px; padding: 12px; box-shadow: 0 1px 4px rgba(0,0,0,.12); }
.card h2 { font-size: 1rem; margin: 0 0 8px; overflow-wrap: anywhere; }
.card img { width: 100%; border-radius: 8px; display: block; background: #ddd; }
.card .empty { width: 100%; aspect-ratio: 16/9; display: flex; align-items: center; justify-content: center; background: #e6e6e6; border-radius: 8px; color: #666; }
.card p { margin: 8px 0 0; font-size: .8rem; color: #555; overflow-wrap: anywhere; }
.card .path { color: #888; }
.card .actions { margin-top: 10px; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.card .result { margin: 0; color: #2e7d32; }
.card .result.error { color: #c62828; }
.notice { color: #666; }
.time-row { display: flex; align-items: center; gap: 8px; margin-top: 8px; }
.footer { margin-top: 20px; display: flex; align-items: center; gap: 12px; }
#status, #save-status, #all-result { font-size: .85rem; color: #555; }
@media (prefers-color-scheme: dark) {
  body { background: #111; color: #eee; }
  .card { background: #1e1e1e; box-shadow: none; }
  .card p { color: #aaa; }
  .card .empty { background: #2a2a2a; color: #999; }
  .card .path { color: #777; }
  input[type=time] { background: #2a2a2a; color: #eee; border-color: #555; }
  #status, #save-status, #all-result { color: #aaa; }
}
"""

PAGE = """<!DOCTYPE html>
<html lang="zh-Hans">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>延时摄影</title>
<style>
__STYLE__
</style>
</head>
<body>
<header>
<h1>延时摄影</h1>
<button id="shoot-all">全部立即抓拍</button>
<button id="reload" class="secondary">刷新</button>
<a class="button-link secondary" href="settings">设置</a>
<span id="all-result"></span>
</header>
__CONTENT__
<script>
async function refreshImage(card) {
  const img = card.querySelector('img');
  const link = card.getAttribute('data-link');
  if (img && link) {
    img.src = link + '/latest.jpg?t=' + Date.now();
    img.style.display = 'block';
  }
}
function setResult(card, data) {
  const result = card.querySelector('.result');
  if (!result) return;
  if (data.ok) {
    result.textContent = '已保存 ' + data.file;
    result.classList.remove('error');
    refreshImage(card);
  } else {
    result.textContent = '失败: ' + (data.error || '未知错误');
    result.classList.add('error');
  }
}
async function shoot(card, button) {
  button.disabled = true;
  const result = card.querySelector('.result');
  result.classList.remove('error');
  result.textContent = '抓拍中…';
  try {
    const response = await fetch('api/capture?name=' + encodeURIComponent(card.getAttribute('data-source')), { method: 'POST' });
    setResult(card, await response.json());
  } catch (error) {
    result.textContent = '请求失败: ' + error;
    result.classList.add('error');
  } finally {
    button.disabled = false;
  }
}
document.querySelectorAll('button.shoot').forEach(function (button) {
  button.addEventListener('click', function () {
    shoot(button.closest('.card'), button);
  });
});
document.getElementById('reload').addEventListener('click', function () { location.reload(); });
document.getElementById('shoot-all').addEventListener('click', async function () {
  const button = this;
  const allResult = document.getElementById('all-result');
  button.disabled = true;
  allResult.textContent = '抓拍中…';
  try {
    const response = await fetch('api/capture?name=*', { method: 'POST' });
    const data = await response.json();
    const results = data.results || [];
    const okCount = results.filter(function (item) { return item.ok; }).length;
    allResult.textContent = '完成 ' + okCount + '/' + results.length;
    results.forEach(function (item) {
      const card = document.querySelector('[data-source="' + CSS.escape(item.source) + '"]');
      if (card) setResult(card, item);
    });
  } catch (error) {
    allResult.textContent = '请求失败: ' + error;
  } finally {
    button.disabled = false;
  }
});
</script>
</body>
</html>
"""

SETTINGS_PAGE = """<!DOCTYPE html>
<html lang="zh-Hans">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>延时摄影 - 设置</title>
<style>
__STYLE__
</style>
</head>
<body>
<header>
<h1>抓拍时间设置</h1>
<a class="button-link secondary" href=".">返回浏览</a>
</header>
<p class="notice">为每个源选择每日抓拍时间点（可添加多个）。保存后应用会自动重启以生效；其他参数请在应用配置页修改。</p>
__CONTENT__
<div class="footer">
<button id="save">保存并重启</button>
<span id="save-status"></span>
</div>
<script>
function makeRow(value) {
  const row = document.createElement('div');
  row.className = 'time-row';
  const input = document.createElement('input');
  input.type = 'time';
  input.value = value || '12:00';
  const remove = document.createElement('button');
  remove.type = 'button';
  remove.className = 'secondary';
  remove.textContent = '删除';
  remove.addEventListener('click', function () { row.remove(); });
  row.append(input, remove);
  return row;
}
document.querySelectorAll('.card[data-source]').forEach(function (card) {
  const times = card.querySelector('.times');
  card.querySelector('button.add').addEventListener('click', function () {
    times.append(makeRow(''));
  });
  card.querySelectorAll('.time-row button').forEach(function (button) {
    button.addEventListener('click', function () { button.closest('.time-row').remove(); });
  });
});
async function waitForRestart(status) {
  for (let attempt = 0; attempt < 30; attempt++) {
    await new Promise(function (resolve) { setTimeout(resolve, 2000); });
    try {
      const response = await fetch('.', { cache: 'no-store' });
      if (response.ok) { location.href = '.'; return; }
    } catch (error) {}
  }
  status.textContent = '等待重启超时，请手动刷新页面';
}
document.getElementById('save').addEventListener('click', async function () {
  const button = this;
  const status = document.getElementById('save-status');
  const payload = { times: {} };
  const emptySources = [];
  document.querySelectorAll('.card[data-source]').forEach(function (card) {
    const values = Array.from(card.querySelectorAll('input[type=time]')).map(function (input) { return input.value; }).filter(Boolean);
    payload.times[card.getAttribute('data-source')] = values;
    if (!values.length && card.getAttribute('data-interval') === '0') emptySources.push(card.getAttribute('data-source'));
  });
  if (emptySources.length && !confirm('以下源既没有时间点也没有间隔，将不再自动抓拍：' + emptySources.join('、') + '。仍然保存？')) return;
  button.disabled = true;
  status.textContent = '保存中…';
  try {
    const response = await fetch('api/settings/times', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    const data = await response.json();
    if (!data.ok) {
      status.textContent = '保存失败: ' + (data.error || '未知错误');
      button.disabled = false;
      return;
    }
    if (data.restart) {
      status.textContent = '已保存，正在重启应用…';
      waitForRestart(status);
    } else {
      status.textContent = '已保存，请手动重启应用生效';
      button.disabled = false;
    }
  } catch (error) {
    status.textContent = '请求失败: ' + error;
    button.disabled = false;
  }
});
</script>
</body>
</html>
"""


class GalleryHandler(SimpleHTTPRequestHandler):
    sources = []
    scheduler = None
    settings = None
    server_version = "http-timelapse/0.3"

    def __init__(self, *args, directory=None, sources=None, scheduler=None, settings=None, **kwargs):
        if sources is not None:
            self.sources = sources
        if scheduler is not None:
            self.scheduler = scheduler
        if settings is not None:
            self.settings = settings
        super().__init__(*args, directory=directory, **kwargs)

    def log_message(self, fmt, *args):
        LOGGER.info("%s %s", self.address_string(), fmt % args)

    def end_headers(self):
        if urlparse(self.path).path.endswith("/latest.jpg"):
            self.send_header("Cache-Control", "no-store, max-age=0")
        super().end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("", "/"):
            self._page(PAGE, self._gallery_cards())
            return
        if path in ("/settings", "/settings/"):
            self._page(SETTINGS_PAGE, self._settings_cards())
            return
        super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/capture":
            self._capture_api()
            return
        if path == "/api/settings/times":
            self._save_times()
            return
        self.send_error(404)

    def _capture_api(self):
        name = (parse_qs(urlparse(self.path).query).get("name") or [""])[0]
        if not name:
            self._json(400, {"ok": False, "error": "missing 'name' query parameter"})
            return

        if self.scheduler is None:
            self._json(503, {"ok": False, "error": "scheduler is not available"})
            return

        if name == "*":
            results = [self._capture_one(source) for source in self.sources]
            self._json(200, {"ok": all(item["ok"] for item in results), "results": results})
            return

        source = next((item for item in self.sources if item.name == name), None)
        if source is None:
            self._json(404, {"ok": False, "error": f"unknown source: {name}"})
            return

        result = self._capture_one(source)
        self._json(200 if result["ok"] else 409, result)

    def _capture_one(self, source):
        future = self.scheduler.submit_capture(source, ["manual"])
        if future is None:
            return {"source": source.name, "ok": False, "error": "busy, a capture is already running"}

        wait = source.timeout * (source.retries + 1) + source.retry_wait * source.retries + 10
        try:
            path = future.result(timeout=wait)
        except FutureTimeoutError:
            return {"source": source.name, "ok": False, "error": f"timed out after {wait}s"}
        except Exception as exc:
            return {"source": source.name, "ok": False, "error": str(exc)}

        if path is None:
            return {"source": source.name, "ok": False, "error": "capture failed, check the app log"}
        return {"source": source.name, "ok": True, "file": Path(path).name}

    def _save_times(self):
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        if length <= 0 or length > 1024 * 1024:
            self._json(400, {"ok": False, "error": "invalid request body"})
            return

        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            self._json(400, {"ok": False, "error": "invalid JSON body"})
            return

        if self.settings is None:
            self._json(503, {"ok": False, "error": "settings backend is not available"})
            return

        times = payload.get("times") if isinstance(payload, dict) else None
        if not isinstance(times, dict):
            self._json(400, {"ok": False, "error": 'expected {"times": {"source": ["HH:MM"]}}'})
            return

        try:
            self.settings.update_times(times)
        except SettingsError as exc:
            self._json(400, {"ok": False, "error": str(exc)})
            return
        except Exception as exc:
            LOGGER.exception("saving times failed")
            self._json(500, {"ok": False, "error": str(exc)})
            return

        restart = bool(self.settings.token)
        if restart:
            threading.Timer(1.0, self.settings.restart).start()
        self._json(200, {"ok": True, "restart": restart})

    def _json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _page(self, template, content):
        body = template.replace("__STYLE__", SHARED_STYLE).replace("__CONTENT__", content).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _relative_link(self, directory):
        try:
            relative = directory.resolve().relative_to(Path(self.directory).resolve())
        except ValueError:
            return None
        return relative.as_posix()

    def _gallery_cards(self):
        cards = [self._gallery_card(source) for source in sorted(self.sources, key=lambda item: item.name)]
        if cards:
            return '<div class="grid">' + "".join(cards) + "</div>"
        return '<p class="notice">还没有配置抓拍源，请在应用配置中添加。</p>'

    def _gallery_card(self, source):
        latest = source.directory / "latest.jpg"
        link = self._relative_link(source.directory)
        name = html.escape(source.name)
        has_latest = link is not None and latest.is_file()

        if link is None:
            image = '<div class="empty">目录不在浏览根目录下</div>'
            link_attr = ""
        else:
            link_attr = html.escape(link)
            source_image = f"{link}/latest.jpg?t={latest.stat().st_mtime_ns}" if has_latest else ""
            display = "block" if has_latest else "none"
            image = (
                f'<a href="{link_attr}/">'
                f'<img src="{html.escape(source_image)}" alt="{name}" style="display:{display}">'
                "</a>"
            )

        updated = (
            datetime.fromtimestamp(latest.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            if has_latest
            else "-"
        )

        return (
            f'<div class="card" data-source="{name}" data-link="{link_attr}">'
            f"<h2>{name}</h2>"
            f"{image}"
            f"<p>最近抓拍: {updated}</p>"
            f'<p class="path">{html.escape(str(source.directory))}</p>'
            '<div class="actions">'
            f'<button class="shoot" data-name="{name}">立即抓拍</button>'
            '<p class="result"></p>'
            "</div>"
            "</div>"
        )

    def _settings_cards(self):
        cards = []
        for source in sorted(self.sources, key=lambda item: item.name):
            name = html.escape(source.name)
            rows = "".join(
                f'<div class="time-row"><input type="time" value="{html.escape(value)}">'
                '<button type="button" class="secondary">删除</button></div>'
                for value in source.times
            )
            cards.append(
                f'<section class="card" data-source="{name}" data-interval="{source.interval_minutes}">'
                f"<h2>{name}</h2>"
                f'<p class="path">抓拍间隔: {source.interval_minutes} 分钟（在应用配置页修改）</p>'
                f'<div class="times">{rows}</div>'
                '<button type="button" class="add secondary">添加时间点</button>'
                "</section>"
            )

        if not cards:
            return '<p class="notice">还没有配置抓拍源，请在应用配置中添加。</p>'
        return '<div class="grid">' + "".join(cards) + "</div>"


class ThreadingHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def serve(media_root, sources, stop_event=None, scheduler=None, settings=None):
    os.makedirs(media_root, exist_ok=True)

    def handler(*args, **kwargs):
        return GalleryHandler(
            *args,
            directory=media_root,
            sources=sources,
            scheduler=scheduler,
            settings=settings,
            **kwargs,
        )

    httpd = ThreadingHTTPServer(("0.0.0.0", PORT), handler)
    LOGGER.info("web gallery listening on port %s rooted at %s", PORT, media_root)
    try:
        httpd.serve_forever(poll_interval=1)
    finally:
        httpd.server_close()
