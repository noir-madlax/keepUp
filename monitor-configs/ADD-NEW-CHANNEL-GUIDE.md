# 添加新监控渠道完整指南

本文档详细说明如何为监控系统添加一个新的渠道。

## 📋 总览

添加一个新渠道需要完成以下步骤：

1. ✅ 准备工作
2. ✅ 创建配置文件
3. ✅ 创建抓取脚本
4. ✅ 数据库配置
5. ✅ GitHub Actions 配置
6. ✅ 前端验证
7. ✅ 测试验证

## 1️⃣ 准备工作

### 1.1 收集必要信息

在开始之前，你需要准备：

- **目标网站URL**：要监控的页面地址
- **Cookie**：导出的认证Cookie（JSON格式）
- **目标数据元素**：要提取的数据在页面上的HTML结构
- **渠道标识**：英文slug，如 `google`、`cursor` 等

### 1.2 页面调研

使用浏览器工具：

1. 打开目标页面
2. 使用浏览器MCP工具访问页面
3. 找到目标数据的HTML元素
4. 记录CSS选择器或其他定位方式
5. 确认数据格式（数字、文本等）

**示例**：
```html
<!-- Google AI Studio 费用示例 -->
<sdui-text-fragment style="font-size: 24px; font-weight: 600;">
  $24.5
</sdui-text-fragment>
```

## 2️⃣ 创建配置文件

### 2.1 创建YAML配置

**位置**: `monitor-configs/{渠道}-simple.yaml`

**模板**:
```yaml
# {渠道名称} 简化配置
name: "{渠道显示名称}"
url: "{目标URL}"
description: "{渠道描述}"

steps:
  # 1. 导航到页面
  - action: "navigate"
    url: "{目标URL}"
    wait_for: "networkidle2"
    timeout: 30000
    comment: "访问 {渠道} 页面"
  
  # 2. 等待页面加载
  - action: "wait"
    selector: "body"
    timeout: 10000
    comment: "等待页面基本加载完成"
  
  # 3. 等待数据加载
  - action: "wait"
    selector: "{数据元素选择器}"
    timeout: 15000
    comment: "等待数据加载"
  
  # 4. 提取数据
  - action: "extract"
    name: "{数据字段名}"
    selector: "{精确的CSS选择器}"
    extract_type: "text"  # 或 "attribute"
    regex_pattern: "{正则表达式}"  # 可选，用于提取特定部分
    regex_group: 1  # 可选，提取正则的第几组
    transform: "float"  # 或 "int", "string"
    comment: "提取{数据说明}"
  
  # 5. 截图
  - action: "screenshot"
    full_page: false
    comment: "截取页面当前视图"

# 验证配置
validation:
  cookie_check:
    selector: "{验证元素选择器}"
    should_exist: true
```

**实际示例** (Google AI Studio):
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
    selector: "sdui-text-fragment"
    timeout: 15000
  
  - action: "extract"
    name: "total_cost"
    selector: "sdui-text-fragment[style*='font-size: 24px'][style*='font-weight: 600']"
    extract_type: "text"
    regex_pattern: "\\$([\\d.]+)"
    regex_group: 1
    transform: "float"
    comment: "提取总费用金额"
  
  - action: "screenshot"
    full_page: false

validation:
  cookie_check:
    selector: "sdui-text-fragment"
    should_exist: true
