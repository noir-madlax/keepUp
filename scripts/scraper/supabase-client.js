import { createClient } from '@supabase/supabase-js';

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

  const { data: cookie, error: cookieError } = await supabase
    .from('cookies')
    .select('*')
    .eq('site_slug', siteSlug)
    .eq('is_valid', true)
    .order('created_at', { ascending: false })
    .limit(1)
    .single();

  if (cookieError) {
    console.warn(`未找到有效Cookie: ${cookieError.message}`);
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
  const { error } = await supabase
    .from('cookies')
    .update({ is_valid: isValid, updated_at: new Date().toISOString() })
    .eq('site_slug', siteSlug);

  if (error) {
    console.error(`更新Cookie状态失败: ${error.message}`);
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

