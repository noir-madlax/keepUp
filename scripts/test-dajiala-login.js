import puppeteer from 'puppeteer';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function testDajialeLogin() {
  let browser;
  
  try {
    console.log('🚀 启动浏览器...');
    browser = await puppeteer.launch({
      headless: false,  // 使用有头模式以便调试
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });
    
    // 先访问主页（不带Cookie）
    console.log('🌐 访问主页...');
    await page.goto('https://dajiala.com/', {
      waitUntil: 'networkidle2',
      timeout: 30000
    });
    
    // 加载Cookie
    console.log('🍪 设置Cookie...');
    const cookieFile = path.join(__dirname, '../cookies-temp/dajiale');
    const cookies = JSON.parse(fs.readFileSync(cookieFile, 'utf8'));
    await page.setCookie(...cookies);
    
    // 刷新页面使Cookie生效
    console.log('🔄 刷新页面使Cookie生效...');
    await page.reload({ waitUntil: 'networkidle2' });
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // 检查是否登录
    console.log('🔍 检查登录状态...');
    const loginStatus = await page.evaluate(() => {
      // 查找用户名或者余额元素
      const userElement = document.querySelector('.username, .user-name, [class*="user"]');
      const balanceElement = document.querySelector('.yue');
      
      return {
        hasUser: !!userElement,
        hasBalance: !!balanceElement,
        userText: userElement ? userElement.textContent.trim() : null,
        balanceText: balanceElement ? balanceElement.textContent.trim() : null
      };
    });
    
    console.log('登录状态:', loginStatus);
    
    // 访问目标页面
    console.log('\n🌐 访问目标页面...');
    await page.goto('https://dajiala.com/main/interface?actnav=0', {
      waitUntil: 'networkidle2',
      timeout: 30000
    });
    
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // 检查余额
    console.log('\n🔍 检查余额显示...');
    const balanceInfo = await page.evaluate(() => {
      const balanceDiv = document.querySelector('div.yue');
      if (!balanceDiv) return { found: false };
      
      return {
        found: true,
        fullText: balanceDiv.textContent.trim(),
        html: balanceDiv.innerHTML,
        spans: Array.from(balanceDiv.querySelectorAll('span')).map(span => ({
          text: span.textContent.trim(),
          className: span.className,
          attributes: Array.from(span.attributes).map(attr => ({
            name: attr.name,
            value: attr.value
          }))
        }))
      };
    });
    
    console.log('余额信息:');
    console.log(JSON.stringify(balanceInfo, null, 2));
    
    // 截图
    const screenshotPath = path.join(__dirname, 'temp', 'dajiale-login-test.png');
    await page.screenshot({ path: screenshotPath, fullPage: false });
    console.log(`\n📸 截图已保存: ${screenshotPath}`);
    
    // 等待一下以便查看
    console.log('\n⏳ 等待10秒以便查看页面...');
    await new Promise(resolve => setTimeout(resolve, 10000));
    
  } catch (error) {
    console.error('❌ 错误:', error);
  } finally {
    if (browser) {
      await browser.close();
      console.log('\n🔚 浏览器已关闭');
    }
  }
}

testDajialeLogin();

