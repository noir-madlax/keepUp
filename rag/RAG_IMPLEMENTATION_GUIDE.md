# KeepUp RAG 功能实施指南

## 📋 整体方案概览

本方案为 KeepUp 项目添加基于向量数据库的 RAG（检索增强生成）搜索功能，让用户能够通过自然语言提问，从文章知识库中获取智能答案。

**核心特点：**
- ✅ **零后端修改**：纯前端 + Supabase Edge Function 实现
- ✅ **全自动向量化**：文章更新自动触发嵌入生成
- ✅ **高性能检索**：768 维 HNSW 索引，毫秒级响应
- ✅ **智能问答**：Gemini 2.5 Flash 生成中文回答

---

## 🏗️ 架构组件

### 1. 数据库层（已完成 ✅）

#### 1.1 向量表 `public.keep_article_embeddings`
```sql
-- 存储文章片段的向量嵌入
create table public.keep_article_embeddings (
  id bigserial primary key,
  article_id bigint references public.keep_articles(id) on delete cascade,
  section_id bigint references public.keep_article_sections(id) on delete cascade,
  language text,
  section_type text,
  chunk_id int,
  content text not null,
  embedding vector(768) not null,  -- 768 维向量（text-multilingual-embed-02）
  meta jsonb default '{}'::jsonb,
  created_at timestamptz default now(),
  unique(section_id, chunk_id)
);

-- HNSW 索引（余弦相似度）
create index idx_keep_article_embeddings_hnsw
on public.keep_article_embeddings
using hnsw (embedding vector_cosine_ops);
```

**RLS 策略：**
- 所有人可读（`SELECT`）
- 仅 `service_role` 可写（`INSERT/UPDATE/DELETE`）

#### 1.2 任务队列 `public.embedding_jobs`
```sql
-- 存储待处理的嵌入生成任务
create table public.embedding_jobs (
  id bigserial primary key,
  section_id bigint references public.keep_article_sections(id) on delete cascade,
  source_hash text not null,
  status text default 'pending',
  retry_count int default 0,
  error_message text,
  created_at timestamptz default now(),
  processed_at timestamptz,
  unique(section_id, source_hash)
);
```

#### 1.3 数据库触发器（已启用 ✅）
```sql
-- 当文章 section 更新时，自动入队嵌入任务
create trigger enqueue_section_for_embedding
after insert or update of content, language on public.keep_article_sections
for each row
when (new.section_type in ('Summary', '人物介绍', 'Key Takeaways', 'Segmented Outline', 'Trending', 'Companies & Products'))
execute function enqueue_embedding_job();
```

---

### 2. 向量化层（已完成 ✅）

#### 2.1 Edge Function: `process_embedding_jobs`
**功能：**
- 从 `embedding_jobs` 队列拉取待处理任务
- 清理文本、分块（最大 5000 字符）
- 超长块（>6000 字符）进行二次摘要
- 调用 Google Embedding API 生成 768 维向量
- 写入 `keep_article_embeddings` 表

**调度：**
- **pg_cron** 每 5 分钟自动执行一次
- 使用 `pg_net` 调用 Edge Function

#### 2.2 已配置的环境变量（Supabase Secrets）
- `GOOGLE_API_KEY`: Google AI Studio API 密钥
- `SUPABASE_URL`: 项目 URL
- `SUPABASE_SERVICE_ROLE_KEY`: 服务角色密钥

---

### 3. RAG 检索层（已完成 ✅）

#### 3.1 相似度搜索函数 `search_article_embeddings`
```sql
create or replace function search_article_embeddings(
  query_embedding vector(768),
  match_threshold float default 0.0,
  match_count int default 8
)
returns table (
  article_id bigint,
  section_id bigint,
  section_type text,
  language text,
  content text,
  score float  -- 相似度得分 (0-1)
)
```

**工作原理：**
1. 计算查询向量与所有嵌入的余弦相似度
2. 过滤相关 section 类型（Summary、Key Takeaways 等）
3. 按相似度排序，返回 Top-K 结果

---

### 4. RAG API 层（已完成 ✅）

