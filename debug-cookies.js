import puppeteer from 'puppeteer';
import fs from 'fs';

async function debugCookies() {
  console.log('=== 调试 Cookie 设置 ===\n');
  
  const cookieData = JSON.parse(fs.readFileSync('cookies-temp/openrouter', 'utf8'));
  console.log(`📖 读取到 ${cookieData.length} 个 Cookie\n`);
  
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  
  // 设置 Cookie
  console.log('🍪 设置 Cookie...');
  const puppeteerCookies = cookieData.map(cookie => ({
    name: cookie.name,
    value: cookie.value,
    domain: cookie.domain,
    path: cookie.path || '/',
    expires: cookie.expirationDate || undefined,
    httpOnly: cookie.httpOnly || false,
    secure: cookie.secure || false,
    sameSite: cookie.sameSite === 'unspecified' ? 'Lax' : cookie.sameSite || 'Lax'
  }));
  
  await page.setCookie(...puppeteerCookies);
  console.log('✅ Cookie 已设置\n');
  
  // 访问页面
  console.log('🌐 访问 OpenRouter...');
  await page.goto('https://openrouter.ai/settings/credits', { 
    waitUntil: 'networkidle0',
    timeout: 45000 
  });
  
  // 读取实际设置的 Cookie
  const actualCookies = await page.cookies();
  console.log(`\n📋 实际设置的 Cookie 数量: ${actualCookies.length}`);
  
  // 检查关键 Cookie
  const sessionCookie = actualCookies.find(c => c.name === '__session');
  const refreshCookie = actualCookies.find(c => c.name === '__refresh_NO6jtgZM');
  
  console.log('\n🔑 关键 Cookie 检查:');
  console.log(`  __session: ${sessionCookie ? '✅ 存在' : '❌ 缺失'}`);
  if (sessionCookie) {
    console.log(`    Value: ${sessionCookie.value.substring(0, 30)}...`);
    console.log(`    HttpOnly: ${sessionCookie.httpOnly}`);
  }
  
  console.log(`  __refresh_NO6jtgZM: ${refreshCookie ? '✅ 存在' : '❌ 缺失'}`);
  if (refreshCookie) {
    console.log(`    Value: ${refreshCookie.value}`);
    console.log(`    HttpOnly: ${refreshCookie.httpOnly}`);
  }
  
  // 检查页面内容
  const title = await page.title();
  console.log(`\n📄 页面标题: ${title}`);
  
  // 检查是否显示登录页面
  const hasSignIn = await page.evaluate(() => {
    return document.body.textContent.includes('Sign in to OpenRouter');
  });
  
  console.log(`🔐 是否显示登录页: ${hasSignIn ? '✅ 是（未登录）' : '❌ 否（已登录）'}`);
  
  // 检查网络请求
  console.log('\n🌐 检查是否有刷新请求...');
  const requests = await page.evaluate(() => {
    return window.performance.getEntries()
      .filter(e => e.entryType === 'resource')
      .map(e => ({ name: e.name, initiatorType: e.initiatorType }))
      .filter(e => e.name.includes('clerk') || e.name.includes('refresh') || e.name.includes('token'));
  });
  
  console.log(`找到 ${requests.length} 个相关请求:`);
  requests.forEach(r => console.log(`  - ${r.name}`));
  
  await browser.close();
}

debugCookies();
