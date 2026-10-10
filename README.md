# 知源问病 · 中医辨证问诊

> 望闻问切四诊合参，辨证论治。标准对标**中医执业医师资格考试**，
> 并更进一步——考试只考「是什么」，这里要说清「为什么是这个证、为什么用这个方、为什么是这个穴」。

**⚠️ 本项目输出的是中医辨证思路与健康建议，不构成处方，不能替代执业医师面诊。用药前须经执业中医师复核签字。**

---

## ⬇️ 下载使用

### 最省事：下载即用（180 KB，解压双击 `index.html`）

**👉 [zhiyuan-wenbing-v1.0.zip](https://github.com/zejunzhou69-ux/zhiyuan-wenbing/releases/download/v1.0.0/zhiyuan-wenbing-v1.0.zip)**

- 不需要装 Python，**不需要联网**，不需要注册
- 解压后**双击 `index.html`** 就在浏览器打开
- 数据不上传、不存储，全部计算在你自己的设备上完成
- Chrome / Edge / Firefox / Safari 均可，手机浏览器同样适配

包内附 `使用说明.md`，双击即可看。校验：`sha256sum -c SHA256SUMS.txt`

### 其他下载方式

| 想要 | 怎么做 |
|---|---|
| 源码打包 | 仓库右上角 <kbd>Code</kbd> → <kbd>Download ZIP</kbd> |
| 全部版本 | [Releases 页面](https://github.com/zejunzhou69-ux/zhiyuan-wenbing/releases) |
| 克隆源码 | `git clone https://github.com/zejunzhou69-ux/zhiyuan-wenbing.git` |

### 手机上怎么用

手机需要网址，本地包打不开。两种办法：

1. **部署一份到自己的静态托管**（免费）：把 `static/` 目录上传到
   GitHub Pages / Cloudflare Pages / Vercel，手机浏览器打开那个网址
2. **同一 Wi-Fi 下局域网共用**：电脑上执行 `npx serve static`，
   手机浏览器打开 `http://电脑IP:3000`

> 想省事的话，Cloudflare Pages 部署只要一条命令，见文末「部署」。

---

## 两种模式

同一套知识库，两个遍历方向。数据一个字节都没多，区别只是入口和顺序。

### 问诊模式（正向）

站在患者一侧：`症状 → 四诊采集 → 辨证 → 方药 / 针灸 / 推拿 → 调护`

- 15 项问卷按「十问歌 + 望闻问切」排序，一轮只问 2 个
- 急症红旗命中即中止（不给方、不给穴）
- 证据不足会明说「尚缺核心项：xxx」，不硬给结论

### 查阅模式（逆向）

站在学习者/临床一侧：`病 → 证 → 症 → 方 → 穴 → 其他疗法`

| 入口 | 输入 | 输出 |
|---|---|---|
| 按病查 | 咳嗽 | 5 个证型全景：主症、舌脉、病机、**鉴别**、方药、经穴、董氏奇穴、推拿、必须排除项 |
| 按症查 | 口苦 | 哪些病哪些证会出现它 |
| 按方查 | 逍遥散 | 出处/组成/方义/类方鉴别/加减/禁忌 + 哪些证型用它 |
| 按穴查 | 太冲 | 定位/解剖层次/深度上限/禁忌 + 哪些证型用得上 |
| 其他疗法 | — | 艾灸·拔罐·刮痧·刺络放血·灯火灸·药膳食疗·足浴·八段锦 |

---

## 知识库规模

| | 数量 |
|---|---|
| 病种 / 证型 | 35 / 125 |
| 方剂（含方义、类方鉴别、加减） | 55 |
| 中药（性味归经、功效、配伍、毒性） | 170 |
| 经穴（定位、解剖层次、针刺深度上限） | 120 |
| 董氏奇穴（杨维杰派，独立通道） | 理论 5 · 穴名层 28 · 定位待原书 |
| 推拿手法 / 病种方案 | 30 / 20 |
| 急症红旗 / 必转诊红旗 | 15 / 12 |

---

## 两条针灸通道（物理隔离）

「董氏奇穴和传统穴位都要有，要分开来」——这是架构级约束，不是输出措辞。

| | 通道一：十四经穴 | 通道二：董氏奇穴 |
|---|---|---|
| 数据 | `data/acupoints.json` | `data/dongshi.json` |
| 检索 | `searchAcupoint()` | `searchDongshi()` |
| 方案字段 | `acupoint_meridian` | `dongshi_channel` |
| 流派 | 经络归属 | `lineage: yangweijie`（可切 `yqj`/`dong`） |

`assertChannelSeparation()` 自检，串了直接抛错。

**董氏奇穴定位当前锁住**：穴名层已入库（系统认识它们、能进配穴思路），
但定位与针刺深度留空，等原书 PDF。理由是各派定位有分歧，凭二手资料写定位会造成误针。

---

## 安全层（独立于任何 AI）

- **15 条急症红旗**：胸痛/心梗、呼吸困难、意识障碍、大出血、颅内出血、**疑似中风**、抽搐、急腹症、过敏性休克、烧烫伤、婴幼儿急症、孕产急症、骨折、电解质紊乱、自伤风险
- **两条硬规则**（不依赖关键词匹配）：
  - **孕期任何腹痛 → 直接按孕产急症处理**（异位妊娠破裂以腹痛为主诉，关键词会漏）
  - **婴儿精神状态改变 → 立即儿科急诊**
- **12 类必转诊红旗**
- **中药安全**：十八反、十九畏、妊娠禁忌、毒性药剂量红线、先煎后下包煎烊化（**不给煎法的方视为不完整**）、中西药相互作用
- **针刺安全**：睛明/风池/百会/膻中/背俞穴等高危穴位深度上限逐穴标注

---

## 运行

### 方式一：静态版（推荐，零成本）

纯静态，无后端、无 API key、无数据上传。直接打开 `static/index.html` 即可，
或部署到 Cloudflare Pages / 任何静态托管。

### 方式二：本地 Python 版（可接大模型）

```bat
启动知源问病.bat
```

浏览器打开 `http://127.0.0.1:8787`。

在 `config/config.json` 填 `llm.base_url` / `api_key` / `model` 即可接任意
OpenAI 兼容接口（智谱 / DeepSeek / Kimi / 本地 Ollama）。**不填也能完整使用**，
只是少了模型的口语理解。

---

## 可选：让静态版也懂口语（Cloudflare Worker）

静态站不能内置 API key（会公开暴露），所以用一层薄代理：

```
浏览器 ──► Cloudflare Worker ──► 大模型
              （key 存在 Cloudflare 环境变量里）
```

**Worker 只做一件事：把口语转成规范术语**（"脑瓜仁儿疼" → "后脑痛"）。
辨证结论、方剂组成、穴位定位、安全警告**一律仍由静态端规则引擎产出**，
模型不参与决策 —— 这样即使模型胡说，也不会污染知识与安全判断。

```bash
npx wrangler secret put LLM_API_KEY
npx wrangler secret put LLM_BASE_URL
npx wrangler secret put LLM_MODEL
npx wrangler deploy --config wrangler-worker.jsonc
```

不部署 Worker 也能用，前端探测不到 `/api/ai` 就自动走纯规则，**功能不受影响**。

---

## 开发

```bash
# 数据体检
python tools/check_json.py

# 深度审计（交叉引用完整性 + 安全规则误报漏报）
python tools/audit.py

# 全链路自检
python tools/demo.py

# 静态引擎测试（Node）
node tools/test_web.mjs

# 静态站端到端（模拟浏览器）
node tools/e2e_web.mjs

# 提交前安全核验（防泄漏教材原文与密钥）
python tools/precommit_check.py
```

### 扩充知识库

`data/*.json` 都是 UTF-8 无 BOM，直接改或追加。

新条目**必须**带 `verified` 字段；`verified: false` 的条目不得用于输出结论 ——
这是防止「凭记忆写知识」的第一道闸。处方组成、剂量、穴位定位这三类尤其不要凭印象写，
写错了会直接造成实际伤害。

扩充后依次跑：

```bash
python tools/check_json.py    # 语法
python tools/audit.py         # 引用完整性
python tools/build_bundle.py  # 重新打包给静态版
node tools/test_web.mjs       # 回归
```

### 教材入库（可选）

```bash
python tools/ingest_textbook.py "教材目录" --batch
```

产出 `knowledge/textbook.jsonl`，带 `《书名》章节 p页码` 供引用溯源。
**该文件已列入 `.gitignore`，不要提交**（教材原文涉及版权）。

董氏奇穴：

```bash
python tools/ingest_dongshi.py "董氏奇穴原书.pdf" --lineage yangweijie --book "书名"
```

---

## 目录

```
├─ static/              静态站（部署用）
│  ├─ index.html
│  ├─ css/app.css
│  └─ js/{bundle,kb,safety,diagnose,inverse,app}.js
├─ worker/index.js      可选 AI 代理
├─ data/*.json          知识库（源数据）
├─ engine/*.py          Python 版引擎
├─ web/                 Python 版服务端
├─ tools/               构建、审计、测试、入库
└─ knowledge/书目清单.md 收录范围与优先级
```

---

## 已知边界

1. **董氏奇穴定位未录**，当前只给配穴思路。
2. **切诊（脉诊）远程不可得**，只能请用户描述快慢浮沉有力无力，不凭空给脉象。
3. **方剂组成/剂量未逐条对照教材**（多数 `verified: false`），输出时标注「组成待核对教材」，
   且始终附「剂量须执业医师核定」。
4. 病种覆盖 35/59（中医内科学），缺口见 `data/gap.json`。
5. 红旗关键词表不是医学全集，**不能替代医生判断**。设计目标是「宁可多问一句，不可漏拦」。

---

## 免责声明

本项目为**学习与健康咨询参考工具**，不是医疗器械，不提供诊断，不开处方。
使用者须为具备资质的人员或在其指导下使用。知识内容为教材通行表述的整理，
**未经逐条核对原文，不得直接用于临床**。

作者不对基于本工具输出的任何医疗决定承担责任。使用即视为接受此声明。
