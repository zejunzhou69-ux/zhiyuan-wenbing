# AI 接入配置（可选）

默认情况下**不需要任何配置**，本应用以纯规则引擎运行，功能完整。

本文说明如何额外接入大模型，用来增强「口语理解」能力。

---

## 一、这个 AI 到底做什么、不做什么

这是最重要的一节，请先读完再决定要不要接。

**会做（仅此一件）**

把用户随手打的口语，转写成规范的中医术语短句，再交给规则引擎。

| 用户输入 | 转写为 |
|---|---|
| 脑瓜仁儿疼 | 后脑痛 |
| 窜稀 | 泄泻 |
| 没胃口 | 不思饮食 |
| 心慌慌 | 心悸 |
| 睡觉老出汗 | 盗汗 |

**绝不会做**

- 不给辨证结论
- 不开方、不列药物组成
- 不给穴位定位与针刺深度
- 不做安全判断与急症拦截

以上全部由前端内置的规则引擎产出，**模型不参与决策**。

这是刻意的架构设计：即使模型胡说或被诱导，也污染不了知识与安全判断。
Worker 里还有一道兜底——模型输出里只要出现「处方」「建议服用」「诊断为」等词，
直接丢弃并退回原文。

---

## 二、为什么需要 Worker（不能把 Key 写进前端）

把 API Key 写进前端代码 = 公开贴在墙上，任何人打开开发者工具就能拿走你的 Key，
然后疯狂消耗你的额度。

所以中间加一层 Cloudflare Worker：Key 存在 Cloudflare 的加密环境变量里，
不进代码、不进 Git 仓库、不进任何静态文件。

```
浏览器  ──POST /api/ai──▶  Worker  ──带 Key──▶  大模型 API
   ▲                        │
   └──只拿规范化后的短句──────┘
        （全程不接触 Key）
```

---

## 三、部署步骤

```powershell
# 1. 装 wrangler（若未装）
npm i -g wrangler

# 2. 登录 Cloudflare
wrangler login

# 3. 进入项目目录
cd 知源问病

# 4. 写入三个必需变量（Key 只进 Cloudflare，不进代码）
wrangler secret put LLM_API_KEY     # 你的 API Key
wrangler secret put LLM_BASE_URL    # 例如 https://api.deepseek.com/v1
wrangler secret put LLM_MODEL       # 例如 deepseek-chat

# 5. 可选：限定 CORS 来源（强烈建议）
wrangler secret put CORS_ORIGIN    # 例如 https://zhiyuan-wenbing.pages.dev

# 6. 部署
wrangler deploy
```

部署后访问 `https://你的worker域名/api/ai`，应返回：

```json
{"ok":true,"enabled":true,"style":"openai","model":"deepseek-chat"}
```

`enabled:true` 即接好了。注意该接口**不会**返回 Key 或 base_url。

---

## 四、各厂商配置对照表

绝大多数厂商都兼容 OpenAI 的 `/chat/completions` 协议，
填 `LLM_BASE_URL` 时**不要**在末尾加 `/chat/completions`，Worker 会自己拼。

| 厂商 | LLM_BASE_URL | LLM_MODEL 示例 | 协议 |
|---|---|---|---|
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` | openai |
| 智谱 GLM | `https://open.bigmodel.cn/api/paas/v4` | `glm-4-flash` | openai |
| 通义千问 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus` | openai |
| Kimi / 月之暗面 | `https://api.moonshot.cn/v1` | `moonshot-v1-8k` | openai |
| 腾讯混元 | `https://api.hunyuan.cloud.tencent.com/v1` | `hunyuan-turbo` | openai |
| 百度千帆 | `https://qianfan.baidubce.com/v2` | `ernie-4.5-turbo-128k` | openai |
| 硅基流动 | `https://api.siliconflow.cn/v1` | `Qwen/Qwen2.5-7B-Instruct` | openai |
| OpenRouter | `https://openrouter.ai/api/v1` | `openai/gpt-4o-mini` | openai |
| OpenAI 官方 | `https://api.openai.com/v1` | `gpt-4o-mini` | openai |
| 本地 Ollama | `http://127.0.0.1:11434/v1` | `qwen2.5:7b` | openai |
| Anthropic 原生 | `https://api.anthropic.com/v1` | `claude-sonnet-4-5` | **anthropic** |

