# hassio-addons

Home Assistant app (formerly add-on) repository.

**English** | [简体中文](README.zh-Hans.md)

[![Add app repository to Home Assistant](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Flachesism233%2Fhassio-addons)
[![Show app on Home Assistant](https://my.home-assistant.io/badges/supervisor_addon.svg)](https://my.home-assistant.io/redirect/supervisor_addon/?addon=http_timelapse&repository_url=https%3A%2F%2Fgithub.com%2Flachesism233%2Fhassio-addons)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Apps

| App | Description |
| --- | --- |
| [HTTP Timelapse](http-timelapse/) | Scheduled JPEG capture from go2rtc/HTTP sources with validation, retries, per-source schedules and a built-in gallery |
| [Heimdall](heimdall/) | Application dashboard with icon tiles for your favourite sites and self-hosted services |
| [SRS Media Server](srs/) | Realtime media server for Home Assistant: RTMP/SRT ingest from OBS or FFmpeg with HLS, HTTP-FLV and WebRTC playback |

## Installation

### One-click (recommended)

1. Click the **Add app repository to Home Assistant** button above and confirm — the repository URL is pre-filled in the app store
2. Click the **Show app on Home Assistant** button above, then install the app from its page

### Manual

Use this method if the buttons above do not work, for example when Home Assistant is not reachable through `my.home-assistant.io`:

1. In Home Assistant, go to **Settings → Apps** and select **Install app**
2. In the top-right corner, open the three-dot menu (⋮) and select **Repositories**
3. Paste `https://github.com/lachesism233/hassio-addons` and select **Add**, then close the dialog
4. Find the app you want — for example **HTTP Timelapse** — and install it

## Documentation

Bilingual (English / Simplified Chinese) documentation:

- [HTTP Timelapse documentation](http-timelapse/DOCS.md) · [changelog](http-timelapse/CHANGELOG.md)
- [Heimdall documentation](heimdall/DOCS.md) · [changelog](heimdall/CHANGELOG.md)
- [SRS Media Server documentation](srs/DOCS.md) · [changelog](srs/CHANGELOG.md)

## Notes

- The apps in this repository are built for Home Assistant Supervisor, so Home Assistant OS or Supervised is required

## Support

- Report bugs or request features via [GitHub Issues](https://github.com/lachesism233/hassio-addons/issues)

## Credits

- [HTTP Timelapse](http-timelapse/) is an original app written for this repository
- [Heimdall](https://github.com/linuxserver/Heimdall) is developed by LinuxServer.io; this app packages the [LinuxServer image](https://hub.docker.com/r/linuxserver/heimdall)
- [SRS](https://github.com/ossrs/srs) is an MIT-licensed realtime media server; this app packages the [official image](https://hub.docker.com/r/ossrs/srs)
- App icons are the logos of the respective upstream projects
- Base images come from [Home Assistant base images](https://github.com/home-assistant/docker-base)

## License

[MIT](LICENSE)
