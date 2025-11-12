import { supabase } from './scraper/supabase-client.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function updateDajialeCookie() {
  try {
    console.log('\n========== 更新大嘉乐Cookie ==========\n');
    
    // 读取Cookie文件
    const cookieFile = path.join(__dirname, '../cookies-temp/dajiala');
    console.log('📄 读取Cookie文件:', cookieFile);
    
    const cookieData = JSON.parse(fs.readFileSync(cookieFile, 'utf8'));
    console.log(`✅ 读取到 ${cookieData.length} 个Cookie`);
    
    // 更新数据库中的Cookie
    console.log('\n🔄 更新Cookie到数据库...');
    const { data, error } = await supabase
      .from('cookies')
      .update({
        cookie_data: cookieData,
        is_valid: true,
        expires_at: '2026-12-12T00:00:00Z',
        updated_at: new Date().toISOString()
      })
      .eq('site_slug', 'dajiala')
      .select();
    
    if (error) {
      throw new Error(`更新失败: ${error.message}`);
    }
    
    console.log('✅ Cookie已更新');
    console.log('更新的记录:', data);
    
    console.log('\n📝 请按以下步骤操作：');
    console.log('1. 在浏览器中访问: https://dajiala.com/main/interface?actnav=0');
    console.log('2. 确保已登录并能看到余额（例如：余额： 189.14）');
    console.log('3. 使用EditThisCookie等工具导出Cookie（JSON格式）');
    console.log('4. 将导出的Cookie覆盖到: cookies-temp/dajiala');
    console.log('5. 再次运行此脚本更新数据库');
    console.log('6. 运行: node scrape-dajiala.js 进行测试\n');
    
  } catch (error) {
    console.error('❌ 错误:', error.message);
    process.exit(1);
  }
}

updateDajialeCookie();

