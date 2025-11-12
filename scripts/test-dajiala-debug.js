import puppeteer from 'puppeteer';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function testDajialeSelector() {
  let browser;
  
  try {
    console.log('🚀 启动浏览器...');
    browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });
    
    // 加载Cookie
    console.log('🍪 加载Cookie...');
    const cookieFile = path.join(__dirname, '../cookies-temp/dajiale');
    const cookies = JSON.parse(fs.readFileSync(cookieFile, 'utf8'));
    await page.setCookie(...cookies);
    
    // 访问页面
    console.log('🌐 访问页面...');
    await page.goto('https://dajiala.com/main/interface?actnav=0', {
      waitUntil: 'networkidle2',
      timeout: 30000
    });
    
    // 等待一下
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // 查找所有可能包含余额的元素
    console.log('\n🔍 查找包含"余额"的元素...');
    const balanceElements = await page.evaluate(() => {
      const results = [];
      
      // 查找所有包含"余额"文本的元素
      const walker = document.createTreeWalker(
        document.body,
        NodeFilter.SHOW_TEXT,
        null,
        false
      );
      
      let node;
      while (node = walker.nextNode()) {
        if (node.textContent.includes('余额')) {
          const parent = node.parentElement;
          results.push({
            tagName: parent.tagName,
            className: parent.className,
            id: parent.id,
            innerHTML: parent.innerHTML,
            textContent: parent.textContent.trim(),
            selector: parent.className ? `${parent.tagName.toLowerCase()}.${parent.className.split(' ')[0]}` : parent.tagName.toLowerCase()
          });
        }
      }
      
      return results;
    });
    
    console.log('找到的元素:');
    balanceElements.forEach((el, i) => {
      console.log(`\n元素 ${i + 1}:`);
      console.log('  Tag:', el.tagName);
      console.log('  Class:', el.className);
      console.log('  ID:', el.id);
      console.log('  Text:', el.textContent);
      console.log('  HTML:', el.innerHTML);
      console.log('  建议选择器:', el.selector);
    });
    
    // 尝试多种选择器
    console.log('\n\n🎯 测试不同的选择器...');
    
    const selectors = [
      'div.yue',
      'div.yue span',
      'div.yue span:last-child',
      'div[data-v-881cd9ba].yue span:last-child',
      '.yue span:nth-child(2)'
    ];
    
    for (const selector of selectors) {
      try {
        const result = await page.evaluate((sel) => {
          const el = document.querySelector(sel);
          if (!el) return { found: false };
          return {
            found: true,
            text: el.textContent.trim(),
            innerHTML: el.innerHTML
          };
        }, selector);
        
        console.log(`\n选择器: ${selector}`);
        if (result.found) {
          console.log('  ✅ 找到元素');
          console.log('  文本:', result.text);
          console.log('  HTML:', result.innerHTML);
        } else {
          console.log('  ❌ 未找到元素');
        }
      } catch (error) {
        console.log(`  ❌ 错误: ${error.message}`);
      }
    }
    
    // 截图
    const screenshotPath = path.join(__dirname, 'temp', 'debug-dajiale.png');
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`\n📸 截图已保存: ${screenshotPath}`);
    
  } catch (error) {
    console.error('❌ 错误:', error);
  } finally {
    if (browser) {
      await browser.close();
      console.log('\n🔚 浏览器已关闭');
    }
  }
}

testDajialeSelector();

