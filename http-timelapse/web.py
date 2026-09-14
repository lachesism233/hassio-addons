import html
import logging
import os
import socketserver
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

LOGGER = logging.getLogger("web")

PORT = 8099

PAGE = """<!DOCTYPE html>
<html lang="zh-Hans">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>延时摄影</title>
<meta http-equiv="refresh" content="60">
<style>
:root {{ color-scheme: light dark; }}
body {{ font-family: system-ui, sans-serif; margin: 0; padding: 24px; background: #f4f4f4; }}
h1 {{ font-size: 1.4rem; margin: 0 0 16px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }}
.card {{ background: #fff; border-radius: 12px; padding: 12px; box-shadow: 0 1px 4px rgba(0,0,0,.12); }}
.card h2 {{ font-size: 1rem; margin: 0 0 8px; overflow-wrap: anywhere; }}
.card img {{ width: 100%; border-radius: 8px; display: block; background: #ddd; }}
.card .empty {{ width: 100%; aspect-ratio: 16/9; display: flex; align-items: center; justify-content: center; background: #e6e6e6; border-radius: 8px; color: #666; }}
.card p {{ margin: 8px 0 0; font-size: .8rem; color: #555; overflow-wrap: anywhere; }}
.card .path {{ color: #888; }}
.notice {{ color: #666; }}
@media (prefers-color-scheme: dark) {{
  body {{ background: #111; color: #eee; }}
  .card {{ background: #1e1e1e; box-shadow: none; }}
  .card p {{ color: #aaa; }}
  .card .empty {{ background: #2a2a2a; color: #999; }}
  .card .path {{ color: #777; }}
}}
</style>
</head>
<body>
<h1>延时摄影</h1>
{content}
</body>
</html>
"""


class GalleryHandler(SimpleHTTPRequestHandler):
    sources = []
    server_version = "http-timelapse/0.2"

    def __init__(self, *args, directory=None, sources=None, **kwargs):
        if sources is not None:
            self.sources = sources
        super().__init__(*args, directory=directory, **kwargs)

    def log_message(self, fmt, *args):
        LOGGER.info("%s %s", self.address_string(), fmt % args)

    def end_headers(self):
        if urlparse(self.path).path.endswith("/latest.jpg"):
            self.send_header("Cache-Control", "no-store, max-age=0")
        super().end_headers()

    def do_GET(self):
        if urlparse(self.path).path in ("", "/"):
            self._gallery()
            return
        super().do_GET()

    def _relative_link(self, directory):
        try:
            relative = directory.resolve().relative_to(Path(self.directory).resolve())
        except ValueError:
            return None
        return relative.as_posix()

    def _gallery(self):
        cards = []
        for source in sorted(self.sources, key=lambda item: item.name):
            latest = source.directory / "latest.jpg"
            link = self._relative_link(source.directory)
            name = html.escape(source.name)
            if link is not None and latest.is_file():
                updated = datetime.fromtimestamp(latest.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                image = (
                    f'<a href="{html.escape(link)}/">'
                    f'<img src="{html.escape(link)}/latest.jpg?t={latest.stat().st_mtime_ns}" alt="{name}">'
                    f"</a>"
                )
            else:
                updated = "-"
                image = '<div class="empty">尚无截图</div>'
            cards.append(
                '<div class="card">'
                f"<h2>{name}</h2>"
                f"{image}"
                f"<p>最近抓拍: {updated}</p>"
                f'<p class="path">{html.escape(str(source.directory))}</p>'
                "</div>"
            )

        if cards:
            content = '<div class="grid">' + "".join(cards) + "</div>"
        else:
            content = '<p class="notice">还没有配置抓拍源，请在应用配置中添加。</p>'

        body = PAGE.format(content=content).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class ThreadingHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def serve(media_root, sources, stop_event=None):
    os.makedirs(media_root, exist_ok=True)

    def handler(*args, **kwargs):
        return GalleryHandler(*args, directory=media_root, sources=sources, **kwargs)

    httpd = ThreadingHTTPServer(("0.0.0.0", PORT), handler)
    LOGGER.info("web gallery listening on port %s rooted at %s", PORT, media_root)
    try:
        httpd.serve_forever(poll_interval=1)
    finally:
        httpd.server_close()
