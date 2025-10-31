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
    const { question, top_k = 20, score_threshold = 0.15, use_layered = true } = await req.json();
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
    let sources = [];
    let searchTime = 0;
    if (use_layered) {
      // === 分层检索模式 ===
      // 第一层：在总结中搜索，快速定位相关文章
      const layer1Start = performance.now();
      const { data: summaryResults, error: summaryError } = await supabase.rpc('search_article_embeddings', {
        query_embedding: `[${queryEmbedding.join(',')}]`,
        match_threshold: 0.1,
        match_count: 20
      });
      if (summaryError) {
        throw new Error(`总结层检索失败: ${summaryError.message}`);
      }
      const layer1Time = performance.now() - layer1Start;
      // 提取相关文章ID
      const relevantArticleIds = summaryResults && summaryResults.length > 0 ? [
        ...new Set(summaryResults.map((r)=>r.article_id))
      ] : null;
      console.log(`第一层检索完成: 找到 ${relevantArticleIds?.length || 0} 篇相关文章`);
      // 第二层：在筛选的文章中搜索原文内容
      const layer2Start = performance.now();
      const { data: transcriptResults, error: transcriptError } = await supabase.rpc('search_article_embeddings_v2', {
        query_embedding: `[${queryEmbedding.join(',')}]`,
        match_threshold: score_threshold,
        match_count: top_k,
        lang: null,
        allowed_types: [
          'transcript',
          '原文字幕',
          'raw',
          'paragraph',
          'section'
        ],
        article_filter: relevantArticleIds,
        ef_search_param: 100
      });
      if (transcriptError) {
        throw new Error(`原文层检索失败: ${transcriptError.message}`);
      }
      const layer2Time = performance.now() - layer2Start;
      searchTime = layer1Time + layer2Time;
      sources = transcriptResults || [];
      console.log(`第二层检索完成: 找到 ${sources.length} 个原文片段`);
      console.log(`检索时间 - 第一层: ${layer1Time.toFixed(2)}ms, 第二层: ${layer2Time.toFixed(2)}ms`);
      // 如果原文检索没有结果，回退使用总结结果
      if (sources.length === 0 && summaryResults && summaryResults.length > 0) {
        console.log('原文检索无结果，回退使用总结内容');
        sources = summaryResults.slice(0, top_k);
      }
    } else {
      // === 传统单层检索模式（仅用于对比测试）===
      const searchStart = performance.now();
      const { data: results, error: searchError } = await supabase.rpc('search_article_embeddings', {
        query_embedding: `[${queryEmbedding.join(',')}]`,
        match_threshold: score_threshold,
        match_count: top_k
      });
      if (searchError) {
        throw new Error(`向量检索失败: ${searchError.message}`);
      }
      searchTime = performance.now() - searchStart;
      sources = results || [];
    }
    // 如果没有找到任何结果
    if (!sources || sources.length === 0) {
      return new Response(JSON.stringify({
        answer: '抱歉，我在知识库中没有找到与您问题相关的内容。请尝试换个问法或提供更多上下文信息。',
        sources: [],
        query_embedding_time_ms: embeddingTime,
        search_time_ms: searchTime,
        generation_time_ms: 0,
        total_time_ms: performance.now() - startTime,
        search_mode: use_layered ? 'layered' : 'single'
      }), {
        status: 200,
        headers: {
          ...corsHeaders,
          'Content-Type': 'application/json'
        }
      });
    }
    // 3. 生成回答
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
      search_mode: use_layered ? 'layered' : 'single'
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
  const prompt = `你是一个专业的内容助手，负责根据提供的文章片段回答用户的问题。

**用户问题：**
${question}

**相关文章片段：**
${context}

**回答要求：**
1. 必须使用中文回答（如果原文是英文，需要直接翻译成中文回答，但是不要修改原来的文字意思，不要调整，直接翻译）
2. 严格基于提供的文章片段内容回答，不要编造信息
3. 如果文章片段无法回答问题，请诚实说明
4. 回答要准确、有条理、有层次
5. 可以引用来源编号（如"根据来源1，文章名称：xxxx"）
6. 保持专业和客观的语气

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
        maxOutputTokens: 15000
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

