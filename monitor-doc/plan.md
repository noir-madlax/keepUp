# KeepUp 费用监控系统完整技术设计方案 v2.0

## 📋 产品需求说明（已澄清）

### 核心功能

1.**费用监控页面**：展示10+个网站的token使用量和费用信息

2.**自动数据抓取**：每天北京时间9点自动访问网站并抓取数据

3.**Cookie管理**：存储和验证Cookie有效性（绿点标识）

4.**截图保存**：每天覆盖保存最新的页面截图

5.**配置化操作**：使用YAML/JSON配置浏览器操作步骤

### 监控网站（初期3个，可扩展到10+）

- OpenRouter：Credits余额
- TikHub：Account Balance
- Cursor：Included-Request Usage (87/500) 和 On-Demand Usage ($1/$10)

## 🏗️ 技术架构设计

### 方案选择：Vercel Cron + Supabase Edge Functions + Puppeteer

**架构图：**

```

┌─────────────────────────────────────────────────────┐

│  前端 (Vue 3)                                        │

│  - /monitor 费用监控页面                             │

│  - 展示卡片列表、Cookie状态、历史数据               │

└────────────────────┬────────────────────────────────┘

                     │ HTTP GET/POST

                     ↓

┌─────────────────────────────────────────────────────┐

│  Supabase Edge Functions (Deno Runtime)             │

│  - scrape_openrouter                                │

│  - scrape_tikhub                                    │

│  - scrape_cursor                                    │

│  - validate_cookies (Cookie有效性检测)              │

│  每个Function独立运行 (并行执行)                     │

└────────┬───────────────────┬────────────────────────┘

         │                   │

         ↓                   ↓

┌────────────────┐  ┌───────────────────────────┐

│ Supabase       │  │ Supabase Storage          │

│ PostgreSQL     │  │ - screenshots bucket      │

│ - 新表设计     │  │ - 每天覆盖保存截图        │

└────────────────┘  └───────────────────────────┘

         ↑

         │ 定时触发 (Cron)

┌────────┴────────────────────────────────────────────┐

│  Vercel Cron Jobs                                   │

│  - cron: "0 1 * * *" (北京时间9点 = UTC 1点)        │

│  - 调用 Edge Functions 并行执行                     │

└─────────────────────────────────────────────────────┘

```

### 技术选型理由

**为什么选择 Supabase Edge Functions？**

1. ✅ 90秒执行时间限制：单个网站访问只需5-10秒，足够使用
2. ✅ 并行执行：每个网站独立的Edge Function，可同时运行
3. ✅ Deno环境：支持Puppeteer Core + Chrome Headless
4. ✅ 免费额度：每月200万次请求，足够使用
5. ✅ 与Supabase深度集成：可直接访问数据库和Storage

**为什么不选择Vercel Serverless Functions？**

- ❌ 50MB部署包限制（Puppeteer + Chrome太大）
- ❌ 10秒执行时间限制（免费版）
- ❌ 需要额外的浏览器环境配置

## 🗄️ 数据库设计

### 1. 网站监控配置表 `keep_monitor_sites`

```sql

CREATETABLEkeep_monitor_sites (

  id bigserialPRIMARY KEY,

nametextNOT NULL,                    -- 网站名称（如：OpenRouter）

  slug textUNIQUENOT NULL,             -- 唯一标识（如：openrouter）

urltextNOT NULL,                     -- 访问URL

  scraper_config jsonb NOT NULL,         -- 抓取配置（YAML转JSON）

  is_active booleanDEFAULT true,        -- 是否启用

  display_order intDEFAULT0,           -- 显示顺序

  icon_url text,                         -- 网站图标

  created_at timestamptzDEFAULTnow(),

  updated_at timestamptzDEFAULTnow()

);

```

### 2. Cookie存储表 `keep_monitor_cookies`