```

### 2.2 保存Cookie文件

**位置**: `cookies-temp/{渠道}`

将导出的Cookie JSON保存到此文件。

**格式要求**:
```json
[
  {
    "domain": ".example.com",
    "name": "session_id",
    "value": "xxx",
    "expirationDate": 1234567890,
    ...
  }
]
```

## 3️⃣ 创建抓取脚本

### 3.1 创建脚本文件

**位置**: `scripts/scrape-{渠道}.js`

**模板**:
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
    console.log('🚀 开始执行抓取...');
    const result = await engine.execute();

    // 5. 保存数据
    if (result.success) {
      console.log('💾 保存抓取数据...');
      
      // 上传截图
      let screenshotUrl = null;
      if (result.screenshot) {
        screenshotUrl = await uploadScreenshot(
          SITE_SLUG,
          result.screenshot,
          `${SITE_SLUG}-${Date.now()}.png`
        );
        console.log(`📸 截图已上传: ${screenshotUrl}`);
      }

      // 保存数据到数据库
      await saveScrapedData(SITE_SLUG, result.data, screenshotUrl);
      await updateCookieStatus(SITE_SLUG, true);
      
      console.log('✅ 抓取成功完成！');
      console.log('📊 提取的数据:', JSON.stringify(result.data, null, 2));
    } else {
      throw new Error(result.error || '抓取失败');
    }

  } catch (error) {
    console.error('❌ 抓取失败:', error.message);
    
    // 更新Cookie状态为无效
    try {
      await updateCookieStatus(SITE_SLUG, false);
    } catch (updateError) {
      console.error('⚠️  无法更新Cookie状态:', updateError.message);
    }
    
    process.exit(1);
  } finally {
    if (engine) {
      await engine.close();
    }
  }
}

main();
```

## 4️⃣ 数据库配置

### 4.1 插入网站配置

使用MCP执行SQL：

```sql
-- 插入网站配置
INSERT INTO websites (
  name, 
  slug, 
  url, 
  scraper_config, 
  display_order, 
  icon_url, 
  description,
  is_active
)
VALUES (
  '{渠道显示名称}',
  '{渠道slug}',
  '{目标URL}',
  '{YAML配置的JSONB格式}'::jsonb,
  {显示顺序},
  '{图标URL}',
  '{详细描述}',
  true
)
RETURNING id, name, slug, is_active;
```

**实际示例** (Google):
```sql
INSERT INTO websites (
  name, 
  slug, 
  url, 
  scraper_config, 
  display_order, 
  icon_url, 
  description,
  is_active
)
VALUES (
  'Google AI Studio',
  'google',
  'https://aistudio.google.com/usage?timeRange=last-7-days&tab=billing&project=xxx',
  '{...}'::jsonb,  -- YAML配置转换的JSON
  4,
  'https://www.google.com/favicon.ico',
  'Google AI Studio 费用监控 - 监控 Gemini API 使用费用',
  true
)
RETURNING id, name, slug, is_active;
```

### 4.2 插入Cookie

使用MCP执行SQL：

```sql
-- 插入Cookie
INSERT INTO cookies (
  site_slug,
  cookie_data,
  is_valid,
  expires_at
)
VALUES (
  '{渠道slug}',
  '{Cookie JSON数组}'::jsonb,
  true,
  '{过期时间}'::timestamptz
)
RETURNING id, site_slug, is_valid;
```

**实际示例** (Google):
```sql
INSERT INTO cookies (
  site_slug,
  cookie_data,
  is_valid,
  expires_at
)
VALUES (
  'google',
  '[{"domain":".google.com",...}]'::jsonb,
  true,
  '2026-11-12'::timestamptz
)
RETURNING id, site_slug, is_valid;
```

## 5️⃣ GitHub Actions 配置

### 5.1 修改统一工作流文件

**文件**: `.github/workflows/monitor-all.yml`

**修改内容**:
```yaml
strategy:
  matrix:
    site: [openrouter, cursor, tikhub, {新渠道}]  # 添加新渠道
  fail-fast: false
```

**实际示例**:
```yaml
strategy:
  matrix:
    site: [openrouter, cursor, tikhub, google]  # 添加google
  fail-fast: false
```

### 5.2 创建独立工作流文件 ⚠️ **重要步骤**

为了能在 GitHub Actions 界面手动触发单个渠道的监控，需要创建独立的 workflow 文件。

**位置**: `.github/workflows/monitor-{渠道}.yml`

**模板**:
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

