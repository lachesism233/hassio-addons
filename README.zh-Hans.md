# hassio-addons

Home Assistant 应用（App，旧称 Add-on）仓库。

[English](README.md) | **简体中文**

[![添加应用仓库到 Home Assistant](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Flachesism233%2Fhassio-addons)
[![在 Home Assistant 中打开应用](https://my.home-assistant.io/badges/supervisor_addon.svg)](https://my.home-assistant.io/redirect/supervisor_addon/?addon=http_timelapse&repository_url=https%3A%2F%2Fgithub.com%2Flachesism233%2Fhassio-addons)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 应用列表

| 应用 | 说明 |
| --- | --- |
| [延时摄影 (HTTP Timelapse)](http-timelapse/) | 按时间点或间隔抓拍 go2rtc/HTTP 的 JPEG 快照，自动校验与重试，支持多源独立配置与浏览面板 |
| [Heimdall（应用导航面板）](heimdall/) | 把常用网站与自托管服务集中为图标磁贴，支持分组、搜索与图标库 |
| [SRS 流媒体服务器 (SRS Media Server)](srs/) | 实时流媒体服务器：OBS/FFmpeg 推流（RTMP/SRT），HLS、HTTP-FLV、WebRTC 多协议播放 |

## 安装

### 一键安装（推荐）

1. 点击上方 **「添加应用仓库到 Home Assistant」** 按钮并在打开的页面中确认，仓库地址会自动填入应用商店
2. 点击 **「在 Home Assistant 中打开应用」** 按钮，或到应用商店搜索「HTTP Timelapse」进行安装

### 手动安装

上方按钮不可用（例如 Home Assistant 无法通过 `my.home-assistant.io` 访问）时，手动添加仓库：

1. 打开 Home Assistant：**设置 → 应用**，点击 **安装应用**
2. 点击右上角菜单 (⋮)，选择 **存储库**
3. 粘贴仓库地址 `https://github.com/lachesism233/hassio-addons`，点击 **添加** 后关闭窗口
4. 在应用商店找到要安装的应用（如 **HTTP Timelapse**），安装并启动

## 文档

使用说明为中英双语：

- [HTTP Timelapse 使用说明](http-timelapse/DOCS.md) · [更新日志](http-timelapse/CHANGELOG.md)
- [Heimdall 使用说明](heimdall/DOCS.md) · [更新日志](heimdall/CHANGELOG.md)
- [SRS Media Server 使用说明](srs/DOCS.md) · [更新日志](srs/CHANGELOG.md)

## 说明

- 本仓库的应用基于 Home Assistant Supervisor，适用于 Home Assistant OS / Supervised 安装方式

## 支持

- 问题反馈与功能建议请提交 [GitHub Issues](https://github.com/lachesism233/hassio-addons/issues)

## 致谢

- [延时摄影](http-timelapse/) 为本仓库原创应用
- [Heimdall](https://github.com/linuxserver/Heimdall) 由 LinuxServer.io 开发，本应用基于其 [LinuxServer 镜像](https://hub.docker.com/r/linuxserver/heimdall) 打包
- [SRS](https://github.com/ossrs/srs) 为 MIT 协议的实时流媒体服务器，本应用基于其 [官方镜像](https://hub.docker.com/r/ossrs/srs) 打包
- 应用图标版权归各上游项目所有
- 基础镜像来自 [Home Assistant base images](https://github.com/home-assistant/docker-base)

## 许可证

[MIT](LICENSE)
