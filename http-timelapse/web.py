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
from urllib.parse import parse_qs, quote, urlparse

from settings import SettingsError

LOGGER = logging.getLogger("web")

PORT = 8099

PAGE_SIZES = (30, 60, 120)
DEFAULT_PAGE_SIZE = 60
IMAGE_SUFFIXES = (".jpg", ".jpeg")
DEFAULT_SORT = "time_desc"
SORT_OPTIONS = (
    ("time_desc", "时间：新 → 旧"),
    ("time_asc", "时间：旧 → 新"),
    ("name_asc", "文件名：A → Z"),
    ("name_desc", "文件名：Z → A"),
    ("size_desc", "大小：大 → 小"),
    ("size_asc", "大小：小 → 大"),
)
SORT_KEYS = {
    "time_desc": (lambda item: (item["mtime"], item["name"].lower()), True),
    "time_asc": (lambda item: (item["mtime"], item["name"].lower()), False),
    "name_asc": (lambda item: item["name"].lower(), False),
    "name_desc": (lambda item: item["name"].lower(), True),
    "size_desc": (lambda item: (item["size"], item["name"].lower()), True),
    "size_asc": (lambda item: (item["size"], item["name"].lower()), False),
}

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
select { font: inherit; padding: 6px 10px; border-radius: 8px; border: 1px solid #bbb; background: #fff; color: #111; }
.toolbar { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; }
.toolbar .count { font-size: .85rem; color: #555; }
.toolbar label { display: inline-flex; align-items: center; gap: 6px; font-size: .85rem; color: #555; }
.view-toggle { display: inline-flex; gap: 8px; }
.view-toggle button.active { background: #03a9f4; }
.items { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 12px; }
.tile { display: block; background: #fff; border-radius: 12px; padding: 8px; box-shadow: 0 1px 4px rgba(0,0,0,.12); color: inherit; text-decoration: none; }
.tile img { width: 100%; aspect-ratio: 16/9; object-fit: cover; border-radius: 8px; display: block; background: #ddd; }
.tile .name, .tile .size { display: none; }
.tile .time { display: block; margin-top: 6px; font-size: .75rem; color: #555; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.badge { display: inline-block; padding: 1px 8px; border-radius: 999px; background: #03a9f4; color: #fff; font-size: .7rem; }
.latest-section { margin-bottom: 20px; }
.latest-section h2 { font-size: 1rem; margin: 0 0 8px; }
.list-header { display: none; grid-template-columns: minmax(0, 1fr) auto auto; gap: 12px; padding: 8px 12px; font-size: .75rem; color: #777; border-bottom: 1px solid #ddd; }
html.view-list .list-header { display: grid; }
html.view-list .items { display: block; }
html.view-list .tile { display: grid; grid-template-columns: minmax(0, 1fr) auto auto; gap: 12px; align-items: center; padding: 10px 12px; margin-bottom: 6px; }
html.view-list .tile img { display: none; }
html.view-list .tile .name { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
html.view-list .tile .size { display: block; }
html.view-list .tile .time { margin: 0; font-size: .8rem; color: #777; }
.pagination { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-top: 20px; }
.pagination .info { font-size: .85rem; color: #555; }
.button-link.disabled { opacity: .45; pointer-events: none; }
.lightbox { position: fixed; inset: 0; z-index: 10; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,.88); }
.lightbox[hidden] { display: none; }
.lightbox img { max-width: 92vw; max-height: 80vh; object-fit: contain; border-radius: 8px; }
.lightbox-close, .lightbox-prev, .lightbox-next { position: absolute; width: 44px; height: 44px; padding: 0; border-radius: 50%; background: rgba(255,255,255,.18); font-size: 1.5rem; line-height: 1; }
.lightbox-close { top: 16px; right: 16px; }
.lightbox-prev { left: 16px; top: 50%; transform: translateY(-50%); }
.lightbox-next { right: 16px; top: 50%; transform: translateY(-50%); }
.lightbox-caption { position: absolute; bottom: 16px; left: 16px; right: 16px; text-align: center; color: #ddd; font-size: .8rem; }
.lightbox-caption a { color: #4fc3f7; }
.lightbox button:disabled { opacity: .35; cursor: default; }
@media (prefers-color-scheme: dark) {
  body { background: #111; color: #eee; }
  .card { background: #1e1e1e; box-shadow: none; }
  .card p { color: #aaa; }
  .card .empty { background: #2a2a2a; color: #999; }
  .card .path { color: #777; }
  input[type=time], select { background: #2a2a2a; color: #eee; border-color: #555; }
  #status, #save-status, #all-result { color: #aaa; }
  .toolbar .count, .toolbar label { color: #aaa; }
  .tile { background: #1e1e1e; box-shadow: none; }
  .tile img { background: #2a2a2a; }
  .tile .time { color: #aaa; }
  .list-header { color: #888; border-color: #333; }
  html.view-list .tile { border-bottom: 1px solid #2f2f2f; }
  html.view-list .tile .time { color: #999; }
  .pagination .info { color: #aaa; }
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

BROWSE_PAGE = """<!DOCTYPE html>
<html lang="zh-Hans">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<script>
try {
  if (localStorage.getItem('timelapse-browse-view') === 'list') document.documentElement.classList.add('view-list');
} catch (error) {}
</script>
<style>
__STYLE__
</style>
</head>
<body>
__CONTENT__
<div id="lightbox" class="lightbox" hidden>
<button type="button" class="lightbox-close" aria-label="关闭">×</button>
<button type="button" class="lightbox-prev" aria-label="上一张">‹</button>
<img alt="">
<button type="button" class="lightbox-next" aria-label="下一张">›</button>
<div class="lightbox-caption"><span></span> <a target="_blank" rel="noopener">在新标签打开原图</a></div>
</div>
<script>
(function () {
  var VIEW_KEY = 'timelapse-browse-view';
  var root = document.documentElement;

  function applyView(view) {
    root.classList.toggle('view-list', view === 'list');
    document.querySelectorAll('.view-toggle button').forEach(function (button) {
      button.classList.toggle('active', button.getAttribute('data-view') === view);
    });
  }
  applyView(root.classList.contains('view-list') ? 'list' : 'grid');
  document.querySelectorAll('.view-toggle button').forEach(function (button) {
    button.addEventListener('click', function () {
      var view = button.getAttribute('data-view');
      try { localStorage.setItem(VIEW_KEY, view); } catch (error) {}
      applyView(view);
    });
  });

  var sort = document.getElementById('sort');
  var per = document.getElementById('per');
  function reload() {
    location.search = '?sort=' + encodeURIComponent(sort.value) + '&per=' + encodeURIComponent(per.value) + '&page=1';
  }
  sort.addEventListener('change', reload);
  per.addEventListener('change', reload);

  var images = Array.from(document.querySelectorAll('img[data-src]'));
  images.forEach(function (img) {
    img.addEventListener('error', function () { img.style.visibility = 'hidden'; });
  });
  function load(img) {
    img.src = img.getAttribute('data-src');
    img.removeAttribute('data-src');
  }
  if ('IntersectionObserver' in window) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        observer.unobserve(entry.target);
        load(entry.target);
      });
    });
    images.forEach(function (img) { observer.observe(img); });
  } else {
    images.forEach(load);
  }

  var links = Array.from(document.querySelectorAll('.items a.tile[data-full]'));
  var box = document.getElementById('lightbox');
  if (!links.length || !box) return;

  var boxImage = box.querySelector('img');
  var caption = box.querySelector('.lightbox-caption span');
  var original = box.querySelector('.lightbox-caption a');
  var prev = box.querySelector('.lightbox-prev');
  var next = box.querySelector('.lightbox-next');
  var current = -1;
  var lastFocus = null;

  function show(index) {
    if (index < 0 || index >= links.length) return;
    current = index;
    var link = links[index];
    var url = link.getAttribute('data-full');
    boxImage.src = url;
    boxImage.alt = link.getAttribute('data-name');
    caption.textContent = link.getAttribute('data-name') + ' · ' + link.getAttribute('data-time') + ' · ' + link.getAttribute('data-size');
    original.href = url;
    prev.disabled = index === 0;
    next.disabled = index === links.length - 1;
    box.hidden = false;
    document.body.style.overflow = 'hidden';
  }
  function close() {
    box.hidden = true;
    boxImage.removeAttribute('src');
    document.body.style.overflow = '';
    if (lastFocus) lastFocus.focus();
  }
  links.forEach(function (link, index) {
    link.addEventListener('click', function (event) {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      lastFocus = link;
      show(index);
    });
  });
  prev.addEventListener('click', function () { show(current - 1); });
  next.addEventListener('click', function () { show(current + 1); });
  box.querySelector('.lightbox-close').addEventListener('click', close);
  box.addEventListener('click', function (event) { if (event.target === box) close(); });
  document.addEventListener('keydown', function (event) {
    if (box.hidden) return;
    if (event.key === 'Escape') close();
    else if (event.key === 'ArrowLeft') show(current - 1);
    else if (event.key === 'ArrowRight') show(current + 1);
  });
})();
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

    def _page(self, template, content, title=None):
        body = template.replace("__STYLE__", SHARED_STYLE).replace("__CONTENT__", content)
        if title is not None:
            body = body.replace("__TITLE__", html.escape(title))
        body = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _relative_link(self, directory):
        try:
            relative = directory.resolve().relative_to(Path(self.directory).resolve())
        except ValueError:
            return None
        return relative.as_posix()

    def list_directory(self, path):
        source = self._source_for_directory(path)
        if source is not None:
            self._page(BROWSE_PAGE, self._browse_content(source), title=f"{source.name} · 抓拍列表")
            return None
        return super().list_directory(path)

    def _source_for_directory(self, path):
        try:
            directory = Path(path).resolve()
        except OSError:
            return None
        for source in self.sources:
            try:
                if source.directory.resolve() == directory:
                    return source
            except OSError:
                continue
        return None

    @staticmethod
    def _int_param(query, key, default):
        try:
            return int((query.get(key) or [default])[0])
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _format_size(size):
        value = float(size)
        if value < 1024:
            return f"{int(value)} B"
        if value < 1024 * 1024:
            return f"{value / 1024:.1f} KB"
        if value < 1024 * 1024 * 1024:
            return f"{value / (1024 * 1024):.1f} MB"
        return f"{value / (1024 * 1024 * 1024):.1f} GB"

    def _scan_items(self, source):
        items = []
        try:
            entries = os.scandir(source.directory)
        except OSError:
            return items
        with entries:
            for entry in entries:
                name = entry.name
                if name == "latest.jpg" or name.endswith(".tmp"):
                    continue
                if Path(name).suffix.lower() not in IMAGE_SUFFIXES:
                    continue
                try:
                    if not entry.is_file():
                        continue
                    stat = entry.stat()
                except OSError:
                    continue
                items.append({"name": name, "mtime": stat.st_mtime, "size": stat.st_size})
        return items

    def _browse_item(self, item):
        name = item["name"]
        url = quote(name)
        label = datetime.fromtimestamp(item["mtime"]).strftime("%Y-%m-%d %H:%M:%S")
        size = self._format_size(item["size"])
        escaped = html.escape(name)
        return (
            f'<a class="tile" href="{url}" data-full="{url}" data-name="{escaped}"'
            f' data-time="{label}" data-size="{size}" title="{escaped}">'
            f'<img data-src="{url}" alt="{escaped}" decoding="async">'
            f'<span class="name">{escaped}</span>'
            f'<span class="time">{label}</span>'
            f'<span class="size">{size}</span>'
            "</a>"
        )

    def _pagination(self, sort, per, page, pages):
        def link(label, target, enabled):
            if enabled:
                href = f"?sort={sort}&amp;per={per}&amp;page={target}"
                return f'<a class="button-link secondary" href="{href}">{label}</a>'
            return f'<span class="button-link secondary disabled">{label}</span>'

        return (
            '<nav class="pagination">'
            + link("首页", 1, page > 1)
            + link("上一页", page - 1, page > 1)
            + f'<span class="info">第 {page} / {pages} 页</span>'
            + link("下一页", page + 1, page < pages)
            + link("末页", pages, page < pages)
            + "</nav>"
        )

    def _browse_content(self, source):
        query = parse_qs(urlparse(self.path).query)

        sort = (query.get("sort") or [DEFAULT_SORT])[0]
        if sort not in SORT_KEYS:
            sort = DEFAULT_SORT

        per = self._int_param(query, "per", DEFAULT_PAGE_SIZE)
        if per not in PAGE_SIZES:
            per = DEFAULT_PAGE_SIZE

        items = self._scan_items(source)
        key, reverse = SORT_KEYS[sort]
        items.sort(key=key, reverse=reverse)

        pages = max(1, (len(items) + per - 1) // per)
        page = min(max(self._int_param(query, "page", 1), 1), pages)
        start = (page - 1) * per
        visible = items[start : start + per]

        relative = self._relative_link(source.directory)
        back = "../" * (len(Path(relative).parts) if relative else 1)

        latest = source.directory / "latest.jpg"
        latest_item = None
        if latest.is_file():
            try:
                stat = latest.stat()
                latest_item = {
                    "name": latest.name,
                    "mtime": stat.st_mtime,
                    "size": stat.st_size,
                }
            except OSError:
                latest_item = None

        sort_options = "".join(
            f'<option value="{value}"{" selected" if value == sort else ""}>{label}</option>'
            for value, label in SORT_OPTIONS
        )
        per_options = "".join(
            f'<option value="{size}"{" selected" if size == per else ""}>{size} 张</option>'
            for size in PAGE_SIZES
        )

        parts = [
            "<header>",
            f"<h1>{html.escape(source.name)} · 抓拍列表</h1>",
            f'<a class="button-link secondary" href="{back}">返回首页</a>',
            "</header>",
            '<div class="toolbar">',
            f'<span class="count">共 {len(items)} 张</span>',
            '<div class="view-toggle">',
            '<button type="button" class="secondary active" data-view="grid">网格</button>',
            '<button type="button" class="secondary" data-view="list">列表</button>',
            "</div>",
            f'<label>排序 <select id="sort">{sort_options}</select></label>',
            f'<label>每页 <select id="per">{per_options}</select></label>',
            "</div>",
        ]

        if latest_item is not None:
            parts.append('<section class="latest-section">')
            parts.append('<h2>最新抓拍 <span class="badge">latest.jpg</span></h2>')
            parts.append('<div class="items">' + self._browse_item(latest_item) + "</div>")
            parts.append("</section>")

        parts.append('<div class="list-header"><span>文件名</span><span>抓拍时间</span><span>大小</span></div>')
        if visible:
            parts.append('<div class="items">' + "".join(self._browse_item(item) for item in visible) + "</div>")
        else:
            parts.append('<p class="notice">还没有抓拍文件。</p>')
        if pages > 1:
            parts.append(self._pagination(sort, per, page, pages))

        return "".join(parts)

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