**实际示例** (Google):
```yaml
name: Monitor Google

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
      
      - name: Run Google scraper
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
          SITE_SLUG: google
        run: |
          cd scripts
          node scrape-google.js
      
      - name: Upload screenshots on failure
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: screenshots-google
          path: scripts/temp/*.png
          retention-days: 7
```

**注意事项**:
- 这个独立的 workflow 文件允许你在 GitHub Actions 界面手动触发单个渠道的监控
- `workflow_dispatch` 启用手动触发
- `workflow_call` 允许被其他 workflow 调用
- 如果没有这个文件，虽然 `monitor-all.yml` 可以运行该渠道，但在 Actions 界面看不到独立的 workflow

### 5.2 配置GitHub Secrets

在GitHub仓库中配置必要的Secrets：

1. 访问 GitHub 仓库页面
2. 进入 `Settings` → `Secrets and variables` → `Actions`
3. 点击 `New repository secret`
4. 添加以下Secrets：
   - `SUPABASE_URL`: Supabase项目URL
   - `SUPABASE_SERVICE_ROLE_KEY`: Supabase服务密钥
   - 其他API密钥（如需要）

### 5.3 启用GitHub Actions

**重要**: 如果这是首次添加workflow，需要确保：

1. **提交workflow文件到GitHub**:
   ```bash
   git add .github/workflows/monitor-all.yml
   git add scripts/scrape-{渠道}.js
   git add monitor-configs/{渠道}-simple.yaml
   git commit -m "feat: 添加{渠道}监控"
   git push origin main
   ```

2. **在GitHub上启用Actions**:
   - 访问仓库的 `Actions` 标签页
   - 如果看到提示，点击 `I understand my workflows, go ahead and enable them`
   - 确认workflow出现在列表中

3. **检查workflow文件权限**:
   - 确保 `.github/workflows/monitor-all.yml` 有正确的权限
   - GitHub Actions 需要 `workflow` 权限才能运行

## 6️⃣ 前端验证

### 6.1 前端自动加载

前端会自动从数据库加载所有 `is_active=true` 的网站配置，**通常不需要修改前端代码**。

**自动加载位置**: `src/views/MonitorView.vue`

```typescript
async function loadWebsites() {
  // 自动从数据库加载所有active的网站
  const { data } = await supabase
    .from('websites')
    .select('*')
    .eq('is_active', true)
    .order('display_order')
  
  websites.value = data  // 新渠道会自动出现
}
```

### 6.2 验证前端显示

1. 启动前端开发服务器
2. 访问监控页面
3. 确认新渠道卡片出现
4. 检查数据显示是否正常

## 7️⃣ 测试验证

### 7.1 本地测试抓取

```bash
cd scripts

# 设置环境变量
export SUPABASE_URL="your_supabase_url"
export SUPABASE_SERVICE_ROLE_KEY="your_service_role_key"

# 运行抓取脚本
node scrape-{渠道}.js
```

**期待输出**:
```
========== 开始抓取: {渠道名称} ==========

📄 加载配置文件...
🔑 获取Cookie...
🚀 开始执行抓取...
💾 保存抓取数据...
📸 截图已上传: https://...
✅ 抓取成功完成！
📊 提取的数据: {
  "field_name": "value"
}
```

### 7.2 数据库验证

```sql
-- 验证网站配置
SELECT * FROM websites WHERE slug = '{渠道}';

-- 验证Cookie
SELECT * FROM cookies WHERE site_slug = '{渠道}';

-- 验证抓取数据
SELECT * FROM scraped_data 
WHERE site_slug = '{渠道}' 
ORDER BY created_at DESC 
LIMIT 1;
```

### 7.3 前端验证

1. 访问 `/monitor` 页面
2. 查看新渠道卡片
3. 点击刷新按钮测试
4. 检查数据更新

### 7.4 提交代码到GitHub

**关键步骤** - 必须执行才能看到Actions！

