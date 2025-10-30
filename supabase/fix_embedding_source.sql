-- =============================================
-- 修复方案：让原文字幕embedding直接来自 keep_article_requests.content
-- =============================================

/*
问题分析：
1. 当前实现：原文字幕通过 ContentPolisherService 润色后，保存到 keep_article_sections 表
2. 然后触发器 trg_enqueue_embedding_job 才会为这些section创建embedding任务
3. 但是很多文章没有调用润色流程，导致没有创建原文字幕section

正确的实现：
1. 原文字幕应该直接来自 keep_article_requests.content（最原始的字幕）
2. 不依赖 keep_article_sections 表中的数据
3. 需要修改数据结构，让embedding可以关联到 keep_article_requests 表
*/

-- =============================================
-- 方案一：修改现有表结构（推荐）
-- =============================================

/*
修改 keep_article_embeddings 表，增加对 keep_article_requests 的支持：
1. 增加 request_id 字段，指向 keep_article_requests.id
2. section_id 改为可空（因为原文字幕不一定有section）
3. 修改触发器逻辑，当 keep_article_requests.content 更新时自动入队
*/

-- Step 1: 修改 keep_article_embeddings 表
-- 注意：这个操作需要谨慎，因为会影响现有数据
ALTER TABLE keep_article_embeddings 
ADD COLUMN IF NOT EXISTS request_id bigint REFERENCES keep_article_requests(id) ON DELETE CASCADE;

ALTER TABLE keep_article_embeddings 
ALTER COLUMN section_id DROP NOT NULL;

-- 添加检查约束：section_id 和 request_id 至少有一个不为空
ALTER TABLE keep_article_embeddings 
ADD CONSTRAINT check_source_exists CHECK (
  (section_id IS NOT NULL AND request_id IS NULL) OR 
  (section_id IS NULL AND request_id IS NOT NULL)
);

-- 为 request_id 创建索引
CREATE INDEX IF NOT EXISTS idx_article_embeddings_request_id 
ON keep_article_embeddings(request_id);

-- Step 2: 修改 embedding_jobs 表
ALTER TABLE embedding_jobs 
ADD COLUMN IF NOT EXISTS request_id bigint REFERENCES keep_article_requests(id) ON DELETE CASCADE;

ALTER TABLE embedding_jobs 
ALTER COLUMN section_id DROP NOT NULL;

-- 添加检查约束
ALTER TABLE embedding_jobs 
ADD CONSTRAINT check_job_source_exists CHECK (
  (section_id IS NOT NULL AND request_id IS NULL) OR 
  (section_id IS NULL AND request_id IS NOT NULL)
);

-- 为 request_id 创建索引
CREATE INDEX IF NOT EXISTS idx_embedding_jobs_request_id 
ON embedding_jobs(request_id);

-- Step 3: 创建新的触发器函数 - 监听 keep_article_requests 表
CREATE OR REPLACE FUNCTION public.enqueue_request_embedding_job()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE
  new_hash text;
  article_id_val bigint;
BEGIN
  -- 只处理有 content 的记录
  IF NEW.content IS NULL OR length(btrim(NEW.content)) = 0 THEN
    RETURN NEW;
  END IF;

  -- 只处理已关联文章的记录
  IF NEW.article_id IS NULL THEN
    RETURN NEW;
  END IF;

  new_hash := encode(digest(coalesce(NEW.content,''), 'md5'), 'hex');

  -- 插入原文字幕的embedding任务
  INSERT INTO public.embedding_jobs(request_id, source_hash, status, updated_at)
  VALUES (NEW.id, new_hash, 'pending', now())
  ON CONFLICT DO NOTHING;  -- 注意：这里需要调整 embedding_jobs 的唯一约束

  RETURN NEW;
END;
$function$;

-- Step 4: 创建触发器 - 监听 keep_article_requests 表
DROP TRIGGER IF EXISTS trg_enqueue_request_embedding_job ON public.keep_article_requests;

CREATE TRIGGER trg_enqueue_request_embedding_job 
AFTER INSERT OR UPDATE OF content, article_id 
ON public.keep_article_requests 
FOR EACH ROW 
WHEN (NEW.article_id IS NOT NULL AND NEW.content IS NOT NULL)
EXECUTE FUNCTION enqueue_request_embedding_job();

-- Step 5: 修改 embedding_jobs 表的唯一约束
-- 先删除旧约束（如果存在）
ALTER TABLE embedding_jobs DROP CONSTRAINT IF EXISTS embedding_jobs_section_id_source_hash_key;

-- 创建新的唯一索引（支持两种source）
CREATE UNIQUE INDEX IF NOT EXISTS embedding_jobs_section_source_unique 
ON embedding_jobs(section_id, source_hash) 
WHERE section_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS embedding_jobs_request_source_unique 
ON embedding_jobs(request_id, source_hash) 
WHERE request_id IS NOT NULL;

-- Step 6: 为1953往后的文章创建原文字幕embedding任务
-- 这会触发新的触发器，自动创建embedding_jobs
UPDATE keep_article_requests 
SET content = content  -- 触发UPDATE触发器
WHERE article_id >= 1953 
AND content IS NOT NULL 
AND length(btrim(content)) > 0;


-- =============================================
-- 方案二：保持现有结构，通过应用层解决（备选）
-- =============================================

/*
不修改数据库结构，通过应用层保证：
1. 每篇文章必须调用 ContentPolisherService.process_article_content
2. 创建一个 section_type='原文字幕' 的 section，内容直接来自 keep_article_requests.content
3. 然后现有的触发器会自动处理embedding

优点：不需要修改数据库结构
缺点：
  - 原文字幕被保存了两次（requests.content 和 sections.content）
  - 依赖应用层逻辑，容易漏掉
  - 数据冗余
*/

-- 如果选择方案二，只需要为缺失的文章创建原文字幕section即可
-- 这个可以通过 API 调用 /polish 接口来完成


-- =============================================
-- 推荐实施步骤
-- =============================================

/*
建议采用方案一，步骤如下：

1. 【数据库修改】执行上面的 Step 1-5（需要在 Supabase 中执行）
   - 修改 keep_article_embeddings 表结构
   - 修改 embedding_jobs 表结构
   - 创建新的触发器函数和触发器

2. 【后端代码修改】修改 embedding worker（处理embedding_jobs的代码）
   - 需要支持从 request_id 获取 content
   - 当 job.request_id 不为空时，从 keep_article_requests 获取 content
   - 当 job.section_id 不为空时，从 keep_article_sections 获取 content

3. 【触发历史数据处理】执行 Step 6
   - UPDATE keep_article_requests 触发新的触发器
   - 为1953往后的文章创建原文字幕embedding任务

4. 【前端修改】更新 RAG 检索逻辑
   - search_article_embeddings_v2 的 allowed_types 需要支持 '原文字幕'
   - 或者为原文字幕定义一个新的 section_type，如 'raw_subtitle'
*/


-- =============================================
-- 注意事项
-- =============================================

/*
1. 外键约束：修改表结构时要注意外键依赖
2. 唯一约束：embedding_jobs 的唯一约束需要调整
3. 数据迁移：现有的 embedding 数据不需要迁移，新旧数据可以共存
4. 应用代码：需要同步修改 backend 中处理 embedding_jobs 的代码
5. section_type：需要为原文字幕定义一个标准的 section_type 名称
*/

