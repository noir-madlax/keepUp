# 最终技术方案 - GitHub Actions + Puppeteer

> ⚠️ 重要更新：放弃Supabase Edge Functions方案，改用GitHub Actions  
> 原因：Edge Functions无法运行浏览器，即使Playwright for Deno也需要浏览器二进制文件

## 🎯 最终方案架构

### 完整架构图

```
┌─────────────────────────────────────────────────────┐
│  前端 (Vue 3 + Vercel)                               │
│  - /monitor 页面展示                                 │
│  - 手动触发按钮                                       │
│  - 实时数据展示                                       │
└─────────────┬───────────────────────────────────────┘
              │
              │ ① 手动触发：调用GitHub API
              │ ② 数据查询：Supabase Client
              ↓
┌──────────────────────────────────┐  ┌──────────────┐
│ GitHub Actions (Workflows)       │  │ Supabase     │
│  定时任务: cron '0 1 * * *'      │←─┤ Database     │
│  手动触发: workflow_dispatch     │  │ + Storage    │
│                                  │  └──────────────┘
│  ┌────────────────────────────┐ │         ↑
│  │ scrape-openrouter.yml      │ │         │
│  │ scrape-tikhub.yml          │ │         │ POST数据
│  │ scrape-cursor.yml          │ │         │
│  │ scrape-all.yml (统一调度)  │ │─────────┘
│  └────────────────────────────┘ │
│                                  │
│  每个workflow:                   │
│  1. 安装Puppeteer               │
│  2. 运行抓取脚本                │
│  3. 保存数据到Supabase          │
│  4. 上传截图到Storage           │
└──────────────────────────────────┘
```

## ✅ 优势说明

### 为什么选择GitHub Actions

1. **完全免费**
   - 2000分钟/月（公开仓库unlimited）
   - 远超Vercel(10秒)和Supabase(90秒)的限制

2. **预装Chrome浏览器**
   - ubuntu-latest镜像自带Chrome/Chromium
   - 无需Docker容器
   - 无需额外配置

3. **无超时限制**
   - 单个job最多6小时
   - 足够运行任何复杂的抓取任务

4. **符合你的要求**
   - ✅ 不用Docker
   - ✅ 前端Vercel
   - ✅ 数据库Supabase
   - ✅ 纯代码配置（YAML）

5. **易于维护**
   - Workflow文件就是配置
   - 可以版本控制
   - 支持secrets管理

## 📁 项目结构

```
keepup-v2/
├── .github/
│   └── workflows/
│       ├── scrape-openrouter.yml    # OpenRouter抓取
│       ├── scrape-tikhub.yml        # TikHub抓取
│       ├── scrape-cursor.yml        # Cursor抓取
│       └── scrape-all.yml           # 统一调度（定时任务）
│
├── scripts/
│   ├── scraper/
│   │   ├── engine.js                # 通用抓取引擎
│   │   ├── config-parser.js         # 配置解析器
│   │   └── supabase-client.js       # Supabase客户端
│   │
│   ├── scrape-openrouter.js         # OpenRouter脚本
│   ├── scrape-tikhub.js             # TikHub脚本
│   ├── scrape-cursor.js             # Cursor脚本
│   └── package.json                 # 依赖配置
│
├── monitor-configs/                  # YAML配置（已有）
│   ├── openrouter.yaml
│   ├── tikhub.yaml
│   └── cursor.yaml
│
├── src/                              # 前端代码（已有）
│   ├── views/
│   │   └── MonitorView.vue
│   └── components/
│       └── MonitorCard.vue
│
└── api/                              # Vercel API（用于手动触发）
    └── trigger-scrape.ts             # 触发GitHub Actions
```

## 🔧 GitHub Actions配置

### 1. 通用抓取workflow示例

