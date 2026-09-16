# Changelog 更新日志

All notable changes to the HTTP Timelapse app. / HTTP Timelapse 应用的版本变更记录。

## 1.2.0 - 2026-09-16

- The web interface now follows the browser language: Simplified Chinese for Chinese browsers, English otherwise.
- 网页界面改为跟随浏览器语言：中文浏览器显示简体中文，其他默认英文。

## 1.1.0 - 2026-09-16

- Rebuilt the per-source capture browser: grid/list toggle remembered per browser, sorting by time/name/size in both directions, 30/60/120 items per page, lazy-loaded grid images, pinned `latest.jpg` and a built-in lightbox.
- 重写每个源的抓拍浏览页：网格/列表视图切换（按浏览器记忆）、按时间/文件名/大小双向排序、每页 30/60/120 张、网格图片懒加载、`latest.jpg` 置顶展示、内置灯箱预览。

## 1.0.1 - 2026-09-15

- Bilingual (English / Simplified Chinese) documentation and this changelog.
- English app name, description and sidebar title in the app store.
- 文档改为中英双语，并新增本更新日志。
- 应用商店名称、描述与侧边栏标题改为英文。

## 1.0.0 - 2026-09-14

- First stable release: rewritten documentation and concise option descriptions.
- 首个稳定版：重写文档，精简配置项描述。

## 0.3.0-alpha3 - 2026-09-14

- Per-source strict scheduled-time file naming; generic defaults.
- 每个源可独立开启「严格计划时间命名」；改用通用默认值。

## 0.3.0-alpha2 - 2026-09-14

- Copy all Python modules into the image.
- 将全部 Python 模块复制进镜像。

## 0.3.0-alpha1 - 2026-09-14

- Media-root defaults, planned-time file names and a time-picker settings page.
- 存储根目录默认值、按计划时间命名，以及时间选择器设置页。

## 0.2.0-alpha2 - 2026-09-14

- Manual capture trigger for debugging.
- 增加手动抓拍触发，便于调试。

## 0.2.0-alpha1 - 2026-09-14

- Scheduled capture engine and gallery: per-source daily times/intervals with validation, retries, atomic writes, `latest.jpg` and retention cleanup; ingress gallery; option translations.
- 定时抓拍引擎与浏览面板：每个源独立的每日时间点/间隔、自动校验、重试、原子写入、`latest.jpg` 与过期清理；内置浏览面板；配置项翻译。

## 0.1.0 - 2026-09-14

- Initial app skeleton: serve timelapse media over HTTP from a shared folder.
- 初始骨架：通过 HTTP 提供共享目录中的延时摄影文件。
