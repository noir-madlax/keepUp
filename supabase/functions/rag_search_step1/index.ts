import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const { createClient } = await import('https://esm.sh/@supabase/supabase-js@2.45.4');

const EMBEDDING_MODEL = Deno.env.get('EMBEDDING_MODEL') || 'gemini-embedding-001';

const cors = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type'
};

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: cors });
  try {
    const { question, top_k = 20, score_threshold = 0.15 } = await req.json();
    if (!question?.trim()) {
      return jsonResp({ error: '问题不能为空' }, 400);
    }
    const startTime = performance.now();

    const embStart = performance.now();
    const queryEmbedding = await generateEmbedding(question);
    const embTime = performance.now() - embStart;

    const sb = createClient(Deno.env.get('SUPABASE_URL'), Deno.env.get('SUPABASE_SERVICE_ROLE_KEY'));

    const { data: priv } = await sb.from('keep_articles').select('id').eq('is_private', true);
    const exIds = priv?.map((a: { id: number }) => a.id) || [];

    const searchStart = performance.now();
    const [r1, r2] = await Promise.all([
      sb.rpc('search_article_embeddings_v3', {
        query_embedding: `[${queryEmbedding.join(',')}]`,
        match_threshold: score_threshold,
        match_count: Math.ceil(top_k / 2),
        allowed_types: ['总结', 'Summary', '人物介绍', 'Key Takeaways'],
        excluded_article_ids: exIds.length > 0 ? exIds : null
      }),
      sb.rpc('search_article_embeddings_v3', {
        query_embedding: `[${queryEmbedding.join(',')}]`,
        match_threshold: score_threshold,
        match_count: Math.ceil(top_k / 2),
        allowed_types: ['原文字幕', 'transcript', 'raw', 'paragraph', 'section'],
        excluded_article_ids: exIds.length > 0 ? exIds : null
      })
    ]);
    const searchTime = performance.now() - searchStart;

    if (r1.error) console.error('summary search error:', r1.error);
    if (r2.error) console.error('transcript search error:', r2.error);

    const summaryResults = r1.data || [];
    const transcriptResults = r2.data || [];
    const all = [...summaryResults, ...transcriptResults];

    const umap = new Map();
    for (const r of all) {
      const k = `${r.article_id}-${r.section_id}-${r.chunk_id || 0}`;
      if (!umap.has(k) || r.score > umap.get(k).score) umap.set(k, r);
    }
    const sources = Array.from(umap.values()).sort((a: { score: number }, b: { score: number }) => b.score - a.score).slice(0, top_k);

    const uniqueArticleIds = new Set(sources.map((s: { article_id: number }) => s.article_id));
    const scores = sources.map((s: { score: number }) => s.score);
    const topScore = scores.length > 0 ? scores[0] : 0;
    const avgScore = scores.length > 0 ? scores.reduce((a: number, b: number) => a + b, 0) / scores.length : 0;

    return jsonResp({
      sources,
      summary_count: summaryResults.length,
      transcript_count: transcriptResults.length,
      unique_article_count: uniqueArticleIds.size,
      query_embedding_time_ms: Math.round(embTime),
      search_time_ms: Math.round(searchTime),
      total_time_ms: Math.round(performance.now() - startTime),
      top_score: topScore,
      avg_score: avgScore
    });
  } catch (error: unknown) {
    console.error('RAG step1 error:', error);
    const msg = error instanceof Error ? error.message : 'server error';
    return jsonResp({ error: msg }, 500);
  }
});

function jsonResp(obj: unknown, status = 200) {
  return new Response(JSON.stringify(obj), { status, headers: { ...cors, 'Content-Type': 'application/json' } });
}

async function generateEmbedding(text: string) {
  const apiKey = Deno.env.get('GOOGLE_API_KEY');
  if (!apiKey) throw new Error('GOOGLE_API_KEY not configured');
  const resp = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/${EMBEDDING_MODEL}:embedContent?key=${apiKey}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: `models/${EMBEDDING_MODEL}`,
        content: { parts: [{ text }] },
        taskType: 'RETRIEVAL_QUERY',
        outputDimensionality: 768
      })
    }
  );
  if (!resp.ok) {
    const t = await resp.text();
    throw new Error(`Embedding failed: ${t}`);
  }
  const data = await resp.json();
  return data.embedding.values;
}
