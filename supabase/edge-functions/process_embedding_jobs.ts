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
// 将处理任务数从20减少到5，避免超时
const TOP_JOBS = 5;

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
  
  let lastError;
  for(let i=0; i<3; i++) {
    try {
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
    } catch(e) {
      console.error(`summary retry ${i+1} failed:`, e);
      lastError = e;
      // 等待一秒后重试
      await new Promise(r => setTimeout(r, 1000));
    }
  }
  throw lastError;
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
  
  let lastError;
  for(let i=0; i<3; i++) {
    try {
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
    } catch(e) {
      console.error(`embed retry ${i+1} failed:`, e);
      lastError = e;
      await new Promise(r => setTimeout(r, 1000));
    }
  }
  throw lastError;
}

async function processJob(sectionId) {
  // 取 section 与所属 article
  const { data: section, error: e1 } = await supabase.from("keep_article_sections").select("id, article_id, language, section_type, content").eq("id", sectionId).maybeSingle();
  if (e1) throw e1;
  if (!section) throw new Error("section_not_found");
  const textRaw = cleanText(section.content || "");
  const needSummary = textRaw.length > CHUNK_CHAR_MAX;
  // summarizeIfNeeded 内部已添加重试
  const baseText = needSummary ? await summarizeIfNeeded(textRaw) : textRaw;
  const chunks = chunkText(baseText);
  let chunkId = 0;
  for (const c of chunks){
    // embed 内部已添加重试
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
    
    // 1. 抓取正常的 pending 任务
    const { data: pendingJobs, error: jErr } = await supabase
      .from("embedding_jobs")
      .select("id, section_id, retry_count, status, updated_at")
      .eq("status", "pending")
      .order("created_at", { ascending: true })
      .limit(TOP_JOBS);
      
    if (jErr) throw jErr;

    let jobsToProcess = pendingJobs || [];

    // 2. 如果配额没满，尝试捞取卡住的任务（处理超过1小时未更新且重试次数<3的任务）
    if (jobsToProcess.length < TOP_JOBS) {
      const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000).toISOString();
      const { data: stuckJobs, error: sErr } = await supabase
        .from("embedding_jobs")
        .select("id, section_id, retry_count, status, updated_at")
        .eq("status", "processing")
        .lt("updated_at", oneHourAgo)
        .lt("retry_count", 3)
        .limit(TOP_JOBS - jobsToProcess.length);
        
      if (!sErr && stuckJobs) {
        jobsToProcess = [...jobsToProcess, ...stuckJobs];
      }
    }

    let handled = 0;
    for (const job of jobsToProcess){
      // 抢占任务，防止其他worker同时处理
      // 如果是 stuck job，将其从 processing -> processing 也是一种更新，可以防止被其他 worker 再次捞取
      // 使用 updated_at 作为乐观锁，防止多个 worker 同时抢到同一个任务
      const { error: updErr } = await supabase.from("embedding_jobs").update({
        status: "processing",
        updated_at: new Date().toISOString()
      })
      .eq("id", job.id)
      .eq("updated_at", job.updated_at);
      
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
        const currentRetryCount = (job.retry_count || 0) + 1;
        // 如果超过3次，标记为 error 并不再重试
        const nextStatus = currentRetryCount >= 3 ? "error" : "pending"; // 失败后退回 pending 等待下一次调度，而不是一直 processing
        
        await supabase.from("embedding_jobs").update({
          status: nextStatus, 
          retry_count: currentRetryCount,
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