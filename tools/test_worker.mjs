// 知源问病 · AI Worker 本地测试
//
// 用 mock 上游代替真实大模型，验证 Worker 的行为边界：
//   1) CORS 预检真的能通过（这是上一版的 bug）
//   2) 没配 secret 时返回 llm_not_configured，前端能退回规则
//   3) 上游超时/报错时降级，不把异常抛给用户
//   4) 模型输出含「处方」等词时丢弃，退回原文
//   5) 限流生效
//   6) CORS 白名单能挡住非授权来源
//   7) API Key 绝不出现在任何响应里
//
// 用法：node tools/test_worker.mjs
import worker from '../worker/index.js';

function mockFetch(behaviour) {
  return async (url, opts = {}) => {
    if (behaviour === 'ok') {
      return new Response(JSON.stringify({
        choices: [{ message: { content: '后脑痛' } }],
      }), { status: 200, headers: { 'Content-Type': 'application/json' } });
    }
    if (behaviour === 'timeout') {
      // 真实 fetch 会响应 abort 信号，mock 也必须响应，
      // 否则测到的只是「mock 睡够了才返回」，验证不到 Worker 的超时逻辑。
      return new Promise((resolve, reject) => {
        const timer = setTimeout(
          () => resolve(new Response('{}', { status: 200 })), 3000);
        const sig = opts.signal;
        const onAbort = () => { clearTimeout(timer); reject(new Error('aborted')); };
        if (sig) {
          if (sig.aborted) return onAbort();
          sig.addEventListener('abort', onAbort);
        }
      });
    }
    if (behaviour === 'error') {
      return new Response('upstream exploded, key=sk-SECRET-123', { status: 500 });
    }
    if (behaviour === 'hallucinate') {
      return new Response(JSON.stringify({
        choices: [{ message: { content: '建议服用麻黄汤，处方如下' } }],
      }), { status: 200 });
    }
    if (behaviour === 'toolong') {
      return new Response(JSON.stringify({
        choices: [{ message: { content: '长'.repeat(400) } }],
      }), { status: 200 });
    }
    return new Response('{}', { status: 404 });
  };
}

let pass = 0, fail = 0;
const t = (name, ok, extra = '') => {
  console.log(`  ${ok ? '✓' : '✗'} ${name}${extra ? '　' + extra : ''}`);
  ok ? pass++ : fail++;
};

const URL_BASE = 'https://ai.example.com';
const ENV_OK = {
  LLM_BASE_URL: 'https://api.deepseek.com/v1',
  LLM_API_KEY: 'sk-SECRET-123',
  LLM_MODEL: 'deepseek-chat',
  LLM_TIMEOUT_MS: '800',
};
const REQ = (path, method, body, headers = {}) => new Request(
  URL_BASE + path,
  {
    method,
    headers: { 'Content-Type': 'application/json', 'CF-Connecting-IP': '1.1.1.1', ...headers },
    body: body ? JSON.stringify(body) : undefined,
  });

