# 添加新监控渠道指南

本文档说明如何为监控系统添加新渠道。

## 📋 核心步骤

1. ✅ 创建 YAML 配置文件
2. ✅ 创建抓取脚本  
3. ✅ 配置数据库
4. ✅ 配置 GitHub Actions
5. ✅ 本地测试
6. ✅ GitHub Actions 测试

---

## 1️⃣ 创建 YAML 配置文件

### 文件位置
`monitor-configs/{渠道}-simple.yaml`

### 配置模板

```yaml
name: "{渠道名称}"
url: "{目标URL}"
description: "{渠道描述}"

steps:
  # 1. 导航到页面
  - action: "navigate"
    url: "{目标URL}"
    wait_for: "networkidle2"
    timeout: 30000
    comment: "访问页面"
  
  # 2. 等待页面加载
  - action: "wait"
    selector: "body"
    timeout: 10000
    comment: "等待页面基本加载"
  
  # 3. 等待数据元素
  - action: "wait"
    selector: "{数据元素CSS选择器}"
    timeout: 20000
    comment: "等待数据加载"
  
  # 4. 提取数据
  - action: "extract"
    name: "{字段名}"
    selector: "{精确CSS选择器}"
    extract_type: "text"
    regex_pattern: "\\$([\\d.]+)"  # 可选
    regex_group: 1                  # 可选
    transform: "float"              # float/int/string
    comment: "提取数据"
  
  # 5. 截图
  - action: "screenshot"
    full_page: false
    comment: "截取页面"

# Cookie验证
validation:
  cookie_check:
    selector: "{验证元素选择器}"
    should_exist: true
```

### 实际示例 (Google)

```yaml
name: "Google AI Studio"
url: "https://aistudio.google.com/usage?timeRange=last-7-days&tab=billing&project=xxx"
description: "Google AI Studio 费用监控"

steps:
  - action: "navigate"
    url: "https://aistudio.google.com/usage?timeRange=last-7-days&tab=billing&project=xxx"
    wait_for: "networkidle2"
    timeout: 30000
  
  - action: "wait"
    selector: "body"
    timeout: 10000
  
  - action: "wait"
    selector: "sdui-block"
    timeout: 25000
    comment: "等待费用容器加载"
  
  - action: "wait"
    selector: "sdui-text-fragment"
    timeout: 20000
  
  - action: "extract"
    name: "total_cost"
    selector: "sdui-text-fragment[style*='font-size: 24px'][style*='font-weight: 600']"
    extract_type: "text"
    regex_pattern: "\\$([\\d.]+)"
    regex_group: 1
    transform: "float"
    comment: "提取总费用"
  
  - action: "screenshot"
    full_page: false

validation:
  cookie_check:
    selector: "sdui-text-fragment[style*='font-size: 24px']"
    should_exist: true
```

**💡 提示**：
- 使用浏览器开发者工具找到目标元素的CSS选择器
- 将参考HTML保存到 `ref/{渠道}.target.div` 方便查看
- CSS选择器要足够精确，避免匹配到错误元素

---

## 2️⃣ 创建抓取脚本

### 文件位置
`scripts/scrape-{渠道}.js`

### 脚本模板

