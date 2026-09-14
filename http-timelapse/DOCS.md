# 延时摄影 (HTTP Timelapse)

无人值守的长期监控延时摄影采集应用：按设定的时间点或固定间隔，向 go2rtc 等 HTTP 端点抓拍 JPEG 快照，
自动进行有效性与重试检查，成功后按日期时间命名保存，并提供一个可在 Home Assistant 侧边栏打开的浏览面板。

## 功能

- **多抓拍源**：可添加任意数量的 URL，每个源独立配置
- **多种触发**：每日时间点（HH:MM，可多条）和/或固定间隔（例如每 5 分钟）
- **可靠性**：请求超时、失败自动重试（次数与等待时间可配）、HTTP 状态码与 JPEG 文件头校验
- **存储**：成功才写盘，文件名 `YYYYMMDD_HHMMSS.jpg`，原子写入，重名自动加后缀
- **latest.jpg**：每个源目录自动维护最新截图，供仪表盘展示
- **自动清理**：每个源可选保留天数，过期截图每日自动删除（默认关闭）
- **可视化配置**：在应用配置页中添加/删除抓拍源并调整参数，字段为中文说明
- **浏览面板**：Home Assistant 侧边栏入口（Ingress），也可映射 8099 端口直接访问

## 安装

1. 设置 → 应用 → 安装应用
2. 右上角菜单 (⋮) → 存储库 → 添加 `https://github.com/lachesism233/hassio-addons`
3. 安装 **延时摄影** 并启动

## 配置

打开应用的 **配置** 标签页，可直接增删抓拍源。等价的 YAML 示例：

```yaml
timezone: Asia/Shanghai
media_root: /share/timelapse
captures:
  - name: Tuya
    url: http://192.168.2.10:1984/api/frame.jpeg?src=Tuya
    directory: /share/timelapse/Tuya
    times:
      - "07:00"
      - "12:00"
      - "18:00"
    interval_minutes: 0
    retries: 3
    retry_wait: 5
    timeout: 10
    min_size: 1024
    keep_days: 0
```

### 全局配置项

| 配置项 | 说明 | 默认值 |
| --- | --- | --- |
| `timezone` | 调度与文件命名的时区；留空自动读取 Home Assistant 时区 | `Asia/Shanghai` |
| `media_root` | 浏览面板的根目录，建议所有抓拍目录放在它下面 | `/share/timelapse` |

### 抓拍源配置项（`captures` 列表中的每一项）

| 配置项 | 必填 | 说明 | 默认值 |
| --- | --- | --- | --- |
| `name` | 是 | 源名称，用于日志和默认存储目录 | - |
| `url` | 是 | 返回 JPEG 的抓拍地址 | - |
| `directory` | 否 | 图片保存目录（容器内路径），留空则使用 `media_root/名称` | - |
| `times` | 否 | 每日抓拍时间点，24 小时制 `HH:MM`，可添加多条 | 无 |
| `interval_minutes` | 否 | 大于 0 时按固定间隔抓拍（分钟） | `0`（关闭） |
| `retries` | 否 | 首次失败后的额外重试次数 | `3` |
| `retry_wait` | 否 | 两次尝试之间的等待秒数 | `5` |
| `timeout` | 否 | 单次 HTTP 请求超时（秒） | `10` |
| `min_size` | 否 | 小于该字节数的响应视为无效 | `1024` |
| `keep_days` | 否 | 大于 0 时每天自动删除超过该天数的截图 | `0`（永久保留） |

> `times` 与 `interval_minutes` 至少配置一个，否则该源不会抓拍（启动日志会有提示）。

## go2rtc 抓拍地址

go2rtc 的单帧 JPEG 接口格式为：

```
http://<go2rtc地址>:1984/api/frame.jpeg?src=<流名称>
```

例如：`http://192.168.2.10:1984/api/frame.jpeg?src=Tuya`

> URL 中含 `?`，在 YAML 中建议使用引号包裹。

## 抓拍与重试逻辑

1. 到点后在后台线程抓拍，多个源互不阻塞；同一源上一次抓拍未结束时跳过本次触发
2. 单次尝试 = 发起请求 + 校验（HTTP 200、大小 ≥ `min_size`、JPEG 文件头 `FF D8 FF`）
3. 失败后等待 `retry_wait` 秒再试，总尝试次数 = 1 + `retries`
4. 全部失败会记录错误日志，不影响之后的调度
5. 成功的文件保存为 `media_root/源/20260914_071500.jpg`，并更新同目录的 `latest.jpg`

若同一秒内产生多张（例如重名），自动命名为 `20260914_071500-1.jpg`、`-2.jpg`……

## 文件与目录

```
/share/timelapse/          <- media_root（share 目录映射到 HA 的 /share）
├── Tuya/
│   ├── 20260914_071500.jpg
│   ├── 20260914_120000.jpg
│   └── latest.jpg         <- 最新一张，方便仪表盘引用
└── Camera2/
    └── ...
```

## 在仪表盘显示最新画面

保留默认的 8099 端口映射后，可在仪表盘中添加图片卡片：

```yaml
type: picture
image: http://<Home Assistant 地址>:8099/Tuya/latest.jpg
```

`latest.jpg` 响应带 `Cache-Control: no-store`，浏览器不会缓存旧画面。

## 浏览面板

- 侧边栏「延时摄影」：通过 Ingress 打开，首页显示每个源的最新截图及时间
- 局域网直接访问：`http://<Home Assistant 地址>:8099/`
- 点击卡片可进入对应目录浏览全部历史截图

## 排错

- **日志**：应用页面 → 日志，会记录每个源的调度信息和每次抓拍的尝试/结果
- **一直失败**：检查 go2rtc 是否可访问、`src` 名称是否正确、URL 是否需要引号
- **没有生成图片**：确认 `times` 或 `interval_minutes` 已配置，且时间格式为 `HH:MM`
- **时间不对**：检查 `timezone`，留空时会自动使用 Home Assistant 的时区

## 说明

- 应用仅映射 `share:rw`，所有截图保存在 `/share` 下，重启后不会丢失
- 若需要更长的录像式延时视频，可在后续版本中加入 ffmpeg 合成功能
