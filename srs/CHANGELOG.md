# Changelog 更新日志

All notable changes to the SRS Media Server app, following [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Version numbers combine the upstream SRS release with this app's packaging revision (e.g. `6.0.191.2`).

SRS Media Server 应用的版本变更记录，格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。版本号由上游 SRS 版本与本应用的打包修订号组合而成（如 `6.0.191.2`）。

## [6.0.191.2](https://github.com/lachesism233/hassio-addons/commit/f749149) - 2026-09-15

### English

#### Changed

- Documentation and this changelog are now bilingual (English / Simplified Chinese).
- App name and description in the app store are now English.

### 简体中文

#### 变更

- 文档与更新日志改为中英双语。
- 应用商店名称与描述改为英文。

## [6.0.191.1](https://github.com/lachesism233/hassio-addons/commit/4b38a60) - 2026-09-15

### English

#### BREAKING

- **Ingress removed**: the sidebar entry is gone because SRS playback needs ports 8080/1985/8000, which a single-port proxy cannot cover. Open `http://<Home Assistant host>:8080` directly, or add a webpage card pointing there; the app page's "Open Web UI" button opens the same address. See [DOCS.md](DOCS.md).

### 简体中文

#### 破坏性变更

- **移除 ingress**：SRS 播放依赖 8080/1985/8000 多个端口，单端口代理无法覆盖，侧边栏入口因此不再提供。请直接访问 `http://<Home Assistant 地址>:8080`，或在仪表盘添加指向该地址的「网页」卡片；应用页的「打开 Web UI」按钮会打开同一地址。详见 [DOCS.md](DOCS.md)。

## [6.0.191](https://github.com/lachesism233/hassio-addons/commit/4a52e88) - 2026-09-15

### English

#### Added

- First release: SRS 6.0 stable from the official [ossrs/srs](https://github.com/ossrs/srs) image; the runtime configuration is generated from the app options (`timezone`, `log_level`, `webrtc_candidate`, `webrtc_tcp_enabled`, `srt_enabled`).
- RTMP and SRT ingest from OBS/FFmpeg with HLS, HTTP-FLV and WebRTC playback, including the built-in player pages.

### 简体中文

#### 新增

- 首个版本：基于官方 [ossrs/srs](https://github.com/ossrs/srs) 镜像打包 SRS 6.0 稳定版；运行配置由应用选项（`timezone`、`log_level`、`webrtc_candidate`、`webrtc_tcp_enabled`、`srt_enabled`）生成。
- 支持 OBS/FFmpeg 以 RTMP、SRT 推流，HLS、HTTP-FLV、WebRTC 多协议播放，内置播放页。