#### 4.1 Edge Function: `rag_search`
**端点：** `https://ojbocxqvufoblihkzijn.supabase.co/functions/v1/rag_search`

**请求示例：**
```typescript
const response = await fetch(
  'https://ojbocxqvufoblihkzijn.supabase.co/functions/v1/rag_search',
  {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${SUPABASE_ANON_KEY}`
    },
    body: JSON.stringify({
      question: "Claude Skills 的核心价值是什么？",
      top_k: 8,           // 可选，默认 8
      score_threshold: 0.0 // 可选，默认 0.0
    })
  }
);

const data = await response.json();
```

**响应格式：**
```typescript
{
  "answer": "根据来源1，Claude Skills 的核心价值是...",
  "sources": [
    {
      "article_id": 123,
      "section_id": 456,
      "section_type": "Summary",
      "language": "zh",
      "content": "文章片段内容...",
      "score": 0.85
    }
  ],
  "query_embedding_time_ms": 250.5,
  "search_time_ms": 45.2,
  "generation_time_ms": 1823.7,
  "total_time_ms": 2119.4
}
```

---

## 🎯 前端集成方案

### 方案 A：Vue Composable（推荐）

创建 `src/composables/useRAG.ts`：

```typescript
import { ref } from 'vue';
import { supabase } from '@/supabaseClient';

export interface RAGSource {
  article_id: number;
  section_id: number;
  section_type: string;
  language: string;
  content: string;
  score: number;
}

export interface RAGResponse {
  answer: string;
  sources: RAGSource[];
  query_embedding_time_ms: number;
  search_time_ms: number;
  generation_time_ms: number;
  total_time_ms: number;
}

export function useRAG() {
  const loading = ref(false);
  const error = ref<string | null>(null);

  const ask = async (
    question: string,
    options?: { top_k?: number; score_threshold?: number }
  ): Promise<RAGResponse | null> => {
    loading.value = true;
    error.value = null;

    try {
      const { data, error: funcError } = await supabase.functions.invoke('rag_search', {
        body: {
          question,
          top_k: options?.top_k ?? 8,
          score_threshold: options?.score_threshold ?? 0.0
        }
      });

      if (funcError) throw funcError;
      return data as RAGResponse;
    } catch (e: any) {
      error.value = e.message || '搜索失败';
      console.error('RAG 错误:', e);
      return null;
    } finally {
      loading.value = false;
    }
  };

  return { ask, loading, error };
}
```

**使用示例（在任意 Vue 组件中）：**
```vue
<script setup lang="ts">
import { ref } from 'vue';
import { useRAG } from '@/composables/useRAG';

const { ask, loading, error } = useRAG();
const question = ref('');
const answer = ref('');
const sources = ref<any[]>([]);

const handleAsk = async () => {
  const result = await ask(question.value);
  if (result) {
    answer.value = result.answer;
    sources.value = result.sources;
  }
};
</script>

<template>
  <div class="rag-search">
    <input v-model="question" placeholder="输入你的问题..." />
    <button @click="handleAsk" :disabled="loading">
      {{ loading ? '搜索中...' : '提问' }}
    </button>

    <div v-if="error" class="error">{{ error }}</div>

    <div v-if="answer" class="answer">
      <h3>答案：</h3>
      <p>{{ answer }}</p>

      <h4>引用来源：</h4>
      <ul>
        <li v-for="(src, i) in sources" :key="i">
          <strong>{{ src.section_type }}</strong> (相似度: {{ src.score.toFixed(2) }})
          <p>{{ src.content.substring(0, 100) }}...</p>
        </li>
      </ul>
    </div>
  </div>
</template>
```

---

### 方案 B：直接调用（不使用 Composable）

```typescript
import { supabase } from '@/supabaseClient';

