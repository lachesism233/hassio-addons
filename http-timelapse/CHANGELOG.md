# Changelog 更新日志

All notable changes to the HTTP Timelapse app. / HTTP Timelapse 应用的版本变更记录。

## 1.3.0 - 2026-09-17

**Highlights 本次亮点**

- **Leaner storage**: `latest.jpg` is gone — the newest frame is resolved on the fly, and a stable virtual URL keeps dashboards working.
- **A more comfortable gallery**: larger thumbnails on desktop, a featured "Latest capture" tile, and an "All" page size that pairs with lazy loading.
- **Clearer configuration**: rewritten option descriptions with examples and documented value ranges; the retry limit is raised to 50.

- **更精简的存储**：不再生成 `latest.jpg`，最新画面即时定位，稳定的虚拟地址让仪表盘照常使用。
- **更舒适的浏览**：桌面端缩略图更大，「最新抓拍」加大展示，「每页」新增「全部」并与懒加载配合。
- **更清晰的配置**：重写选项说明并补充示例与取值范围，重试上限提升至 50。

**Upgrade notes 升级说明**

- Dashboard cards that used `http://<host>:8099/<source>/latest.jpg` should switch to `http://<host>:8099/latest/<source>.jpg`.

- 仪表盘若使用 `http://<主机>:8099/<源名>/latest.jpg`，请改为 `http://<主机>:8099/latest/<源名>.jpg`。

## 1.2.0 - 2026-09-16

- The web interface follows the browser language: Simplified Chinese for Chinese browsers, English otherwise.

- 网页界面跟随浏览器语言：中文浏览器显示简体中文，其他显示英文。

## 1.1.0 - 2026-09-16

- Rebuilt the capture browser: grid/list views, sorting, paging, lazy loading, pinned latest.jpg and a lightbox.

- 重写抓拍浏览页：网格/列表视图、排序、分页、懒加载、latest.jpg 置顶与灯箱预览。

## 1.0.1 - 2026-09-15

- Bilingual (English / Simplified Chinese) documentation and this changelog.
- English app name, description and sidebar title in the app store.

- 文档与更新日志改为中英双语。
- 应用商店名称、描述与侧边栏标题改为英文。

## 1.0.0 - 2026-09-14

- First stable release: rewritten documentation and concise option descriptions.

- 首个稳定版：重写文档，精简配置项描述。

## 0.3.0-alpha3 - 2026-09-14

- Per-source strict schedule-time naming and generic defaults.

- 每个源可独立开启严格计划时间命名；默认值改为通用值。

## 0.3.0-alpha2 - 2026-09-14

- Fixed the image build to include all Python modules.

- 修复镜像构建，包含全部 Python 模块。

## 0.3.0-alpha1 - 2026-09-14

- Media-root defaults, schedule-time file naming and a time-picker settings page.

- 存储根目录默认值、按计划时间命名与时间选择器设置页。

## 0.2.0-alpha2 - 2026-09-14

- Manual capture trigger for debugging.

- 手动抓拍触发，便于调试。

## 0.2.0-alpha1 - 2026-09-14

- Scheduled capture engine and gallery: per-source daily times/intervals, validation, retries, atomic writes, latest.jpg and retention cleanup.

- 定时抓拍引擎与浏览面板：每源独立的每日时间点/间隔、校验、重试、原子写入、latest.jpg 与过期清理。

## 0.1.0 - 2026-09-14

- Initial skeleton: serve timelapse media over HTTP from a shared folder.

- 初始骨架：通过 HTTP 提供共享目录中的延时摄影文件。
