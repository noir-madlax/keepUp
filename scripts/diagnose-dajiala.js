import puppeteer from 'puppeteer';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function diagnoseDajiala() {
  let browser;
  
  try {
    console.log('🚀 启动浏览器（有头模式以便检查）...');
    browser = await puppeteer.launch({
      headless: false,  // 有头模式
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });
    
    // 加载Cookie
    console.log('🍪 加载Cookie...');
    const cookieFile = path.join(__dirname, '../cookies-temp/dajiala');
    const cookies = JSON.parse(fs.readFileSync(cookieFile, 'utf8'));
    console.log(`找到 ${cookies.length} 个Cookie`);
    
    // 先访问主页再设置Cookie
    console.log('\n🌐 访问主页（不带Cookie）...');
    await page.goto('https://dajiala.com/', {
      waitUntil: 'networkidle2',
      timeout: 30000
    });
    
    console.log('🍪 设置所有Cookie...');
    await page.setCookie(...cookies);
    
    // 刷新页面
    console.log('🔄 刷新页面...');
    await page.reload({ waitUntil: 'networkidle2' });
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // 检查LocalStorage和SessionStorage
    console.log('\n📦 检查存储：');
    const storage = await page.evaluate(() => {
      return {
        localStorage: Object.keys(localStorage).map(key => ({
          key,
          value: localStorage.getItem(key)
        })),
        sessionStorage: Object.keys(sessionStorage).map(key => ({
          key,
          value: sessionStorage.getItem(key)
        }))
      };
    });
    
    console.log('LocalStorage:', JSON.stringify(storage.localStorage, null, 2));
    console.log('SessionStorage:', JSON.stringify(storage.sessionStorage, null, 2));
    
    // 访问目标页面
    console.log('\n🌐 访问目标页面...');
    await page.goto('https://dajiala.com/main/interface?actnav=0', {
      waitUntil: 'networkidle2',
      timeout: 30000
    });
    
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // 检查余额显示
    const balanceInfo = await page.evaluate(() => {
      const balanceDiv = document.querySelector('div.yue');
      if (!balanceDiv) return { found: false };
      
      const spans = Array.from(balanceDiv.querySelectorAll('span'));
      return {
        found: true,
        fullText: balanceDiv.textContent.trim(),
        spans: spans.map(span => span.textContent.trim())
      };
    });
    
    console.log('\n💰 余额信息:', JSON.stringify(balanceInfo, null, 2));
    
    // 截图
    const screenshotPath = path.join(__dirname, 'temp', 'diagnose-dajiala.png');
    await page.screenshot({ path: screenshotPath, fullPage: false });
    console.log(`📸 截图已保存: ${screenshotPath}`);
    
    console.log('\n⏳ 等待30秒以便您检查页面...');
    console.log('请检查浏览器窗口，看是否显示正确的余额');
    await new Promise(resolve => setTimeout(resolve, 30000));
    
  } catch (error) {
    console.error('❌ 错误:', error);
  } finally {
    if (browser) {
      await browser.close();
      console.log('\n🔚 浏览器已关闭');
    }
  }
}

diagnoseDajiala();