```bash
# 1. 查看待提交的文件
git status

# 2. 添加新文件
git add .github/workflows/monitor-all.yml
git add scripts/scrape-{渠道}.js
git add monitor-configs/{渠道}-simple.yaml

# 3. 提交更改
git commit -m "feat: 添加{渠道}监控功能

- 添加{渠道}-simple.yaml配置文件
- 创建scrape-{渠道}.js抓取脚本
- 更新monitor-all.yml工作流
- 配置数据库表和Cookie"

# 4. 推送到远程仓库
git push origin main
```

**重要提示**:
- 如果有删除的文件，使用 `git add -A` 或 `git rm` 命令
- 确认所有相关文件都已添加到git
- 推送成功后，GitHub Actions才会生效

### 7.5 GitHub Actions 验证

**提交代码后的验证步骤**:

**步骤1**: 确认workflow已提交
1. 访问 `https://github.com/{your-username}/keepup/tree/main/.github/workflows`
2. 确认 `monitor-all.yml` 文件存在
3. 查看文件内容，确认包含新渠道

**步骤2**: 查看Actions标签页
1. 访问 `https://github.com/{your-username}/keepup/actions`
2. 如果首次使用，可能需要点击 `I understand my workflows, go ahead and enable them`
3. 应该能看到 `Monitor All Sites Daily` workflow

**步骤3**: 手动触发测试

**方式1**: 手动触发（推荐）
1. 访问 GitHub Actions 页面
2. 选择 `Monitor All Sites Daily` workflow
3. 点击 `Run workflow` 按钮
4. 选择 `main` 分支
5. 点击 `Run workflow` 确认
6. 等待workflow运行（会并行运行所有渠道）

**方式2**: 等待每日自动运行
- 每天 UTC 1:00 自动运行
- 北京时间 上午9:00

**步骤4**: 查看运行结果
1. 点击运行记录查看详情
2. 查看每个渠道的job执行情况
3. 如果失败，查看日志定位问题
4. 检查截图artifacts（失败时上传）

## 📝 完整文件清单

添加一个新渠道后，应该有以下文件：

```
keepup-v2/
├── monitor-configs/
│   ├── {渠道}-simple.yaml          # ✅ 配置文件
│   └── {渠道}.target.div           # 📋 参考HTML（可选）
├── cookies-temp/
│   └── {渠道}                      # 📋 Cookie文件（临时）
├── scripts/
│   └── scrape-{渠道}.js            # ✅ 抓取脚本
└── .github/workflows/
    ├── monitor-all.yml             # ✅ 已修改（matrix 添加新渠道）
    └── monitor-{渠道}.yml          # ✅ 新增独立 workflow 文件 ⚠️ 重要！
```

**重要提醒**: 必须同时创建独立的 workflow 文件，否则在 GitHub Actions 界面看不到该渠道！

## 🔍 常见问题

### Q0: GitHub上看不到Actions？⚠️ **最常见问题**

**A**: 
1. **最常见原因**: 没有创建独立的 workflow 文件 ⚠️
   - 即使 `monitor-all.yml` 的 matrix 包含了新渠道，也必须创建独立文件
   - 必须创建 `.github/workflows/monitor-{渠道}.yml`
   - 参考第 5.2 节的模板创建
   - 示例: `.github/workflows/monitor-google.yml`, `.github/workflows/monitor-dajiala.yml`

2. **workflow文件还未提交到GitHub**:
   ```bash
   git status  # 查看是否有未提交的文件
   git add .github/workflows/monitor-{渠道}.yml
   git commit -m "feat: 添加 {渠道} 的 GitHub Actions workflow"
   git push origin main
   ```

3. **Actions未启用**: 
   - 访问仓库的 `Actions` 标签页
   - 点击 `I understand my workflows, go ahead and enable them`

4. **workflow文件位置错误**: 
   - 必须在 `.github/workflows/` 目录下
   - 文件名必须是 `.yml` 或 `.yaml` 后缀

