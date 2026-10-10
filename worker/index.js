/**
 * 知源问病 · AI 代理 Worker（可选）
 *
 * 为什么需要它：静态站不能内置大模型 API key —— 写进前端代码等于公开贴在墙上，
 * 谁都能拿去刷你的额度。这个 Worker 做中间层，key 存在 Cloudflare 的环境变量里。
 *
 * 前端会自动探测 /api/ai：
 *   有 Worker → AI 负责「理解口语 + 组织表达」
 *   没 Worker → 纯规则引擎，功能完整
 * 两档都是完整功能，不是"有 AI 才能用"。
 *
 * ⚠️ 重要边界（不可放宽）：
 * Worker 只做两件事：① 把用户口语「转成规范术语」② 把规则引擎的结果「说得更顺」。
 * **辨证结论、方剂组成、穴位定位、安全警告一律由静态端的规则引擎产出**，
 * 模型不参与决策。这样即使模型胡说，也不会污染知识与安全判断。
 *
 * 部署：
 *   wrangler secret put LLM_API_KEY     # 你的 key，存 Cloudflare，不进代码
 *   wrangler secret put LLM_BASE_URL    # 例如 https://api.deepseek.com/v1
 *   wrangler secret put LLM_MODEL       # 例如 deepseek-chat
 *   npx wrangler deploy
 *
 * 不配任何 secret 也能部署，前端探测不到 /api/ai 就自动走纯规则，功能不受影响。
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

/** 处理 CORS 预检 */
function corsHeaders() {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '86400',
  };
}

const RATE_LIMIT = new Map();   // 简单限流：同一 IP 每分钟不超过 N 次
const RATE_MAX = 20;

function rateLimited(ip) {
  const now = Date.now();
  const win = 60000;
  const hits = (RATE_LIMIT.get(ip) || []).filter((t) => now - t < win);
  hits.push(now);
  RATE_LIMIT.set(ip, hits);
  return hits.length > RATE_MAX;
}

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { 'Content-Type': 'application/json; charset=utf-8', ...corsHeaders() },
  });
}

async function callLLM(env, userText) {
  const base = (env.LLM_BASE_URL || '').replace(/\/+$/, '');
  const key = env.LLM_API_KEY || '';
  const model = env.LLM_MODEL || '';
  if (!base || !key || !model) return null;      // 没配就返回 null，前端自动退回规则

  const res = await fetch(`${base}/chat/completions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${key}` },
    body: JSON.stringify({
      model,
      temperature: 0.1,
      max_tokens: 200,
      messages: [
        { role: 'system', content: SYSTEM_PROMPT },
        { role: 'user', content: userText.slice(0, 500) },
      ],
    }),
  });

  if (!res.ok) throw new Error(`上游返回 ${res.status}`);
  const data = await res.json();
  const out = data?.choices?.[0]?.message?.content?.trim();
  // 只接受短文本，防止模型长篇大论污染输入
  if (!out || out.length > 300) return null;
  return out;
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // 健康检查：前端靠它判断有没有 AI
    if (url.pathname === '/api/ai' && request.method === 'GET') {
      const enabled = !!(env.LLM_BASE_URL && env.LLM_API_KEY && env.LLM_MODEL);
      return json({ ok: true, enabled });
    }

    if (url.pathname === '/api/ai' && request.method === 'POST') {
      if (request.method === 'OPTIONS') {
        return new Response(null, { status: 204, headers: corsHeaders() });
      }

      const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
      if (rateLimited(ip)) return json({ ok: false, error: 'rate limited' }, 429);

      try {
        const { text } = await request.json();
        if (!text || typeof text !== 'string') {
          return json({ ok: false, error: 'bad request' }, 400);
        }

        const normalized = await callLLM(env, text);
        if (normalized === null) {
          return json({ ok: true, normalized: null, reason: 'llm_not_configured' });
        }
        return json({ ok: true, normalized });
      } catch (e) {
        // AI 挂了不能让应用挂掉：返回 null，前端走纯规则
        return json({ ok: true, normalized: null, reason: String(e.message || e) });
      }
    }

    return json({ ok: false, error: 'not found' }, 404);
  },
};
