-- =============================================
-- Supabase 函数定义
-- =============================================

-- 1. 自动创建原文字幕section的触发器函数（2025-10-30新增）
CREATE OR REPLACE FUNCTION public.auto_create_transcript_section()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
  -- 只处理有 content 和 article_id 的记录
  IF NEW.content IS NULL OR NEW.article_id IS NULL THEN
    RETURN NEW;
  END IF;

  -- 检查content是否为空字符串
  IF length(btrim(NEW.content)) = 0 THEN
    RETURN NEW;
  END IF;

  -- 检查是否已存在原文字幕section（防止重复）
  PERFORM 1 
  FROM keep_article_sections 
  WHERE article_id = NEW.article_id 
    AND section_type = '原文字幕';

  -- 如果不存在，则创建
  IF NOT FOUND THEN
    INSERT INTO keep_article_sections (
      article_id,
      section_type,
      content,
      sort_order,
      language
    ) VALUES (
      NEW.article_id,
      '原文字幕',
      NEW.content,
      1000,
      'zh'
    );
    
    RAISE NOTICE '已为文章 % 自动创建原文字幕section', NEW.article_id;
  END IF;

  RETURN NEW;
END;
$function$;

-- 2. 入队embedding任务的触发器函数
CREATE OR REPLACE FUNCTION public.enqueue_embedding_job()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE
  st text;
  new_hash text;
BEGIN
  st := coalesce(NEW.section_type, '');

  -- 扩展为包含原文类型（在保留现有摘要类型基础上）
  IF st NOT IN (
    'transcript','raw','paragraph','section','sentence',
    'Summary','Key Takeaways','Segmented Outline','Trending','Companies & Products',
    '总结','要点总结','分段大纲','趋势','公司与产品','人物介绍','核心观点','名词解释','QA环节','金句','未总结内容','彩蛋','典型案例','背景','结构图','思维导图','原文字幕'
  ) THEN
    RETURN NEW;
  END IF;

  IF NEW.content IS NULL OR length(btrim(NEW.content)) = 0 THEN
    RETURN NEW;
  END IF;

  new_hash := encode(digest(coalesce(NEW.content,''), 'md5'), 'hex');

  INSERT INTO public.embedding_jobs(section_id, source_hash, status, updated_at)
  VALUES (NEW.id, new_hash, 'pending', now())
  ON CONFLICT (section_id, source_hash) DO NOTHING;

  RETURN NEW;
END;
$function$;

-- 2. 增加文章浏览计数
CREATE OR REPLACE FUNCTION public.increment_article_viewer_count(article_id bigint)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
BEGIN
    UPDATE keep_articles 
    SET viewer_count = COALESCE(viewer_count, 0) + 1 
    WHERE id = article_id;
END;
$function$;

-- 3. 执行SQL的安全函数
CREATE OR REPLACE FUNCTION public.run_sql(query text)
 RETURNS jsonb
 LANGUAGE plpgsql
 SECURITY DEFINER
AS $function$
DECLARE
    result JSONB;
    temp_result text;
BEGIN
    -- 尝试将查询结果转换为JSON
    BEGIN
        EXECUTE format('WITH query_result AS (%s) SELECT json_agg(row_to_json(query_result)) FROM query_result', query) INTO result;
        
        -- 如果结果为null（没有行返回），返回空数组
        IF result IS NULL THEN
            result := '[]'::jsonb;
        END IF;
    EXCEPTION WHEN OTHERS THEN
        -- 如果转换失败，尝试执行原始查询并将结果转换为文本
        BEGIN
            EXECUTE query INTO temp_result;
            -- 如果执行成功但没有返回值，返回成功消息
            IF temp_result IS NULL THEN
                result := jsonb_build_object('message', 'Query executed successfully');
            ELSE
                result := jsonb_build_object('result', temp_result);
            END IF;
        EXCEPTION WHEN OTHERS THEN
            -- 如果仍然失败，返回错误信息
            result := jsonb_build_object('error', SQLERRM);
        END;
    END;
    
    RETURN result;
END;
$function$;

-- 4. 搜索文章embeddings（旧版）
CREATE OR REPLACE FUNCTION public.search_article_embeddings(query_embedding vector, match_threshold double precision DEFAULT 0.0, match_count integer DEFAULT 8)
 RETURNS TABLE(article_id bigint, section_id bigint, section_type text, language text, content text, score double precision)
 LANGUAGE sql
 STABLE
AS $function$
  select
    e.article_id,
    e.section_id,
    e.section_type,
    e.language,
    e.content,
    1 - (e.embedding <=> query_embedding) as score
  from public.keep_article_embeddings e
  where
    e.section_type in (
      'Summary',
      '人物介绍',
      'Key Takeaways',
      'Segmented Outline',
      'Trending',
      'Companies & Products'
    )
    and (1 - (e.embedding <=> query_embedding)) >= match_threshold
  order by e.embedding <=> query_embedding asc
  limit match_count;
$function$;

-- 5. 搜索文章embeddings V2（支持更多参数）
CREATE OR REPLACE FUNCTION public.search_article_embeddings_v2(
  query_embedding vector, 
  match_threshold double precision DEFAULT 0.2, 
  match_count integer DEFAULT 32, 
  lang text DEFAULT NULL::text, 
  allowed_types text[] DEFAULT ARRAY['transcript'::text, 'raw'::text, 'paragraph'::text, 'section'::text, 'sentence'::text], 
  article_filter bigint[] DEFAULT NULL::bigint[], 
  ef_search_param integer DEFAULT 80
)
 RETURNS TABLE(article_id bigint, section_id bigint, section_type text, language text, chunk_id integer, content text, score double precision)
 LANGUAGE plpgsql
 STABLE
AS $function$
BEGIN
  -- 设置 HNSW 搜索宽度（在线调参）
  PERFORM set_config('hnsw.ef_search', ef_search_param::text, true);

  RETURN QUERY
  SELECT
    e.article_id,
    e.section_id,
    e.section_type,
    e.language,
    e.chunk_id,
    e.content,
    1 - (e.embedding <=> query_embedding) AS score
  FROM public.keep_article_embeddings e
  WHERE
    (lang IS NULL OR e.language = lang)
    AND (allowed_types IS NULL OR e.section_type = ANY(allowed_types))
    AND (article_filter IS NULL OR e.article_id = ANY(article_filter))
    AND (1 - (e.embedding <=> query_embedding)) >= match_threshold
  ORDER BY e.embedding <=> query_embedding ASC
  LIMIT match_count;
END;
$function$;

-- 6. 更新updated_at列
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$function$;

-- 7. 更新updated_time列
CREATE OR REPLACE FUNCTION public.update_updated_time()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    NEW.updated_time := now();
    RETURN NEW;
END;
$function$;

