-- =============================================
-- Supabase 触发器定义
-- =============================================

-- 1. 在keep_article_requests表上，自动创建原文字幕section（2025-10-30新增）
CREATE TRIGGER trg_auto_create_transcript
AFTER INSERT OR UPDATE OF content, article_id
ON keep_article_requests
FOR EACH ROW
WHEN (NEW.content IS NOT NULL AND NEW.article_id IS NOT NULL)
EXECUTE FUNCTION auto_create_transcript_section();

-- 2. 在keep_article_sections表上，当INSERT或UPDATE时自动入队embedding任务
CREATE TRIGGER trg_enqueue_embedding_job 
AFTER INSERT OR UPDATE OF content, section_type 
ON public.keep_article_sections 
FOR EACH ROW 
EXECUTE FUNCTION enqueue_embedding_job();

-- 3. 在keep_articles表上，UPDATE时自动更新updated_time
CREATE TRIGGER set_updated_time 
BEFORE UPDATE 
ON public.keep_articles 
FOR EACH ROW 
EXECUTE FUNCTION update_updated_time();

-- 4. 在keep_chat_sessions表上，UPDATE时自动更新updated_at
CREATE TRIGGER update_chat_sessions_updated_at 
BEFORE UPDATE 
ON public.keep_chat_sessions 
FOR EACH ROW 
EXECUTE FUNCTION update_updated_at_column();

