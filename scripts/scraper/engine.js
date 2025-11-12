import puppeteer from 'puppeteer';
import fs from 'fs';
import path from 'path';

/**
 * 通用抓取引擎
 */
export class ScraperEngine {
  constructor(config, cookies) {
    this.config = config;
    this.cookies = cookies;
    this.browser = null;
    this.page = null;
    this.extractedData = {};
  }

  /**
   * 初始化浏览器
   */
  async init() {
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

    // 在 GitHub Actions 环境中使用系统 Chrome
    if (process.env.GITHUB_ACTIONS === 'true') {
      console.log('🔧 检测到 GitHub Actions 环境，使用系统 Chrome');
      launchOptions.executablePath = '/usr/bin/google-chrome';
    } else {
      console.log('🔧 本地环境，使用 Puppeteer Chromium');
    }

    this.browser = await puppeteer.launch(launchOptions);

    this.page = await this.browser.newPage();
    await this.page.setViewport({ width: 1920, height: 1080 });

    if (this.cookies && this.cookies.cookie_data) {
      console.log('🍪 设置Cookies...');
      await this.page.setCookie(...this.cookies.cookie_data);
    }

    // 如果有storage_data，设置LocalStorage
    if (this.cookies && this.cookies.storage_data) {
      console.log('📦 设置LocalStorage...');
      // 先访问域名以便设置LocalStorage
      const url = new URL(this.config.url);
      await this.page.goto(`${url.protocol}//${url.host}`, { waitUntil: 'domcontentloaded' });
      
      // 设置LocalStorage
      await this.page.evaluate((storageData) => {
        Object.keys(storageData).forEach(key => {
          localStorage.setItem(key, storageData[key]);
        });
      }, this.cookies.storage_data);
      
      console.log(`✅ 已设置 ${Object.keys(this.cookies.storage_data).length} 个LocalStorage项`);
    }
  }

  /**
   * 执行所有步骤
   */
  async execute() {
    for (const step of this.config.steps) {
      await this.executeStep(step);
    }
    return this.extractedData;
  }

  /**
   * 执行单个步骤
   */
  async executeStep(step) {
    console.log(`📍 执行步骤: ${step.action} ${step.comment || ''}`);

    switch (step.action) {
      case 'navigate':
        await this.navigate(step);
        break;
      case 'wait':
        await this.wait(step);
        break;
      case 'extract':
        await this.extract(step);
        break;
      case 'screenshot':
        return await this.screenshot(step);
      default:
        console.warn(`⚠️  未知操作: ${step.action}`);
    }
  }

  /**
   * 导航到URL
   */
  async navigate(step) {
    const timeout = step.timeout || 30000;
    const waitUntil = step.wait_for || 'networkidle2';

    await this.page.goto(step.url, {
      timeout,
      waitUntil
    });

    // 导航后，如果有storage_data，重新设置LocalStorage
    if (this.cookies && this.cookies.storage_data) {
      console.log('📦 重新设置LocalStorage...');
      await this.page.evaluate((storageData) => {
        Object.keys(storageData).forEach(key => {
          localStorage.setItem(key, storageData[key]);
        });
        // 验证设置是否成功
        return {
          keys: Object.keys(localStorage),
          userInfo: localStorage.getItem('userInfo')
        };
      }, this.cookies.storage_data).then(result => {
        console.log(`✅ LocalStorage已设置: ${result.keys.join(', ')}`);
      });
    }

    console.log(`✅ 已导航到: ${step.url}`);
  }

  /**
   * 等待元素
   */
  async wait(step) {
    const timeout = step.timeout || 15000;
    
    try {
      await this.page.waitForSelector(step.selector, { timeout });
      console.log(`✅ 元素已出现: ${step.selector}`);
    } catch (error) {
      throw new Error(`等待元素超时: ${step.selector}`);
    }
  }

  /**
   * 提取数据
   */
  async extract(step) {
    const { name, selector, extract_type, attribute, regex_pattern, regex_group, transform } = step;

    try {
      let value;

      if (extract_type === 'attribute') {
        value = await this.page.$eval(selector, (el, attr) => el.getAttribute(attr), attribute);
      } else if (extract_type === 'text') {
        value = await this.page.$eval(selector, el => el.textContent.trim());
      } else if (extract_type === 'regex') {
        const text = await this.page.$eval(selector, el => el.textContent.trim());
        const match = text.match(new RegExp(regex_pattern));
        value = match && match[regex_group] ? match[regex_group] : null;
      }

      if (regex_pattern && extract_type !== 'regex') {
        const match = (value || '').match(new RegExp(regex_pattern));
        value = match && match[regex_group] ? match[regex_group] : null;
      }

      if (transform === 'int') {
        value = parseInt(value, 10);
      } else if (transform === 'float') {
        value = parseFloat(value);
      }

      this.extractedData[name] = value;
      console.log(`✅ 提取数据 ${name}: ${value}`);
    } catch (error) {
      console.error(`❌ 提取失败 ${name}: ${error.message}`);
      this.extractedData[name] = null;
    }
  }

  /**
   * 截图
   */
  async screenshot(step) {
    const tempDir = path.resolve('./temp');
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir, { recursive: true });
    }

    const fileName = `screenshot-${Date.now()}.png`;
    const filePath = path.join(tempDir, fileName);

    await this.page.screenshot({
      path: filePath,
      fullPage: step.full_page !== false,
      type: 'png'
    });

    console.log(`✅ 截图已保存: ${filePath}`);
    return filePath;
  }

  /**
   * 验证Cookie有效性
   */
  async validateCookie() {
    if (!this.config.validation || !this.config.validation.cookie_check) {
      console.warn('⚠️  配置中未定义Cookie验证规则');
      return true;
    }

    const { selector, should_exist } = this.config.validation.cookie_check;

    try {
      const element = await this.page.$(selector);
      const exists = element !== null;

      if (exists === should_exist) {
        console.log('✅ Cookie验证通过');
        return true;
      } else {
        console.error('❌ Cookie验证失败');
        return false;
      }
    } catch (error) {
      console.error(`❌ Cookie验证出错: ${error.message}`);
      return false;
    }
  }

  /**
   * 关闭浏览器
   */
  async close() {
    if (this.browser) {
      await this.browser.close();
      console.log('🔚 浏览器已关闭');
    }
  }
}