5. **workflow语法错误**: 
   - 检查YAML缩进
   - 使用 `yamllint` 验证语法
   - 查看GitHub Actions页面的错误提示

6. **权限问题**:
   - 检查仓库的 Actions 权限设置
   - `Settings` → `Actions` → `General` → 确保 `Allow all actions` 已启用

### Q1: 选择器找不到元素？

**A**: 
1. 检查页面是否完全加载
2. 增加等待时间
3. 使用浏览器MCP工具确认选择器
4. 尝试使用更宽泛的选择器

### Q2: Cookie失效？

**A**:
1. 重新导出Cookie
2. 检查Cookie过期时间
3. 更新数据库中的Cookie
4. 确认目标网站未更改认证机制

### Q3: 数据提取不正确？

**A**:
1. 检查选择器是否精确
2. 确认正则表达式正确
3. 检查数据类型转换
4. 使用浏览器工具测试选择器

### Q4: 前端不显示新渠道？

**A**:
1. 确认数据库 `websites.is_active = true`
2. 检查 `display_order` 是否正确
3. 清除浏览器缓存
4. 重启前端开发服务器

### Q5: GitHub Actions 失败？

**A**:
1. 检查环境变量配置
2. 验证Secret是否设置正确
3. 查看Actions日志定位问题
4. 本地测试是否成功

## 📊 最佳实践

### 1. 命名规范

- **Slug**: 小写英文，如 `google`、`openrouter`
- **文件名**: 使用slug，如 `scrape-google.js`
- **配置名**: 使用slug，如 `google-simple.yaml`

### 2. 选择器策略

- 优先使用稳定的属性（class、id）
- 避免使用容易变化的索引
- 使用属性选择器增加精确度
- 添加注释说明选择器用途

### 3. 错误处理

- 捕获所有可能的异常
- 提供清晰的错误信息
- 更新Cookie状态
- 记录详细日志

### 4. 数据验证

- 验证提取的数据格式
- 检查数据合理性
- 处理边界情况
- 提供默认值

### 5. 测试流程

1. 本地测试通过
2. 数据库验证通过
3. 前端显示正常
4. GitHub Actions 测试通过

## 🎯 检查清单

在提交代码前，确认以下项目：

- [ ] ✅ YAML配置文件创建并测试
- [ ] ✅ 抓取脚本创建并测试
- [ ] ✅ 数据库websites表插入成功
- [ ] ✅ 数据库cookies表插入成功
- [ ] ✅ monitor-all.yml 的 matrix 已添加新渠道
- [ ] ✅ **创建独立的 workflow 文件** `.github/workflows/monitor-{渠道}.yml` ⚠️ **重要！**
- [ ] ✅ workflow 文件已提交并推送到 GitHub
- [ ] ✅ GitHub Secrets已配置
- [ ] ✅ 在 GitHub Actions 界面可以看到新的 workflow
- [ ] ✅ 本地抓取测试成功
- [ ] ✅ 数据库数据验证成功
- [ ] ✅ 前端显示验证成功
- [ ] ✅ Cookie有效期确认
- [ ] ✅ 文档更新完整
- [ ] ✅ **代码已提交到GitHub**
- [ ] ✅ **GitHub Actions已启用并可见**

## 📚 参考示例

### 完整示例：Google AI Studio

可以参考以下文件作为完整示例：

1. **配置**: `monitor-configs/google-simple.yaml`
2. **脚本**: `scripts/scrape-google.js`
3. **文档**: `monitor-configs/GOOGLE-SETUP-COMPLETE.md`

### 其他渠道示例

- **Cursor**: `monitor-configs/cursor-simple.yaml`
- **TikHub**: `monitor-configs/tikhub-simple.yaml`
- **OpenRouter**: `monitor-configs/openrouter.yaml`

---

**文档版本**: v1.0  
**创建日期**: 2025-11-12  
**最后更新**: 2025-11-12  
**维护者**: Development Team