```javascript
import { ScraperEngine } from './scraper/engine.js';
import { loadConfig, validateConfig } from './scraper/config-parser.js';
import { getSiteConfig, saveScrapedData, updateCookieStatus, uploadScreenshot } from './scraper/supabase-client.js';
import fs from 'fs';

const SITE_SLUG = '{渠道}';
const CONFIG_PATH = '../monitor-configs/{渠道}-simple.yaml';

async function main() {
  let engine = null;

  try {
    console.log(`\\n========== 开始抓取: {渠道名称} ==========\\n`);

    // 1. 加载配置
    console.log('📄 加载配置文件...');
    const config = loadConfig(CONFIG_PATH);
    validateConfig(config);

    // 2. 获取Cookie
    console.log('🔑 获取Cookie...');
    const { website, cookie } = await getSiteConfig(SITE_SLUG);
    
    if (!cookie) {
      throw new Error('未找到有效的Cookie');
    }

    // 3. 初始化抓取引擎
    engine = new ScraperEngine(config, cookie);
    await engine.init();

    // 4. 执行抓取
    console.log('🕷️  开始抓取数据...');
    const data = await engine.execute();

    // 5. 验证Cookie
    console.log('🔍 验证Cookie有效性...');
    const isValid = await engine.validateCookie();
    await updateCookieStatus(SITE_SLUG, isValid);

    if (!isValid) {
      throw new Error('Cookie验证失败');
    }

    // 6. 截图并保存
    console.log('📸 截取页面截图...');
    const screenshotPath = await engine.screenshot({ full_page: false });
    const screenshotBuffer = fs.readFileSync(screenshotPath);
    const screenshotUrl = await uploadScreenshot(SITE_SLUG, screenshotBuffer);

    // 7. 保存数据
    await saveScrapedData(SITE_SLUG, data, screenshotUrl);

    console.log('\\n✅ 抓取完成！');
    console.log('提取的数据:', JSON.stringify(data, null, 2));

  } catch (error) {
    console.error('\\n❌ 抓取失败:', error.message);
    await updateCookieStatus(SITE_SLUG, false);
    process.exit(1);
  } finally {
    if (engine) {
      await engine.close();
    }
  }
}

main();
```

**注意**：只需修改 `SITE_SLUG` 和 `CONFIG_PATH`，其他代码保持不变。

---

## 3️⃣ 配置数据库

### 3.1 插入网站配置

```sql
INSERT INTO websites (name, slug, url, display_order, description, is_active)
VALUES (
  '{渠道显示名称}',
  '{渠道slug}',
  '{目标URL}',
  {显示顺序},
  '{描述}',
  true
)
RETURNING id, name, slug;
```

**示例 (Google)**:

```sql
INSERT INTO websites (name, slug, url, display_order, description, is_active)
VALUES (
  'Google AI Studio',
  'google',
  'https://aistudio.google.com/usage?timeRange=last-7-days&tab=billing&project=gen-lang-client-0662613502',
  4,
  'Google AI Studio 费用监控',
  true
)
RETURNING id, name, slug;
```

### 3.2 插入 Cookie

```sql
INSERT INTO cookies (site_slug, cookie_data, is_valid, expires_at)
VALUES (
  '{渠道slug}',
  '[{...完整Cookie JSON数组...}]'::jsonb,
  true,
  '{过期时间}'::timestamptz
)
RETURNING id, site_slug, is_valid;
```

**如何获取 Cookie**:
1. 浏览器登录目标网站
2. 打开开发者工具 → Application → Cookies
3. 使用 EditThisCookie 插件导出为 JSON
4. 临时保存到 `cookies-temp/{渠道}` 文件
5. 使用 MCP 插入数据库后，删除临时文件

---

## 4️⃣ 配置 GitHub Actions

### 4.1 更新 monitor-all.yml

**文件**: `.github/workflows/monitor-all.yml`

修改 matrix 添加新渠道：

```yaml
strategy:
  matrix:
    site: [openrouter, cursor, tikhub, google, dajiala, {新渠道}]
  fail-fast: false
```

### 4.2 创建独立 workflow 文件 ⚠️ 重要！

**文件**: `.github/workflows/monitor-{渠道}.yml`

```yaml
name: Monitor {渠道名称}

on:
  workflow_dispatch:
  workflow_call:

jobs:
  scrape:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: scripts/package-lock.json
      
      - name: Install dependencies
        run: |
          cd scripts
          npm ci
        env:
          PUPPETEER_SKIP_DOWNLOAD: 'true'
      
      - name: Run {渠道名称} scraper
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
          SITE_SLUG: {渠道slug}
        run: |
          cd scripts
          node scrape-{渠道slug}.js
      
      - name: Upload screenshots on failure
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: screenshots-{渠道slug}
          path: scripts/temp/*.png
          retention-days: 7
```

