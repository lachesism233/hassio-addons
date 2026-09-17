# Changelog 更新日志

All notable changes to the Heimdall app, following [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Version numbers follow upstream Heimdall; the last digit is this app's packaging revision.

Heimdall 应用的版本变更记录，格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。版本号跟随上游 Heimdall，最后一位为本应用的打包修订号。

## [2.8.3.1](https://github.com/lachesism233/hassio-addons/commit/f749149) - 2026-09-15

### English

#### Changed

- Documentation and this changelog are now bilingual (English / Simplified Chinese).
- App description in the app store is now English.

### 简体中文

#### 变更

- 文档与更新日志改为中英双语。
- 应用商店描述改为英文。

## [2.8.3](https://github.com/lachesism233/hassio-addons/commit/cc6f309) - 2026-09-14

### English

#### Changed

- Version numbers now follow upstream Heimdall: 2.8.3 is the direct successor of 1.0.0, not a major upgrade.

#### Security

- Internal-address lookups are now allowed by default (`allow_internal_requests: true`), so internal URLs get their titles and icons automatically. If you expose Heimdall through a reverse proxy, set it to `false` to keep SSRF protection. See [DOCS.md](DOCS.md).

### 简体中文

#### 变更

- 版本号改为跟随上游 Heimdall：2.8.3 是 1.0.0 的直接后续版本，并非跨大版本升级。

#### 安全

- 默认允许向内网/私有地址发起查找请求（`allow_internal_requests: true`），内网 URL 可自动获取标题与图标。若通过反向代理把 Heimdall 暴露到公网，请改为 `false` 以保留 SSRF 防护。详见 [DOCS.md](DOCS.md)。

## [1.0.0](https://github.com/lachesism233/hassio-addons/commit/664310a) - 2026-09-14

### English

#### Added

- First release: Heimdall packaged from the [LinuxServer image](https://github.com/linuxserver/Heimdall), with `timezone` and `allow_internal_requests` options.
- Web UI on host port 10000; data (database, icons, `APP_KEY`) lives in `/addon_configs/<repository id>_heimdall` and survives app updates.

### 简体中文

#### 新增

- 首个版本：基于 [LinuxServer 镜像](https://github.com/linuxserver/Heimdall) 打包 Heimdall，提供 `timezone` 与 `allow_internal_requests` 选项。
- Web UI 固定使用主机端口 10000；数据（数据库、图标、`APP_KEY`）保存在 `/addon_configs/<仓库标识>_heimdall`，升级应用不会丢失。
