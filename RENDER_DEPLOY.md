# Stock Analyst - Render 部署指南

> 版本：v1.0
> 更新日期：2026-02-12
> 平台：Render (render.com)

---

## 快速开始

### 第一步：注册 Render 账号

1. 访问 [Render 官网](https://render.com)
2. 点击 "Sign Up" 注册
3. **选择 "Sign up with GitHub"**（推荐，后续自动部署需要）
4. 授权 Render 访问您的 GitHub 账号

### 第二步：创建新服务

1. 登录后，点击右上角 "New +" 按钮
2. 选择 "Web Service"

### 第三步：配置服务

**基本配置：**

| 选项 | 值 |
|------|-----|
| **Name** | stock-analyst |
| **Repository** | kennyzhang2026/stock_analyst |
| **Branch** | cloud-deploy |
| **Runtime** | Python 3 |

**构建配置：**

| 选项 | 值 |
|------|-----|
| **Build Command** | `pip install --upgrade pip && pip install -r requirements.txt` |
| **Start Command** | `gunicorn -c gunicorn_config.py backend.app:app` |

或者直接使用 `render.yaml` 配置文件（推荐）。

### 第四步：选择实例类型

选择 **Free** 免费套餐：
- 512 MB RAM
- 750 小时/月
- 15分钟无活动后休眠

### 第五步：部署

点击 "Create Web Service"，Render 会自动：
1. 从 GitHub 拉取代码
2. 安装依赖
3. 启动服务

**部署时间**：约 3-5 分钟

### 第六步：获取访问地址

部署成功后，Render 会分配一个域名：
`https://stock-analyst.onrender.com`

点击即可访问您的应用！

---

## 使用 render.yaml 自动部署（推荐）

项目已包含 `render.yaml` 配置文件，使用方法：

1. 在 Render 创建 "New Web Service"
2. 连接 GitHub 仓库 `kennyzhang2026/stock_analyst`
3. Render 会自动检测 `render.yaml` 并填充配置
4. 确认分支为 `cloud-deploy`
5. 点击创建

---

## 更新应用

部署后，当您推送新代码到 `cloud-deploy` 分支时：

1. Render 会自动检测到更新
2. 自动重新构建和部署
3. 通常需要 3-5 分钟

如需手动重新部署：
1. 进入 Render 控制台
2. 找到您的服务
3. 点击 "Manual Deploy" → "Deploy latest commit"

---

## 监控和日志

### 查看日志

1. 进入 Render 控制台
2. 选择您的服务
3. 点击 "Logs" 标签
4. 实时查看应用日志

### 资源使用情况

在控制台可以看到：
- CPU 使用率
- 内存使用情况
- 本月剩余免费小时数
- 服务状态（运行中/休眠）

---

## 关于休眠

### 休眠机制

- **触发条件**：15分钟无 HTTP 请求
- **唤醒时间**：5-10 秒（首次访问）
- **影响**：唤醒期间会显示加载中

### 减少休眠影响

1. **添加健康检查**：已配置 `/api/health` 端点
2. **定时访问**：可用外部服务每10分钟ping一次（可选）
3. **升级套餐**：升级到付费套餐可不休眠

---

## 常见问题

### Q1: 部署失败怎么办？

**检查项**：
1. 查看部署日志，找到错误信息
2. 确认 `requirements.txt` 在项目根目录
3. 确认选择的分支是 `cloud-deploy`
4. 本地测试确保代码可运行

### Q2: 应用无法访问？

**可能原因**：
- 服务正在启动中（等待几分钟）
- 服务已休眠（刷新页面，等待5-10秒）
- 部署失败（检查日志）

### Q3: 如何绑定自定义域名？

1. 进入服务设置
2. 点击 "Custom Domains"
3. 添加域名并配置 DNS

---

## 免费额度说明

| 资源 | 限制 |
|------|------|
| 每月运行时间 | 750 小时 |
| 内存 | 512 MB |
| CPU | 共享 |
| 构建时间 | 500 分钟/月 |

**注意**：750小时足够全月运行一个服务。休眠是 Render 的策略，与额度无关。

---

## 相关链接

- [Render 官方文档](https://render.com/docs)
- [Render YAML 规范](https://render.com/docs/yaml-spec)
- [Render 免费套餐说明](https://render.com/pricing)
- [项目仓库](https://github.com/kennyzhang2026/stock_analyst)

---

## 技术支持

如遇到问题：
1. 查看 [Render 常见问题](https://render.com/docs/troubleshooting)
2. 检查部署日志
3. 查看 [GitHub Issues](https://github.com/kennyzhang2026/stock_analyst/issues)
