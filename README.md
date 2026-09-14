# hassio-addons

Home Assistant app (formerly add-on) repository.

**English** | [简体中文](README.zh-Hans.md)

[![Add app repository to Home Assistant](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Flachesism233%2Fhassio-addons)
[![Show app on Home Assistant](https://my.home-assistant.io/badges/supervisor_addon.svg)](https://my.home-assistant.io/redirect/supervisor_addon/?addon=http_timelapse&repository_url=https%3A%2F%2Fgithub.com%2Flachesism233%2Fhassio-addons)

## Apps

| App | Description |
| --- | --- |
| [HTTP Timelapse (延时摄影)](http-timelapse/) | Scheduled JPEG capture from go2rtc/HTTP sources with validation, retries, per-source schedules and a built-in gallery |

## Installation

### One-click (recommended)

1. Click the **Add app repository to Home Assistant** button above and confirm — the repository URL is pre-filled in the app store
2. Click the **Show app on Home Assistant** button, or search for **HTTP Timelapse** in the app store, and install it

### Manual

1. In Home Assistant, go to **Settings → Apps → Install app**
2. Open the menu (⋮) → **Repositories**
3. Add `https://github.com/lachesism233/hassio-addons`
4. Install **延时摄影 (HTTP Timelapse)** and start it

## Documentation

- [HTTP Timelapse documentation (Simplified Chinese)](http-timelapse/DOCS.md)

## Notes

- The apps in this repository are built for Home Assistant Supervisor, so Home Assistant OS or Supervised is required
