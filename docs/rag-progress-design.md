# RAG 搜索进度展示 - 设计方案

## 一、现状分析

### 当前流程

```
用户提问 → 调用 rag_search Edge Function → 等待全部完成 → 一次性返回结果
```

### 耗时分布（后端已返回的计时数据）

| 阶段 | 操作 | 预估耗时 |
|------|------|---------|
| 阶段1 | 生成问题向量 Embedding | ~0.5-1.5s |
| 阶段2 | 双路并行向量搜索 | ~1-3s |
| 阶段3 | Gemini 2.5 Pro 生成回答 | ~5-15s |
| **总计** | | **~7-20s** |

### 当前问题

- 用户只看到三个跳动圆点，不知道后台在做什么
- 等待时间长（可达 20 秒），用户容易以为卡住了
- 无法感知搜索过程中的任何信息（匹配了多少文章、相似度如何等）

---

## 二、设计方案：多阶段请求 + 实时进度展示

### 核心思路

**将原来的一次请求拆分为两次请求**，在两次请求之间前端可以展示真实的搜索结果信息：

```
请求1: rag_search_step1 → 返回 Embedding + 向量搜索结果（sources）
  ↓ 前端实时展示搜索到的分片信息
请求2: rag_generate → 将 sources 发给后端生成回答
  ↓ 前端展示生成中
最终展示完整回答
```

### 方案优势

1. **不需要 SSE**：仍然是普通的 HTTP 请求
2. **展示真实数据**：搜索到多少分片、来自哪些文章、相似度分布——这些都是真实数据
3. **感知更快**：第一阶段（搜索）完成后立即展示结果，用户在等待 AI 生成期间有东西可看
4. **改动可控**：后端拆成两个小函数，前端增加进度状态管理

---

## 三、后端修改

### 3.1 新增 Edge Function: `rag_search_step1`

功能：**生成 Embedding + 向量搜索**，返回匹配到的 sources（不生成 AI 回答）。

```
POST /functions/v1/rag_search_step1
Body: { question, top_k, score_threshold }
Response: {
  sources: RAGSource[],
  summary_count: number,        // 总结类匹配数
  transcript_count: number,     // 原文类匹配数
  unique_article_count: number, // 涉及的不同文章数
  query_embedding_time_ms: number,
  search_time_ms: number,
  top_score: number,            // 最高相似度
  avg_score: number             // 平均相似度
}
```

### 3.2 新增 Edge Function: `rag_generate`

功能：**根据 sources 生成 AI 回答**（接收前端传回的 sources）。

```
POST /functions/v1/rag_generate
Body: { question, sources }
Response: {
  answer: string,
  generation_time_ms: number
}
```

### 3.3 保留原有 `rag_search`

原有的一次性接口保留不动，作为兼容方案。新的拆分接口是增量添加。

---

## 四、前端修改

### 4.1 进度状态模型

在 `useRAG.ts` 中新增进度状态：

```typescript
export interface RAGProgress {
  stage: 'embedding' | 'searching' | 'search_done' | 'generating' | 'done' | 'error';
  message: string;                    // 当前阶段描述
  detail?: string;                    // 详细信息
  searchResult?: {                    // 搜索完成后填充
    totalChunks: number;              // 匹配到的总分片数
    summaryCount: number;             // 总结类分片数
    transcriptCount: number;          // 原文类分片数
    uniqueArticleCount: number;       // 涉及的文章数
    topScore: number;                 // 最高相似度
    avgScore: number;                 // 平均相似度
    topSources: RAGSource[];          // 前几条高分结果预览
  };
  elapsedMs?: number;                 // 已用时间
}
```

### 4.2 `useRAG.ts` 修改

新增 `progress` ref 和阶段化的 `ask` 方法：

```typescript
const progress = ref<RAGProgress | null>(null);

const ask = async (question, options) => {
  progress.value = { stage: 'embedding', message: '正在理解你的问题...' };
  
  // 第一步：搜索
  progress.value = { stage: 'searching', message: '正在检索知识库...' };
  const step1Result = await supabase.functions.invoke('rag_search_step1', { body: { question, top_k, score_threshold } });
  
  // 展示搜索结果
  progress.value = {
    stage: 'search_done',
    message: `已找到 ${step1Result.sources.length} 个相关片段`,
    searchResult: { ... }
  };
  
  // 第二步：生成回答
  progress.value = { stage: 'generating', message: '正在整合信息生成回答...', searchResult: progress.value.searchResult };
  const step2Result = await supabase.functions.invoke('rag_generate', { body: { question, sources: step1Result.sources } });
  
  progress.value = { stage: 'done', message: '回答完成' };
};
```

### 4.3 `RAGChatModal.vue` 进度 UI

将原来的三点动画替换为**多阶段进度面板**：

