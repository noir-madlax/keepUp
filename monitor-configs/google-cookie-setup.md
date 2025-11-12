# Google AI Studio Cookie 设置说明

## Cookie 已准备就绪

Cookie 文件位置：`cookies-temp/google`

## 插入Cookie到数据库

### 方式一：使用Node.js脚本（推荐）

```bash
cd scripts

# 设置环境变量（从Supabase项目设置中获取）
export SUPABASE_URL="your_supabase_url"
export SUPABASE_SERVICE_ROLE_KEY="your_service_role_key"

# 运行插入脚本
node insert-google-cookie.js
```

### 方式二：直接在Supabase Dashboard SQL编辑器中执行

1. 打开 Supabase Dashboard
2. 进入 SQL Editor
3. 执行以下SQL（需要手动复制cookie内容）:

```sql
INSERT INTO cookies (
  site_slug,
  cookie_data,
  is_valid,
  expires_at
)
VALUES (
  'google',
  '在这里粘贴cookies-temp/google文件的完整JSON内容'::jsonb,
  true,
  '2026-11-12 00:00:00+00'  -- 根据cookie中的最晚过期时间调整
)
ON CONFLICT (site_slug)
DO UPDATE SET
  cookie_data = EXCLUDED.cookie_data,
  is_valid = EXCLUDED.is_valid,
  expires_at = EXCLUDED.expires_at,
  updated_at = NOW();
```

## 验证Cookie是否插入成功

```sql
SELECT 
  site_slug,
  is_valid,
  jsonb_array_length(cookie_data) as cookie_count,
  expires_at,
  created_at,
  updated_at
FROM cookies 
WHERE site_slug = 'google';
```

## 测试抓取脚本

在插入Cookie后，可以测试抓取功能：

```bash
cd scripts

# 设置环境变量
export SUPABASE_URL="your_supabase_url"
export SUPABASE_SERVICE_ROLE_KEY="your_service_role_key"

# 运行抓取脚本
node scrape-google.js
```

## 数据库表结构

当前项目使用的表名：
- `websites` - 网站配置
- `cookies` - Cookie存储
- `scraped_data` - 抓取数据

字段映射：
- `cookie_data` - Cookie JSON数组
- `site_slug` - 网站标识符（google）

## 前端访问

Cookie插入成功后，前端会自动从数据库加载：
1. 访问监控页面
2. 应该能看到 "Google AI Studio" 卡片
3. 点击刷新按钮测试数据抓取

##注意事项

1. Cookie有效期至2026年11月
2. 如果cookie失效，需要重新导出并更新
3. 抓取脚本会自动验证cookie有效性

