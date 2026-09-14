# HTTP Timelapse

Serves timelapse media (images/videos) over HTTP from a folder in your Home Assistant installation.

## Installation

1. Settings → Apps → Install app
2. Menu (⋮) → Repositories
3. Add `https://github.com/huangzumings/http-timelapse`
4. Install **HTTP Timelapse** and start it
5. Open the Web UI (port 8099) to browse the media

## Options

| Option | Description | Default |
| --- | --- | --- |
| `directory` | Folder inside the container to serve | `/share/timelapse` |

## Notes

`/share/timelapse` maps to `share/timelapse` on your Home Assistant host,
so you can drop timelapse files there (via Samba, SSH, or another app) and
they will show up on the web page.
