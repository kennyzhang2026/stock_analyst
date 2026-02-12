# Stock Analyst 云端部署指南

> 版本：v1.0
> 适用于：主机屋（1H1G5M）或其他类似配置的云服务器
> 更新日期：2026-02-12

---

## 部署架构

```
┌─────────────────────────────────────────────┐
│              用户（浏览器）                   │
└─────────────────┬───────────────────────────┘
                  │ HTTP
┌─────────────────▼───────────────────────────┐
│              Nginx (80端口)                  │
│         反向代理 + 静态文件                   │
└─────────────────┬───────────────────────────┘
                  │ HTTP (127.0.0.1:5000)
┌─────────────────▼───────────────────────────┐
│         Gunicorn + Flask App                 │
│         (2 workers, 2 threads each)          │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│          AkShare (数据API)                    │
└─────────────────────────────────────────────┘
```

---

## 前提条件

1. **云服务器**：主机屋或其他 Linux 服务器（Ubuntu/CentOS）
2. **域名**（可选）：如果有域名，可以配置SSL
3. **本地环境**：用于上传项目文件

---

## 快速部署

### 方法一：使用自动部署脚本（推荐）

```bash
# 1. 在服务器上下载项目
cd /tmp
git clone <your-repo-url> stock_analyst
cd stock_analyst

# 2. 运行部署脚本
chmod +x deploy/deploy.sh
sudo ./deploy/deploy.sh
```

### 方法二：手动部署

#### 步骤1：更新系统并安装依赖

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx

# CentOS
sudo yum update -y
sudo yum install -y python3 python3-pip nginx
```

#### 步骤2：创建项目目录

```bash
sudo mkdir -p /opt/stock_analyst
sudo chown $USER:$USER /opt/stock_analyst
cd /opt
```

#### 步骤3：上传项目文件

使用 SCP、SFTP 或 Git：

```bash
# 使用 Git
git clone <your-repo-url> stock_analyst

# 或使用 SCP（从本地）
scp -r stock_analyst/* user@your-server:/opt/stock_analyst/
```

#### 步骤4：创建虚拟环境并安装依赖

```bash
cd /opt/stock_analyst
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### 步骤5：配置 Nginx

```bash
# 复制配置文件
sudo cp deploy/nginx.conf /etc/nginx/sites-available/stock_analyst

# 修改域名（如需要）
sudo nano /etc/nginx/sites-available/stock_analyst
# 将 your-domain.com 改为你的域名或服务器IP

# 启用站点
sudo ln -s /etc/nginx/sites-available/stock_analyst /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

#### 步骤6：配置 Systemd 服务

```bash
# 复制服务文件
sudo cp deploy/stock_analyst.service /etc/systemd/system/

# 重载并启动服务
sudo systemctl daemon-reload
sudo systemctl enable stock_analyst
sudo systemctl start stock_analyst
```

#### 步骤7：检查服务状态

```bash
# 检查应用服务
sudo systemctl status stock_analyst

# 检查 Nginx
sudo systemctl status nginx

# 查看日志
sudo journalctl -u stock_analyst -f
```

---

## 部署配置说明

### Gunicorn 配置 ([gunicorn_config.py](gunicorn_config.py))

针对 **1H1G5M** 配置优化：

| 参数 | 值 | 说明 |
|------|-----|------|
| workers | 2 | 工作进程数（建议 2 × CPU核心数） |
| threads | 2 | 每进程线程数 |
| worker_class | sync | 同步模式（简单可靠） |
| timeout | 120 | 请求超时时间（秒） |

### Systemd 服务说明

- **用户**：www-data
- **工作目录**：/opt/stock_analyst
- **自动重启**：失败后 10 秒重启
- **日志**：通过 journalctl 查看

---

## 常见问题排查

### 服务无法启动

```bash
# 查看详细日志
sudo journalctl -u stock_analyst -n 50

# 手动测试运行
cd /opt/stock_analyst
source venv/bin/activate
gunicorn -c gunicorn_config.py backend.app:app
```

### 端口被占用

```bash
# 检查端口占用
sudo netstat -tlnp | grep 5000

# 终止占用进程
sudo kill -9 <PID>
```

### Nginx 502 错误

1. 检查 Gunicorn 是否运行：`sudo systemctl status stock_analyst`
2. 检查端口是否正确：配置文件中应为 `http://127.0.0.1:5000`
3. 查看 Nginx 错误日志：`sudo tail -f /var/log/nginx/stock_analyst_error.log`

---

## 更新应用

```bash
# 1. 拉取最新代码
cd /opt/stock_analyst
git pull

# 2. 更新依赖（如有变化）
source venv/bin/activate
pip install -r requirements.txt

# 3. 重启服务
sudo systemctl restart stock_analyst
```

---

## 安全建议

1. **配置防火墙**：只开放 80/443 端口
2. **使用 HTTPS**：配置 Let's Encrypt SSL 证书
3. **定期更新**：保持系统和依赖包最新
4. **限制访问**：可配置 Nginx 基本认证

---

## 资源限制参考（1H1G5M）

| 资源 | 配置 | 说明 |
|------|------|------|
| CPU | 1核 | Gunicorn 2 workers 足够 |
| 内存 | 1GB | 建议留 200MB 给系统 |
| 带宽 | 5Mbps | 约 600KB/s，适合轻量应用 |

---

## 参考资料

- [Gunicorn 官方文档](https://docs.gunicorn.org/)
- [Nginx 反向代理配置](https://nginx.org/en/docs/http/ngx_http_proxy_module.html)
- [Systemd 服务管理](https://www.freedesktop.org/software/systemd/man/systemd.service.html)

---

## 支持

如有问题，请检查：
1. 服务状态：`sudo systemctl status stock_analyst`
2. 应用日志：`sudo journalctl -u stock_analyst -f`
3. Nginx 日志：`sudo tail -f /var/log/nginx/*.log`
