# 监控系统设置指南

## 环境变量配置

### 1. Vercel 环境变量

在Vercel项目设置中添加以下环境变量：

```
GITHUB_TOKEN=你的GitHub Personal Access Token
GITHUB_OWNER=noir-madlax
GITHUB_REPO=keepUp
```

### 2. GitHub Secrets

在GitHub仓库的 Settings > Secrets and variables > Actions 中添加：

```
SUPABASE_URL=你的Supabase项目URL
SUPABASE_SERVICE_ROLE_KEY=你的Supabase服务密钥
```

## GitHub Token 创建步骤

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token" > "Generate new token (classic)"
3. 勾选以下权限：
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
4. 生成token并复制

## Vercel Cron Job

已配置为每天北京时间9:00 AM（UTC 1:00 AM）自动运行。

时间表达式：`0 1 * * *`

## 手动触发

访问 `/monitor` 页面，点击每个卡片的"刷新"按钮即可手动触发单个网站的数据抓取。

## 数据库表结构

- `websites`: 网站配置
- `cookies`: Cookie存储
- `scraped_data`: 抓取的数据和截图

## 访问监控页面

直接访问: `https://你的域名/monitor`