```sql

CREATETABLEkeep_monitor_cookies (

  id bigserialPRIMARY KEY,

  site_slug textREFERENCES keep_monitor_sites(slug) ON DELETE CASCADE,

  cookies jsonb NOT NULL,                -- Cookie数组（JSON格式）

  is_valid booleanDEFAULT true,         -- Cookie是否有效

  last_validated_at timestamptz,         -- 最后验证时间

  expires_at timestamptz,                -- 过期时间（从Cookie中解析）

  created_at timestamptzDEFAULTnow(),

  updated_at timestamptzDEFAULTnow(),

UNIQUE(site_slug)

);

```

### 3. 监控数据表 `keep_monitor_records`

```sql

CREATETABLEkeep_monitor_records (

  id bigserialPRIMARY KEY,

  site_slug textREFERENCES keep_monitor_sites(slug) ON DELETE CASCADE,

data jsonb NOT NULL,                   -- 抓取的数据（灵活结构）

  screenshot_url text,                   -- 截图URL（Storage路径）

  scrape_duration int,                   -- 抓取耗时（毫秒）

statustextCHECK (statusIN ('success', 'failed', 'cookie_invalid')),

  error_message text,                    -- 错误信息

  created_at timestamptzDEFAULTnow(),


-- 索引优化

INDEX idx_site_date (site_slug, created_at DESC)

);

```

### 4. 数据示例

**OpenRouter 数据格式：**

```json

{

"credits": 7.73,

"currency": "USD",

"scraped_at": "2025-11-11T09:00:00Z"

}

```

**TikHub 数据格式：**

```json

{

"balance": 9.0416,

"free_credit": 0.0006,

"daily_cost": 0.0020,

"api_requests_today": 2,

"scraped_at": "2025-11-11T09:00:00Z"

}

```

**Cursor 数据格式：**

```json

{

"included_usage": {

"used": 87,

"total": 500

  },

"on_demand_usage": {

"spent": 1,

"limit": 10,

"currency": "USD"

  },

"scraped_at": "2025-11-11T09:00:00Z"

}

```

## ⚙️ 配置化操作步骤设计

### YAML配置格式（存储在 scraper_config 字段）

```yaml

# OpenRouter配置示例

name:OpenRouter

url:https://openrouter.ai/settings/credits

steps:

-action:navigate

url:"{{url}}"

wait_for_selector:"body"


-action:wait

selector:"div:has-text('Credits')"

timeout:10000


-action:extract

name:credits

selector:"text=/\\$\\s*([\\d.]+)/"

extract_type:regex

regex_group:1

transform:float


-action:screenshot

filename:"openrouter-{date}.png"

full_page: false


validation:

cookie_check:

selector:"text=/Sign Out|Logout/"

inverse: false  # 如果找到则Cookie有效

```

### 支持的操作类型

1.**navigate** - 导航到URL

2.**wait** - 等待元素出现

3.**click** - 点击元素

4.**type** - 输入文本

5.**extract** - 提取数据（支持selector、regex、xpath）

6.**screenshot** - 截图

7.**scroll** - 滚动页面

8.**conditional** - 条件判断（if/else）

### 配置解析器设计

Edge Function中的解析器会：

1. 读取YAML配置转换为JSON
2. 按顺序执行步骤
3. 支持变量替换（如 `{{ url }}`）
4. 支持数据转换（string → float/int）
5. 错误处理和重试机制

## 🔧 Supabase Edge Functions实现

### 1. 通用抓取器 `functions/scraper/index.ts`

