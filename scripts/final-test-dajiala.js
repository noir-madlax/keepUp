import puppeteer from 'puppeteer';
import { getSiteConfig } from './scraper/supabase-client.js';

async function finalTest() {
  let browser;
  
  try {
    console.log('🚀 启动浏览器...');
    browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });
    
    // 获取Cookie和LocalStorage
    const { website, cookie } = await getSiteConfig('dajiala');
    console.log('Cookie和Storage:', {
      hasCookie: !!cookie?.cookie_data,
      hasStorage: !!cookie?.storage_data
    });
    
    // 设置Cookie
    if (cookie && cookie.cookie_data) {
      await page.setCookie(...cookie.cookie_data);
    }
    
    // 访问主页并设置LocalStorage
    await page.goto('https://dajiala.com/', { waitUntil: 'domcontentloaded' });
    if (cookie && cookie.storage_data) {
      await page.evaluate((storageData) => {
        Object.keys(storageData).forEach(key => {
          localStorage.setItem(key, storageData[key]);
        });
      }, cookie.storage_data);
    }
    
    // 访问目标页面
    await page.goto('https://dajiala.com/main/interface?actnav=0', {
      waitUntil: 'networkidle2',
      timeout: 30000
    });
    
    // 重新设置LocalStorage
    if (cookie && cookie.storage_data) {
      await page.evaluate((storageData) => {
        Object.keys(storageData).forEach(key => {
          localStorage.setItem(key, storageData[key]);
        });
      }, cookie.storage_data);
    }
    
    // 等待元素
    await page.waitForSelector('div.yue', { timeout: 15000 });
    await page.waitForSelector('div.yue span:last-child', { timeout: 10000 });
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // 提取数据 - 方式1：直接获取文本
    const test1 = await page.evaluate(() => {
      const el = document.querySelector('div.yue span:last-child');
      return {
        found: !!el,
        text: el ? el.textContent.trim() : null,
        html: el ? el.innerHTML.trim() : null
      };
    });
    console.log('\n测试1 - 直接提取:', test1);
    
    // 提取数据 - 方式2：使用$eval
    const test2 = await page.$eval('div.yue span:last-child', el => ({
      text: el.textContent.trim(),
      html: el.innerHTML.trim()
    })).catch(e => ({ error: e.message }));
    console.log('测试2 - $eval:', test2);
    
    // 测试正则
    if (test1.text) {
      const match = test1.text.match(/([0-9.]+)/);
      console.log('\n正则测试:');
      console.log('  原始文本:', test1.text);
      console.log('  匹配结果:', match);
      console.log('  提取值:', match ? match[1] : 'null');
      console.log('  转换float:', match ? parseFloat(match[1]) : 'NaN');
    }
    
  } catch (error) {
    console.error('❌ 错误:', error);
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

finalTest();

