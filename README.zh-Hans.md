# hassio-addons

Home Assistant 应用（App，旧称 Add-on）仓库。

[English](README.md) | **简体中文**

[![添加应用仓库到 Home Assistant](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Flachesism233%2Fhassio-addons)
[![在 Home Assistant 中打开应用](https://my.home-assistant.io/badges/supervisor_addon.svg)](https://my.home-assistant.io/redirect/supervisor_addon/?addon=http_timelapse&repository_url=https%3A%2F%2Fgithub.com%2Flachesism233%2Fhassio-addons)

## 应用列表

| 应用 | 说明 |
| --- | --- |
| [延时摄影 (HTTP Timelapse)](http-timelapse/) | 按时间点或间隔抓拍 go2rtc/HTTP 的 JPEG 快照，自动校验与重试，支持多源独立配置与浏览面板 |

## 安装

### 一键安装（推荐）

1. 点击上方 **「添加应用仓库到 Home Assistant」** 按钮并在打开的页面中确认，仓库地址会自动填入应用商店
2. 点击 **「在 Home Assistant 中打开应用」** 按钮，或到应用商店搜索「延时摄影」进行安装

### 手动安装

1. 打开 Home Assistant：**设置 → 应用 → 安装应用**
2. 右上角菜单 (⋮) → **存储库**
3. 添加仓库地址 `https://github.com/lachesism233/hassio-addons`
4. 在应用商店中找到 **延时摄影** 并安装启动

## 文档

- [延时摄影 使用说明](http-timelapse/DOCS.md)

## 说明

- 本仓库的应用基于 Home Assistant Supervisor，适用于 Home Assistant OS / Supervised 安装方式
