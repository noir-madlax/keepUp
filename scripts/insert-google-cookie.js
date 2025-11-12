import { createClient } from '@supabase/supabase-js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Supabase 配置
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!supabaseUrl || !supabaseKey) {
  console.error('错误: 缺少 SUPABASE_URL 或 SUPABASE_SERVICE_ROLE_KEY 环境变量');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

async function insertGoogleCookie() {
  try {
    // 读取 cookie 文件
    const cookiePath = path.join(__dirname, '../cookies-temp/google');
    const cookieData = JSON.parse(fs.readFileSync(cookiePath, 'utf8'));

    console.log(`📖 读取到 ${cookieData.length} 个 Cookie`);

    // 计算过期时间（从cookie中找最晚的过期时间）
    const expirationDates = cookieData
      .filter(c => c.expirationDate)
      .map(c => new Date(c.expirationDate * 1000));
    
    const latestExpiration = expirationDates.length > 0 
      ? new Date(Math.max(...expirationDates.map(d => d.getTime())))
      : null;

    console.log('📅 Cookie 最晚过期时间:', latestExpiration);

    // 插入到数据库
    const { data, error } = await supabase
      .from('cookies')
      .upsert({
        site_slug: 'google',
        cookie_data: cookieData,
        is_valid: true,
        expires_at: latestExpiration?.toISOString() || null,
        updated_at: new Date().toISOString()
      }, {
        onConflict: 'site_slug'
      });

    if (error) {
      throw error;
    }

    console.log('✅ Google Cookie 成功插入数据库');
    console.log('数据:', data);

  } catch (error) {
    console.error('❌ 插入失败:', error.message);
    process.exit(1);
  }
}

insertGoogleCookie();

