# HZC - Hetzner 流量保护面板

面向 Hetzner 的轻量运维工具：
**流量监控 + 重建策略 + 快照管理 + Telegram 一键运维 + Web 一键升级**。

> 设计目标：简单、稳、可追踪、可恢复。

---

## 功能亮点

- 服务器状态与流量总览（含每日趋势）
- 手动重建（保留原 IP 重建新机）
- 自动重建策略（按阈值触发）
- 快照管理（创建 / 删除 / 重命名）
- 删除服务器（可选保留 IPv4/IPv6）
- Telegram 机器人快捷操作
- Web / TG 一键升级 + 升级日志

---

## 页面截图

### 仪表盘

![HZC Dashboard](docs/screenshots/dashboard.jpg)

### 手机端创建弹窗（已支持可滚动）

![Mobile Create Modal](docs/screenshots/mobile-create-modal.jpg)

---

## 小白快速安装（Debian 推荐）

如果你是第一次使用，推荐直接用下面的 **一键脚本菜单**。脚本会帮你安装 Docker、拉取项目、创建配置文件，并直接拉取 GitHub Actions 构建好的镜像启动面板。

### 第 1 步：准备 Hetzner Token

1. 打开 Hetzner Cloud 控制台。
2. 进入你的 Project。
3. 找到 **Security → API Tokens**。
4. 点击 **Generate API token**。
5. 权限请选择 **Read & Write**，否则无法创建、删除、重建服务器。
6. 复制生成的 Token，后面安装时会用到。

> 注意：Token 只会显示一次，请先保存好。

### 第 2 步：登录你的服务器

用 SSH 登录你准备安装面板的机器：

```bash
ssh root@你的服务器IP
```

如果你不是 root 用户，请先切换到 root，或者在命令前加 `sudo`。

### 第 3 步：运行一键安装脚本

复制下面这一行，在服务器终端里粘贴执行：

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/WonderMaker123/hzc/main/scripts/bootstrap.sh)
```

脚本启动后，按菜单提示选择安装即可。安装过程中如果提示填写 `HETZNER_TOKEN`，就粘贴第 1 步复制的 Token。

也可以直接跳过菜单，一行命令安装：

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/WonderMaker123/hzc/main/scripts/bootstrap.sh) install
```

### 第 4 步：打开面板

安装完成后，在浏览器打开：

```text
http://你的服务器IP:1227
```

例如你的服务器 IP 是 `1.2.3.4`，就打开：

```text
http://1.2.3.4:1227
```

### 第 5 步：确认是否运行成功

在服务器上执行：

```bash
docker ps
```

如果看到 `hetzner-traffic-guard`，说明容器已经启动。

也可以查看日志：

```bash
docker logs -f hetzner-traffic-guard
```

---

## 常用管理命令

下面这些命令都在服务器终端执行。

### 查看状态

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/WonderMaker123/hzc/main/scripts/bootstrap.sh) status
```

### 升级到最新版

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/WonderMaker123/hzc/main/scripts/bootstrap.sh) upgrade
```

### 卸载

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/WonderMaker123/hzc/main/scripts/bootstrap.sh) uninstall
```

---

## Docker 用户安装方式

如果你的机器已经有 Docker，也可以直接用 Docker Compose 拉取 GitHub 构建好的镜像启动，不需要在服务器本地编译。

### 第 1 步：克隆项目

```bash
git clone https://github.com/WonderMaker123/hzc.git
cd hzc
```

### 第 2 步：创建 `.env` 配置文件

```bash
cp .env.example .env 2>/dev/null || touch .env
nano .env
```

把下面内容填进去，并把 `你的HetznerToken` 改成你自己的 Token：

```env
HETZNER_TOKEN=你的HetznerToken
TRAFFIC_LIMIT_TB=20
ROTATE_THRESHOLD=0.98
CHECK_INTERVAL_MINUTES=5
SAFE_MODE=true
TZ=Asia/Shanghai
```

保存方式：

- `nano` 里按 `Ctrl + O` 保存
- 按 `Enter` 确认
- 按 `Ctrl + X` 退出

### 第 3 步：拉取镜像并启动面板

```bash
docker compose pull
docker compose up -d
```

如果你的系统使用旧版 Compose，可以执行：

```bash
docker-compose pull
docker-compose up -d
```

### 第 4 步：访问面板

```text
http://你的服务器IP:1227
```

---

## Docker Compose 配置示例

如果你想手动创建 `docker-compose.yml`，可以参考下面配置：

```yaml
services:
  hetzner-traffic-guard:
    image: ghcr.io/wondermaker123/hzc:latest
    container_name: hetzner-traffic-guard
    restart: unless-stopped
    ports:
      - "1227:1227"
    env_file:
      - .env
    dns:
      - 1.1.1.1
      - 8.8.8.8
    volumes:
      - ./state:/app/state
      - ./:/opt/hzc
      - /var/run/docker.sock:/var/run/docker.sock
