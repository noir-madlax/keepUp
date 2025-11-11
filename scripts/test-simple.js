import { supabase } from './scraper/supabase-client.js';

async function test() {
  console.log('🧪 测试 Supabase 连接...');
  
  try {
    // 测试查询网站配置
    const { data: websites, error } = await supabase
      .from('websites')
      .select('*')
      .eq('slug', 'openrouter');
    
    if (error) {
      console.error('❌ 查询失败:', error);
      return;
    }
    
    console.log('✅ 查询成功:', websites);
    
    // 测试插入数据
    const { data: inserted, error: insertError } = await supabase
      .from('scraped_data')
      .insert({
        site_slug: 'openrouter',
        data: { credits: 7.999, test: true },
        screenshot_url: null
      })
      .select();
    
    if (insertError) {
      console.error('❌ 插入失败:', insertError);
      return;
    }
    
    console.log('✅ 插入成功:', inserted);
    
  } catch (err) {
    console.error('❌ 测试失败:', err);
  }
}

test();

