# Stock Analyst - Vercel 部署指南

> 版本：v1.0
> 更新日期：2026-02-12
> 平台：Vercel (vercel.com)

---

## 为什么选择 Vercel

| 特性 | 说明 |
|------|------|
| ✅ **完全免费** | Hobby 计划无需信用卡 |
| ✅ **Python 支持** | 原生支持 Flask 应用 |
| ✅ **自动部署** | 连接 GitHub，推送即部署 |
| ✅ **国内可访问** | 虽然是国外服务，但可正常访问 |
| ⚠️ **有休眠** | 类似 Render，首次访问需唤醒 |

---

## 快速开始

### 第一步：注册 Vercel 账号

1. 访问 [vercel.com](https://vercel.com)
2. 点击 **Sign Up**
3. **选择 "Continue with GitHub"**（推荐）
4. 授权 Vercel 访问您的 GitHub 账号
5. 无需信用卡！

### 第二步：导入项目

1. 登录后，点击 **Add New Project**
2. 在仓库列表中找到：`kennyzhang2026/stock_analyst`
3. **重要**：如果还没切换分支，需要先选择 `cloud-deploy`

### 第三步：配置项目

Vercel 会自动检测 Python 项目，配置如下：

| 选项 | 值 |
|------|-----|
| **Framework Preset** | Python |
| **Root Directory** | ./ |
| **Build Command** | （留空，自动检测）|
| **Output Directory** | （留空）|
| **Install Command** | `pip install -r requirements.txt` |

### 第四步：环境变量（可选）

点击 "Environment Variables"，添加：

| Key | Value |
|-----|-------|
| `FLASK_ENV` | production |
| `PYTHON_VERSION` | 3.11 |

### 第五步：部署

点击 **Deploy**，等待 1-3 分钟

### 第六步：获取访问地址

部署成功后，Vercel 会分配域名：
`https://stock-analyst.vercel.app`

---

## 使用 vercel.json 自动配置（推荐）

项目已包含 `vercel.json` 配置文件，Vercel 会自动读取。

---

## 更新应用

部署后，当您推送新代码到 `cloud-deploy` 分支时：

1. Vercel 会自动检测到更新
2. 自动重新构建和部署
3. 通常需要 1-2 分钟

---

## 监控和日志

### 查看日志

1. 进入 Vercel 控制台
2. 选择您的项目
3. 点击 "Deployments" 标签
4. 点击具体部署 → "View Logs"

### 资源使用情况

在控制台可以看到：
- 带宽使用
- 函数执行次数
- 构建时间

---

## 关于 Serverless

Vercel 使用 Serverless 架构，与传统的持续运行服务器不同：

| 特性 | 传统服务器 | Vercel Serverless |
|------|-----------|------------------|
| **运行方式** | 持续运行 | 按需启动 |
| **定时任务** | ✅ 支持 | ⚠️ 需要额外配置 |
| **15分钟更新** | ✅ 支持 | ⚠️ 需要使用 Cron Jobs |

### ⚠️ 重要提示

您的项目有**定时自动更新**功能（每15分钟），这在 Vercel 上需要特殊处理。

如果定时任务对您很重要，建议使用 **Render** 或直接回到原 Render 账号。

---

## 常见问题

### Q1: 部署失败怎么办？

1. 查看部署日志找到错误
2. 检查 `requirements.txt` 是否在根目录
3. 确认选择的分支是 `cloud-deploy`

### Q2: 定时任务不工作？

Vercel Serverless 默认不支持后台定时任务。解决方案：
1. 使用外部 Cron 服务定期访问应用
2. 或切换到 Render/主机屋等传统服务器

### Q3: 如何绑定自定义域名？

1. 进入项目设置
2. 点击 "Domains"
3. 添加域名并配置 DNS

---

## 免费额度说明

| 资源 | Hobby 免费限制 |
|------|----------------|
| 带宽 | 100 GB/月 |
| Serverless 函数执行 | 100 GB-Hrs/月 |
| 构建时间 | 6000 分钟/月 |
| 团队成员 | 无限 |

**注意**：对于个人股票分析项目，免费额度完全够用。

---

## 相关链接

- [Vercel 官方文档](https://vercel.com/docs)
- [Vercel Python 指南](https://vercel.com/docs/frameworks/python)
- [项目仓库](https://github.com/kennyzhang2026/stock_analyst)

---

## 技术支持

如遇到问题：
1. 查看 [Vercel 文档](https://vercel.com/docs)
2. 检查部署日志
3. 查看 [GitHub Issues](https://github.com/kennyzhang2026/stock_analyst/issues)