async function searchArticles(question: string) {
  const { data, error } = await supabase.functions.invoke('rag_search', {
    body: {
      question,
      top_k: 8,
      score_threshold: 0.0
    }
  });

  if (error) {
    console.error('搜索失败:', error);
    return null;
  }

  console.log('答案:', data.answer);
  console.log('来源:', data.sources);
  return data;
}
```

---

## ⚠️ 纯前端方案的限制与注意事项

### 1. CORS 配置
- ✅ **已处理**：Edge Function 已配置 CORS 头，允许跨域调用

### 2. API 密钥安全
- ⚠️ **重要**：前端只能使用 `SUPABASE_ANON_KEY`（已公开的匿名密钥）
- ✅ **安全设计**：
  - Google API Key 存储在 Supabase Secrets 中，前端无法访问
  - RLS 策略保护数据库，`anon` 角色只能读取嵌入，不能写入

### 3. 请求速率限制
- Supabase Edge Functions 免费版限制：
  - **500K 次请求/月**
  - **单次最大执行时间：150 秒**
- RAG 典型响应时间：1.5-4 秒，远低于限制

### 4. 向量数据同步
- ✅ **自动同步**：文章更新后 5 分钟内自动向量化
- ⚠️ **冷启动延迟**：新发布文章可能需要等待最多 5 分钟才能被搜索到
- 💡 **优化建议**：可将 cron 间隔缩短至 1-2 分钟（需评估成本）

### 5. 错误处理
- ✅ **已实现**：
  - 无结果时返回友好提示
  - API 失败时返回详细错误信息
  - 前端可捕获异常并显示提示

---

## 📝 环境变量配置清单

### Supabase Dashboard → Project Settings → Edge Functions → Secrets
| 变量名 | 说明 | 如何获取 |
|--------|------|---------|
| `GOOGLE_API_KEY` | Google AI Studio API 密钥 | https://aistudio.google.com/apikey |
| `SUPABASE_URL` | 项目 URL（自动注入） | Dashboard → Project Settings → API |
| `SUPABASE_SERVICE_ROLE_KEY` | 服务角色密钥（自动注入） | Dashboard → Project Settings → API |

### 前端环境变量（`.env` 或 Vercel）
```bash
# Supabase 配置（已有）
VITE_SUPABASE_URL=https://ojbocxqvufoblihkzijn.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGci...（已有的 anon key）

# RAG 功能不需要额外前端环境变量
```

---

## ✅ 实施检查清单

### 数据库层
- [x] `keep_article_embeddings` 表已创建
- [x] HNSW 索引已创建（vector_cosine_ops）
- [x] RLS 策略已启用
- [x] `embedding_jobs` 队列表已创建
- [x] 触发器已部署（自动入队新 sections）
- [x] `search_article_embeddings` 函数已创建

### 向量化层
- [x] `process_embedding_jobs` Edge Function 已部署
- [x] pg_cron 定时任务已配置（每 5 分钟）
- [x] pg_net 扩展已启用
- [x] Vault 密钥已存储（project_url, anon_key, function_url）

### RAG API 层
- [x] `rag_search` Edge Function 已部署
- [x] CORS 配置已添加
- [x] 相似度搜索逻辑已实现
- [x] Gemini 2.5 Flash 集成已完成

### 前端集成（待完成）
- [ ] 创建 `src/composables/useRAG.ts`
- [ ] 在目标页面/组件中集成 RAG 搜索 UI
- [ ] 添加加载状态、错误提示
- [ ] 设计引用来源展示方式
- [ ] 端到端测试

---

## 🧪 测试步骤

### 1. 测试向量化（手动触发）
```sql
-- 插入/更新一条测试 section
insert into public.keep_article_sections (article_id, section_type, content, language)
values (
  1,  -- 替换为真实的 article_id
  'Summary',
  '这是一篇测试文章，讲述了 AI 技术的最新进展，包括大语言模型和向量数据库的应用。',
  'zh'
);

-- 检查是否入队
select * from public.embedding_jobs order by created_at desc limit 5;

-- 等待 5 分钟后检查嵌入是否生成
select 
  article_id,
  section_id,
  section_type,
  chunk_id,
  substring(content, 1, 50) as content_preview,
  created_at