```
┌──────────────────────────────────────────────────┐
│  🔍 正在为你搜索...                                │
│                                                    │
│  ✅ 理解问题          0.8s                         │
│  ✅ 检索知识库        2.1s                         │
│     ├ 找到 15 个相关片段                            │
│     ├ 涉及 6 篇文章                                │
│     ├ 总结类: 7 条 | 原文类: 8 条                   │
│     └ 最高相似度: 89% | 平均: 72%                   │
│  ⏳ 生成回答中...                                   │
│                                                    │
│  ┌─ 匹配预览 ─────────────────────────────────┐    │
│  │ 📄 AI Agent 技术解析 - 总结 (89%)          │    │
│  │ 📄 MCP 协议详解 - 原文字幕 (85%)           │    │
│  │ 📄 Claude 3.5 新功能 - Summary (82%)       │    │
│  └─────────────────────────────────────────────┘    │
│                                                    │
│  ⏱ 已用时间: 4.2s                                  │
└──────────────────────────────────────────────────┘
```

### 4.4 UI 各阶段展示内容

| 阶段 | 图标 | 显示内容 |
|------|------|---------|
| `embedding` | ⏳ 旋转 | "正在理解你的问题..." |
| `searching` | 🔍 动画 | "正在检索知识库..." |
| `search_done` | ✅ | "找到 N 个相关片段，涉及 M 篇文章" + 分片统计 + 预览卡片 |
| `generating` | ✨ 动画 | "正在整合信息生成回答..." + 搜索结果保持展示 |
| `done` | ✅ | 进度面板消失，展示最终回答 |
| `error` | ❌ | 错误信息 + 重试按钮 |

### 4.5 额外的 UX 优化

1. **计时器**：从发起请求开始，实时显示已用时间（前端 setInterval）
2. **搜索结果预览卡片**：在 AI 生成回答期间，展示 top 3 匹配结果的简要信息（文章标题/类型/相似度），让用户有东西可看
3. **阶段勾选动画**：每完成一个阶段，前一个阶段打上 ✅ 并附上耗时，有进度感
4. **平滑过渡**：各阶段之间用 Vue transition 做平滑动画

---

## 五、修改文件清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `supabase/functions/rag_search_step1/index.ts` | **新增** | 搜索阶段函数（Embedding + 向量搜索） |
| `supabase/functions/rag_generate/index.ts` | **新增** | 生成阶段函数（AI 回答生成） |
| `supabase/functions/rag_search/index.ts` | 保留不动 | 兼容原有接口 |
| `src/composables/useRAG.ts` | **修改** | 添加 progress 状态，拆分为两步调用 |
| `src/components/RAGChatModal.vue` | **修改** | 加载动画替换为进度面板 |

---

## 六、数据流示意

```
用户输入问题
  │
  ├──→ [前端] progress = { stage: 'embedding' }
  │        显示: ⏳ 正在理解你的问题...
  │
  ├──→ [请求1] POST rag_search_step1
  │        后端: generateEmbedding() + 并行向量搜索
  │
  │    [前端] progress = { stage: 'searching' }
  │        显示: 🔍 正在检索知识库...
  │
  ├──→ [请求1返回] sources + 统计数据
  │
  │    [前端] progress = { stage: 'search_done', searchResult: {...} }
  │        显示: ✅ 找到 15 个片段 / 6 篇文章 / 最高 89%
  │        显示: 匹配预览卡片
  │
  ├──→ [请求2] POST rag_generate
  │        后端: generateAnswer(question, sources)
  │
  │    [前端] progress = { stage: 'generating' }
  │        显示: ✨ 正在整合信息生成回答...
  │        保持显示: 搜索结果统计 + 预览卡片
  │
  ├──→ [请求2返回] answer
  │
  └──→ [前端] progress = { stage: 'done' }
           进度面板消失，显示完整回答 + 引用来源
```

---

## 七、实现注意事项

1. **安全性**：`rag_generate` 接口接受前端传入的 sources，需要验证 sources 格式，避免注入
2. **容错**：如果 step1 成功但 step2 失败，应该展示搜索到的 sources 并提示生成失败、允许重试
3. **保留原接口**：原有 `rag_search` 不删除，保证向后兼容
4. **进度面板收起**：回答生成后，进度面板带动画收起，不占用空间
5. **计时器清理**：组件卸载或请求完成时清除 setInterval

---

## 八、方案备选：纯前端模拟进度（无后端改动）

如果不想修改后端，也可以只在前端做模拟进度：

- 根据经验预估各阶段时间，用 setTimeout 切换阶段显示
- 缺点：进度是假的，搜索统计数据无法提前获取，只能在最终结果返回后才能展示

**推荐方案：拆分后端请求（本文档主方案）**，因为可以展示真实的搜索数据，用户体验更真实。
