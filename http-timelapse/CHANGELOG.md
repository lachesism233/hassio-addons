# Changelog 更新日志

All notable changes to the HTTP Timelapse app, following [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions use [Semantic Versioning](https://semver.org/).

HTTP Timelapse 应用的版本变更记录，格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循[语义化版本](https://semver.org/lang/zh-CN/)。

## [2.0.0](https://github.com/lachesism233/hassio-addons/commit/c9f6683) - 2026-09-17

### English

#### BREAKING

- **The latest-frame URL has changed**: dashboard cards that used `http://<host>:8099/<source>/latest.jpg` must switch to `http://<host>:8099/latest/<source>.jpg` before upgrading — the old address is no longer served. See [DOCS.md](DOCS.md). This release was first committed as 1.3.0 and renumbered to 2.0.0 because the change is incompatible.

#### Changed

- **Leaner storage**: `latest.jpg` is no longer written to disk; the newest capture is resolved on the fly, so a source folder only contains its captures.
- **More comfortable browsing**: larger thumbnails on desktop, the newest capture featured in its own tile above the list, and a new "All" items-per-page option that pairs with lazy loading.
- **Clearer configuration**: option descriptions rewritten with examples and documented ranges; the retry limit is raised from 20 to 50.

### 简体中文

#### 破坏性变更

- **最新画面地址已变更**：仪表盘若使用 `http://<主机>:8099/<源名>/latest.jpg`，请在升级前改为 `http://<主机>:8099/latest/<源名>.jpg`，旧地址不再提供服务。详见 [DOCS.md](DOCS.md)。本版本最初以 1.3.0 编号提交，因包含不兼容变更，已重新编号为 2.0.0。

#### 变更

- **更精简的存储**：不再写入 `latest.jpg`，最新画面在请求时即时定位，源目录中只保留抓拍文件。
- **更舒适的浏览**：桌面端缩略图更大，「最新抓拍」在列表上方独立成卡片；「每页」新增「全部」并与懒加载配合。
- **更清晰的配置**：重写选项说明并补充示例与取值范围；重试上限由 20 提升至 50。

## [1.2.0](https://github.com/lachesism233/hassio-addons/commit/8c7f844) - 2026-09-16

### English

#### Added

- The web interface now follows the browser language: Simplified Chinese for Chinese browsers, English otherwise.

### 简体中文

#### 新增

- 网页界面跟随浏览器语言：中文浏览器显示简体中文，其他显示英文。

## [1.1.0](https://github.com/lachesism233/hassio-addons/commit/172dbd0) - 2026-09-16

### English

#### Added

- Rebuilt capture browser: grid/list views (remembered per browser), sorting by time, file name or size in both directions, paging at 30/60/120 items, lazy-loaded grid images, the newest capture pinned above the list, and a lightbox (`←`/`→` to switch, `Esc` to close, or open the original in a new tab).

### 简体中文

#### 新增

- 重写抓拍浏览页：网格/列表视图（按浏览器记忆）、按时间/文件名/大小双向排序、每页 30/60/120、网格图片懒加载、最新抓拍在列表上方置顶，以及灯箱预览（`←`/`→` 切换、`Esc` 关闭、可打开原图）。

## [1.0.1](https://github.com/lachesism233/hassio-addons/commit/f749149) - 2026-09-15

### English

#### Changed

- Documentation and this changelog are now bilingual (English / Simplified Chinese).
- App name, description and sidebar title in the app store are now English.

### 简体中文

#### 变更

- 文档与更新日志改为中英双语。
- 应用商店名称、描述与侧边栏标题改为英文。

## [1.0.0](https://github.com/lachesism233/hassio-addons/commit/71691d5) - 2026-09-14

### English

#### Changed

- First stable release: documentation rewritten and option descriptions made concise.

### 简体中文

#### 变更

- 首个稳定版：重写文档并精简配置项描述。

## [0.3.0-alpha3](https://github.com/lachesism233/hassio-addons/commit/884b7a2) - 2026-09-14

*Pre-release 预发布*

### English

#### Added

- Per-source **strict schedule naming**: captures are named after the planned trigger time even when retries run past it (on by default).

#### Changed

- Default file name format is now `snap_%Y%m%d_%H%M%S.jpg`.
- New installations start with an empty capture list and follow the Home Assistant timezone instead of shipping a sample source.

### 简体中文

#### 新增

- 每个源可独立开启**严格计划时间命名**：即使重试拖延，文件名仍使用计划触发时间（默认开启）。

#### 变更

- 默认文件名格式改为 `snap_%Y%m%d_%H%M%S.jpg`。
- 新安装默认抓拍源列表为空并跟随 Home Assistant 时区，不再附带示例源。

## [0.3.0-alpha2](https://github.com/lachesism233/hassio-addons/commit/6efda6f) - 2026-09-14

*Pre-release 预发布*

### English

#### Fixed

- Fixed a missing Python module in the image that made the app crash at startup with `ModuleNotFoundError`.

### 简体中文

#### 修复

- 修复镜像中缺少一个 Python 模块、导致应用启动即崩溃（`ModuleNotFoundError`）的问题。

## [0.3.0-alpha1](https://github.com/lachesism233/hassio-addons/commit/bb9afe4) - 2026-09-14

*Pre-release 预发布*

### English

#### Added

- Default save locations: `media_root` falls back to `/media/timelapse`, and each source to `<root>/<name>` when left empty.
- Per-source `filename_format`, with the planned trigger time as the default.
- A Settings page that edits per-source daily times with a time picker and applies changes with an automatic app restart.

### 简体中文

#### 新增

- 默认保存位置：`media_root` 留空即 `/media/timelapse`，每个源留空即 `<根目录>/<名称>`。
- 每个源可配置 `filename_format`，默认使用计划触发时间。
- 新增设置页：用时间选择器编辑每个源的每日时间点，保存后自动重启应用生效。

## [0.2.0-alpha2](https://github.com/lachesism233/hassio-addons/commit/b2c244d) - 2026-09-14

*Pre-release 预发布*

### English

#### Added

- "Capture now" and "Capture all now" buttons in the gallery (backed by `POST /api/capture`) to capture immediately, ignoring the schedule.

### 简体中文

#### 新增

- 图库新增「立即抓拍」与「全部立即抓拍」按钮（由 `POST /api/capture` 提供），忽略计划立即抓拍，便于调试。

## [0.2.0-alpha1](https://github.com/lachesism233/hassio-addons/commit/9a94636) - 2026-09-14

*Pre-release 预发布*

### English

#### Added

- Scheduled capture engine: per-source daily times and fixed intervals, with configuration validation.
- Automatic retries with a configurable wait between attempts.
- Atomic writes (temp file + rename), so partial downloads never appear in the gallery.
- Retention cleanup (`keep_days`) that only touches each source's own folder.
- Built-in gallery over HTTP, with Simplified Chinese and English option translations.
- A `latest.jpg` per source for dashboards.

### 简体中文

#### 新增

- 定时抓拍引擎：每个源可配置每日时间点与固定间隔，并进行配置校验。
- 失败自动重试，重试间隔可配置。
- 原子写入（临时文件 + 重命名），半截文件不会出现在浏览页。
- 过期清理（`keep_days`），且仅作用于各源自己的目录。
- 内置 HTTP 浏览面板，配置项提供简体中文与英文翻译。
- 每个源提供 `latest.jpg`，便于仪表盘显示最新画面。

## [0.1.0](https://github.com/lachesism233/hassio-addons/commit/e7e1fbf) - 2026-09-14

### English

#### Added

- First release: serve timelapse images from `/share/timelapse` over HTTP on port 8099.

### 简体中文

#### 新增

- 首个版本：通过 HTTP（8099 端口）提供 `/share/timelapse` 中的延时摄影图片。
