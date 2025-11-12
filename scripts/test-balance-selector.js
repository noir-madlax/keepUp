import puppeteer from 'puppeteer';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { getSiteConfig } from './scraper/supabase-client.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function testBalanceSelector() {
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
    
    // 设置Cookie
    if (cookie && cookie.cookie_data) {
      await page.setCookie(...cookie.cookie_data);
    }
    
    // 访问主页并设置LocalStorage
    if (cookie && cookie.storage_data) {
      await page.goto('https://dajiala.com/', { waitUntil: 'domcontentloaded' });
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
    
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // 测试不同的选择器
    const tests = [
      'div.yue',
      'div.yue span',
      'div.yue span:last-child',
      'div.yue span:nth-child(2)',
      'div[data-v-881cd9ba].yue span:last-child'
    ];
    
    console.log('\n🔍 测试选择器：\n');
    
    for (const selector of tests) {
      const result = await page.evaluate((sel) => {
        const el = document.querySelector(sel);
        if (!el) return { found: false };
        return {
          found: true,
          text: el.textContent.trim(),
          innerHTML: el.innerHTML.trim()
        };
      }, selector);
      
      console.log(`选择器: ${selector}`);
      if (result.found) {
        console.log(`  文本: "${result.text}"`);
        console.log(`  HTML: ${result.innerHTML}`);
        
        // 测试正则提取
        const match = result.text.match(/([\\d.]+)/);
        console.log(`  正则匹配: ${match ? match[1] : '无匹配'}`);
        console.log(`  转换为float: ${match ? parseFloat(match[1]) : 'NaN'}`);
      } else {
        console.log('  ❌ 未找到');
      }
      console.log('');
    }
    
  } catch (error) {
    console.error('❌ 错误:', error);
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

testBalanceSelector();