**Anthropic 需要额外设置协议**：

```powershell
wrangler secret put LLM_API_STYLE   # 填 anthropic
```

其余厂商不用管这个变量（默认 `openai`）。

**本地 Ollama 注意**：Key 填任意非空字符串即可（如 `ollama`）。
但 Worker 跑在 Cloudflare 边缘，访问不到你家里的 `127.0.0.1`，
本地模型需要用 ngrok / cloudflared 之类的内网穿透工具暴露为公网地址，
再把那个地址填进 `LLM_BASE_URL`。

---

## 五、可选参数

| 变量 | 默认 | 说明 |
|---|---|---|
| `LLM_API_STYLE` | `openai` | 协议风格，`openai` 或 `anthropic` |
| `LLM_TEMPERATURE` | `0.1` | 越低越稳定。术语规范化建议 0～0.3 |
| `LLM_TIMEOUT_MS` | `15000` | 上游超时。超时后自动退回规则引擎 |
| `CORS_ORIGIN` | 不设 | 限定调用来源，不设则任何站点都能调用 |
| `RATE_LIMIT_MAX` | `20` | 每 IP 每分钟请求数上限 |

---

## 六、安全说明（请如实理解，不要高估）

**已经做到的**

- Key 只存 Cloudflare 环境变量，不进代码、不进仓库、不进静态文件
- 健康检查接口不回显 Key，也不回显 base_url
- 上游报错时不把上游响应原文回传浏览器（可能含账号信息）
- 请求超时上限 15 秒，上游卡死不会拖住页面
- 模型输出超长或含「处方」类内容时直接丢弃
- 可用 `CORS_ORIGIN` 限定来源
- 已通过 24 项自动化测试（见 `tools/test_worker.mjs`）

**已知局限（如实说明，不假装很强）**

- **内存限流挡不住分布式刷**：Worker 跑在边缘运行时，实例随时回收，
  内存 Map 不共享也不持久，只能挡住单实例上的突发。
  个人小额 Key 够用；若要公开运营，请接 Cloudflare Rate Limiting 或 KV。
- **前端仍会尝试请求 `/api/ai`**：不部署 Worker 时该请求失败，
  自动退回纯规则，功能不受影响，但浏览器控制台会有一条红色报错。属正常现象。
- **模型成本由你承担**：如果有人用你的 Worker，消耗的是你的额度。
  强烈建议设置 `CORS_ORIGIN` + `RATE_LIMIT_MAX`。

---

## 七、本地测试

```powershell
node tools/test_worker.mjs
```

用 mock 上游测试，不会真的调用大模型、不会产生费用。
覆盖：CORS 预检、未配置降级、上游超时、上游报错、越界输出拦截、
限流、CORS 白名单、Key 不泄露、Anthropic 协议分支。

---

## 八、常见问题

**Q：部署了 Worker 但前端仍显示「规则引擎」？**
A：前端启动时探测一次 `/api/ai`。请确认：
① 三个 secret 都已设置（`wrangler secret list` 查看）；
② `CORS_ORIGIN` 与实际页面域名一致；
③ 刷新页面重试。

**Q：能不能不部署 Worker，只在本地接大模型？**
A：可以。本地版（`启动知源问病.bat`）直接读 `config/config.json`，不经过 Worker。
参考 `config/config.json` 里的 `llm_examples`。

**Q：模型会不会给出错误的辨证结论？**
A：不会。模型只输出术语短句，辨证结论完全由规则引擎从知识库检索得出。
换句话说，即使把模型换成随机字符串输出，辨证结果也不变（只会导致口语理解失效）。

**Q：为什么把模型换成胡说八道也不会污染辨证？**
A：模型的输出会经过长度检查、越界词拦截，然后才交给规则引擎；
若被拦截则直接用用户原文。规则引擎读的是知识库，不读模型结论。
