import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from 'jsr:@supabase/supabase-js@2';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type'
};

Deno.serve(async (req)=>{
  // 处理 CORS 预检请求
  if (req.method === 'OPTIONS') {
    return new Response('ok', {
      headers: corsHeaders
    });
  }
  try {
    const { question, top_k = 20, score_threshold = 0.15 } = await req.json();
    if (!question || question.trim().length === 0) {
      return new Response(JSON.stringify({
        error: '问题不能为空'
      }), {
        status: 400,
        headers: {
          ...corsHeaders,
          'Content-Type': 'application/json'
        }
      });
    }
    const startTime = performance.now();
    
    // 1. 生成查询嵌入
    const embeddingStart = performance.now();
    const queryEmbedding = await generateEmbedding(question);
    const embeddingTime = performance.now() - embeddingStart;
    
    const supabase = createClient(Deno.env.get('SUPABASE_URL') ?? '', Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? '');
    
    // 2. 获取私有文章ID列表（用于排除）
    const { data: privateArticles } = await supabase
      .from('keep_articles')
      .select('id')
      .eq('is_private', true);
    const privateArticleIds = privateArticles?.map(a => a.id) || [];
    console.log(`排除 ${privateArticleIds.length} 篇私有文章`);
    
    // 3. === 并行检索模式（v3.0）===
    // 同时搜索"总结"和"原文字幕"，避免总结没命中导致原文遗漏
    const searchStart = performance.now();
    
    // 并行执行两个搜索
    const [summarySearchResult, transcriptSearchResult] = await Promise.all([
      // 搜索总结内容
      supabase.rpc('search_article_embeddings_v3', {
        query_embedding: `[${queryEmbedding.join(',')}]`,
        match_threshold: score_threshold,
        match_count: Math.ceil(top_k / 2),
        allowed_types: ['总结', 'Summary', '人物介绍', 'Key Takeaways'],
        excluded_article_ids: privateArticleIds.length > 0 ? privateArticleIds : null
      }),
      // 搜索原文字幕内容
      supabase.rpc('search_article_embeddings_v3', {
        query_embedding: `[${queryEmbedding.join(',')}]`,
        match_threshold: score_threshold,
        match_count: Math.ceil(top_k / 2),
        allowed_types: ['原文字幕', 'transcript', 'raw', 'paragraph', 'section'],
        excluded_article_ids: privateArticleIds.length > 0 ? privateArticleIds : null
      })
    ]);
    
    const searchTime = performance.now() - searchStart;
    
    // 检查错误
    if (summarySearchResult.error) {
      console.error('总结搜索失败:', summarySearchResult.error);
    }
    if (transcriptSearchResult.error) {
      console.error('原文搜索失败:', transcriptSearchResult.error);
    }
    
    // 4. 合并结果并去重
    const summaryResults = summarySearchResult.data || [];
    const transcriptResults = transcriptSearchResult.data || [];
    
    console.log(`总结搜索: ${summaryResults.length} 条, 原文搜索: ${transcriptResults.length} 条`);
    
    // 合并并按相似度排序
    const allResults = [...summaryResults, ...transcriptResults];
    
    // 去重（同一个 section_id 只保留分数最高的）
    const uniqueResults = new Map();
    for (const result of allResults) {
      const key = `${result.article_id}-${result.section_id}-${result.chunk_id || 0}`;
      const existing = uniqueResults.get(key);
      if (!existing || result.score > existing.score) {
        uniqueResults.set(key, result);
      }
    }
    
    // 按相似度排序，取 top_k
    let sources = Array.from(uniqueResults.values())
      .sort((a, b) => b.score - a.score)
      .slice(0, top_k);
    
    console.log(`合并去重后: ${sources.length} 条结果`);
    
    // 如果没有找到任何结果
    if (!sources || sources.length === 0) {
      return new Response(JSON.stringify({
        answer: '抱歉，我在知识库中没有找到与您问题相关的内容。请尝试换个问法或提供更多上下文信息。',
        sources: [],
        query_embedding_time_ms: embeddingTime,
        search_time_ms: searchTime,
        generation_time_ms: 0,
        total_time_ms: performance.now() - startTime,
        search_mode: 'parallel'
      }), {
        status: 200,
        headers: {
          ...corsHeaders,
          'Content-Type': 'application/json'
        }
      });
    }
    
    // 5. 生成回答
    const generationStart = performance.now();
    const answer = await generateAnswer(question, sources);
    const generationTime = performance.now() - generationStart;
    const totalTime = performance.now() - startTime;
    
    return new Response(JSON.stringify({
      answer,
      sources,
      query_embedding_time_ms: embeddingTime,
      search_time_ms: searchTime,
      generation_time_ms: generationTime,
      total_time_ms: totalTime,
      search_mode: 'parallel'
    }), {
      status: 200,
      headers: {
        ...corsHeaders,
        'Content-Type': 'application/json'
      }
    });
  } catch (error) {
    console.error('RAG 错误:', error);
    return new Response(JSON.stringify({
      error: error.message || '服务器错误'
    }), {
      status: 500,
      headers: {
        ...corsHeaders,
        'Content-Type': 'application/json'
      }
    });
  }
});

