import { createClient } from '@supabase/supabase-js';
import * as dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// 加载环境变量
dotenv.config({ path: join(__dirname, '../../.env') });

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!supabaseUrl || !supabaseKey) {
  throw new Error('缺少 SUPABASE_URL 或 SUPABASE_SERVICE_ROLE_KEY 环境变量');
}

export const supabase = createClient(supabaseUrl, supabaseKey, {
  auth: {
    autoRefreshToken: false,
    persistSession: false
  }
});

/**
 * 获取网站配置和Cookie
 */
export async function getSiteConfig(siteSlug) {
  const { data: website, error: websiteError } = await supabase
    .from('websites')
    .select('*')
    .eq('slug', siteSlug)
    .eq('is_active', true)
    .single();

  if (websiteError) {
    throw new Error(`获取网站配置失败: ${websiteError.message}`);
  }

  // 首先尝试获取有效的 Cookie
  let { data: cookie, error: cookieError } = await supabase
    .from('cookies')
    .select('*')
    .eq('site_slug', siteSlug)
    .eq('is_valid', true)
    .order('created_at', { ascending: false })
    .limit(1)
    .maybeSingle();

  // 如果没有有效的 Cookie，尝试获取最新的一个（不管是否有效）
  if (!cookie) {
    console.warn(`未找到有效Cookie，尝试获取最新Cookie...`);
    const { data: latestCookie, error: latestError } = await supabase
      .from('cookies')
      .select('*')
      .eq('site_slug', siteSlug)
      .order('created_at', { ascending: false })
      .limit(1)
      .maybeSingle();
    
    if (latestError) {
      console.error(`获取Cookie失败: ${latestError.message}`);
      return { website, cookie: null };
    }
    
    cookie = latestCookie;
  }

  if (!cookie) {
    console.warn(`站点 ${siteSlug} 没有任何Cookie数据`);
    return { website, cookie: null };
  }

  return { website, cookie };
}

/**
 * 保存抓取数据
 */
export async function saveScrapedData(siteSlug, data, screenshotUrl) {
  const { error } = await supabase
    .from('scraped_data')
    .insert({
      site_slug: siteSlug,
      data,
      screenshot_url: screenshotUrl
    });

  if (error) {
    throw new Error(`保存数据失败: ${error.message}`);
  }

  console.log(`✅ 数据已保存到数据库: ${siteSlug}`);
}

/**
 * 更新Cookie状态
 */
export async function updateCookieStatus(siteSlug, isValid) {
  // 先检查是否存在记录
  const { data: existing, error: checkError } = await supabase
    .from('cookies')
    .select('id')
    .eq('site_slug', siteSlug)
    .maybeSingle();

  if (checkError) {
    console.error(`检查Cookie记录失败: ${checkError.message}`);
    throw checkError;
  }

  if (existing) {
    // 更新现有记录
    const { error } = await supabase
      .from('cookies')
      .update({ 
        is_valid: isValid,
        updated_at: new Date().toISOString() 
      })
      .eq('site_slug', siteSlug);

    if (error) {
      console.error(`更新Cookie状态失败: ${error.message}`);
      throw error;
    }
  } else {
    // 创建新记录（用于不需要真实Cookie的API方式）
    const { error } = await supabase
      .from('cookies')
      .insert({
        site_slug: siteSlug,
        cookies: {},  // 空对象，因为不需要真实Cookie
        is_valid: isValid
      });

    if (error) {
      console.error(`创建Cookie记录失败: ${error.message}`);
      throw error;
    }
  }
}

/**
 * 上传截图到Supabase Storage
 */
export async function uploadScreenshot(siteSlug, buffer) {
  const fileName = `${siteSlug}-${Date.now()}.png`;
  const filePath = `${siteSlug}/${fileName}`;

  const { data, error } = await supabase.storage
    .from('monitor-screenshots')
    .upload(filePath, buffer, {
      contentType: 'image/png',
      upsert: false
    });

  if (error) {
    throw new Error(`上传截图失败: ${error.message}`);
  }

  const { data: { publicUrl } } = supabase.storage
    .from('monitor-screenshots')
    .getPublicUrl(filePath);

  console.log(`✅ 截图已上传: ${publicUrl}`);
  return publicUrl;
}

