import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const GENERATION_MODEL = Deno.env.get('RAG_GENERATION_MODEL') || 'gemini-3-flash-preview';

const cors = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type'
};

interface RAGSource {
  article_id: number;
  section_id: number;
  section_type?: string;
  language?: string;
  content: string;
  score?: number;
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: cors });
  try {
    const { question, sources } = await req.json();

    if (!question?.trim()) {
      return jsonResp({ error: '问题不能为空' }, 400);
    }
    if (!Array.isArray(sources) || sources.length === 0) {
      return jsonResp({ error: '没有可用的搜索结果' }, 400);
    }
    if (sources.length > 50) {
      return jsonResp({ error: 'sources 数量超出限制' }, 400);
    }

    const sanitizedSources: RAGSource[] = sources.map((s: RAGSource) => ({
      article_id: Number(s.article_id),
      section_id: Number(s.section_id),
      section_type: String(s.section_type || ''),
      language: String(s.language || ''),
      content: String(s.content || '').slice(0, 5000),
      score: Number(s.score || 0)
    }));

    const genStart = performance.now();
    const answer = await generateAnswer(question, sanitizedSources);
    const genTime = performance.now() - genStart;

    return jsonResp({
      answer,
      generation_time_ms: Math.round(genTime)
    });
  } catch (error: unknown) {
    console.error('RAG generate error:', error);
    const msg = error instanceof Error ? error.message : 'server error';
    return jsonResp({ error: msg }, 500);
  }
});

function jsonResp(obj: unknown, status = 200) {
  return new Response(JSON.stringify(obj), { status, headers: { ...cors, 'Content-Type': 'application/json' } });
}

async function generateAnswer(question: string, sources: RAGSource[]) {
  const apiKey = Deno.env.get('GOOGLE_API_KEY');
  if (!apiKey) throw new Error('GOOGLE_API_KEY not configured');
  const ctx = sources.map((s, i) => {
    return `【来源 ${i+1}】\n类型: ${s.section_type||'?'}\n语言: ${s.language||'?'}\n相似度: ${s.score?.toFixed(3)||'?'}\n内容: ${s.content}`;
  }).join('\n---\n');
  const prompt = `你是一个专业的知识库助手，负责根据搜索到的文章片段，为用户提供完整、详细的回答。

**用户问题：**
${question}

**搜索到的相关内容：**
${ctx}

**回答要求：**
1. **必须使用中文回答**：如果原文是英文，直接翻译成中文呈现，保持原意不变
2. **详细展示原文内容**：不要让用户去查看原文，直接在回答中完整呈现搜索到的关键内容
3. **组织语言，整合多个来源**：将相关的内容按主题归类整理，如果多个来源讨论同一话题，合并呈现并标注来源，按逻辑顺序组织回答
4. **回答可以较长**：宁可详细也不要遗漏重要信息
5. **保持原文准确性**：严格基于搜索到的内容回答，不要编造信息
6. **格式清晰**：使用标题、列表、分段等方式组织内容，在引用具体内容时标注来源编号
7. 如果搜索到的内容无法完全回答问题，诚实说明哪些部分可以回答，哪些部分信息不足

**你的回答：**`;
  const resp = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/${GENERATION_MODEL}:generateContent?key=${apiKey}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts: [{ text: prompt }] }],
        generationConfig: { temperature: 0.7, maxOutputTokens: 15000 }
      })
    }
  );
  if (!resp.ok) {
    const t = await resp.text();
    throw new Error(`Generation failed: ${t}`);
  }
  const data = await resp.json();
  const c = data?.candidates?.[0]?.content?.parts?.[0]?.text;
  if (!c) throw new Error('Cannot parse answer');
  return c;
}
