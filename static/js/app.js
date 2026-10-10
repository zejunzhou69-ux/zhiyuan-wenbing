/* 知源问病 · 前端逻辑
 * 纯静态：无后端、无 API key、无数据上传。所有计算在浏览器里完成。
 * 两条链路：
 *   问诊模式 = 症状 → 采集 → 辨证 → 方案
 *   查阅模式 = 病/症/方/穴 → 知识页
 */
(function () {
  'use strict';

  const $ = (id) => document.getElementById(id);
  let kb = null, safety = null, inv = null;
  let sess = null;
  let MODE = 'ask', KIND = 'disease';
  let AI = false;          // Worker 是否可用（只用于「术语规范化」，不参与决策）

  const DISEASES = ['感冒', '咳嗽', '哮病', '喘证', '胸痹', '头痛', '眩晕', '不寐', '心悸',
    '胃痛', '泄泻', '痢疾', '便秘', '腹痛', '胁痛', '黄疸', '鼓胀', '痹证', '腰痛',
    '郁证', '痰饮', '水肿', '淋证', '癃闭', '虚劳', '内伤发热', '消渴', '中风', '遗尿',
    '月经不调', '咽喉肿痛', '口疮', '鼻渊', '小儿积食', '小儿腹泻', '小儿夜啼'];
  const SYMPTOMS = ['口苦', '咽干', '不思饮食', '五更泻', '头重如裹', '自汗', '盗汗',
    '痛经', '便溏', '痰多', '失眠', '头晕', '耳鸣', '口干', '乏力', '怕冷', '潮热'];
  const FORMULAS = ['逍遥散', '柴胡疏肝散', '半夏泻心汤', '补中益气汤', '六味地黄丸',
    '血府逐瘀汤', '温胆汤', '甘麦大枣汤', '半夏白术天麻汤', '酸枣仁汤', '平胃散',
    '二陈汤', '银翘散', '麻黄汤', '龙胆泻肝汤', '天王补心丹', '旋覆代赭汤', '炙甘草汤',
    '温胆汤', '桂枝汤', '小柴胡汤', '大柴胡汤', '半夏厚朴汤', '越鞠丸', '贝母瓜蒌散'];
  const ACUPOINTS = ['合谷', '太冲', '足三里', '三阴交', '内关', '神门', '中脘', '关元',
    '气海', '百会', '风池', '太溪', '涌泉', '丰隆', '肺俞', '肾俞', '委中', '阳陵泉',
    '曲池', '列缺', '天枢', '阴陵泉', '太溪'];

  const TIPS = {
    disease: '输入病名，输出该病完整证谱：每个证型的主症、舌脉、病机、鉴别、方药、经穴、董氏奇穴、推拿。点下面病名可快速填。',
    symptom: '输入症状，输出哪些病哪些证会出现它。⚠️ 这是知识对照，不能据此自诊。',
    formula: '输入方名，输出出处、组成、方义、类方鉴别、加减、禁忌，以及本库中哪些证型用它。',
    acupoint: '输入穴名，输出定位、解剖层次、针刺深度上限、禁忌，以及哪些证型用这个穴。经穴与董氏奇穴分开返回。',
    therapy: '艾灸、拔罐、刮痧、刺络放血、灯火灸、药膳食疗、足浴、八段锦的做法与禁忌。',
  };

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function add(who, text) {
    const d = document.createElement('div');
    d.className = 'msg ' + who;
    d.innerHTML = (who === 'bot' ? '<h4>知源问病</h4>' : '') +
      '<pre>' + esc(text) + '</pre>';
    $('log').appendChild(d);
    window.scrollTo(0, document.body.scrollHeight);
  }

  function setMode(m) {
    MODE = m;
    $('tabAsk').className = m === 'ask' ? 'on' : '';
    $('tabLook').className = m === 'look' ? 'on' : '';
    $('modeDesc').textContent = m === 'ask' ? '症 → 辨证 → 方药针灸推拿' : '病 → 证 → 症 → 方 → 穴';
    $('setup').className = m === 'ask' ? 'card' : 'card hidden';
    $('lookup').className = m === 'look' ? 'card' : 'card hidden';
    $('askComposer').className = m === 'ask' ? 'composer' : 'composer hidden';
    $('progWrap').style.display = m === 'ask' ? 'block' : 'none';
    if (m === 'look') setKind(KIND);
  }

  function setKind(k) {
    KIND = k;
    document.querySelectorAll('.kind').forEach((b) => {
      b.className = b.dataset.k === k ? 'kind on' : 'kind';
    });
    const map = { disease: DISEASES, symptom: SYMPTOMS, formula: FORMULAS,
                  acupoint: ACUPOINTS, therapy: [] };
    const ph = {
      disease: '输入病名，如：咳嗽',
      symptom: '输入症状，如：口苦',
      formula: '输入方名，如：逍遥散',
      acupoint: '输入穴名，如：太冲',
      therapy: '点「查」看全部其他疗法',
    };
    $('q').placeholder = ph[k];
    $('kindTip').textContent = TIPS[k];
    const box = $('chips');
    box.innerHTML = '';
    (map[k] || []).forEach((w) => {
      const s = document.createElement('span');
      s.className = 'chip';
      s.textContent = w;
      s.onclick = () => { $('q').value = w; lookup(); };
      box.appendChild(s);
    });
  }

  // ------------------------------------------------------------ 查阅
  function lookup() {
    const t = $('q').value.trim();
    if (!t && KIND !== 'therapy') { add('bot', '请输入要查的内容。'); return; }
    let out;
    try {
      if (KIND === 'disease') out = renderDisease(inv.byDisease(t));
      else if (KIND === 'symptom') out = renderSymptom(inv.bySymptom(t));
      else if (KIND === 'formula') out = renderFormula(inv.byFormula(t));
      else if (KIND === 'acupoint') out = renderAcupoint(inv.byAcupoint(t));
      else out = renderTherapy();
    } catch (e) {
      out = '查询出错：' + e.message;
    }
    add('bot', out);
  }

  // ------------------------------------------------------------ 可选 AI
  // 只做一件事：把口语转成规范术语，交给规则引擎。
  // 辨证、方药、穴位、安全警告全部仍由规则引擎产出，模型不参与决策。
  async function probeAI() {
    try {
      const r = await fetch('/api/ai', { method: 'GET' });
      if (!r.ok) return false;
      const j = await r.json();
      return !!(j && j.enabled);
    } catch (e) {
      return false;   // 没有 Worker / 网络不通 → 纯规则，功能完整
    }
  }

  async function normalize(text) {
    if (!AI) return text;
    try {
      const r = await fetch('/api/ai', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text }),
      });
      if (!r.ok) return text;
      const j = await r.json();
      // normalized 为 null 表示 Worker 没配 key 或调用失败，用原文
      return (j && typeof j.normalized === 'string' && j.normalized) ? j.normalized : text;
    } catch (e) {
      return text;
    }
  }

  // ------------------------------------------------------------ 问诊
  function start() {
    sess = new FourDiagSession({
      sex: $('sex').value,
      age: parseInt($('age').value || '30', 10),
      pregnant: $('preg').value === '1',
      liver_kidney: $('lk').value === '1',
      medications: $('meds').value ? [$('meds').value] : [],
    });
    $('setup').style.display = 'none';
    add('bot',
      '说说你的症状，用大白话就行，专业的术语不用管。\n\n' +
      '我会一次问两个问题；说不出就答「不知道」，我不会替你编。\n\n' +
      '⚠️ 急症会直接拦下让你去医院——这类误诊的代价远大于多问一句。');
  }

  function askReply(text) {
    const blk = safety.emergencyBlock(text, sess.profile);
    if (blk) return emergencyReply(blk);

    // 问诊的第一问就是「最不舒服的地方」，所以第一条输入无条件当主诉。
    // 不能只靠 inferField ——「后脑勺疼」会被判成 head_body，chief 就空了，
    // 而病种匹配的权重恰恰依赖 chief。
    const firstChief = !sess.collected.chief;
    if (firstChief) sess.record('chief', text);

    const field = inferField(text, sess.profile);
    if (field) sess.record(field, text);
    else if (!firstChief) {
      sess.record('chief', ((sess.collected.chief || '') + ' ' + text).trim());
    }

    const c = sess.completeness();
    const disease = (() => {
      const m = kb.matchDisease(sess.text(), sess.collected.chief || '');
      return m.length ? m[0].d.name : null;
    })();

    if (c.ready) {
      const cands = rankSyndromes(kb, sess, disease);
      if (cands.length && cands[0].score > 0) {
        return renderPlan(buildPlan(kb, safety, cands[0].id, sess, sess.profile));
      }
      return '已采集 ' + c.done + '/' + c.total + ' 项，但现有信息不足以定证。\n' +
             '还缺关键项：' + c.missing.slice(0, 3).map((q) => q.q).join('\n') + '\n补齐后我再辨。';
    }

    const qs = sess.nextQuestions(2);
    const L = ['已采集 ' + c.done + '/' + c.total + ' 项（' + c.percent + '%）。'];
    if (disease) L.push('初步看病种在「' + disease + '」这一类，先往下问。');
    L.push('', '本次请你答两个：');
    qs.forEach((q, i) => L.push((i + 1) + '. ' + q.q));
    L.push('', '（不是考你，是用来区分证型的关键信息；说不出就答「不知道」，我不会替你编。）');
    return L.join('\n');
  }

  function send() {
    const inp = $('inp');
    const t = inp.value.trim();
    if (!t || !sess) { if (!sess) add('bot', '请先点「开始问诊」并填基本信息。'); return; }
    inp.value = '';
    add('me', t);
    const c = sess.completeness();
    $('bar').style.width = c.percent + '%';
    $('meta').textContent = '四诊采集 ' + c.done + '/' + c.total + '（' + c.percent + '%）';

    if (AI) {
      // AI 只做术语规范化；红旗扫描先用原文做一次，避免延迟漏掉急症
      const urgent = safety.emergencyBlock(t, sess.profile);
      if (urgent) { add('bot', emergencyReply(urgent)); return; }
      $('mode').textContent = 'AI 规范化中…';
      normalize(t).then((norm) => {
        const out = askReply(norm === t ? t : t + '（' + norm + '）');
        $('mode').textContent = '规则引擎 + AI 辅助';
        add('bot', out);
      });
      return;
    }
    add('bot', askReply(t));
  }

  // ------------------------------------------------------------ 启动
  async function init() {
    try {
      kb = await loadKB();
    } catch (e) {
      $('log').innerHTML = '<div class="msg bot"><h4>加载失败</h4><pre>' +
        esc('知识库加载失败：' + e.message) + '</pre></div>';
      return;
    }
    safety = new Safety(kb);
    inv = new Inverse(kb);
    setInverseKB(kb);

    // 通道自检：串了直接抛错，不静默通过
    for (const id of Object.keys(kb.sById).slice(0, 200)) {
      KnowledgeBase.assertChannelSeparation(kb.pointsMeridian(id),
                                            kb.pointsDongshi(id).matches);
    }

    const st = kb.stats();
    $('statsLine').textContent =
      `知识库：${st['病种']} 病 · ${st['证型']} 证型 · ${st['方剂']} 方 · ${st['中药']} 药 · ` +
      `经穴 ${st['经穴']}（董氏奇穴独立通道，流派 ${kb.dongshiLineage}）· ` +
      `推拿 ${st['推拿手法']} 手法 · 急症红旗 ${st['红旗']} 条`;
    $('meta').textContent = '未开始';

    // 探测可选 AI（Worker）。没有就用纯规则，功能完全一样。
    AI = await probeAI();
    $('mode').textContent = AI ? '规则引擎 + AI 辅助' : '规则引擎';

    setMode('ask');
  }

  window.switchMode = setMode;
  window.setKind = setKind;
  window.lookup = lookup;
  window.start = start;
  window.send = send;

  $('inp').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
  });
  $('q').addEventListener('keydown', (e) => { if (e.key === 'Enter') lookup(); });

  init();
})();
