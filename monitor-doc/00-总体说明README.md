# KeepUp 费用监控系统 - 完整文档

> 版本: 1.0.0  
> 最后更新: 2025-11-11  
> 作者: AI Assistant + Rigel

## 📚 文档目录

本文件夹包含费用监控系统的所有设计文档：

1. **[01-技术架构设计.md](./01-技术架构设计.md)** - 系统架构、技术选型、设计决策
2. **[02-数据库设计.md](./02-数据库设计.md)** - 数据库表结构、字段说明、示例数据
3. **[03-网站配置YAML.md](../monitor-configs/)** - 3个网站的详细抓取配置
4. **[05-测试用例.md](./05-测试用例.md)** - 完整的测试计划和用例
5. **[06-核心代码实现.md](./06-核心代码实现.md)** - Edge Functions和前端核心代码
6. **[plan.md](./plan.md)** - 原始设计方案

## 🎯 项目概述

### 功能简介

一个自动化的费用监控系统，用于跟踪多个第三方服务的费用使用情况：

- 🤖 **OpenRouter**: AI API聚合平台，监控Credits余额
- 🎵 **TikHub**: TikTok数据API，监控账户余额
- ✨ **Cursor**: AI编程工具，监控请求配额和费用

### 核心特性

✅ **自动抓取**: 每天北京时间9点自动访问网站获取数据  
✅ **手动触发**: 前端卡片支持单独刷新  
✅ **Cookie管理**: 自动检测Cookie有效性  
✅ **截图保存**: 每天保存最新页面截图  
✅ **配置化**: YAML格式配置抓取步骤，易于维护  
✅ **Glassmorphism设计**: 2025年流行的透明玻璃视觉效果  

## 🏗️ 技术栈

### 前端
- **框架**: Vue 3 + TypeScript
- **构建**: Vite
- **样式**: Tailwind CSS + Custom Glassmorphism
- **部署**: Vercel

### 后端
- **无服务器**: Supabase Edge Functions (Deno)
- **浏览器自动化**: Playwright for Deno
- **数据库**: PostgreSQL (Supabase)
- **存储**: Supabase Storage

### 自动化
- **定时任务**: Vercel Cron Jobs
- **频率**: 每天 UTC 01:00 (北京时间 09:00)

## 🚀 快速开始

### 前置要求

- Node.js 18+
- Supabase CLI
- Vercel CLI
- Git

### 1. 克隆项目

```bash
git clone <repository-url>
cd keepup-v2
```

### 2. 安装依赖

```bash
npm install
```

### 3. 配置环境变量

复制`.env.example`到`.env`并填写：

```env
VITE_SUPABASE_URL=https://ojbocxqvufoblihkzijn.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
CRON_SECRET=generate-random-secret
```

### 4. 初始化数据库

数据库表已通过MCP创建完成，包括：
- ✅ keep_monitor_sites (3个网站配置已导入)
- ✅ keep_monitor_cookies (3个Cookie已导入)
- ✅ keep_monitor_records

验证数据：

```bash
# 使用MCP或Supabase SQL Editor执行
SELECT * FROM keep_monitor_sites;
SELECT * FROM keep_monitor_cookies;
```

### 5. 创建Storage Bucket

在Supabase Dashboard创建：

1. 访问 https://supabase.com/dashboard/project/ojbocxqvufoblihkzijn/storage/buckets
2. 点击"New Bucket"
3. 名称: `monitor-screenshots`
4. 设置为Public
5. 创建RLS策略允许public读取

或通过SQL：

```sql
INSERT INTO storage.buckets (id, name, public)
VALUES ('monitor-screenshots', 'monitor-screenshots', true);

CREATE POLICY "Public Access"
ON storage.objects FOR SELECT
USING (bucket_id = 'monitor-screenshots');
```

### 6. 部署Edge Functions

```bash
cd supabase

# 部署通用抓取器
supabase functions deploy scrape-site

# 部署批量触发器
supabase functions deploy scrape-all
```

### 7. 本地开发

```bash
# 启动前端开发服务器
npm run dev

# 在另一个终端测试Edge Function
supabase functions serve scrape-site --no-verify-jwt
```

访问 http://localhost:3000/monitor

### 8. 部署到Vercel

```bash
# 登录Vercel
vercel login

# 部署
vercel deploy --prod

# 配置环境变量（在Vercel Dashboard或CLI）
vercel env add VITE_SUPABASE_URL
vercel env add VITE_SUPABASE_ANON_KEY
vercel env add SUPABASE_SERVICE_ROLE_KEY
vercel env add CRON_SECRET
```