```yaml
# .github/workflows/scrape-openrouter.yml
name: Scrape OpenRouter

on:
  # 手动触发
  workflow_dispatch:
  
  # 可被其他workflow调用
  workflow_call:

jobs:
  scrape:
    runs-on: ubuntu-latest
    
    steps:
      # 1. 检出代码
      - name: Checkout code
        uses: actions/checkout@v3
      
      # 2. 设置Node.js环境
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: scripts/package-lock.json
      
      # 3. 安装依赖（包括Puppeteer）
      - name: Install dependencies
        run: |
          cd scripts
          npm ci
      
      # 4. 运行抓取脚本
      - name: Run scraper
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
          SITE_SLUG: openrouter
        run: |
          cd scripts
          node scrape-openrouter.js
      
      # 5. 上传截图（备份）
      - name: Upload screenshots
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: screenshots-openrouter
          path: scripts/temp/*.png
          retention-days: 7
```

### 2. 统一调度workflow

```yaml
# .github/workflows/scrape-all.yml
name: Daily Monitor All Sites

on:
  # 定时任务：每天UTC 1:00（北京时间9:00）
  schedule:
    - cron: '0 1 * * *'
  
  # 手动触发
  workflow_dispatch:

jobs:
  scrape-all:
    runs-on: ubuntu-latest
    strategy:
      # 并行执行多个网站
      matrix:
        site: [openrouter, tikhub, cursor]
      # 失败后继续其他任务
      fail-fast: false
    
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          cd scripts
          npm ci
      
      - name: Scrape ${{ matrix.site }}
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
          SITE_SLUG: ${{ matrix.site }}
        run: |
          cd scripts
          node scrape-${{ matrix.site }}.js
```

## 📝 抓取脚本实现

### 通用抓取引擎 (scripts/scraper/engine.js)

