# HTTP Timelapse

**English** | [简体中文](#简体中文) | [Changelog 更新日志](CHANGELOG.md)

Scheduled JPEG snapshots from go2rtc or any HTTP endpoint, with validation and retries, saved
with the scheduled time in the file name — built for unattended long-term runs.

## Use cases

- **Timelapse**: capture one frame every 5 minutes or every minute, combine them into a video later
- **Regular archive**: record the scene at fixed times of day (morning, noon, evening)
- **Evidence**: retry automatically when the network or the video service is flaky, so frames are rarely lost
- **Live view**: every source keeps a `latest.jpg` that can be shown on a dashboard

## Quick start

1. Install and start the app
2. Open the app **Configuration** tab and click **Add** to create a capture source:
   - **Name**: e.g. `camera1`
   - **Snapshot URL**: e.g. `http://192.168.1.10:1984/api/frame.jpeg?src=camera1`
   - **Daily times**: e.g. `07:00`, `12:00`, `18:00` (can also be edited later with the time picker on the gallery Settings page)
3. Save and restart the app — captures start automatically

Default save location: `/media/timelapse/camera1/snap_20260914_070000.jpg`

## Snapshot URL

go2rtc single-frame endpoint:

```
http://<go2rtc host>:1984/api/frame.jpeg?src=<stream name>
```

Any HTTP endpoint that returns a JPEG directly works; URLs contain `?`, so quote them in YAML.

## Configuration

### Global

| Option | Description | Default |
| --- | --- | --- |
| `timezone` | Timezone used for scheduling and file names | empty (follows HA) |
| `media_root` | Storage root, also the gallery root | empty → `/media/timelapse` |

### Per capture source

| Option | Description | Default |
| --- | --- | --- |
| `name` | Source name (required) | - |
| `url` | Snapshot URL (required) | - |
| `times` | Daily times `HH:MM`, multiple entries | none |
| `interval_minutes` | Capture every N minutes; works alongside daily times | `0` (off) |
| `directory` | Custom directory | empty → `<root>/<name>` |
| `filename_format` | File name format | `snap_%Y%m%d_%H%M%S.jpg` |
| `strict_schedule_time` | Name files with the scheduled time | on |
| `retries` | Extra attempts after a failure | `3` |
| `retry_wait` | Seconds to wait between attempts | `5` |
| `timeout` | Per-request timeout in seconds | `10` |
| `min_size` | Responses smaller than this many bytes are rejected | `1024` |
| `keep_days` | Delete captures older than N days; 0 keeps everything | `0` |

> Set at least one of `times` and `interval_minutes`, otherwise the source never captures automatically.

## File names and time

Default `snap_%Y%m%d_%H%M%S.jpg`, where the time part is the **scheduled time**:

- With **strict scheduled time** on: a 07:00 capture that only succeeds at 07:05 after retries is still named `snap_20260914_070000.jpg`
- With it off: the actual save time is used
- Manual captures always use the actual time
- Name collisions in the same second get a suffix, e.g. `snap_20260914_070000-1.jpg`

## Gallery and settings

Open the gallery from the sidebar **HTTP Timelapse** (or directly via `http://<HA host>:8099/`):

- **Home**: latest snapshot and last capture time per source; click a source card to open the capture browser
- **Capture now / Capture all now**: for debugging, ignores the schedule and captures immediately
- **Settings**: edit per-source daily times with a time picker; saving restarts the app automatically
- **Capture browser** (one page per source):
  - grid/list view toggle, remembered per browser
  - sort by time, file name or size, each in both directions
  - 30 / 60 / 120 items per page
  - grid images are loaded lazily, only when they scroll into view
  - `latest.jpg` is pinned at the top, outside sorting and paging
  - click an image to open the built-in lightbox: `←` / `→` to switch, `Esc` to close, or open the original in a new tab
  - a back-to-home link returns to the gallery

## Show the latest frame on a dashboard

```yaml
type: picture
image: http://<Home Assistant host>:8099/camera1/latest.jpg
```

## Directory layout

```
/media/timelapse/              <- storage root (/media is mapped)
├── camera1/
│   ├── snap_20260914_070000.jpg
│   ├── snap_20260914_120000.jpg
│   └── latest.jpg             <- most recent capture
└── camera2/
```

## Troubleshooting

- **Logs**: app page → Logs; every schedule run and capture result is logged
- **Always failing**: check that the URL is reachable, `src` is correct and the URL is quoted
- **No images**: make sure `times` or `interval_minutes` is set
- **File name is the actual time**: turn on strict scheduled time for that source
- **Wrong time**: check the timezone option; empty follows Home Assistant
- **Settings page fails to save**: look for `settings` / `web` entries in the logs

## Notes

- The app can write to the Home Assistant `media` and `share` folders; captures default to `/media/timelapse`
- Cleanup only touches each source's own directory; `latest.jpg` is never deleted

---

# 简体中文

按设定的时间点或固定间隔，向 go2rtc 等 HTTP 接口抓拍 JPEG 快照，自动校验和重试，
按计划时间命名保存，无人值守长期运行。

## 用途

- **延时摄影**：每 5 分钟、每 1 分钟抓拍一帧，后期合成延时视频
- **定期留档**：每天固定时刻（如早中晚）各记录一张现场画面
- **监控取证**：网络波动或视频服务异常时自动重试，尽量不丢帧
- **实时展示**：每个源维护 `latest.jpg`，可在仪表盘显示最新画面

## 快速开始

1. 安装并启动本应用
2. 打开应用 **配置** 页，点击「添加」创建抓拍源：
   - **名称**：如 `camera1`
   - **抓拍地址**：如 `http://192.168.1.10:1984/api/frame.jpeg?src=camera1`
   - **每日时间点**：如 `07:00`、`12:00`、`18:00`（也可稍后在浏览面板用时间选择器编辑）
3. 保存并重启应用，即可自动抓拍

默认保存位置：`/media/timelapse/camera1/snap_20260914_070000.jpg`

## 抓拍地址

go2rtc 单帧接口：

```
http://<go2rtc地址>:1984/api/frame.jpeg?src=<流名称>
```

任何直接返回 JPEG 的 HTTP 地址都可以使用；URL 含 `?`，在 YAML 中建议加引号。

## 配置项

### 全局

| 配置项 | 说明 | 默认值 |
| --- | --- | --- |
| `timezone` | 调度与文件命名的时区 | 留空（跟随 HA） |
| `media_root` | 存储根目录，同时是浏览面板根目录 | 留空即 `/media/timelapse` |

### 每个抓拍源

| 配置项 | 说明 | 默认值 |
| --- | --- | --- |
| `name` | 源名称（必填） | - |
| `url` | 抓拍地址（必填） | - |
| `times` | 每日时间点 `HH:MM`，可多条 | 无 |
| `interval_minutes` | 按固定间隔抓拍（分钟），与时间点可同时使用 | `0`（关闭） |
| `directory` | 自定义保存目录 | 留空即 `根目录/名称` |
| `filename_format` | 文件名格式 | `snap_%Y%m%d_%H%M%S.jpg` |
| `strict_schedule_time` | 严格计划时间命名 | 开启 |
| `retries` | 失败后的额外重试次数 | `3` |
| `retry_wait` | 重试等待秒数 | `5` |
| `timeout` | 单次请求超时秒数 | `10` |
| `min_size` | 小于该字节数的响应视为无效 | `1024` |
| `keep_days` | 超过天数自动清理，0 永久保留 | `0` |

> `times` 与 `interval_minutes` 至少填一个，否则该源不会自动抓拍。

## 文件名与时间

默认 `snap_%Y%m%d_%H%M%S.jpg`，时间部分为**计划触发时间**：

- 开启「严格计划时间命名」：07:00 的抓拍，即使重试到 07:05 成功，文件名仍是 `snap_20260914_070000.jpg`
- 关闭：使用图片实际保存时间
- 手动抓拍：始终使用实际时间
- 同一秒重名时自动加后缀，如 `snap_20260914_070000-1.jpg`

## 浏览与设置

通过侧边栏「HTTP Timelapse」打开浏览面板（也可用 `http://<HA地址>:8099/` 直接访问）：

- **首页**：每个源的最新截图、最近抓拍时间；点击卡片进入抓拍浏览页
- **立即抓拍 / 全部立即抓拍**：调试用，忽略计划立即抓拍一张
- **设置**：用时间选择器编辑每个源的每日时间点，保存并自动重启生效
- **抓拍浏览页**（每个源一个页面）：
  - 网格 / 列表视图切换，按浏览器记忆偏好
  - 按时间、文件名或大小排序，各支持正反序
  - 每页 30 / 60 / 120 张
  - 网格图片懒加载，滚动到可视区域才会下载
  - `latest.jpg` 置顶「最新抓拍」，不参与排序与分页
  - 点击图片打开内置灯箱：`←` / `→` 切换、`Esc` 关闭，也可在新标签页打开原图
  - 「返回首页」链接回到浏览面板

## 仪表盘显示最新画面

```yaml
type: picture
image: http://<Home Assistant 地址>:8099/camera1/latest.jpg
```

## 目录结构

```
/media/timelapse/              <- 存储根目录（/media 已映射）
├── camera1/
│   ├── snap_20260914_070000.jpg
│   ├── snap_20260914_120000.jpg
│   └── latest.jpg             <- 最新一张
└── camera2/
```

## 排错

- **日志**：应用页面 → 日志，包含调度与每次抓拍的结果
- **一直失败**：检查地址是否可访问、`src` 名称是否正确、URL 是否加了引号
- **没有生成图片**：确认已填写时间点或间隔
- **文件名是实际时间**：打开该源的「严格计划时间命名」
- **时间不对**：检查时区设置，留空会跟随 Home Assistant
- **设置页保存失败**：查看日志中的 `settings` / `web` 记录

## 说明

- 应用可写入 Home Assistant 的 `media` 与 `share` 目录，默认截图保存在 `/media/timelapse`
- 清理仅作用于各源自己的目录，`latest.jpg` 不会被删除
