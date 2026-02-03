# KeepUp RAG 原文向量化实施文档

> 最后更新：2026-02-03  
> 版本：v3.0 - 并行检索版（修复分层检索问题）

---

## 📋 目录

- [系统概述](#系统概述)
- [数据库架构](#数据库架构)
- [Edge Functions](#edge-functions)
- [并行检索逻辑](#并行检索逻辑)
- [Supabase配置](#supabase配置)
- [当前数据状态](#当前数据状态)
- [免费额度管理](#免费额度管理)
- [维护指南](#维护指南)
- [故障排查](#故障排查)
- [问题修复记录](#问题修复记录)

---

## 🔧 问题修复记录（2026-02-03）

### 发现的问题与修复状态

| 问题 | 状态 | 根因 | 修复方案 |
|------|------|------|----------|
| 第一层 section_type 不匹配 | ✅ 已修复 | 函数用 'Summary' 但数据存 '总结' | 改用并行搜索，直接匹配中文类型 |
| 分层设计缺陷 | ✅ 已修复 | 总结没命中就搜不到原文 | 改为并行搜索总结+原文（方案B） |
| 私有文章被搜索到 | ✅ 已修复 | 搜索函数没过滤 is_private | 新函数 v3 支持 excluded_article_ids |
| 向量化任务失败不重试 | ✅ 已重置 | 重试3次后标记error | 16个任务已重置为 pending |
| 首页加载慢 | ✅ 已优化 | 缺少数据库索引 | 添加5个索引 |

### 数据状态快照（修复前）

```
总文章数: 343
有向量化的文章数: 334 (97.4%)
原文字幕向量: 925 条
总结向量: 746 条
私有文章: 18 篇
私有文章的 embeddings: 50 条

向量化任务状态:
  - done: 674
  - error: 16 (15个429配额限制 + 1个404模型错误)

失败的文章 ID: 2110, 2111, 2112, 2113, 2114, 2115, 2116, 2132, 2271
```

### 修复执行记录（2026-02-03 完成）

#### 1. RAG 检索改为并行模式（方案B）✅
- [x] 修改 `rag_search` Edge Function，改为并行搜索
- [x] 同时搜索"总结"和"原文字幕"类型
- [x] 合并结果，按相似度排序去重
- [x] 部署 Edge Function 成功

#### 2. 私有文章排除 ✅
- [x] 创建新函数 `search_article_embeddings_v3`
- [x] 支持 `excluded_article_ids` 参数
- [x] Edge Function 先查询私有文章ID，再排除

#### 3. 重置失败任务 ✅
- [x] 16个 error 状态任务已重置为 pending
- [x] retry_count 重置为 0
- [x] 等待 pg_cron 每5分钟自动处理

#### 4. 首页加载优化 ✅
新增索引：
- [x] `idx_keep_articles_is_visible`
- [x] `idx_keep_articles_is_private`
- [x] `idx_keep_articles_created_at`
- [x] `idx_keep_articles_user_id`
- [x] `idx_keep_articles_homepage_query` (复合索引)

---

## 系统概述

### 架构设计

```
┌─────────────────┐
│  前端 (Vue 3)   │
│  useRAG.ts      │
└────────┬────────┘
         │ HTTP POST
         ↓
┌─────────────────────────────────────────┐
│  Supabase Edge Function: rag_search     │
│  - 分层检索（总结→原文）                 │
│  - Google text-embedding-004 (768维)    │
│  - Gemini 2.5 Flash 生成                │
└────────┬────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────────┐
│  PostgreSQL + pgvector                  │
│  - keep_article_embeddings (向量表)     │
│  - HNSW索引 (vector_cosine_ops)         │
│  - RLS策略 (anon只读)                   │
└─────────────────────────────────────────┘
         ↑
         │ pg_cron (每5分钟)
┌────────┴────────────────────────────────┐
│  Edge Function: process_embedding_jobs  │
│  - 自动处理pending任务                  │
│  - 文本清理、分块、向量化               │
│  - 触发器自动入队                       │
└─────────────────────────────────────────┘
```

### 核心特性

1. **并行检索（v3.0 新架构）**
   - 同时搜索"总结"和"原文字幕"类型的 embeddings
   - 合并结果，按相似度排序
   - 自动排除私有文章（is_private = true）
   - 避免了分层检索的"总结没命中就遗漏原文"问题

2. **自动向量化**
   - 触发器：`keep_article_sections`表INSERT/UPDATE时自动入队
   - 定时处理：pg_cron每5分钟调用Edge Function处理20个任务
   - 支持类型：原文（transcript、原文字幕）+ 总结类型

3. **多语言支持**
   - 向量模型：text-embedding-004（支持中英文，768维）
   - 生成模型：Gemini 2.5 Flash（中文输出）
   - 原文为英文时自动翻译为中文回答

---

## 数据库架构

### 表结构

#### 1. `keep_article_embeddings` - 向量存储表

```sql
CREATE TABLE public.keep_article_embeddings (
  id bigserial PRIMARY KEY,
  article_id bigint REFERENCES public.keep_articles(id) ON DELETE CASCADE,
  section_id bigint REFERENCES public.keep_article_sections(id) ON DELETE CASCADE,
  language text,                    -- 语言：'zh', 'en', etc.
  section_type text,                -- 类型：'transcript', '原文字幕', '总结', etc.
  chunk_id integer NOT NULL,        -- 分块ID（同一section的第N块）
  content text NOT NULL,            -- 实际文本内容（600-900字符）
  embedding vector(768) NOT NULL,   -- 768维向量
  meta jsonb DEFAULT '{}'::jsonb,   -- 元数据（如needSummary标志）
  created_at timestamptz DEFAULT now(),
  UNIQUE(section_id, chunk_id)
);

-- HNSW索引（余弦相似度）
CREATE INDEX idx_keep_article_embeddings_hnsw 
ON public.keep_article_embeddings 
USING hnsw (embedding vector_cosine_ops);

-- 性能索引（2025-10-30新增）
CREATE INDEX idx_embeddings_article_id ON keep_article_embeddings(article_id);
CREATE INDEX idx_embeddings_section_type ON keep_article_embeddings(section_type);
CREATE INDEX idx_embeddings_language ON keep_article_embeddings(language);
CREATE INDEX idx_embeddings_article_type ON keep_article_embeddings(article_id, section_type);
```

**RLS策略：**
```sql
-- 所有人可读
CREATE POLICY "Enable read access for all users" 
ON keep_article_embeddings FOR SELECT 
USING (true);

-- 仅service_role可写
CREATE POLICY "Enable insert for service_role only" 
ON keep_article_embeddings FOR INSERT 
WITH CHECK (auth.role() = 'service_role');
```

#### 2. `embedding_jobs` - 任务队列表

```sql
CREATE TABLE public.embedding_jobs (
  id bigserial PRIMARY KEY,
  section_id bigint REFERENCES keep_article_sections(id) ON DELETE CASCADE,
  source_hash text NOT NULL,        -- MD5哈希（防止重复）
  status text DEFAULT 'pending',    -- pending, processing, done, error
  retry_count int DEFAULT 0,
  last_error text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  UNIQUE(section_id, source_hash)
);
```

### 触发器函数

#### `enqueue_embedding_job()` - 自动入队

```sql
CREATE OR REPLACE FUNCTION public.enqueue_embedding_job()
RETURNS trigger
LANGUAGE plpgsql
AS $function$
DECLARE
  st text;
  new_hash text;
BEGIN
  st := coalesce(NEW.section_type, '');

  -- 支持的section类型（原文 + 总结）
  IF st NOT IN (
    -- 原文类型
    'transcript','raw','paragraph','section','sentence','原文字幕',
    -- 总结类型
    'Summary','Key Takeaways','Segmented Outline','Trending','Companies & Products',
    '总结','要点总结','分段大纲','趋势','公司与产品','人物介绍','核心观点',
    '名词解释','QA环节','金句','未总结内容','彩蛋','典型案例','背景',
    '结构图','思维导图','分段详述','额外补充'
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

-- 绑定触发器
CREATE TRIGGER trg_enqueue_embedding_job
AFTER INSERT OR UPDATE OF content, language 
ON public.keep_article_sections
FOR EACH ROW
EXECUTE FUNCTION enqueue_embedding_job();
```

### 检索函数

#### `search_article_embeddings_v2()` - 分层检索函数

```sql
CREATE OR REPLACE FUNCTION public.search_article_embeddings_v2(
  query_embedding vector(768),
  match_threshold double precision DEFAULT 0.2,
  match_count integer DEFAULT 32,
  lang text DEFAULT NULL,
  allowed_types text[] DEFAULT ARRAY['transcript', 'raw', 'paragraph', 'section', 'sentence'],
  article_filter bigint[] DEFAULT NULL,  -- 关键：用于第二层筛选
  ef_search_param integer DEFAULT 80
)
RETURNS TABLE(
  article_id bigint,
  section_id bigint,
  section_type text,
  language text,
  chunk_id integer,
  content text,
  score double precision
)
LANGUAGE plpgsql STABLE
AS $function$
BEGIN
  -- 设置HNSW搜索宽度
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
    AND (article_filter IS NULL OR e.article_id = ANY(article_filter))  -- 关键过滤
    AND (1 - (e.embedding <=> query_embedding)) >= match_threshold
  ORDER BY e.embedding <=> query_embedding ASC
  LIMIT match_count;
END;
$function$;
```

#### `search_article_embeddings()` - 总结检索函数

```sql
CREATE OR REPLACE FUNCTION public.search_article_embeddings(
  query_embedding vector(768),
  match_threshold double precision DEFAULT 0.0,
  match_count integer DEFAULT 8
)
RETURNS TABLE(
  article_id bigint,
  section_id bigint,
  section_type text,
  language text,
  content text,
  score double precision
)
LANGUAGE sql STABLE
AS $function$
  SELECT
    e.article_id,
    e.section_id,
    e.section_type,
    e.language,
    e.content,
    1 - (e.embedding <=> query_embedding) as score
  FROM public.keep_article_embeddings e
  WHERE
    e.section_type IN (
      'Summary','人物介绍','Key Takeaways','Segmented Outline',
      'Trending','Companies & Products'
    )
    AND (1 - (e.embedding <=> query_embedding)) >= match_threshold
  ORDER BY e.embedding <=> query_embedding ASC
  LIMIT match_count;
$function$;
```

---

## Edge Functions

### 1. `rag_search` - RAG问答接口

**路径：** Supabase Dashboard → Edge Functions → `rag_search`  
**当前版本：** v11  
**模型：** text-embedding-004 (查询), Gemini 2.5 Flash (生成)

#### 请求格式

```typescript
POST https://ojbocxqvufoblihkzijn.supabase.co/functions/v1/rag_search
Headers:
  Content-Type: application/json
  Authorization: Bearer <SUPABASE_ANON_KEY>

Body:
{
  "question": "How does cursor work?",
  "top_k": 10,              // 可选，默认10
  "score_threshold": 0.15,  // 可选，默认0.15
  "use_layered": true       // 可选，默认true（分层检索）
}
```

#### 响应格式

```typescript
{
  "answer": "根据来源1...",
  "sources": [
    {
      "article_id": 1977,
      "section_id": 7122,
      "section_type": "transcript",
      "language": "en",
      "chunk_id": 0,
      "content": "...",
      "score": 0.678
    }
  ],
  "query_embedding_time_ms": 318,
  "search_time_ms": 700,
  "generation_time_ms": 13686,
  "total_time_ms": 14704,
  "search_mode": "layered"
}
```

#### 核心逻辑（分层检索）

```typescript
// 第一层：总结层快速筛选
const { data: summaryResults } = await supabase.rpc('search_article_embeddings', {
  query_embedding: `[${queryEmbedding.join(',')}]`,
  match_threshold: 0.1,
  match_count: 8
});

// 提取相关文章ID
const relevantArticleIds = [...new Set(summaryResults.map(r => r.article_id))];

// 第二层：原文层精确检索
const { data: transcriptResults } = await supabase.rpc('search_article_embeddings_v2', {
  query_embedding: `[${queryEmbedding.join(',')}]`,
  match_threshold: score_threshold,
  match_count: top_k,
  allowed_types: ['transcript', '原文字幕', 'raw', 'paragraph', 'section'],
  article_filter: relevantArticleIds,  // 限定在第一层筛选的文章中
  ef_search_param: 100
});

// 回退逻辑
if (transcriptResults.length === 0 && summaryResults.length > 0) {
  sources = summaryResults.slice(0, top_k);
} else {
  sources = transcriptResults;
}
```

### 2. `process_embedding_jobs` - 向量化处理

**路径：** Supabase Dashboard → Edge Functions → `process_embedding_jobs`  
**当前版本：** v9  
**模型：** text-embedding-004 (768维)  
**调度：** pg_cron每5分钟自动调用

#### 处理流程

```typescript
1. 从embedding_jobs拉取20个pending任务
2. 标记为processing
3. 对每个任务：
   - 读取section内容
   - cleanText()：清理代码块、多余换行
   - 如果>900字符：调用Gemini 2.5 Flash生成摘要（450-600字）
   - chunkText()：分块（600-900字符）
   - 调用Google Embedding API生成向量
   - 写入keep_article_embeddings表
4. 更新任务状态为done
```

#### 环境变量

在Supabase Dashboard → Project Settings → Edge Functions → Secrets配置：

```env
EMBEDDING_MODEL=text-embedding-004
GEN_MODEL_SUMMARY=gemini-2.5-flash
CHUNK_CHAR_TARGET=600
CHUNK_CHAR_MAX=900
GOOGLE_API_KEY=<your_google_api_key>
SUPABASE_URL=<auto_injected>
SUPABASE_SERVICE_ROLE_KEY=<auto_injected>
```

---

## 分层检索逻辑

### 为什么需要分层检索？

1. **效率**：总结内容少（57个embeddings），检索快
2. **准确性**：第一层快速定位相关文章，第二层在有限范围内精确匹配
3. **质量**：最终返回原文内容，信息完整度高

### 检索流程图

```
用户问题："How does cursor editor work?"
    ↓
【步骤1】查询向量化
    - Google text-embedding-004
    - 生成768维向量
    - 耗时：~300ms
    ↓
【步骤2】第一层 - 总结层筛选
    - 在57个总结embeddings中搜索
    - 使用search_article_embeddings()
    - 返回Top 8篇相关文章
    - 提取article_ids: [1977, 1954, ...]
    - 耗时：~50ms
    ↓
【步骤3】第二层 - 原文层检索
    - 在134个原文embeddings中搜索
    - 限定article_filter=[1977, 1954, ...]
    - 使用search_article_embeddings_v2()
    - 返回Top 10个最相关原文片段
    - 耗时：~650ms
    ↓
【步骤4】AI生成回答
    - 将10个原文片段+问题拼接为prompt
    - 调用Gemini 2.5 Flash
    - 要求：用中文回答，基于原文
    - 耗时：~13秒
    ↓
返回结果
```

### 参数调优建议

| 参数 | 默认值 | 说明 | 调优建议 |
|-----|--------|------|---------|
| `top_k` | 10 | 第二层返回的原文片段数 | 10-20个，太少信息不足，太多影响生成质量 |
| `score_threshold` | 0.15 | 第二层相似度阈值 | 0.1-0.3，太低噪音多，太高结果少 |
| `match_count`(第一层) | 8 | 第一层返回的文章数 | 5-10篇，太少遗漏相关文章，太多范围太广 |
| `ef_search_param` | 100 | HNSW搜索宽度 | 50-200，越大越准确但越慢 |

---

## Supabase配置

### pg_cron定时任务

```sql
-- 查看定时任务
SELECT jobid, schedule, command, active, jobname 
FROM cron.job 
WHERE jobname LIKE '%embedding%';

-- 输出：
jobid: 1
schedule: */5 * * * *  (每5分钟)
command: 
  SELECT net.http_post(
    url := (SELECT decrypted_secret FROM vault.decrypted_secrets WHERE name = 'embedding_function_url'),
    headers := jsonb_build_object(
      'Content-Type', 'application/json',
      'Authorization', 'Bearer ' || (SELECT decrypted_secret FROM vault.decrypted_secrets WHERE name = 'supabase_anon_key')
    ),
    body := jsonb_build_object('trigger', 'cron', 'time', now())
  );
active: true
jobname: process-embedding-jobs-every-5-min
```

### Vault密钥配置

在Supabase Dashboard配置以下密钥：

```sql
-- 查看vault密钥
SELECT name FROM vault.decrypted_secrets;

-- 需要的密钥：
-- 1. embedding_function_url: Edge Function的完整URL
-- 2. supabase_anon_key: 项目的anon key
```

配置方法：
```sql
-- 1. 在Dashboard → Project Settings → API获取：
--    - Project URL: https://ojbocxqvufoblihkzijn.supabase.co
--    - anon key: eyJhbGci...

-- 2. 在SQL Editor执行：
INSERT INTO vault.secrets (name, secret)
VALUES 
  ('embedding_function_url', 'https://ojbocxqvufoblihkzijn.supabase.co/functions/v1/process_embedding_jobs'),
  ('supabase_anon_key', '<your_anon_key>')
ON CONFLICT (name) DO UPDATE SET secret = EXCLUDED.secret;
```

---

## 当前数据状态

### 向量化覆盖情况

**截至 2025-10-30：**

| 指标 | 数值 | 说明 |
|------|------|------|
| 总文章数 | 1,610 | keep_articles表总记录数 |
| 有向量的文章数 | 32 | 至少有一个embedding的文章 |
| 有原文向量的文章数 | 11 | 有transcript或原文字幕embedding |
| 只有总结向量的文章数 | 21 | ⚠️ 只能检索总结，无法检索原文 |

### Embeddings分布

```
类型：transcript (英文原文)
  - 数量：111个
  - 覆盖文章：1篇（完全向量化）
  - 平均长度：798字符/chunk
  - 状态：✅ 完成

类型：原文字幕 (中文)
  - 数量：17个（已向量化）
  - 总sections：34个
  - 未向量化：17个 ⏳
  - 覆盖文章：6篇

类型：原文字幕 (英文)
  - 数量：6个（已向量化）
  - 总sections：18个
  - 未向量化：12个 ⏳
  - 覆盖文章：3篇

类型：总结 (中文)
  - 数量：57个
  - 覆盖文章：22篇
  - 平均长度：575字符
  - 状态：✅ 持续更新
```

### 任务队列状态

```
pending: 36个     ⏳ 等待处理
processing: 4个   🔄 正在处理
done: 142个       ✅ 已完成
error: 0个        ❌ 失败任务
```

**预计完成时间：** 约30-40分钟（36个pending任务，每5分钟处理20个）

### ⚠️ 当前问题

**21篇文章只有总结向量，缺少原文向量**

**影响：**
- 这21篇文章的RAG查询会回退使用总结内容
- 回答可能较抽象，缺少原文细节

**原因：**
- 这些文章的`keep_article_sections`表中没有原文类型的section
- 或原文section的content为空/NULL

**解决方案：**
1. 检查这些文章的`keep_article_requests`表，确认content字段是否有原文
2. 如果有，需要将content解析为sections并插入`keep_article_sections`
3. 触发器会自动为新插入的sections创建向量化任务

---

## 免费额度管理

### Supabase免费计划

| 资源 | 限制 | 当前使用 | 使用率 |
|------|------|---------|--------|
| 数据库存储 | 500 MB | 223 MB | 45% |
| Edge Functions调用 | 500K次/月 | <1K | <1% |
| Egress流量 | 5 GB/月 | 未知 | 需监控 |
| Realtime连接 | 200 | 0 | 0% |

### Google Generative AI免费层

| API | 速率限制 | 用量限制 | 说明 |
|-----|---------|---------|------|
| text-embedding-004 | 1,500 RPM | 无月度限制 | ✅ 完全够用 |
| Gemini 2.5 Flash | 15 RPM | 无月度限制 | ⚠️ 高峰时可能排队 |

**RPM (Requests Per Minute)：每分钟请求数**

**成本估算（假设月活跃）：**
- 向量化：1,000个新sections × 0次收费 = $0
- RAG查询：5,000次查询 × 0次收费 = $0
- **总计：$0（完全在免费额度内）**

**何时需要升级？**
- Supabase Pro ($25/月)：
  - 数据库>500MB
  - Edge Functions调用>500K/月
- Google付费：
  - 需要>15 RPM的生成速率
  - 企业级SLA保障

---

## 维护指南

### 日常监控

#### 1. 检查向量化进度

```sql
-- 查看任务队列状态
SELECT 
  status,
  COUNT(*) as count,
  MIN(created_at) as earliest,
  MAX(updated_at) as latest
FROM embedding_jobs
GROUP BY status;

-- 查看失败任务
SELECT 
  ej.id,
  ej.section_id,
  s.section_type,
  s.article_id,
  ej.retry_count,
  ej.last_error,
  ej.created_at
FROM embedding_jobs ej
JOIN keep_article_sections s ON ej.section_id = s.id
WHERE ej.status = 'error'
ORDER BY ej.updated_at DESC
LIMIT 10;
```

#### 2. 检查embeddings覆盖率

```sql
-- 哪些文章缺少原文向量？
SELECT 
  a.id as article_id,
  a.title,
  a.created_at,
  EXISTS(SELECT 1 FROM keep_article_embeddings e 
         WHERE e.article_id = a.id 
         AND e.section_type IN ('transcript', '原文字幕')) as has_transcript,
  EXISTS(SELECT 1 FROM keep_article_embeddings e 
         WHERE e.article_id = a.id 
         AND e.section_type IN ('总结', 'Summary')) as has_summary
FROM keep_articles a
WHERE a.id IN (
  SELECT DISTINCT article_id FROM keep_article_embeddings
)
ORDER BY a.created_at DESC
LIMIT 50;
```

#### 3. 监控数据库大小

```sql
-- 各表大小
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename LIKE '%article%'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Embeddings表详情
SELECT 
  pg_size_pretty(pg_total_relation_size('keep_article_embeddings')) as total_size,
  pg_size_pretty(pg_relation_size('keep_article_embeddings')) as table_size,
  pg_size_pretty(pg_indexes_size('keep_article_embeddings')) as indexes_size,
  COUNT(*) as row_count
FROM keep_article_embeddings;
```

### 手动触发向量化

#### 为特定section创建任务

```sql
-- 单个section
INSERT INTO embedding_jobs (section_id, source_hash, status, updated_at)
SELECT 
  id,
  encode(digest(content, 'md5'), 'hex'),
  'pending',
  now()
FROM keep_article_sections
WHERE id = <section_id>
ON CONFLICT DO NOTHING;

-- 批量补充缺失的原文
INSERT INTO embedding_jobs (section_id, source_hash, status, updated_at)
SELECT 
  s.id,
  encode(digest(s.content, 'md5'), 'hex'),
  'pending',
  now()
FROM keep_article_sections s
WHERE s.section_type IN ('原文字幕', 'transcript')
  AND NOT EXISTS (
    SELECT 1 FROM keep_article_embeddings e WHERE e.section_id = s.id
  )
ON CONFLICT DO NOTHING;
```

#### 手动调用Edge Function

```bash
# 使用curl（需要service_role_key）
curl -X POST \
  "https://ojbocxqvufoblihkzijn.supabase.co/functions/v1/process_embedding_jobs" \
  -H "Authorization: Bearer <SERVICE_ROLE_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"trigger": "manual"}'

# 或在SQL Editor中
SELECT net.http_post(
  url := 'https://ojbocxqvufoblihkzijn.supabase.co/functions/v1/process_embedding_jobs',
  headers := jsonb_build_object(
    'Authorization', 'Bearer <SERVICE_ROLE_KEY>',
    'Content-Type', 'application/json'
  ),
  body := jsonb_build_object('trigger', 'manual')
);
```

### 重新向量化（内容更新时）

```sql
-- 1. 删除旧的embeddings
DELETE FROM keep_article_embeddings
WHERE section_id = <section_id>;

-- 2. 删除旧的jobs（如果有）
DELETE FROM embedding_jobs
WHERE section_id = <section_id>;

-- 3. 更新section触发自动入队
UPDATE keep_article_sections
SET updated_at = now()
WHERE id = <section_id>;
```

### 清理无效数据

```sql
-- 清理孤儿embeddings（section已删除）
DELETE FROM keep_article_embeddings
WHERE section_id NOT IN (SELECT id FROM keep_article_sections);

-- 清理孤儿jobs
DELETE FROM embedding_jobs
WHERE section_id NOT IN (SELECT id FROM keep_article_sections);

-- 清理stuck的processing任务（超过1小时）
UPDATE embedding_jobs
SET status = 'pending', updated_at = now()
WHERE status = 'processing'
  AND updated_at < now() - interval '1 hour';
```

---

## 故障排查

### 问题1：向量化任务不处理

**症状：** pending任务长时间不减少

**排查步骤：**
```sql
-- 1. 检查pg_cron是否运行
SELECT * FROM cron.job WHERE jobname LIKE '%embedding%';

-- 2. 检查cron执行历史
SELECT * FROM cron.job_run_details 
WHERE jobid = 1 
ORDER BY start_time DESC 
LIMIT 10;

-- 3. 检查Edge Function日志
-- 在Dashboard → Edge Functions → process_embedding_jobs → Logs

-- 4. 检查vault密钥
SELECT name FROM vault.decrypted_secrets;
```

**解决方案：**
- 如果cron.job的active=false：`UPDATE cron.job SET active = true WHERE jobid = 1;`
- 如果vault密钥缺失：重新配置密钥（见"Supabase配置"章节）
- 如果Edge Function报错：检查GOOGLE_API_KEY是否有效

### 问题2：RAG搜索返回空结果

**症状：** 前端调用rag_search，返回"没有找到相关内容"

**排查步骤：**
```sql
-- 1. 检查embeddings数量
SELECT section_type, COUNT(*) 
FROM keep_article_embeddings 
GROUP BY section_type;

-- 2. 测试向量搜索
WITH test_vec AS (
  SELECT embedding FROM keep_article_embeddings LIMIT 1
)
SELECT COUNT(*) 
FROM keep_article_embeddings e, test_vec t
WHERE 1 - (e.embedding <=> t.embedding) > 0.1;

-- 3. 检查RLS策略
SELECT * FROM pg_policies WHERE tablename = 'keep_article_embeddings';
```

**解决方案：**
- 如果embeddings为空：检查向量化任务
- 如果搜索函数报错：检查函数定义（可能向量维度不匹配）
- 如果RLS阻止：确认anon角色有SELECT权限

### 问题3：生成的回答质量差

**症状：** 回答不相关、太简略或包含错误信息

**可能原因及解决：**

1. **检索到的内容不相关**
   ```typescript
   // 调整相似度阈值
   {
     "score_threshold": 0.25,  // 提高阈值，过滤低质量结果
     "top_k": 5               // 减少数量，只用最相关的
   }
   ```

2. **只检索到总结内容**
   ```sql
   -- 检查该文章是否有原文embeddings
   SELECT section_type, COUNT(*) 
   FROM keep_article_embeddings 
   WHERE article_id = <article_id>
   GROUP BY section_type;
   ```
   
3. **Prompt需要优化**
   - 修改`rag_search` Edge Function中的prompt模板
   - 添加更具体的指令或示例

### 问题4：Google API配额用尽

**症状：** Edge Function返回429错误或quota exceeded

**临时解决：**
```typescript
// 在Edge Function中添加重试逻辑
async function embedWithRetry(text, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await embed(text);
    } catch (error) {
      if (error.message.includes('429') && i < maxRetries - 1) {
        await new Promise(resolve => setTimeout(resolve, (i + 1) * 1000));
        continue;
      }
      throw error;
    }
  }
}
```

**长期解决：**
- 升级到Google付费计划
- 或减少向量化频率（调整pg_cron为每10分钟）

---

## 附录

### A. 前端集成示例

```typescript
// src/composables/useRAG.ts
import { ref } from 'vue';
import { supabase } from '@/supabaseClient';

export function useRAG() {
  const loading = ref(false);
  const error = ref<string | null>(null);

  const ask = async (question: string, options?: {
    top_k?: number;
    score_threshold?: number;
  }) => {
    loading.value = true;
    error.value = null;

    try {
      const { data, error: funcError } = await supabase.functions.invoke('rag_search', {
        body: {
          question: question.trim(),
          top_k: options?.top_k ?? 10,
          score_threshold: options?.score_threshold ?? 0.15,
          use_layered: true
        }
      });

      if (funcError) throw funcError;
      return data;
    } catch (e: any) {
      error.value = e.message || '搜索失败';
      return null;
    } finally {
      loading.value = false;
    }
  };

  return { ask, loading, error };
}
```

### B. 常用SQL查询

```sql
-- 查看最近向量化的内容
SELECT 
  e.id,
  e.article_id,
  a.title,
  e.section_type,
  e.language,
  LEFT(e.content, 100) as content_preview,
  e.created_at
FROM keep_article_embeddings e
JOIN keep_articles a ON e.article_id = a.id
ORDER BY e.created_at DESC
LIMIT 20;

-- 统计各文章的embedding数量
SELECT 
  a.id,
  a.title,
  COUNT(e.id) as embedding_count,
  STRING_AGG(DISTINCT e.section_type, ', ') as types
FROM keep_articles a
LEFT JOIN keep_article_embeddings e ON a.id = e.article_id
WHERE a.id IN (SELECT DISTINCT article_id FROM keep_article_embeddings)
GROUP BY a.id, a.title
ORDER BY embedding_count DESC;

-- 查看pending任务最多的section类型
SELECT 
  s.section_type,
  COUNT(*) as pending_count
FROM embedding_jobs ej
JOIN keep_article_sections s ON ej.section_id = s.id
WHERE ej.status = 'pending'
GROUP BY s.section_type
ORDER BY pending_count DESC;
```

### C. 数据库迁移记录

```
2025-10-29 04:34:57 - create_embeddings_and_jobs_v4
2025-10-29 07:02:24 - enable_pg_cron_pg_net
2025-10-29 07:03:06 - setup_cron_for_embeddings_v2
2025-10-29 07:04:23 - create_search_function_for_rag
2025-10-30 03:23:27 - expand_embedding_for_raw_content
2025-10-30 04:05:XX - add_embeddings_performance_indexes
```

---

## 更新日志

### v2.0 (2025-10-30)
- ✅ 实现分层检索（总结→原文）
- ✅ 更新为text-embedding-004模型
- ✅ 添加4个性能索引
- ✅ 支持原文字幕向量化
- ✅ 修复触发器支持原文类型
- ✅ 补充43个缺失的向量化任务

### v1.0 (2025-10-29)
- ✅ 基础RAG功能实现
- ✅ 仅支持总结内容检索
- ✅ 使用text-multilingual-embed-02

---

**文档版本：** 2.0  
**最后更新：** 2025-10-30  
**维护者：** KeepUp Team

