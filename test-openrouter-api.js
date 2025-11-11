// 测试 OpenRouter API
import fetch from 'node-fetch';

async function testAPI() {
  console.log('=== 测试 OpenRouter API ===\n');
  
  // 常见的 API endpoints
  const endpoints = [
    'https://openrouter.ai/api/v1/auth/key',
    'https://openrouter.ai/api/v1/credits',
    'https://openrouter.ai/api/credits',
    'https://openrouter.ai/api/v1/account',
  ];
  
  for (const url of endpoints) {
    try {
      console.log(`尝试: ${url}`);
      const res = await fetch(url, {
        headers: {
          'User-Agent': 'Mozilla/5.0'
        }
      });
      console.log(`  状态: ${res.status} ${res.statusText}`);
      
      if (res.status !== 404) {
        const text = await res.text();
        console.log(`  响应: ${text.substring(0, 100)}...`);
      }
    } catch (err) {
      console.log(`  错误: ${err.message}`);
    }
    console.log();
  }
}

testAPI();