```typescript

importpuppeteerfrom"https://deno.land/x/puppeteer@16.2.0/mod.ts";


interfaceScraperConfig {

name:string;

url:string;

steps:Step[];

validation?:ValidationConfig;

}


interfaceStep {

action:'navigate'|'wait'|'extract'|'screenshot'|'click'|'type';

[key:string]:any;

}


exportasyncfunctionscrape(

siteSlug:string,

config:ScraperConfig,

cookies:any[]

):Promise<{ data:any; screenshot:Uint8Array; duration:number }> {

conststartTime=Date.now();


constbrowser=awaitpuppeteer.launch({

args:['--no-sandbox', '--disable-setuid-sandbox']

  });


constpage=awaitbrowser.newPage();


// 设置Cookie

awaitpage.setCookie(...cookies);


constdata= {};

letscreenshot:Uint8Array;


try {

// 执行配置步骤

for (conststepofconfig.steps) {

switch (step.action) {

case'navigate':

awaitpage.goto(step.url, { waitUntil:'networkidle2' });

break;

case'wait':

awaitpage.waitForSelector(step.selector, { timeout:step.timeout||5000 });

break;

case'extract':

data[step.name]=awaitextractData(page, step);

break;

case'screenshot':

screenshot=awaitpage.screenshot({ fullPage:step.full_page });

break;

// ... 其他操作

      }

    }

  } finally {

awaitbrowser.close();

  }


return {

data,

screenshot,

duration:Date.now() -startTime

  };

}

```

### 2. 定时任务触发器 `functions/scrape-all/index.ts`

```typescript

import { createClient } from'@supabase/supabase-js';


Deno.serve(async (req) => {

constsupabase=createClient(

Deno.env.get('SUPABASE_URL')!,

Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!

  );


// 获取所有启用的网站

const { data: sites } =awaitsupabase

    .from('keep_monitor_sites')

    .select('*')

    .eq('is_active', true);


// 并行执行所有抓取任务

constpromises=sites.map(site=>

fetch(`${Deno.env.get('SUPABASE_URL')}/functions/v1/scrape-site`, {

method:'POST',

body:JSON.stringify({ site_slug:site.slug })

    })

  );


awaitPromise.allSettled(promises);


returnnewResponse(JSON.stringify({ success: true }), {

headers: { 'Content-Type':'application/json' }

  });

});

```

## 📱 前端页面设计

### 路由配置

```typescript

// src/router/index.ts

{

  path: '/monitor',

  name: 'monitor',

  component: () =>import('../views/MonitorView.vue')

}

```

### 页面组件结构

```

MonitorView.vue

├── MonitorHeader.vue (标题、刷新按钮)

├── MonitorCard.vue × N (每个网站一个卡片)

│   ├── 网站图标和名称

│   ├── Cookie状态指示器（绿/红点）

│   ├── 数据展示区域

│   ├── 截图预览

│   └── 最后更新时间

└── MonitorSettings.vue (配置入口)

```

### 卡片设计（MonitorCard.vue）

```vue

<template>

<divclass="monitor-card">

<divclass="card-header">

<img :src="site.icon_url"class="site-icon"/>

<h3>{{site.name}}</h3>

<divclass="cookie-status" :class="{ valid:cookieValid }"></div>

</div>


<divclass="card-body">

<!-- 动态渲染数据 -->

<divv-for="(value, key) inlatestData" :key="key"class="data-row">

<spanclass="label">{{formatLabel(key) }}:</span>

<spanclass="value">{{formatValue(value) }}</span>

</div>

</div>


<divclass="card-footer">

<imgv-if="screenshotUrl" :src="screenshotUrl"class="screenshot-thumb"/>

<spanclass="timestamp">{{formatTime(updatedAt) }}</span>

</div>

</div>

</template>

```

## 🕐 Vercel Cron配置

### vercel.json

```json

{

"crons": [{

"path": "/api/cron/scrape-monitor",

"schedule": "0 1 * * *"

  }]

}

```

**注意：** Vercel Cron会调用一个API endpoint，该endpoint再调用Supabase Edge Function。

### API Route (可选的协调器)

```typescript

// api/cron/scrape-monitor.ts

exportdefaultasyncfunctionhandler(req:Request) {

// 验证Cron secret

if (req.headers.get('authorization') !==`Bearer ${process.env.CRON_SECRET}`) {

returnnewResponse('Unauthorized', { status:401 });

  }


// 调用Supabase Edge Function

constresponse=awaitfetch(

`${process.env.VITE_SUPABASE_URL}/functions/v1/scrape-all`,

    {

headers: {

'Authorization':`Bearer ${process.env.SUPABASE_SERVICE_ROLE_KEY}`

      }

    }

  );


returnresponse;

}

```