```

> `/var/run/docker.sock` 用于 Web / Telegram 一键升级。它权限较高，如果你把面板暴露到公网，请务必做好访问限制。

---

## GitHub 镜像说明

本项目已经配置 GitHub Actions 自动构建 Docker 镜像：

- 镜像地址：`ghcr.io/wondermaker123/hzc:latest`
- 每次推送到 `main` 分支后，GitHub 会自动构建并推送 `latest` 镜像。
- 推送 `v*` 标签时，也会生成对应版本标签。
- Pull Request 会执行构建检查，但不会推送镜像。

如果你 fork 了本项目，需要在 GitHub 仓库设置里确认 **Actions → General → Workflow permissions** 允许 `Read and write permissions`，这样 GitHub Actions 才能推送 GHCR 镜像。

---

## 一键升级

### Web / TG 一键升级

- 页面顶部：`🚀 一键升级`
- Telegram：`/upgrade`

### 命令行升级（兜底）

```bash
cd hzc
./scripts/upgrade.sh
```

升级逻辑：

- 拉取 `origin/main`
- 已最新则不重复升级
- 有新版本自动拉取 GitHub 镜像并更新容器
- 升级后自动健康检查 `/api/ping`
- 自动清理部分历史镜像/构建缓存（降低磁盘堆积）

---

## 首次使用建议

### 1. 先保持安全模式开启

默认参数：

- `SAFE_MODE=true`（只告警，不自动执行危险动作）
- `ROTATE_THRESHOLD=0.98`
- `CHECK_INTERVAL_MINUTES=5`

建议先观察流量数据是否正常，再逐步开启自动化操作。

### 2. 自动重建前先创建快照

自动重建需要选择镜像或快照。建议先在面板里创建一个可用快照，再配置自动重建策略。

### 3. 不建议直接裸奔公网

面板包含重建、删除、重置密码、一键升级等高权限操作。建议至少做到其中一种：

- 只允许自己的 IP 访问 `1227` 端口
- 使用 Nginx / Caddy 加密码
- 使用 Cloudflare Access
- 通过 SSH 隧道访问

---

## 常用环境变量

### 必填

- `HETZNER_TOKEN`：Hetzner API Token，必须是 Read & Write 权限

### 常用

- `TRAFFIC_LIMIT_TB`：每台机器的月流量额度，默认 `20`
- `ROTATE_THRESHOLD`：全局告警 / 重建阈值，默认 `0.98`
- `CHECK_INTERVAL_MINUTES`：检查间隔分钟数，默认 `5`
- `SAFE_MODE`：安全模式，默认 `true`
- `APP_VERSION`：前端显示版本号
- `TZ`：时区，例如 `Asia/Shanghai`

### Telegram（可选）

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

### qB（可选）

- `QB_URL`
- `QB_USERNAME`
- `QB_PASSWORD`

---

## 常见问题

### 1) 打不开面板怎么办？

先确认容器是否运行：

```bash
docker ps
```

再看日志：

```bash
docker logs -f hetzner-traffic-guard
```

如果容器正常，但浏览器打不开，请检查服务器防火墙 / 安全组是否放行 `1227` 端口。

### 2) 提示 HETZNER_TOKEN missing 怎么办？

说明 `.env` 里没有正确配置 `HETZNER_TOKEN`。

进入项目目录后编辑：

```bash
cd hzc
nano .env
```

确认里面有类似下面这一行：

```env
HETZNER_TOKEN=你的HetznerToken
```

保存后重启：

```bash
docker compose restart
```

### 3) 页面样式旧 / 按钮位置异常

先强刷浏览器：

- Windows/Linux: `Ctrl + Shift + R`
- macOS: `Cmd + Shift + R`

### 4) 一键升级“触发了但版本没变”

优先看：

- `/api/ping`
- TG 的“升级日志”（`/upgradelog`）

### 5) 升级失败怎么查？

```bash
docker logs -f hetzner-traffic-guard
```

并结合：

```bash
cd hzc
./scripts/upgrade.sh
```

---

## 免责声明

关闭 `SAFE_MODE` 后，自动动作可能涉及重建/删除。  
请先在测试环境验证，再用于生产。