**💡 重要**：必须创建独立 workflow 文件，否则无法在 GitHub Actions 界面看到该渠道！

---

## 5️⃣ 本地测试

### 5.1 设置环境变量

在项目根目录的 `.env` 文件中设置（或临时导出）：

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

### 5.2 运行本地测试

```bash
cd scripts
node scrape-{渠道}.js
```

### 5.3 期待输出

```
========== 开始抓取: {渠道名称} ==========

📄 加载配置文件...
🔑 获取Cookie...
🚀 启动浏览器...
🔧 本地环境，使用 Puppeteer Chromium
🍪 设置Cookies...
🕷️  开始抓取数据...
📍 执行步骤: navigate 访问页面
✅ 已导航到: {URL}
📍 执行步骤: wait 等待页面基本加载
✅ 元素已出现: body
📍 执行步骤: extract 提取数据
✅ 提取数据 {字段名}: {值}
🔍 验证Cookie有效性...
✅ Cookie验证通过
📸 截取页面截图...
✅ 截图已上传: https://...
✅ 数据已保存到数据库: {渠道}

✅ 抓取完成！
提取的数据: {
  "{字段名}": {值}
}
```

### 5.4 验证数据库

```sql
-- 查看最新数据
SELECT site_slug, data, created_at
FROM scraped_data 
WHERE site_slug = '{渠道}'
ORDER BY created_at DESC
LIMIT 1;
```

---

## 6️⃣ GitHub Actions 生产测试

### 6.1 提交代码

```bash
# 查看待提交文件
git status

# 添加所有相关文件
git add monitor-configs/{渠道}-simple.yaml
git add scripts/scrape-{渠道}.js
git add .github/workflows/monitor-{渠道}.yml
git add .github/workflows/monitor-all.yml

# 提交
git commit -m "添加 {渠道} 监控功能

- 创建 {渠道}-simple.yaml 配置
- 创建 scrape-{渠道}.js 脚本
- 添加独立 workflow 文件
- 更新 monitor-all.yml"

# 推送到 GitHub
git push origin main
```

### 6.2 等待部署完成

- **Vercel 部署**: 约 30-60 秒
- **GitHub 识别 workflow**: 约 10 秒

### 6.3 触发测试

**方式 1: 通过 Vercel API** (推荐，快速)

```bash
curl -X POST "https://keep-up-nine.vercel.app/api/trigger-scrape?site={渠道}" \
  -H "Content-Type: application/json"
```

**方式 2: GitHub Actions 界面手动触发**

1. 访问 `https://github.com/{user}/{repo}/actions`
2. 点击左侧 `Monitor {渠道名称}`
3. 点击 `Run workflow` → 选择 `main` → 点击 `Run workflow`

**方式 3: 触发所有渠道**

```bash
curl -X POST "https://keep-up-nine.vercel.app/api/trigger-scrape" \
  -H "Content-Type: application/json"
```

### 6.4 等待执行

- **执行时间**: 约 60-90 秒
- **查看日志**: Actions 页面 → 点击运行记录 → 查看详细日志

### 6.5 验证结果

**查看 GitHub Actions 日志**:
```
https://github.com/{user}/{repo}/actions
```

**查看数据库**:

```sql
-- 查看最近 5 分钟的数据
SELECT 
  site_slug,
  data,
  created_at,
  ROUND(EXTRACT(EPOCH FROM (NOW() - created_at))/60, 1) as 分钟前
FROM scraped_data 
WHERE site_slug = '{渠道}'
  AND created_at > NOW() - INTERVAL '5 minutes'
ORDER BY created_at DESC;
```

**查看前端**:
访问 `https://keep-up-nine.vercel.app/monitor` 确认卡片显示正常。

---

## 📋 完整文件清单

添加新渠道后应有的文件：

