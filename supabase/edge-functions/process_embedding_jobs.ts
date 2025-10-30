import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.4";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL");
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
const GOOGLE_API_KEY = Deno.env.get("GOOGLE_API_KEY");

// 更新为 text-embedding-004（768维）
const EMBEDDING_MODEL = Deno.env.get("EMBEDDING_MODEL") ?? "text-embedding-004";
const GEN_MODEL_SUMMARY = Deno.env.get("GEN_MODEL_SUMMARY") ?? "gemini-2.5-flash";
const CHUNK_CHAR_TARGET = Number(Deno.env.get("CHUNK_CHAR_TARGET") ?? "600");
const CHUNK_CHAR_MAX = Number(Deno.env.get("CHUNK_CHAR_MAX") ?? "900");
const TOP_JOBS = 20;

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
  global: {
    headers: {
      "Authorization": `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`
    }
  }
});

function cleanText(input) {
  return input.replace(/```[\s\S]*?```/g, " ").replace(/\r\n|\n|\r/g, "\n").replace(/\n{2,}/g, "\n").replace(/[\t ]{2,}/g, " ").trim();
}

function chunkText(text) {
  if (text.length <= CHUNK_CHAR_MAX) return [
    text
  ];
  const parts = [];
  const paragraphs = text.split(/\n{1,}/);
  let buf = "";
  const pushBuf = ()=>{
    if (buf.trim().length) {
      parts.push(buf.trim());
      buf = "";
    }
  };
  for (const p of paragraphs){
    const line = p.trim();
    if (!line) continue;
    if ((buf + "\n" + line).length <= CHUNK_CHAR_MAX) {
      buf = buf ? buf + "\n" + line : line;
    } else {
      if (buf.length < CHUNK_CHAR_TARGET && line.length < CHUNK_CHAR_MAX) {
        // 行过长则直接切分
        pushBuf();
        if (line.length > CHUNK_CHAR_MAX) {
          for(let i = 0; i < line.length; i += CHUNK_CHAR_MAX)parts.push(line.slice(i, i + CHUNK_CHAR_MAX));
        } else {
          buf = line;
        }
      } else {
        pushBuf();
        buf = line;
      }
    }
  }
  pushBuf();
  return parts;
}

async function summarizeIfNeeded(text) {
  if (text.length <= CHUNK_CHAR_MAX) return text;
  const body = {
    contents: [
      {
        role: "user",
        parts: [
          {
            text: `请将以下中文内容压缩为检索友好的要点摘要（保留关键信息、实体与术语，去掉赘述，450-600字）：\n\n${text}`
          }
        ]
      }
    ]
  };
  const resp = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${GEN_MODEL_SUMMARY}:generateContent?key=${encodeURIComponent(GOOGLE_API_KEY)}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(body)
  });
  if (!resp.ok) {
    const t = await resp.text();
    throw new Error(`summary_error: ${resp.status} ${t}`);
  }
  const data = await resp.json();
  const textOut = data?.candidates?.[0]?.content?.parts?.[0]?.text ?? "";
  return textOut.trim() || text;
}

async function embed(text) {
  const body = {
    model: `models/${EMBEDDING_MODEL}`,
    content: {
      parts: [
        {
          text
        }
      ]
    },
    taskType: "RETRIEVAL_DOCUMENT"
  };
  const resp = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${EMBEDDING_MODEL}:embedContent?key=${encodeURIComponent(GOOGLE_API_KEY)}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(body)
  });
  if (!resp.ok) {
    const t = await resp.text();
    throw new Error(`embed_error: ${resp.status} ${t}`);
  }
  const data = await resp.json();
  const vec = data?.embedding?.values;
  if (!vec || !Array.isArray(vec)) throw new Error("embed_empty_vector");
  return vec;
}

async function processJob(sectionId) {
  // 取 section 与所属 article
  const { data: section, error: e1 } = await supabase.from("keep_article_sections").select("id, article_id, language, section_type, content").eq("id", sectionId).maybeSingle();
  if (e1) throw e1;
  if (!section) throw new Error("section_not_found");
  const textRaw = cleanText(section.content || "");
  const needSummary = textRaw.length > CHUNK_CHAR_MAX;
  const baseText = needSummary ? await summarizeIfNeeded(textRaw) : textRaw;
  const chunks = chunkText(baseText);
  let chunkId = 0;
  for (const c of chunks){
    const vec = await embed(c);
    const { error: upErr } = await supabase.from("keep_article_embeddings").upsert({
      article_id: section.article_id,
      section_id: section.id,
      language: section.language || null,
      section_type: section.section_type || null,
      chunk_id: chunkId++,
      content: c,
      embedding: vec,
      meta: {
        needSummary
      }
    }, {
      onConflict: "section_id,chunk_id"
    });
    if (upErr) throw upErr;
  }
}

Deno.serve(async (req)=>{
  try {
    const url = new URL(req.url);
    const onlySection = url.searchParams.get("section_id");
    if (onlySection) {
      await processJob(Number(onlySection));
      return new Response(JSON.stringify({
        ok: true,
        handled: 1
      }), {
        headers: {
          "Content-Type": "application/json"
        }
      });
    }
    // 抓取 pending 任务
    const { data: jobs, error: jErr } = await supabase.from("embedding_jobs").select("id, section_id").eq("status", "pending").order("created_at", {
      ascending: true
    }).limit(TOP_JOBS);
    if (jErr) throw jErr;
    let handled = 0;
    for (const job of jobs ?? []){
      // 抢占
      const { error: updErr } = await supabase.from("embedding_jobs").update({
        status: "processing",
        updated_at: new Date().toISOString()
      }).eq("id", job.id).eq("status", "pending");
      if (updErr) continue;
      try {
        await processJob(job.section_id);
        await supabase.from("embedding_jobs").update({
          status: "done",
          updated_at: new Date().toISOString(),
          last_error: null
        }).eq("id", job.id);
        handled++;
      } catch (err) {
        await supabase.from("embedding_jobs").update({
          status: "error",
          retry_count: (handled ?? 0) + 1,
          last_error: String(err),
          updated_at: new Date().toISOString()
        }).eq("id", job.id);
      }
    }
    return new Response(JSON.stringify({
      ok: true,
      handled
    }), {
      headers: {
        "Content-Type": "application/json"
      }
    });
  } catch (e) {
    return new Response(JSON.stringify({
      ok: false,
      error: String(e)
    }), {
      status: 500,
      headers: {
        "Content-Type": "application/json"
      }
    });
  }
});

