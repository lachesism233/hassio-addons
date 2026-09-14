# Heimdall（应用导航面板）

把常用网站与自托管服务集中为图标磁贴的导航面板，支持分组、搜索栏与图标库，可作为浏览器起始页。

## 快速开始

1. 安装并启动本应用（首次启动需要初始化，通常 10 秒 ~ 1 分钟，视设备性能而定）
2. 点击应用页面的「打开 Web UI」，或直接访问 `http://<Home Assistant 地址>:10000`
3. 在界面中登录并添加磁贴：填写名称、URL，选择图标即可

默认配置即可直接使用，无需修改任何配置项。

## 配置项

| 配置项 | 说明 | 默认值 |
| --- | --- | --- |
| `timezone` | 容器时区；留空时自动读取 Home Assistant 的时区，读取失败则回退 UTC | 留空（跟随 HA） |
| `allow_internal_requests` | 允许 Heimdall 向私有/保留 IP 地址发起查找请求；磁贴指向内网服务并使用在线查找/抓取图标时开启 | `false` |

## 数据与备份

- 应用数据保存在 HA 的 `/addon_configs/<仓库标识>_heimdall`（容器内挂载为 `/config`），包含 SQLite 数据库、`.env`（APP_KEY）、图标与背景图
- 该目录随应用一起备份与恢复；卸载应用不会自动删除数据
- 首次启动时数据目录会被初始化为 `abc`(911) 属主，属正常现象

## 访问方式与侧边栏

- 本应用不使用 HA ingress（Heimdall 不支持子路径代理），容器 80 端口固定映射到主机 **10000**
- 如需侧边栏入口，可在仪表盘中添加「网页」卡片，URL 填 `http://<Home Assistant 地址>:10000`
- 若 10000 端口被占用，修改本应用 `config.yaml` 中的 `80/tcp: 10000` 后重新安装

## 升级

1. 查看上游新版本：https://hub.docker.com/r/linuxserver/heimdall/tags
2. 修改 `build.yaml` 中两个架构的 tag，例如 `arm64v8-2.8.4` 与 `amd64-2.8.4`
3. 提升 `config.yaml` 的 `version`，例如 `1.0.1`
4. 推送后用户在应用商店更新即可；更新会重建镜像，数据与配置不受影响

## 故障排查

- 在 HA 的 应用 → Heimdall → 日志 中查看启动日志，正常顺序为 s6 初始化 → nginx/php-fpm 启动
- 首次打开页面较慢属正常现象（自动执行数据库迁移与种子数据）
- 若因 AppArmor 导致启动失败，可在 `config.yaml` 中增加 `apparmor: false` 后更新应用
- `allow_internal_requests` 修改后需重启应用生效
