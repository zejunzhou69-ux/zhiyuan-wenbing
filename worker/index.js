/**
 * 知源问病 · AI 代理 Worker（可选增强）
 * ============================================================
 *
 * 【为什么必须有它】
 * 静态站不能内置大模型 API key —— 写进前端代码等于公开贴在墙上，
 * 谁都能拿去刷你的额度。这个 Worker 是中间层，key 存在 Cloudflare
 * 环境变量里，不进代码、不进仓库。
 *
 * 【安全边界（不可放宽）】
 * Worker 只做一件事：把用户口语「转成规范中医术语」。
 * 辨证结论、方剂组成、穴位定位、安全警告一律由静态端的规则引擎产出，
 * 模型不参与决策。模型即使胡说，也污染不了知识与安全判断。
 *
 * 【降级设计】
 * 不配任何 secret 也能部署。前端探测不到 /api/ai 就自动走纯规则引擎，
 * 功能完整（只是少了口语理解）。AI 挂了、超时了、限流了，一样退回规则。
 *
 * 【部署】
 *   npx wrangler secret put LLM_API_KEY      # 你的 key
 *   npx wrangler secret put LLM_BASE_URL     # 例如 https://api.deepseek.com/v1
 *   npx wrangler secret put LLM_MODEL        # 例如 deepseek-chat
 *   npx wrangler deploy
 *
 * 【可选配置】
 *   LLM_API_STYLE    openai（默认）| anthropic
 *   LLM_TEMPERATURE  0.1
 *   LLM_TIMEOUT_MS   15000
 *   CORS_ORIGIN      限定来源，如 https://xxx.pages.dev；不设则不限制
 *   RATE_LIMIT_MAX   每 IP 每分钟请求数，默认 20
 */

const SYSTEM_PROMPT = `你是中医术语规范化助手，服务于一个中医辨证应用。

你的唯一任务：把用户的口语描述，转写成规范的中医术语短句。

规则：
1. 只输出转写结果，不要解释、不要加诊断、不要给方子。
2. 保留用户原意与否定词。不确定的词保持原样，不要猜。
3. 口语映射示例：
   - 脑瓜仁儿疼 / 后脑勺疼 / 脑袋疼 → 后脑痛
   - 嗓子疼 / 喉咙疼 → 咽痛
   - 拉肚子 / 窜稀 → 泄泻
   - 拉不出 / 大便不通 → 便秘
   - 没胃口 / 不想吃 → 不思饮食
   - 爱出汗 / 动不动出汗 → 自汗
   - 睡觉出汗 → 盗汗
   - 五更泻 / 早上拉 → 黎明泻
   - 喘不上来气 → 喘息不能平卧
   - 心慌慌 → 心悸
4. 输出格式：一行，不超过 60 字，只写症状描述本身。
5. 如果输入与症状无关（如打招呼），原样返回。`;

// ---------------------------------------------------------------- CORS

/**
 * 生成 CORS 头。
 *
 * ⚠️ 与上一版的差别：原来硬编码 '*'。公开站点用 '*' 意味着任何第三方
 * 网站都能从用户浏览器调用你的 Worker、消耗你的额度。现在支持用
 * CORS_ORIGIN 限定来源；未配置时才放开（本地开发方便）。
 */
function corsHeaders(request, env) {
  const allow = env.CORS_ORIGIN;
  const origin = request.headers.get('Origin');
  const value = allow ? (origin && origin === allow ? origin : null) : '*';
  const h = {
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '86400',
    'Vary': 'Origin',
  };
  // 白名单不匹配时故意不加 Allow-Origin，浏览器自会拦截
  if (value) h['Access-Control-Allow-Origin'] = value;
  return h;
}

function json(obj, status, request, env) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      ...corsHeaders(request, env),
    },
  });
}

// ---------------------------------------------------------------- 限流

/**
 * 内存限流。
 *
 * ⚠️ 已知局限（如实说明，不假装它很强）：Worker 跑在边缘运行时，
 * 实例随时回收，Map 不共享也不持久，只能挡住单实例上的突发，
 * 挡不住分布式刷。对个人小额 key 够用；公开运营请接 Cloudflare
 * Rate Limiting 或 KV。届时只需替换下面两个函数体，调用方不用改。
 */
const RATE = new Map();

function rateLimited(ip, env) {
  const max = parseInt(env.RATE_LIMIT_MAX || '20', 10);
  const now = Date.now();
  const win = 60000;
  const hits = (RATE.get(ip) || []).filter((t) => now - t < win);
  if (hits.length >= max) return true;
  hits.push(now);
  RATE.set(ip, hits);
  // 顺手清理，避免 Map 无限增长
  if (RATE.size > 5000) {
    for (const [k, v] of RATE) {
      if (!v.some((t) => now - t < win)) RATE.delete(k);
    }
  }
  return false;
}

// ---------------------------------------------------------------- 上游调用