```
keepup-v2/
├── monitor-configs/
│   ├── {渠道}-simple.yaml          # ✅ 配置文件
│   └── ref/
│       └── {渠道}.target.div       # 📋 参考HTML（可选）
├── scripts/
│   └── scrape-{渠道}.js            # ✅ 抓取脚本
└── .github/workflows/
    ├── monitor-all.yml             # ✅ 已修改（matrix添加新渠道）
    └── monitor-{渠道}.yml          # ✅ 独立workflow文件 ⚠️ 重要！
```

---

## 🔍 故障排查

### 本地测试失败

**问题**: 元素等待超时
- 检查 CSS 选择器是否正确
- 增加 timeout 时间
- 添加调试截图步骤查看页面状态

**问题**: Cookie 无效
- 重新导出最新的 Cookie
- 检查 Cookie 过期时间
- 确认浏览器中可以正常访问

### GitHub Actions 失败

**问题**: npm ci 报错
- 确保 `package-lock.json` 已更新（运行 `npm install`）
- 提交 package-lock.json 到 git

**问题**: 找不到 workflow
- 确认 workflow 文件已提交到 GitHub
- 检查文件名格式: `monitor-{渠道}.yml`
- 检查文件位置: `.github/workflows/`

**问题**: 环境变量未设置
- 在 GitHub 仓库设置中添加 Secrets:
  - `SUPABASE_URL`
  - `SUPABASE_SERVICE_ROLE_KEY`

---

## 📊 Cookie 有效期管理

定期检查所有渠道的 Cookie 状态：

```sql
SELECT 
  site_slug AS 渠道,
  is_valid AS 是否有效,
  expires_at AS 过期时间,
  CASE 
    WHEN expires_at IS NULL THEN '未设置'
    WHEN expires_at < NOW() THEN '已过期'
    WHEN expires_at < NOW() + INTERVAL '30 days' THEN '30天内过期'
    ELSE '长期有效'
  END AS 状态,
  ROUND(EXTRACT(EPOCH FROM (expires_at - NOW())) / 86400) AS 剩余天数
FROM cookies
ORDER BY expires_at NULLS LAST;
```

**建议**:
- 长期 Cookie (1年): 每3个月检查一次
- 短期 Cookie (1个月): 每周检查一次
- 如果抓取失败，立即检查并更新 Cookie

---

## 🎯 代码架构说明

### 抓取逻辑在哪里？

```
scrape-{渠道}.js (入口文件)
    ↓
    ├─ 加载配置: {渠道}-simple.yaml  ← 【抓取逻辑定义在这里！】
    │   └─ config-parser.js (解析YAML)
    │
    ├─ 获取Cookie: 从数据库读取
    │   └─ supabase-client.js
    │
    ├─ 执行抓取: ScraperEngine
    │   └─ engine.js  ← 【通用引擎，执行YAML指令】
    │       ├─ navigate (访问页面)
    │       ├─ wait (等待元素)
    │       ├─ extract (提取数据)
    │       └─ screenshot (截图)
    │
    └─ 保存数据: 保存到数据库
        └─ supabase-client.js
```

**重点**:
- `scrape-{渠道}.js`: 不包含抓取逻辑，只是协调流程
- `{渠道}-simple.yaml`: **抓取元素和逻辑定义在这里**
- `engine.js`: 通用引擎，读取并执行 YAML 配置

---

## ✅ 检查清单

添加新渠道前确认：

- [ ] 创建 `{渠道}-simple.yaml` 配置文件
- [ ] 创建 `scrape-{渠道}.js` 脚本
- [ ] 数据库插入 `websites` 记录
- [ ] 数据库插入 `cookies` 记录
- [ ] 更新 `monitor-all.yml` 的 matrix
- [ ] 创建 `monitor-{渠道}.yml` 独立workflow
- [ ] 本地测试成功
- [ ] 提交所有文件到 GitHub
- [ ] GitHub Actions 测试成功
- [ ] 数据库验证数据已保存
- [ ] 前端页面显示正常

---

**文档版本**: v2.0  
**最后更新**: 2025-11-12  
**维护**: Development Team