### 9. 配置Vercel Cron

在`vercel.json`中已配置：

```json
{
  "crons": [{
    "path": "/api/cron/scrape-monitor",
    "schedule": "0 1 * * *"
  }]
}
```

部署后自动生效。

## 📖 使用说明

### 访问监控页面

部署后访问：`https://your-domain.vercel.app/monitor`

### 手动触发抓取

点击任意卡片右下角的🔄按钮，即可手动触发该网站的数据抓取。

### 查看截图

点击卡片底部的缩略图可以查看完整截图。

### 查看历史数据

通过Supabase Dashboard的SQL Editor查询：

```sql
-- 查看最近7天的记录
SELECT 
  site_slug,
  data,
  status,
  created_at
FROM keep_monitor_records
WHERE created_at > NOW() - INTERVAL '7 days'
ORDER BY created_at DESC;
```

## 🔧 维护指南

### 添加新网站

1. **创建YAML配置文件**
   
   在`monitor-configs/`目录创建`newsite.yaml`

2. **插入数据库配置**
   
   ```sql
   INSERT INTO keep_monitor_sites (name, slug, url, scraper_config, display_order)
   VALUES ('New Site', 'newsite', 'https://...', '<yaml转JSON>', 4);
   ```

3. **导入Cookie**
   
   ```sql
   INSERT INTO keep_monitor_cookies (site_slug, cookies, is_valid, expires_at)
   VALUES ('newsite', '<cookie JSON>', true, '2026-01-01');
   ```

4. **测试抓取**
   
   ```bash
   curl -X POST https://...supabase.co/functions/v1/scrape-site \
     -H 'Authorization: Bearer <key>' \
     -d '{"site_slug": "newsite"}'
   ```

### 更新Cookie

当Cookie失效时（卡片显示红点）：

1. 手动登录网站
2. 导出新Cookie（使用浏览器插件）
3. 更新数据库：

```sql
UPDATE keep_monitor_cookies
SET 
  cookies = '<new cookie JSON>',
  is_valid = true,
  expires_at = '<new expiry date>',
  updated_at = NOW()
WHERE site_slug = 'openrouter';
```

### 修改抓取配置

修改YAML文件后，更新数据库：

```sql
UPDATE keep_monitor_sites
SET 
  scraper_config = '<updated config JSON>',
  updated_at = NOW()
WHERE slug = 'openrouter';
```

### 调整定时任务时间

修改`vercel.json`中的schedule：

```json
{
  "schedule": "0 2 * * *"  // UTC 2点 = 北京时间10点
}
```

重新部署即可生效。

## 🐛 故障排查

### Edge Function超时

**症状**: 抓取失败，提示timeout

**解决方案**:
1. 增加timeout配置
2. 检查网站是否有Cloudflare保护
3. 查看Edge Function日志

### Cookie失效

**症状**: 卡片显示红点，status='cookie_invalid'

**解决方案**:
1. 重新登录网站获取新Cookie
2. 检查Cookie的expires时间
3. 确认没有2FA认证要求

### 截图上传失败

**症状**: screenshot_url为null

**解决方案**:
1. 检查Storage bucket是否存在
2. 验证RLS策略是否正确
3. 检查Service Role Key权限

### Vercel Cron未触发

**症状**: 定时任务不执行

**解决方案**:
1. 检查vercel.json配置
2. 确认项目已部署到Pro计划（免费版有限制）
3. 查看Vercel Dashboard的Cron日志

## 📊 监控指标

系统本身的健康监控：

- ✅ 每日抓取成功率: > 95%
- ✅ 单个网站抓取时间: < 10秒
- ✅ 并行抓取总时间: < 20秒
- ✅ Cookie有效期: 提前7天告警
- ✅ Storage使用: < 1GB

## 🔐 安全注意事项

1. **Never commit secrets**: .env文件已在.gitignore中
2. **Rotate keys regularly**: 定期更换CRON_SECRET
3. **Review RLS policies**: 确保Cookie表只有service_role可访问
4. **Monitor access logs**: 定期检查Edge Function调用日志

## 📝 更新日志

### v1.0.0 (2025-11-11)

- ✅ 初始版本发布
- ✅ 支持3个网站监控
- ✅ Glassmorphism UI设计
- ✅ 数据库表创建和数据导入
- ✅ Cookie数据导入完成
- ✅ 完整文档编写

## 🤝 贡献指南

暂不接受外部贡献，这是私有项目。

## 📄 许可证

Private - All Rights Reserved

## 📞 联系方式

如有问题，请联系项目维护者。

---

**Happy Monitoring! 🎉**