async function run() {
  const real = globalThis.fetch;
  try {
    console.log('\n【1】CORS 预检（上一版的 bug 点）');
    let res = await worker.fetch(REQ('/api/ai', 'OPTIONS'), {}, {});
    t('OPTIONS 返回 204', res.status === 204, `实际 ${res.status}`);
    t('带 Allow-Methods', !!res.headers.get('Access-Control-Allow-Methods'),
      res.headers.get('Access-Control-Allow-Methods') || '(无)');
    t('带 Allow-Origin', !!res.headers.get('Access-Control-Allow-Origin'),
      res.headers.get('Access-Control-Allow-Origin') || '(无)');

    console.log('\n【2】未配置 secret（纯规则模式）');
    res = await worker.fetch(REQ('/api/ai', 'GET'), {}, {});
    let j = await res.json();
    t('GET 返回 enabled=false', j.enabled === false);
    res = await worker.fetch(REQ('/api/ai', 'POST', { text: '脑瓜仁儿疼' }), {}, {});
    j = await res.json();
    t('POST 返回 llm_not_configured', j.reason === 'llm_not_configured');
    t('未配置时 HTTP 仍为 200', res.status === 200, `实际 ${res.status}`);

    console.log('\n【3】正常调用（mock 返回「后脑痛」）');
    globalThis.fetch = mockFetch('ok');
    res = await worker.fetch(REQ('/api/ai', 'POST', { text: '脑瓜仁儿疼' }), ENV_OK, {});
    j = await res.json();
    t('成功转写', j.normalized === '后脑痛', JSON.stringify(j));

    console.log('\n【4】信息泄露检查');
    res = await worker.fetch(REQ('/api/ai', 'GET'), ENV_OK, {});
    const body = await res.text();
    t('响应不含 api key', !body.includes('SECRET-123'), body.slice(0, 70));
    t('响应不含 base_url', !body.includes('deepseek.com'));
    j = JSON.parse(body);
    t('回显模型名便于确认', j.model === 'deepseek-chat');

    console.log('\n【5】上游超时（挂起 3s，worker timeout 800ms）');
    globalThis.fetch = mockFetch('timeout');
    const t0 = Date.now();
    res = await worker.fetch(REQ('/api/ai', 'POST', { text: '头疼' }), ENV_OK, {});
    const cost = Date.now() - t0;
    j = await res.json();
    t('超时后降级而非报错', j.ok === true && j.normalized === null);
    t('确实提前返回', cost < 2500, `${cost}ms`);
    t('未泄露上游细节', j.reason === 'upstream_failed', j.reason);

    console.log('\n【6】上游 5xx（响应体含 key）');
    globalThis.fetch = mockFetch('error');
    res = await worker.fetch(REQ('/api/ai', 'POST', { text: '头疼' }), ENV_OK, {});
    const body2 = await res.text();
    j = JSON.parse(body2);
    t('返回降级结果', j.normalized === null);
    t('不回传上游错误内容', !body2.includes('SECRET-123'), body2.slice(0, 70));

    console.log('\n【7】模型越界输出');
    globalThis.fetch = mockFetch('hallucinate');
    res = await worker.fetch(REQ('/api/ai', 'POST', { text: '头疼' }), ENV_OK, {});
    j = await res.json();
    t('含「处方」的越界输出被丢弃', j.normalized === null, JSON.stringify(j));

    globalThis.fetch = mockFetch('toolong');
    res = await worker.fetch(REQ('/api/ai', 'POST', { text: '头疼' }), ENV_OK, {});
    j = await res.json();
    t('超长输出被丢弃', j.normalized === null);

    console.log('\n【8】限流（RATE_LIMIT_MAX=3，连发 6 次）');
    globalThis.fetch = mockFetch('ok');
    const envLimit = { ...ENV_OK, RATE_LIMIT_MAX: '3' };
    let limited = 0;
    for (let i = 0; i < 6; i++) {
      const r = await worker.fetch(REQ('/api/ai', 'POST', { text: '头疼' },
        { 'CF-Connecting-IP': '9.9.9.9' }), envLimit, {});
      const jj = await r.json();
      if (jj.reason === 'rate_limited') limited++;
    }
    t('超出次数被限流', limited === 3, `6 次中限流 ${limited} 次`);

    console.log('\n【9】CORS 白名单');
    const envCors = { ...ENV_OK, CORS_ORIGIN: 'https://ok.pages.dev' };
    res = await worker.fetch(
      REQ('/api/ai', 'OPTIONS', null, { Origin: 'https://ok.pages.dev' }), envCors, {});
    t('白名单内来源放行',
      res.headers.get('Access-Control-Allow-Origin') === 'https://ok.pages.dev');

    res = await worker.fetch(
      REQ('/api/ai', 'OPTIONS', null, { Origin: 'https://evil.com' }), envCors, {});
    t('白名单外来源被挡',
      res.headers.get('Access-Control-Allow-Origin') === null,
      `实际 ${res.headers.get('Access-Control-Allow-Origin')}`);

    console.log('\n【10】输入校验与其他路径');
    res = await worker.fetch(REQ('/api/ai', 'POST', { text: 123 }), ENV_OK, {});
    t('非字符串输入报 400', res.status === 400, `实际 ${res.status}`);
    res = await worker.fetch(REQ('/api/ai', 'DELETE'), ENV_OK, {});
    t('不支持的方法报 405', res.status === 405, `实际 ${res.status}`);
    res = await worker.fetch(REQ('/other', 'GET'), ENV_OK, {});
    t('未知路径报 404', res.status === 404, `实际 ${res.status}`);

    console.log('\n【11】Anthropic 协议分支');
    globalThis.fetch = async (url, opts) => {
      if (!String(url).endsWith('/messages')) throw new Error('wrong url: ' + url);
      if (opts.headers['x-api-key'] !== 'sk-SECRET-123') throw new Error('missing x-api-key');
      return new Response(JSON.stringify({
        content: [{ type: 'text', text: '咽痛' }],
      }), { status: 200 });
    };
    res = await worker.fetch(REQ('/api/ai', 'POST', { text: '嗓子疼' }),
      { ...ENV_OK, LLM_API_STYLE: 'anthropic', LLM_BASE_URL: 'https://api.anthropic.com/v1' }, {});
    j = await res.json();
    t('anthropic 分支可解析', j.normalized === '咽痛', JSON.stringify(j));
  } finally {
    globalThis.fetch = real;
  }

  console.log('\n' + '='.repeat(60));
  console.log(`结果：${pass} 通过 / ${fail} 失败`);
  process.exit(fail ? 1 : 0);
}

run();