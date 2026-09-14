# Heimdall

**English** | [简体中文](#简体中文) | [Changelog 更新日志](CHANGELOG.md)

The [LinuxServer](https://github.com/linuxserver/Heimdall) build of Heimdall: an application dashboard
that turns your favourite sites and self-hosted services into icon tiles, with groups, a search bar and
an icon library. It can serve as your browser start page.

## Quick start

1. Install and start the app (the first start initialises the database, usually 10 seconds to 1 minute depending on the device)
2. Click the app page's **Open Web UI** button, or go to `http://<Home Assistant host>:10000`
3. Log in and add tiles: enter a name and a URL, pick an icon

The defaults work out of the box; no option has to be changed.

## Options

| Option | Description | Default |
| --- | --- | --- |
| `timezone` | Container timezone; when empty the Home Assistant timezone is used, falling back to UTC | empty (follows HA) |
| `allow_internal_requests` | Allow Heimdall to make lookup requests to private/reserved IP addresses (needed to fetch titles/icons for internal URLs) | `true` |

> The defaults target pure-LAN setups. If you expose Heimdall to the internet through a reverse proxy, set this to `false` to enable SSRF protection.

## Data and backup

- App data lives in HA's `/addon_configs/<repository id>_heimdall` (mounted as `/config` in the container) and contains the SQLite database, `.env` (APP_KEY), icons and background images
- The directory is backed up and restored together with the app; uninstalling the app does not delete it
- On first start the data directory is chowned to `abc` (911) — this is normal

## Access and sidebar

- The app does not use HA ingress (Heimdall cannot be served under a sub-path), so it is always available on the fixed host port **10000**
- For a sidebar entry, add a **webpage** card to a dashboard with the URL `http://<Home Assistant host>:10000`
- If port 10000 is taken, open the app's **Network** settings and change the host port

## Troubleshooting

- Check the startup log under HA → Apps → Heimdall → Logs; the normal order is s6 init → nginx/php-fpm
- The first page load is slow (database migration and seed data run automatically)
- Changes to `allow_internal_requests` take effect after restarting the app

---

# 简体中文

基于 [LinuxServer](https://github.com/linuxserver/Heimdall) 打包的 Heimdall 镜像：把常用网站与自托管服务集中为图标磁贴的导航面板，支持分组、搜索栏与图标库，可作为浏览器起始页。

## 快速开始

1. 安装并启动本应用（首次启动需要初始化，通常 10 秒 ~ 1 分钟，视设备性能而定）
2. 点击应用页面的「打开 Web UI」，或直接访问 `http://<Home Assistant 地址>:10000`
3. 在界面中登录并添加磁贴：填写名称、URL，选择图标即可

默认配置即可直接使用，无需修改任何配置项。

## 配置项

| 配置项 | 说明 | 默认值 |
| --- | --- | --- |
| `timezone` | 容器时区；留空时自动读取 Home Assistant 的时区，读取失败则回退 UTC | 留空（跟随 HA） |
| `allow_internal_requests` | 允许 Heimdall 向私有/保留 IP 地址发起查找请求（填内网 URL 自动抓取标题/图标需要它） | `true` |

> 默认值面向纯内网使用场景。若通过反向代理把 Heimdall 暴露到公网，请改为 `false`，以启用 SSRF 防护。

## 数据与备份

- 应用数据保存在 HA 的 `/addon_configs/<仓库标识>_heimdall`（容器内挂载为 `/config`），包含 SQLite 数据库、`.env`（APP_KEY）、图标与背景图
- 该目录随应用一起备份与恢复；卸载应用不会自动删除数据
- 首次启动时数据目录会被初始化为 `abc`(911) 属主，属正常现象

## 访问方式与侧边栏

- 本应用不使用 HA ingress（Heimdall 不支持子路径代理），固定使用主机端口 **10000**
- 如需侧边栏入口，可在仪表盘中添加「网页」卡片，URL 填 `http://<Home Assistant 地址>:10000`
- 若 10000 端口被占用，可在应用页面的 **网络** 设置中修改主机端口

## 故障排查

- 在 HA 的 应用 → Heimdall → 日志 中查看启动日志，正常顺序为 s6 初始化 → nginx/php-fpm 启动
- 首次打开页面较慢属正常现象（自动执行数据库迁移与种子数据）
- `allow_internal_requests` 修改后需重启应用生效
