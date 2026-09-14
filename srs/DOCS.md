# SRS Media Server

**English** | [简体中文](#简体中文) | [Changelog 更新日志](CHANGELOG.md)

Realtime media server based on [SRS](https://github.com/ossrs/srs) (6.0 stable): ingest from OBS or
FFmpeg over RTMP/SRT, play over HLS, HTTP-FLV or WebRTC — handy for bringing a camera or an OBS
scene into Home Assistant.

## Quick start

1. Install and start the app (the first start takes only a few seconds)
2. Push from OBS:
   - Service: **Custom**
   - Server: `rtmp://<Home Assistant host>:1935/live`
   - Stream key: `livestream` (the stream name; any name works)
3. Playback (replace `<HA>` with the Home Assistant host IP or domain):

| Protocol | URL | Latency | Notes |
| --- | --- | --- | --- |
| HLS | `http://<HA>:8080/live/livestream.m3u8` | ~10 s | Best compatibility; works in VLC and HA |
| HTTP-FLV | `http://<HA>:8080/live/livestream.flv` | ~1 s | Needs an FLV-capable player (e.g. HA's go2rtc) |
| WebRTC | WebRTC player page under `http://<HA>:8080/players/` | <1 s | See the WebRTC section below |

> In HA, put the HLS or HTTP-FLV URL into the go2rtc `streams` configuration, or add a **webpage** card pointing at the built-in player page.

## WebRTC

- In bridge mode SRS auto-detects the container IP, which browsers cannot reach: **set "WebRTC candidate" to the HA host's LAN IP** (see Settings → System → Network, e.g. `192.168.1.10`), save and restart the app
- Play from the WebRTC page under `http://<HA>:8080/players/`, or connect a WHIP/WHEP client to `http://<HA>:1985/rtc/v1/whep/?app=live&stream=livestream`
- If UDP is blocked, enable "WebRTC over TCP" and map TCP 8000 to the host

## SRT

Enable "SRT server" and restart; OBS can then push over SRT (more resilient to packet loss):

- URL: `srt://<HA>:10080?streamid=#!::r=live/livestream,m=publish`

## Access

- The app does not use ingress (playback needs ports 8080/1985/8000, which a single-port proxy cannot cover); open `http://<HA>:8080` directly
- The app page's **Open Web UI** button opens the same address; you can also add a **webpage** card pointing at it

## Options

| Option | Description | Default |
| --- | --- | --- |
| `timezone` | Container timezone for log timestamps; empty means UTC | empty |
| `log_level` | Log level: `trace`/`debug`/`info`/`warn`/`error` | `info` |
| `webrtc_candidate` | Address advertised in the WebRTC SDP; set to the HA host LAN IP | empty (auto) |
| `webrtc_tcp_enabled` | Also enable WebRTC over TCP (TCP 8000) | `false` |
| `srt_enabled` | Enable the SRT ingest server (UDP 10080) | `false` |

## Ports

| Port | Purpose | Notes |
| --- | --- | --- |
| 1935/tcp | RTMP ingest | Host port editable on the app page |
| 1985/tcp | HTTP API | Host port editable on the app page |
| 8080/tcp | HLS/HTTP-FLV/player pages | Host port editable on the app page (used by "Open Web UI") |
| 8000/udp | WebRTC media | **Do not remap** (the SDP always advertises port 8000) |
| 8000/tcp | WebRTC over TCP | Only active when the matching option is enabled |
| 10080/udp | SRT ingest | Only active when the matching option is enabled |

## Custom SRS configuration

- The default config is generated from the app options; no manual maintenance needed
- Advanced: put your own `srs.conf` in the host's `/addon_configs/<repository id>_srs/` (mounted as `/addon_config`). On start the app uses it as-is and skips option generation; restart the app after editing
- Syntax reference: upstream [full.conf](https://github.com/ossrs/srs/blob/v6.0-r1/trunk/conf/full.conf)

## HTTP API examples

```bash
curl http://<HA>:1985/api/v1/versions
curl http://<HA>:1985/api/v1/streams
curl http://<HA>:1985/api/v1/clients
```

> The API has no authentication by default. Never expose port 1985 to the internet; if you need remote access, put it behind a reverse proxy with access control.

## Data and logs

- App logs: the app page's Logs tab (SRS logs to the container console; HTML is escaped to plain text)
- HLS segments are generated inside the container and are cleared on restart (normal for live streaming)
- User data directory: `/addon_configs/<repository id>_srs/`, where a custom `srs.conf` goes

## Troubleshooting

- Push fails: make sure the OBS server is `rtmp://<HA>:1935/live` and the key is just the stream name (no `rtmp://` prefix or app name)
- Port conflict: change the host ports for 1935/1985/8080 on the app page's Network tab (not 8000/udp)
- WebRTC fails: verify `webrtc_candidate` is the HA host LAN IP; check ICE candidates and errors in the browser dev tools
- Check the service: `curl http://<HA>:1985/api/v1/versions` should return version info

---

# 简体中文

基于 [SRS](https://github.com/ossrs/srs)（6.0 稳定版）的实时流媒体服务器：OBS/FFmpeg 推流（RTMP/SRT），HLS、HTTP-FLV、WebRTC 多协议播放，适合把摄像头或 OBS 画面接入 Home Assistant。

## 快速开始

1. 安装并启动本应用（首次启动只需数秒）
2. 用 OBS 推流：
   - 服务：**自定义**
   - 服务器：`rtmp://<Home Assistant 地址>:1935/live`
   - 串流密钥：`livestream`（即流名，可任意命名）
3. 播放（把 `<HA>` 换成 Home Assistant 的主机 IP 或域名）：

| 协议 | 地址 | 延迟 | 说明 |
| --- | --- | --- | --- |
| HLS | `http://<HA>:8080/live/livestream.m3u8` | ~10 秒 | 兼容性最好，VLC/HA 通用 |
| HTTP-FLV | `http://<HA>:8080/live/livestream.flv` | ~1 秒 | 需支持 FLV 的播放器（如 HA 的 go2rtc） |
| WebRTC | `http://<HA>:8080/players/` 中的 WebRTC 播放页 | <1 秒 | 见下方「WebRTC」章节 |

> 在 HA 中使用时，推荐把 HLS 或 HTTP-FLV 地址填进 go2rtc 的 `streams` 配置，或添加「网页」卡片直接打开 SRS 内置播放页。

## WebRTC

- 桥接网络下 SRS 自动探测到的是容器内网 IP，浏览器无法直达：**请把「WebRTC 对外地址」填为 HA 主机的局域网 IP**（在 HA 的「设置 → 系统 → 网络」中查看，如 `192.168.1.10`），保存后重启应用生效
- 播放方式：打开 `http://<HA>:8080/players/` 中的 WebRTC 播放页，或用支持 WHIP/WHEP 的客户端连接 `http://<HA>:1985/rtc/v1/whep/?app=live&stream=livestream`
- 若网络封锁 UDP，可打开「启用 WebRTC over TCP」，并把 TCP 8000 映射到主机后使用

## SRT

打开「启用 SRT 服务器」并重启后，OBS 可用 SRT 推流（抗丢包能力更强）：

- URL：`srt://<HA>:10080?streamid=#!::r=live/livestream,m=publish`

## 访问方式

- 本应用未启用 ingress（SRS 播放依赖 8080/1985/8000 多个端口，单端口代理无法工作），请直接访问 `http://<HA>:8080`
- 应用页的「打开 Web UI」按钮会打开同一地址；也可在仪表盘中添加「网页」卡片指向它

## 配置项

| 配置项 | 说明 | 默认值 |
| --- | --- | --- |
| `timezone` | 容器时区，影响日志时间戳；留空为 UTC | 留空 |
| `log_level` | 日志级别：`trace`/`debug`/`info`/`warn`/`error` | `info` |
| `webrtc_candidate` | WebRTC SDP 中通告的地址，填 HA 主机局域网 IP | 留空（自动探测） |
| `webrtc_tcp_enabled` | 额外启用 WebRTC over TCP（TCP 8000） | `false` |
| `srt_enabled` | 启用 SRT 推流服务（UDP 10080） | `false` |

## 端口

| 端口 | 用途 | 备注 |
| --- | --- | --- |
| 1935/tcp | RTMP 推流 | 主机端口可在应用页面修改 |
| 1985/tcp | HTTP API | 主机端口可在应用页面修改 |
| 8080/tcp | HLS/HTTP-FLV/内置播放页 | 主机端口可在应用页面修改（「打开 Web UI」使用此端口） |
| 8000/udp | WebRTC 媒体 | **不要修改主机映射**（SDP 中通告的端口固定为 8000） |
| 8000/tcp | WebRTC over TCP | 仅在开启对应选项后有效 |
| 10080/udp | SRT 推流 | 仅在开启对应选项后有效 |

## 自定义 SRS 配置

- 默认配置由应用选项生成，无需手动维护
- 进阶用法：在主机 `/addon_configs/<仓库标识>_srs/`（容器内挂载为 `/addon_config`）放置 `srs.conf`，应用启动时会完全使用它并跳过选项生成；修改后重启应用生效
- 配置语法见上游 [full.conf](https://github.com/ossrs/srs/blob/v6.0-r1/trunk/conf/full.conf)

## HTTP API 示例

```bash
curl http://<HA>:1985/api/v1/versions
curl http://<HA>:1985/api/v1/streams
curl http://<HA>:1985/api/v1/clients
```

> 默认 API 无鉴权，请勿把 1985 端口直接暴露到公网；如需公网访问请经反向代理并自行增加访问控制。

## 数据与日志

- 应用日志：应用页面「日志」标签（SRS 输出到容器控制台，HTML 日志转义为文本显示）
- HLS 切片在容器内生成，重启后清空（直播场景正常现象）
- 用户数据目录：`/addon_configs/<仓库标识>_srs/`，自定义 `srs.conf` 放在这里

## 故障排查

- 推流失败：确认 OBS 服务器地址为 `rtmp://<HA>:1935/live`，密钥只填流名（不要带 `rtmp://` 前缀或应用名）
- 端口占用：在应用页面「网络」中修改 1935/1985/8080 的主机端口（8000/udp 除外）
- WebRTC 失败：确认 `webrtc_candidate` 已填 HA 主机局域网 IP；浏览器 F12 查看 ICE 候选与报错
- 确认服务是否正常：`curl http://<HA>:1985/api/v1/versions` 应返回版本信息