function timeoutSignal(ms) {
  if (typeof AbortSignal !== 'undefined' && AbortSignal.timeout) {
    return AbortSignal.timeout(ms);
  }
  const c = new AbortController();
  setTimeout(() => c.abort(), ms);
  return c.signal;
}

/** 从各家返回体里取文本 */
function extractText(data, style) {
  if (style === 'anthropic') {
    const parts = data?.content;
    if (Array.isArray(parts)) {
      return parts.filter((p) => p?.type === 'text').map((p) => p.text).join('').trim();
    }
    return '';
  }
  // OpenAI 兼容（DeepSeek / 智谱 / 通义 / Kimi / OpenRouter / Ollama 均适用）
  return (data?.choices?.[0]?.message?.content || '').trim();
}

/** 调用上游大模型。没配全就返回 null，前端自动退回规则引擎。 */
async function callLLM(env, userText) {
  const base = (env.LLM_BASE_URL || '').replace(/\/+$/, '');
  const key = env.LLM_API_KEY || '';
  const model = env.LLM_MODEL || '';
  if (!base || !key || !model) return null;

  const style = (env.LLM_API_STYLE || 'openai').toLowerCase();
  const temperature = parseFloat(env.LLM_TEMPERATURE ?? '0.1');
  const timeoutMs = parseInt(env.LLM_TIMEOUT_MS || '15000', 10);

  let url, headers, body;

  if (style === 'anthropic') {
    url = `${base}/messages`;
    headers = {
      'Content-Type': 'application/json',
      'x-api-key': key,
      'anthropic-version': '2023-06-01',
    };
    body = {
      model, max_tokens: 200, temperature,
      system: SYSTEM_PROMPT,
      messages: [{ role: 'user', content: userText.slice(0, 500) }],
    };
  } else {
    // openai 与 ollama 共用这一支（ollama 的 key 随便填非空即可）
    url = `${base}/chat/completions`;
    headers = { 'Content-Type': 'application/json', Authorization: `Bearer ${key}` };
    body = {
      model, temperature, max_tokens: 200,
      messages: [
        { role: 'system', content: SYSTEM_PROMPT },
        { role: 'user', content: userText.slice(0, 500) }],
    };
  }

  // 上游不通时不能让整个请求挂住：超时即放弃，前端退回规则
  const res = await fetch(url, {
    method: 'POST', headers, body: JSON.stringify(body),
    signal: timeoutSignal(timeoutMs),
  });

  if (!res.ok) {
    // 不把上游原文回传浏览器：可能含账号信息，也可能很长
    throw new Error(`upstream_${res.status}`);
  }
  const data = await res.json();
  const out = extractText(data, style);

  // 只接受短文本，防止模型长篇大论污染规则引擎的输入
  if (!out || out.length > 300) return null;
  // 兜底：万一模型开始输出诊断或方剂，直接丢弃，退回原文
  if (/(处方|建议服用|主治|诊断为)/.test(out)) return null;
  return out;
}

// ---------------------------------------------------------------- 主处理

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const isAi = url.pathname === '/api/ai';

    // ---- CORS 预检：必须在方法判断之前 ----
    // 上一版把 OPTIONS 写在了 `method === 'POST'` 分支内部，而 OPTIONS
    // 请求的 method 是 'OPTIONS'，永远进不去那个分支，等于死代码，
    // 浏览器预检会失败。这里提到最前面单独处理。
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders(request, env) });
    }

    if (!isAi) return json({ ok: false, error: 'not found' }, 404, request, env);

    const configured = !!(env.LLM_BASE_URL && env.LLM_API_KEY && env.LLM_MODEL);

    // ---- 健康检查：前端靠它决定要不要走 AI ----
    if (request.method === 'GET') {
      return json({
        ok: true,
        enabled: configured,
        // 只回显协议与模型名，方便确认接对了；不回显 key、不回显 base_url
        style: configured ? (env.LLM_API_STYLE || 'openai') : null,
        model: configured ? env.LLM_MODEL : null,
      }, 200, request, env);
    }

    if (request.method !== 'POST') {
      return json({ ok: false, error: 'method not allowed' }, 405, request, env);
    }

    if (!configured) {
      // 不算错误：明确告诉前端「没配 AI」，前端退回纯规则
      return json({ ok: true, normalized: null, reason: 'llm_not_configured' }, 200, request, env);
    }

    const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
    if (rateLimited(ip, env)) {
      return json({ ok: true, normalized: null, reason: 'rate_limited' }, 200, request, env);
    }

    try {
      const { text } = await request.json();
      if (!text || typeof text !== 'string') {
        return json({ ok: false, error: 'bad request' }, 400, request, env);
      }
      const normalized = await callLLM(env, text);
      return json({ ok: true, normalized }, 200, request, env);
    } catch {
      // AI 出任何问题都不许让应用挂掉：返回 null，前端走纯规则
      return json({ ok: true, normalized: null, reason: 'upstream_failed' }, 200, request, env);
    }
  },
};