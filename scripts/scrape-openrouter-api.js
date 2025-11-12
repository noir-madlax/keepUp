#!/usr/bin/env node

/**
 * OpenRouter API 监控脚本
 * 使用 OpenRouter API 获取 Credits 余额，不再依赖浏览器自动化
 */

import { getSiteConfig, saveScrapedData, updateCookieStatus } from './scraper/supabase-client.js';
import * as dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

dotenv.config({ path: join(__dirname, '../.env') });

const SITE_SLUG = 'openrouter';

/**
 * 调用 OpenRouter API 获取 Credits 余额
 */
async function fetchCredits() {
  const apiKey = process.env.OPENROUTER_PROVISION_KEY;
  
  if (!apiKey) {
    throw new Error('❌ 缺少环境变量: OPENROUTER_PROVISION_KEY');
  }

  console.log('📡 调用 OpenRouter API 获取 Credits...');
  
  const response = await fetch('https://openrouter.ai/api/v1/credits', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json'
    }
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API 请求失败 (${response.status}): ${errorText}`);
  }

  const data = await response.json();
  return data;
}

/**
 * 从 API 响应中提取 Credits 数据
 */
function extractCreditsData(apiResponse) {
  if (!apiResponse.data) {
    throw new Error('API 响应格式错误: 缺少 data 字段');
  }

  const { total_credits, total_usage } = apiResponse.data;
  
  // 计算余额
  const balance = total_credits - total_usage;
  
  // 提取关键数据
  const extractedData = {
    total_credits: total_credits,
    total_usage: total_usage,
    balance: balance
  };

  console.log('\n📊 提取的数据:');
  console.log(`  总 Credits: ${total_credits}`);
  console.log(`  已使用: ${total_usage}`);
  console.log(`  余额: ${balance}`);

  return extractedData;
}

/**
 * 主函数
 */
async function main() {
  console.log('\n========== 开始抓取: OpenRouter Credits (API 方式) ==========\n');

  try {
    // 1. 获取网站配置（验证数据库连接）
    console.log('🔑 获取网站配置...');
    const { website } = await getSiteConfig(SITE_SLUG);
    console.log(`✅ 网站: ${website.name}`);

    // 2. 调用 OpenRouter API 获取 Credits
    const apiResponse = await fetchCredits();
    console.log(`✅ API 调用成功`);

    // 3. 提取 Credits 数据
    const extractedData = extractCreditsData(apiResponse);

    // 4. 保存到数据库（不需要截图，因为是 API 方式）
    console.log('\n💾 保存数据到数据库...');
    await saveScrapedData(SITE_SLUG, extractedData, null);
    console.log('✅ 数据已保存到数据库');

    // 5. 更新 Cookie 状态为有效（API 调用成功即视为有效）
    console.log('\n🔄 更新状态为有效...');
    await updateCookieStatus(SITE_SLUG, true);
    console.log('✅ 状态已更新为有效');

    console.log('\n✅ OpenRouter Credits 抓取完成！');
    console.log('提取的数据:', JSON.stringify(extractedData, null, 2));

  } catch (error) {
    console.error('\n❌ 抓取失败:', error.message);
    if (error.stack) {
      console.error('错误堆栈:', error.stack);
    }
    
    // 更新 Cookie 状态为无效
    try {
      await updateCookieStatus(SITE_SLUG, false);
      console.log('⚠️  状态已更新为无效');
    } catch (updateError) {
      console.error('更新状态失败:', updateError.message);
    }
    
    process.exit(1);
  }
}

// 执行主函数
main();

