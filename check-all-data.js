import { createClient } from '@supabase/supabase-js';
import * as dotenv from 'dotenv';
dotenv.config();

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY
);

async function checkAllData() {
  console.log('=== 检查所有站点的最新数据 ===\n');
  
  const sites = ['cursor', 'openrouter', 'tikhub'];
  
  for (const site of sites) {
    console.log(`--- ${site.toUpperCase()} ---`);
    
    const { data, error } = await supabase
      .from('scraped_data')
      .select('data, screenshot_url, created_at')
      .eq('site_slug', site)
      .order('created_at', { ascending: false })
      .limit(1)
      .maybeSingle();
    
    if (error) {
      console.log(`❌ 查询失败: ${error.message}\n`);
      continue;
    }
    
    if (!data) {
      console.log(`⚠️  没有数据\n`);
      continue;
    }
    
    console.log(`✅ 最新数据 (${new Date(data.created_at).toLocaleString('zh-CN')})`);
    console.log(`数据:`, JSON.stringify(data.data, null, 2));
    console.log(`截图: ${data.screenshot_url ? '✅ 已保存' : '❌ 无'}\n`);
  }
}

checkAllData();