## 📦 Supabase Storage配置

### 创建Bucket

```sql

-- 在Supabase Dashboard执行

INSERT INTO storage.buckets (id, name, public)

VALUES ('monitor-screenshots', 'monitor-screenshots', true);


-- 设置访问策略（公开读取）

CREATEPOLICY"Public Access"

ON storage.objects FORSELECT

USING (bucket_id ='monitor-screenshots');

```

### 截图命名规则

```

monitor-screenshots/

  ├── openrouter/latest.png  (总是覆盖)

  ├── tikhub/latest.png

  └── cursor/latest.png

```

## 🔐 环境变量配置

### Supabase Edge Functions

```env

SUPABASE_URL=https://ojbocxqvufoblihkzijn.supabase.co

SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key>

```

### Vercel

```env

VITE_SUPABASE_URL=https://ojbocxqvufoblihkzijn.supabase.co

VITE_SUPABASE_ANON_KEY=<your-anon-key>

SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key>

CRON_SECRET=<random-secret>

```

## 🎯 实施步骤

### 阶段一：数据库和基础设施（1-2小时）

1. 创建数据库表结构
2. 创建Supabase Storage bucket
3. 导入初始Cookie数据

### 阶段二：Edge Functions开发（3-4小时）

1. 开发通用抓取器引擎
2. 实现配置解析器
3. 创建3个网站的Edge Functions
4. 测试Cookie验证和数据抓取

### 阶段三：前端页面开发（2-3小时）

1. 创建MonitorView页面
2. 开发MonitorCard组件
3. 实现数据展示和刷新逻辑
4. 添加截图预览功能

### 阶段四：定时任务配置（1小时）

1. 配置Vercel Cron
2. 创建协调器API
3. 测试定时触发

### 阶段五：测试和优化（1-2小时）

1. 端到端测试
2. 性能优化
3. 错误处理完善

## ✅ 技术可行性确认

### Supabase项目状态

- ✅ 项目ID：ojbocxqvufoblihkzijn
- ✅ 区域：ap-northeast-1（日本）
- ✅ 数据库版本：PostgreSQL 15.6
- ✅ 状态：ACTIVE_HEALTHY

### Storage访问

- ⚠️ 当前无Storage bucket（需要创建）
- ✅ MCP有完整数据库访问权限
- ✅ 可通过Supabase Dashboard管理Storage（https://supabase.com/dashboard/project/ojbocxqvufoblihkzijn/storage/buckets）

### Vercel Token

- ✅ Token已提供：TcnvoJSbdutybqtQL7bPDzWS
- ✅ 可配置Cron Jobs

### Cookie数据

- ✅ OpenRouter：10个cookies，有效期至2026年
- ✅ TikHub：7个cookies，sessionid有效期至2025-12-30
- ✅ Cursor：5个cookies，WorkosCursorSessionToken有效期至2026-12-28

### Edge Functions限制评估

- 单个网站访问：5-10秒 ✅
- Edge Function超时：90秒 ✅
- 并行执行：3个网站同时运行 ✅
- 总耗时预估：10-15秒（足够安全）

## 🚀 下一步行动

1.**确认方案**：请Review此设计，确认是否符合预期

2.**开始实施**：获得确认后开始实施

3.**扩展性考虑**：后续添加网站只需：

    - 在数据库添加配置

    - 上传Cookie

    - 创建对应的Edge Function（或复用通用抓取器）

## 💡 关键优势

1.**不修改后端**：完全基于前端+Supabase实现

2.**配置化灵活**：YAML配置支持快速调整

3.**并行高效**：多网站同时抓取，总耗时不超过15秒

4.**成本可控**：Supabase和Vercel免费额度足够使用

5.**易于扩展**：添加新网站只需配置，无需改代码