from public.keep_article_embeddings
order by created_at desc
limit 5;
```

### 2. 测试 RAG 搜索（前端代码）
```typescript
// 在浏览器控制台执行
const { data } = await supabase.functions.invoke('rag_search', {
  body: {
    question: "AI 技术有哪些最新进展？",
    top_k: 5
  }
});
console.log(data);
```

### 3. 测试相似度计算
```sql
-- 直接调用搜索函数（需要一个真实的 embedding 向量）
select 
  article_id,
  section_type,
  score,
  substring(content, 1, 100) as preview
from search_article_embeddings(
  (select embedding from keep_article_embeddings limit 1),  -- 使用已有向量测试
  0.0,
  5
);
```

---

## 🚀 上线后监控

### 1. 监控 Edge Function 调用
- Dashboard → Edge Functions → `rag_search` → Invocations 查看请求量和错误率

### 2. 监控向量化任务
```sql
-- 查看待处理任务数
select status, count(*) from embedding_jobs group by status;

-- 查看失败任务
select 
  id,
  section_id,
  status,
  retry_count,
  error_message,
  created_at
from embedding_jobs
where status = 'failed'
order by created_at desc;
```

### 3. 监控数据库存储
```sql
-- 查看嵌入总数和存储使用
select 
  count(*) as total_embeddings,
  count(distinct article_id) as unique_articles,
  pg_size_pretty(pg_total_relation_size('keep_article_embeddings')) as table_size
from keep_article_embeddings;
```

---

## 💰 成本估算（免费额度内）

### Supabase 免费计划
- ✅ 数据库存储：500 MB（向量数据预计占用 < 100 MB）
- ✅ Edge Functions：500K 请求/月
- ✅ Realtime/Auth：无限制

### Google AI Studio（免费试用）
- ✅ Gemini Flash：15 RPM（每分钟请求数）
- ✅ Embeddings：1500 RPM
- 💡 **预估**：每月 10K 次 RAG 查询 ≈ $0（在免费额度内）

### Vercel 部署（免费）
- ✅ 前端托管：无额外费用
- ✅ 带宽：100 GB/月

**结论：整个方案可在免费额度内运行，适合初期验证。**

---

## 🔧 故障排查

### 问题 1：向量化不工作
**症状：** `embedding_jobs` 有 pending 任务但长时间不处理

**排查步骤：**
```sql
-- 1. 检查 cron 任务是否激活
select jobname, active from cron.job where jobname like '%embedding%';

-- 2. 检查 Edge Function URL 是否正确
select decrypted_secret from vault.decrypted_secrets where name = 'embedding_function_url';

-- 3. 查看最近的 HTTP 请求日志
select * from net._http_response order by created desc limit 5;
```

### 问题 2：RAG 搜索返回空结果
**症状：** 提问后没有找到相关内容

**可能原因：**
1. 数据库中还没有嵌入数据
2. 相似度阈值设置过高
3. 问题与知识库内容不相关

**解决方法：**
```sql
-- 检查嵌入数据量
select count(*) from keep_article_embeddings;

-- 降低相似度阈值重试
```

### 问题 3：API 调用失败
**症状：** 前端收到 500 错误

**排查：**
1. 查看 Dashboard → Edge Functions → `rag_search` → Logs
2. 检查 Google API Key 是否有效
3. 确认 Supabase Secrets 是否正确配置

---

## 📚 相关资源

- [Supabase Vector Docs](https://supabase.com/docs/guides/ai/vector-columns)
- [Google Generative AI Embeddings](https://ai.google.dev/gemini-api/docs/embeddings)
- [pg_cron Documentation](https://supabase.com/docs/guides/database/extensions/pgcron)
- [Edge Functions Guide](https://supabase.com/docs/guides/functions)

---

## 🎉 总结

KeepUp 的 RAG 功能现已**完全就绪**，整个架构：

✅ **数据库** → 向量表 + 索引 + RLS + 触发器  
✅ **向量化** → 自动入队 + Edge Function 处理 + 定时调度  
✅ **检索** → 相似度搜索函数 + HNSW 加速  
✅ **API** → RAG Edge Function（嵌入 + 检索 + 生成）  
⏳ **前端** → 待集成 Vue Composable

**下一步：你只需在前端添加调用逻辑即可！**

