import { ScraperEngine } from './scraper/engine.js';
import { loadConfig, validateConfig } from './scraper/config-parser.js';
import { getSiteConfig, saveScrapedData, updateCookieStatus, uploadScreenshot } from './scraper/supabase-client.js';
import fs from 'fs';

const SITE_SLUG = 'tikhub';
const CONFIG_PATH = '../monitor-configs/tikhub-simple.yaml';

async function main() {
  let engine = null;

  try {
    console.log(`\n========== 开始抓取: TikHub ==========\n`);

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

    // 6. 截图
    console.log('📸 截取页面截图...');
    const screenshotPath = await engine.screenshot({ full_page: false });
    const screenshotBuffer = fs.readFileSync(screenshotPath);
    const screenshotUrl = await uploadScreenshot(SITE_SLUG, screenshotBuffer);

    // 7. 保存数据
    await saveScrapedData(SITE_SLUG, data, screenshotUrl);

    console.log('\n✅ TikHub 抓取完成！');
    console.log('提取的数据:', JSON.stringify(data, null, 2));

  } catch (error) {
    console.error('\n❌ 抓取失败:', error.message);
    await updateCookieStatus(SITE_SLUG, false);
    process.exit(1);
  } finally {
    if (engine) {
      await engine.close();
    }
  }
}

main();