// 生成文本嵌入（使用 Google text-embedding-004，768维）
async function generateEmbedding(text) {
  const apiKey = Deno.env.get('GOOGLE_API_KEY');
  if (!apiKey) {
    throw new Error('未配置 GOOGLE_API_KEY');
  }
  const url = `https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key=${apiKey}`;
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: 'models/text-embedding-004',
      content: {
        parts: [
          {
            text
          }
        ]
      },
      taskType: 'RETRIEVAL_QUERY'
    })
  });
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`嵌入生成失败: ${errorText}`);
  }
  const data = await response.json();
  return data.embedding.values;
}

// 生成回答（使用 Gemini 2.5 Pro）
async function generateAnswer(question, sources) {
  const apiKey = Deno.env.get('GOOGLE_API_KEY');
  if (!apiKey) {
    throw new Error('未配置 GOOGLE_API_KEY');
  }
  // 构建上下文，优先显示section_type和相似度
  const contextParts = sources.map((source, i)=>{
    const sectionType = source.section_type || '未知类型';
    const score = source.score ? source.score.toFixed(3) : 'N/A';
    const language = source.language || 'unknown';
    return `【来源 ${i + 1}】
类型: ${sectionType}
语言: ${language}
相似度: ${score}
内容: ${source.content}
`;
  });
  const context = contextParts.join('\n---\n\n');
  const prompt = `你是一个专业的知识库助手，负责根据搜索到的文章片段，为用户提供完整、详细的回答。

**用户问题：**
${question}

**搜索到的相关内容：**
${context}

**回答要求：**
1. **必须使用中文回答**：如果原文是英文，直接翻译成中文呈现，保持原意不变
2. **详细展示原文内容**：不要让用户去查看原文，直接在回答中完整呈现搜索到的关键内容
3. **组织语言，整合多个来源**：
   - 将相关的内容按主题归类整理
   - 如果多个来源讨论同一话题，合并呈现并标注来源
   - 按逻辑顺序组织回答，让用户一次性获取所有相关信息
4. **回答可以较长**：宁可详细也不要遗漏重要信息，确保用户不需要再去原文查找
5. **保持原文准确性**：严格基于搜索到的内容回答，不要编造信息
6. **格式清晰**：
   - 使用标题、列表、分段等方式组织内容
   - 在引用具体内容时标注来源编号（如"根据来源1"）
   - 如果有多个相关文章，分别说明各文章的观点
7. 如果搜索到的内容无法完全回答问题，诚实说明哪些部分可以回答，哪些部分信息不足

**你的回答：**`;
  const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key=${apiKey}`;
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      contents: [
        {
          parts: [
            {
              text: prompt
            }
          ]
        }
      ],
      generationConfig: {
        temperature: 0.7,
        maxOutputTokens: 30000
      }
    })
  });
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`答案生成失败: ${errorText}`);
  }
  const data = await response.json();
  if (data.candidates && data.candidates.length > 0) {
    const candidate = data.candidates[0];
    if (candidate.content && candidate.content.parts && candidate.content.parts.length > 0) {
      return candidate.content.parts[0].text;
    }
  }
  throw new Error('无法解析生成的回答');
}

