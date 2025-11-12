import puppeteer from 'puppeteer';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { getSiteConfig, saveScrapedData, updateCookieStatus, uploadScreenshot } from './scraper/supabase-client.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const SITE_SLUG = 'dajiala';

async function main() {
  let browser = null;
  
  try {
    console.log(`\n========== 开始抓取: 大嘉乐 ==========\n`);
    
    // 1. 获取Cookie和LocalStorage配置
    console.log('🔑 获取Cookie和LocalStorage配置...');
    const { website, cookie } = await getSiteConfig(SITE_SLUG);
    
    if (!cookie || !cookie.cookie_data) {
      throw new Error('未找到有效的Cookie');
    }
    
    if (!cookie.storage_data) {
      throw new Error('未找到LocalStorage配置');
    }
    
    // 2. 启动浏览器
    console.log('🚀 启动浏览器...');
    const launchOptions = {
      headless: 'new',
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu'
      ]
    };
    
    if (process.env.GITHUB_ACTIONS === 'true') {
      console.log('🔧 检测到 GitHub Actions 环境，使用系统 Chrome');
      launchOptions.executablePath = '/usr/bin/google-chrome';
    } else {
      console.log('🔧 本地环境，使用 Puppeteer Chromium');
    }
    
    browser = await puppeteer.launch(launchOptions);
    const page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });
    
    // 3. 设置Cookie
    console.log('🍪 设置Cookies...');
    await page.setCookie(...cookie.cookie_data);
    
    // 4. 访问主页并设置LocalStorage
    console.log('🌐 访问主页并设置LocalStorage...');
    await page.goto('https://dajiala.com/', { 
      waitUntil: 'domcontentloaded',
      timeout: 30000
    });
    
    await page.evaluate((storageData) => {
      Object.keys(storageData).forEach(key => {
        localStorage.setItem(key, storageData[key]);
      });
    }, cookie.storage_data);
    console.log(`✅ 已设置 ${Object.keys(cookie.storage_data).length} 个LocalStorage项`);
    
    // 5. 访问目标页面
    console.log('🌐 访问目标页面...');
    await page.goto('https://dajiala.com/main/interface?actnav=0', {
      waitUntil: 'networkidle2',
      timeout: 30000
    });
    
    // 6. 重新设置LocalStorage（关键步骤！）
    console.log('📦 重新设置LocalStorage...');
    await page.evaluate((storageData) => {
      Object.keys(storageData).forEach(key => {
        localStorage.setItem(key, storageData[key]);
      });
    }, cookie.storage_data);
    
    // 7. 等待余额元素
    console.log('⏳ 等待余额元素加载...');
    await page.waitForSelector('div.yue', { timeout: 15000 });
    await page.waitForSelector('div.yue span:last-child', { timeout: 10000 });
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // 8. 提取余额数据
    console.log('📊 提取余额数据...');
    const balance = await page.$eval('div.yue span:last-child', el => el.textContent.trim());
    console.log(`  原始值: "${balance}"`);
    
    const match = balance.match(/([0-9.]+)/);
    if (!match) {
      throw new Error(`无法从 "${balance}" 中提取数字`);
    }
    
    const balanceValue = parseFloat(match[1]);
    console.log(`✅ 提取余额: ${balanceValue}`);
    
    // 9. 截图
    console.log('📸 截取页面截图...');
    const tempDir = path.join(__dirname, 'temp');
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir, { recursive: true });
    }
    
    const screenshotPath = path.join(tempDir, `screenshot-${Date.now()}.png`);
    await page.screenshot({ path: screenshotPath, fullPage: false });
    const screenshotBuffer = fs.readFileSync(screenshotPath);
    
    // 10. 上传截图
    const screenshotUrl = await uploadScreenshot(SITE_SLUG, screenshotBuffer);
    console.log(`✅ 截图已上传: ${screenshotUrl}`);
    
    // 11. 保存数据
    const data = { balance: balanceValue };
    await saveScrapedData(SITE_SLUG, data, screenshotUrl);
    await updateCookieStatus(SITE_SLUG, true);
    
    console.log('\n✅ 大嘉乐 抓取完成！');
    console.log('📊 提取的数据:', JSON.stringify(data, null, 2));
    
  } catch (error) {
    console.error('\n❌ 抓取失败:', error.message);
    console.error(error.stack);
    
    try {
      await updateCookieStatus(SITE_SLUG, false);
    } catch (updateError) {
      console.error('⚠️  无法更新Cookie状态:', updateError.message);
    }
    
    process.exit(1);
  } finally {
    if (browser) {
      await browser.close();
      console.log('🔚 浏览器已关闭');
    }
  }
}

main();

