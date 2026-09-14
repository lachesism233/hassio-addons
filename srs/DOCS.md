# SRS 流媒体服务器

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

- 默认配置由应用选项生成，保存在容器内 `/data/srs.conf`
- 进阶用法：在主机 `/addon_configs/<仓库标识>_srs/`（容器内挂载为 `/addon_config`）放置 `srs.conf`，应用启动时会完全使用它并跳过选项生成；修改后重启应用生效
- 配置语法见上游 [full.conf](https://github.com/ossrs/srs/blob/v6.0-r1/trunk/conf/full.conf)

## HTTP API 示例

```bash
curl http://<HA>:1985/api/v1/versions
curl http://<HA>:1985/api/v1/streams
curl http://<HA>:1985/api/v1/clients
```

> 默认 API 无鉴权，请勿把 1985 端口直接暴露到公网；如需公网访问请经反向代理并自行增加访问控制。

## 版本号规则

- 应用版本与上游稳定版保持一致（上游 `6.0.191` 时本应用也是 `6.0.191`）
- 仅修改打包层而不升级上游时，用第四位递增区分，例如 `6.0.191.1`，并同步 `build.yaml` 中的镜像 tag

## 升级

1. 查看上游新版本：https://hub.docker.com/r/ossrs/srs/tags
2. 修改 `build.yaml` 中两个架构的 tag，并把 `config.yaml` 的 `version` 同步为新版本
3. 推送后用户在应用商店更新即可；更新会重建镜像，应用选项与自定义配置不受影响

## 数据与日志

- 应用日志：应用页面「日志」标签（SRS 输出到容器控制台，HTML 日志转义为文本显示）
- HLS 切片默认写入容器内 `/usr/local/srs/objs/nginx/html/live/`，重启后清空（直播场景正常现象）
- 应用数据目录：`/addon_configs/<仓库标识>_srs/`

## 故障排查

- 推流失败：确认 OBS 服务器地址为 `rtmp://<HA>:1935/live`，密钥只填流名（不要带 `rtmp://` 前缀或应用名）
- 端口占用：在应用页面「网络」中修改 1935/1985/8080 的主机端口（8000/udp 除外）
- WebRTC 失败：确认 `webrtc_candidate` 已填 HA 主机局域网 IP；浏览器 F12 查看 ICE 候选与报错
- 确认服务是否正常：`curl http://<HA>:1985/api/v1/versions` 应返回版本信息
