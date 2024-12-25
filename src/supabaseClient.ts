import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseAnonKey,{
    auth: {
      persistSession: true,        // 确保会话持久化
      detectSessionInUrl: true,    // 允许从 URL 检测会话（例如 OAuth 回调）
    },
  })