```javascript
const puppeteer = require('puppeteer');
const fs = require('fs').promises;
const path = require('path');
const { createClient } = require('./supabase-client');

class ScraperEngine {
  constructor(config, cookies) {
    this.config = config;
    this.cookies = cookies;
    this.supabase = createClient();
  }

  async scrape() {
    const startTime = Date.now();
    let browser, page;
    
    try {
      // 1. 启动浏览器
      browser = await puppeteer.launch({
        headless: 'new',
        args: [
          '--no-sandbox',
          '--disable-setuid-sandbox',
          '--disable-dev-shm-usage',
          '--disable-gpu'
        ]
      });

      page = await browser.newPage();
      
      // 2. 设置viewport和user-agent
      await page.setViewport({ width: 1920, height: 1080 });
      await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36');
      
      // 3. 设置Cookie
      await page.setCookie(...this.normalizeCookies(this.cookies));
      
      // 4. 执行配置步骤
      const data = {};
      let screenshotBuffer = null;
      
      for (const step of this.config.steps) {
        await this.executeStep(page, step, data);
      }
      
      // 5. 验证Cookie有效性
      const cookieValid = await this.validateCookie(page);
      
      // 6. 保存结果
      const result = {
        success: cookieValid,
        status: cookieValid ? 'success' : 'cookie_invalid',
        data: { ...data, scraped_at: new Date().toISOString() },
        duration: Date.now() - startTime,
        cookie_valid: cookieValid
      };
      
      // 7. 保存到Supabase
      await this.saveToDatabase(result);
      
      return result;
      
    } catch (error) {
      console.error('Scrape error:', error);
      
      // 保存错误记录
      await this.saveToDatabase({
        success: false,
        status: 'failed',
        error_message: error.message,
        duration: Date.now() - startTime
      });
      
      throw error;
      
    } finally {
      if (browser) {
        await browser.close();
      }
    }
  }

  async executeStep(page, step, data) {
    console.log(`Executing step: ${step.action}`);
    
    switch (step.action) {
      case 'navigate':
        await page.goto(step.url, {
          waitUntil: step.wait_for || 'networkidle2',
          timeout: step.timeout || 30000
        });
        break;
      
      case 'wait':
        await page.waitForSelector(step.selector, {
          timeout: step.timeout || 10000
        }).catch(() => {
          console.warn(`Element not found: ${step.selector}`);
        });
        break;
      
      case 'extract':
        const value = await this.extractData(page, step);
        data[step.name] = value;
        console.log(`Extracted ${step.name}:`, value);
        break;
      
      case 'screenshot':
        const screenshot = await page.screenshot({
          type: 'png',
          fullPage: step.full_page || false
        });
        
        // 保存到本地临时目录
        const tempDir = path.join(__dirname, '..', 'temp');
        await fs.mkdir(tempDir, { recursive: true });
        const localPath = path.join(tempDir, `${this.config.name}.png`);
        await fs.writeFile(localPath, screenshot);
        
        // 上传到Supabase Storage
        await this.uploadScreenshot(screenshot);
        break;
      
      case 'click':
        await page.click(step.selector);
        break;
      
      case 'type':
        await page.type(step.selector, step.value);
        break;
      
      default:
        console.warn(`Unknown action: ${step.action}`);
    }
  }

  async extractData(page, step) {
    const { selector, extract_type, regex_pattern, regex_group, transform } = step;
    
    let rawValue;
    
    try {
      if (extract_type === 'regex' || regex_pattern) {
        // 正则提取
        const bodyText = await page.evaluate(() => document.body.innerText);
        const pattern = new RegExp(regex_pattern || selector.replace('text=/', '').replace('/', ''));
        const match = bodyText.match(pattern);
        rawValue = match && match[regex_group || 1] ? match[regex_group || 1] : null;
      } else {
        // CSS选择器提取
        rawValue = await page.$eval(selector, el => el.textContent).catch(() => null);
      }
      
      // 数据转换
      if (rawValue && transform) {
        switch (transform) {
          case 'float':
            return parseFloat(rawValue);
          case 'int':
            return parseInt(rawValue, 10);
          case 'date':
            return new Date(rawValue).toISOString();
          default:
            return rawValue;
        }
      }
      
      return rawValue;
      
    } catch (error) {
      console.error(`Extract error for ${step.name}:`, error);
      return null;
    }
  }

  async validateCookie(page) {
    if (!this.config.validation || !this.config.validation.cookie_check) {
      return true; // 没有配置验证规则，默认有效
    }
    
    const { selector, should_exist = true } = this.config.validation.cookie_check;
    
    try {
      const elementCount = await page.$$eval(selector, els => els.length);
      const exists = elementCount > 0;
      return exists === should_exist;
    } catch (error) {
      console.warn('Cookie validation failed:', error);
      return false;
    }
  }

  async uploadScreenshot(buffer) {
    const siteSlug = this.config.name.toLowerCase().replace(/\s+/g, '-');
    const filename = `${siteSlug}/latest.png`;
    
    const { error } = await this.supabase.storage
      .from('monitor-screenshots')
      .upload(filename, buffer, {
        contentType: 'image/png',
        upsert: true
      });
    
    if (error) {
      console.error('Screenshot upload error:', error);
    } else {
      console.log('Screenshot uploaded:', filename);
    }
  }

  async saveToDatabase(result) {
    const siteSlug = this.config.name.toLowerCase().replace(/\s+/g, '-');
    
    // 保存记录
    const { error: recordError } = await this.supabase
      .from('keep_monitor_records')
      .insert({
        site_slug: siteSlug,
        data: result.data || {},
        screenshot_url: result.success ? `monitor-screenshots/${siteSlug}/latest.png` : null,
        scrape_duration: result.duration,
        status: result.status,
        error_message: result.error_message || null,
        trigger_source: 'auto'
      });
    
    if (recordError) {
      console.error('Database save error:', recordError);
    }
    
    // 更新Cookie状态
    const { error: cookieError } = await this.supabase
      .from('keep_monitor_cookies')
      .update({
        is_valid: result.cookie_valid !== false,
        last_validated_at: new Date().toISOString(),
        validation_error: result.error_message || null
      })
      .eq('site_slug', siteSlug);
    
    if (cookieError) {
      console.error('Cookie update error:', cookieError);
    }
  }

  normalizeCookies(cookies) {
    return cookies.map(c => ({
      name: c.name,
      value: c.value,
      domain: c.domain,
      path: c.path || '/',
      expires: c.expirationDate,
      httpOnly: c.httpOnly || false,
      secure: c.secure || false,
      sameSite: c.sameSite === 'unspecified' ? 'lax' : c.sameSite
    }));
  }
}

module.exports = ScraperEngine;
```

