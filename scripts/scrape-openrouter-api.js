#!/usr/bin/env node

/**
 * OpenRouter API 监控脚本
 * 使用 OpenRouter API 获取 API Key 使用情况，不再依赖浏览器自动化
 */

import { getSiteConfig, storeScrapedData } from './scraper/supabase-client.js';
import * as dotenv from 'dotenv';

dotenv.config({ path: '../.env' });

const SITE_SLUG = 'openrouter';
const TARGET_KEY_NAME = 'dev-for-keep-lightsail'; // 目标监控的 API Key 名称

/**
 * 调用 OpenRouter API 获取 API Keys 列表
 */
async function fetchApiKeys() {
  const provisionKey = process.env.OPENROUTER_PROVISION_KEY;
  
  if (!provisionKey) {
    throw new Error('❌ 缺少环境变量: OPENROUTER_PROVISION_KEY');
  }

  console.log('📡 调用 OpenRouter API...');
  
  const response = await fetch('https://openrouter.ai/api/v1/keys', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${provisionKey}`,
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
 * 从 API 响应中提取目标 Key 的数据
 */
function extractKeyData(apiResponse) {
  if (!apiResponse.data || !Array.isArray(apiResponse.data)) {
    throw new Error('API 响应格式错误: 缺少 data 数组');
  }

  // 查找目标 API Key
  const targetKey = apiResponse.data.find(key => key.name === TARGET_KEY_NAME);
  
  if (!targetKey) {
    console.warn(`⚠️  未找到名为 "${TARGET_KEY_NAME}" 的 API Key`);
    console.log('📋 可用的 API Keys:');
    apiResponse.data.forEach(key => {
      console.log(`  - ${key.name} (${key.disabled ? '已禁用' : '启用中'})`);
    });
    throw new Error(`未找到目标 API Key: ${TARGET_KEY_NAME}`);
  }

  console.log(`✅ 找到目标 Key: ${targetKey.name}`);
  
  // 提取关键数据
  const extractedData = {
    name: targetKey.name,
    label: targetKey.label,
    disabled: targetKey.disabled,
    limit: targetKey.limit,
    limit_remaining: targetKey.limit_remaining,
    usage: targetKey.usage,
    usage_daily: targetKey.usage_daily,
    usage_weekly: targetKey.usage_weekly,
    usage_monthly: targetKey.usage_monthly,
    limit_reset: targetKey.limit_reset,
    created_at: targetKey.created_at,
    updated_at: targetKey.updated_at
  };

  console.log('\n📊 提取的数据:');
  console.log(`  额度限制: ${extractedData.limit}`);
  console.log(`  剩余额度: ${extractedData.limit_remaining}`);
  console.log(`  总使用量: ${extractedData.usage}`);
  console.log(`  本月使用: ${extractedData.usage_monthly}`);
  console.log(`  状态: ${extractedData.disabled ? '❌ 已禁用' : '✅ 启用中'}`);

  return extractedData;
}

/**
 * 主函数
 */
async function main() {
  console.log('\n========== 开始抓取: OpenRouter (API 方式) ==========\n');

  try {
    // 1. 获取网站配置（验证数据库连接）
    console.log('🔑 获取网站配置...');
    const { website } = await getSiteConfig(SITE_SLUG);
    console.log(`✅ 网站: ${website.name}`);

    // 2. 调用 OpenRouter API
    const apiResponse = await fetchApiKeys();
    console.log(`✅ API 返回 ${apiResponse.data.length} 个 API Keys`);

    // 3. 提取目标 Key 的数据
    const extractedData = extractKeyData(apiResponse);

    // 4. 保存到数据库（不需要截图，因为是 API 方式）
    console.log('\n💾 保存数据到数据库...');
    await storeScrapedData(SITE_SLUG, extractedData, null);
    console.log('✅ 数据已保存到数据库');

    console.log('\n✅ OpenRouter (API) 抓取完成！');
    console.log('提取的数据:', JSON.stringify(extractedData, null, 2));

  } catch (error) {
    console.error('\n❌ 抓取失败:', error.message);
    if (error.stack) {
      console.error('错误堆栈:', error.stack);
    }
    process.exit(1);
  }
}

// 执行主函数
main();

