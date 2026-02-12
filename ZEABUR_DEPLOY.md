# Stock Analyst - Zeabur 部署指南

> 版本：v1.0
> 更新日期：2026-02-12
> 平台：Zeabur (www.zeabur.com)

---

## 快速开始

### 第一步：注册 Zeabur 账号

1. 访问 [Zeabur 官网](https://zeabur.com)
2. 点击右上角"登录"
3. 选择"使用 GitHub 登录"（推荐，后续自动部署需要）
4. 授权 Zeabur 访问您的 GitHub 账号

### 第二步：创建新项目

1. 登录后，点击"创建新项目"
2. 选择"空项目"

### 第三步：部署应用

**方式一：从 GitHub 部署（推荐）**

1. 点击"添加服务"
2. 选择"从 GitHub 部署"
3. 在仓库列表中找到 `kennyzhang2026/stock_analyst`
4. 选择分支：`cloud-deploy`
5. Zeabur 会自动检测 Python 项目并配置

**方式二：手动配置**

1. 点击"添加服务" → "服务"
2. 选择"预构建镜像"或"市场模板"
3. 配置以下参数：
   - **运行环境**：Python 3.11
   - **构建命令**：`pip install -r requirements.txt`
   - **启动命令**：`gunicorn -c gunicorn_config.py backend.app:app`

### 第四步：获取访问地址

1. 部署完成后，Zeabur 会自动分配一个域名
2. 格式类似：`https://stock-analyst-xxx.zeabur.app`
3. 点击域名即可访问您的应用

---

## 部署配置说明

### 自动配置文件

项目已包含以下配置文件：

| 文件 | 说明 |
|------|------|
| `zeabur.toml` | Zeabur 主配置文件 |
| `.zeabur/config.yaml` | 额外服务配置 |
| `gunicorn_config.py` | Gunicorn 服务器配置 |
| `requirements.txt` | Python 依赖 |

### 关键配置

```toml
# zeabur.toml 内容
[service]
name = "stock-analyst"
build_command = "pip install --upgrade pip && pip install -r requirements.txt"
start_command = "gunicorn -c gunicorn_config.py backend.app:app"

[service.env]
PYTHON_VERSION = "3.11"
```

---

## 更新应用

部署后，当您推送新代码到 `cloud-deploy` 分支时：

1. Zeabur 会自动检测到更新
2. 自动重新构建和部署
3. 通常需要 1-3 分钟

如需手动重新部署：
1. 进入 Zeabur 控制台
2. 找到您的项目和服务
3. 点击"重新部署"按钮

---

## 监控和日志

### 查看日志

1. 进入 Zeabur 控制台
2. 选择您的项目
3. 点击"日志"标签
4. 实时查看应用日志

### 资源使用情况

在控制台可以看到：
- CPU 使用率
- 内存使用情况
- 本月免费额度消耗
- 服务运行时间

---

## 常见问题

### Q1: 部署失败怎么办？

**可能原因**：
- 依赖安装失败
- 端口配置问题
- 代码错误

**解决方法**：
1. 查看部署日志
2. 检查 `requirements.txt` 是否正确
3. 本地测试确保代码可运行

### Q2: 服务暂停了怎么办？

如果服务显示"已暂停"：
1. 进入 Zeabur 控制台
2. 找到对应服务
3. 点击"恢复"或"重新部署"

### Q3: 如何绑定自定义域名？

1. 在 Zeabur 控制台选择您的服务
2. 进入"域名设置"
3. 添加自定义域名
4. 按照提示配置 DNS

---

## 免费额度说明

| 资源 | 限制 |
|------|------|
| 每月额度 | $5 美元 |
| CPU | 最高 1 vCPU |
| 内存 | 最高 2GB |
| 存储 | 包含在内 |

**注意**：免费额度足够运行此股票分析应用，不会超限。

---

## 相关链接

- [Zeabur 官方文档](https://zeabur.com/docs)
- [Zeabur GitHub 部署教程](https://zeabur.com/docs/deploy/github)
- [项目仓库](https://github.com/kennyzhang2026/stock_analyst)

---

## 技术支持

如遇到问题：
1. 查看 [Zeabur 常见问题](https://zeabur.com/docs/faq)
2. 检查部署日志
3. 查看 [GitHub Issues](https://github.com/kennyzhang2026/stock_analyst/issues)