### 具体网站脚本示例 (scripts/scrape-openrouter.js)

```javascript
const yaml = require('js-yaml');
const fs = require('fs').promises;
const path = require('path');
const ScraperEngine = require('./scraper/engine');
const { createClient } = require('./scraper/supabase-client');

async function main() {
  try {
    console.log('Starting OpenRouter scraper...');
    
    const supabase = createClient();
    
    // 1. 从数据库获取配置和Cookie
    const { data: site } = await supabase
      .from('keep_monitor_sites')
      .select('*')
      .eq('slug', 'openrouter')
      .single();
    
    const { data: cookieData } = await supabase
      .from('keep_monitor_cookies')
      .select('*')
      .eq('site_slug', 'openrouter')
      .single();
    
    if (!site || !cookieData) {
      throw new Error('Site or cookie data not found');
    }
    
    // 2. 创建抓取引擎
    const engine = new ScraperEngine(
      site.scraper_config,
      cookieData.cookies
    );
    
    // 3. 执行抓取
    const result = await engine.scrape();
    
    console.log('Scrape completed:', result);
    process.exit(result.success ? 0 : 1);
    
  } catch (error) {
    console.error('Fatal error:', error);
    process.exit(1);
  }
}

main();
```

## 🔐 GitHub Secrets配置

在GitHub仓库Settings → Secrets and variables → Actions中添加：

```
SUPABASE_URL = https://ojbocxqvufoblihkzijn.supabase.co
SUPABASE_SERVICE_ROLE_KEY = your-service-role-key
```

## 🎮 前端手动触发

### API Route (api/trigger-scrape.ts)

```typescript
import type { VercelRequest, VercelResponse } from '@vercel/node';

export default async function handler(
  req: VercelRequest,
  res: VercelResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { site_slug } = req.body;
  
  if (!site_slug) {
    return res.status(400).json({ error: 'Missing site_slug' });
  }

  try {
    // 触发GitHub Actions workflow
    const response = await fetch(
      `https://api.github.com/repos/${process.env.GITHUB_REPO}/actions/workflows/scrape-${site_slug}.yml/dispatches`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${process.env.GITHUB_TOKEN}`,
          'Accept': 'application/vnd.github.v3+json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ref: 'main'
        })
      }
    );

    if (!response.ok) {
      throw new Error(`GitHub API error: ${response.statusText}`);
    }

    return res.status(200).json({
      success: true,
      message: `Triggered scrape for ${site_slug}`
    });

  } catch (error) {
    console.error('Trigger error:', error);
    return res.status(500).json({
      success: false,
      error: error.message
    });
  }
}
```

## ✅ 方案优势总结

1. **完全符合需求**
   - ✅ 无需Docker
   - ✅ 前端Vercel
   - ✅ 数据库Supabase
   - ✅ 配置化YAML

2. **成本优势**
   - ✅ 完全免费（公开仓库）
   - ✅ 无需付费的浏览器服务

3. **易于维护**
   - ✅ Workflow即配置
   - ✅ 版本控制
   - ✅ 可视化执行日志

4. **性能优势**
   - ✅ 无超时限制
   - ✅ 预装Chrome
   - ✅ 并行执行

## 🔄 迁移步骤

1. 删除`supabase/functions/`相关代码
2. 创建`.github/workflows/`目录
3. 创建`scripts/`目录和抓取脚本
4. 配置GitHub Secrets
5. 测试手动触发workflow
6. 等待定时任务自动执行

这个方案完全满足您的要求：纯前端Vercel + Supabase，无Docker，配置化操作！

