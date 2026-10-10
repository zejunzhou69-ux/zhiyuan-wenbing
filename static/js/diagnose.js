/* 知源问病 · 四诊采集与辨证引擎（JS 版）
 * 与 Python 版 engine/diagnose.py 行为一致。
 * 正向：症 → 四诊采集 → 证 → 方药/针灸/推拿
 * 方案里 acupoint_meridian 与 dongshi_channel 是两个独立字段，永不合并。
 */
(function (global) {
  'use strict';

  const QUESTIONS = [
    { key: 'chief', stage: '问', q: '最不舒服的地方是哪里？什么时候开始的？' },
    { key: 'cold_heat', stage: '问', q: '怕冷还是怕热？手脚是凉还是热？' },
    { key: 'sweat', stage: '问', q: '出汗吗？是自汗（不动也出）、盗汗（睡着才出）、还是刚才发热出的汗？' },
    { key: 'head_body', stage: '问', q: '头和身上哪里疼？（后脑、太阳穴、头重、关节、腰…）是一阵一阵还是一直疼？' },
    { key: 'stool', stage: '问', q: '大便怎么样？一天几次、成形还是稀、什么颜色、有没有带血？' },
    { key: 'urine', stage: '问', q: '小便怎么样？次数多不多、颜色黄不黄、有没有泡沫？夜里起来几次？' },
    { key: 'diet', stage: '问', q: '胃口怎么样？吃冷的是舒服还是难受？有没有反酸、嗳气、恶心？' },
    { key: 'chest_abdomen', stage: '问', q: '胸口和肚子有没有胀痛、堵闷？按着疼还是不按也疼？' },
    { key: 'sleep', stage: '问', q: '睡觉怎么样？入睡难还是容易醒、多梦还是整夜不睡？' },
    { key: 'emotion', stage: '问', q: '心情怎么样？有没有烦、闷、爱叹气、压力大？情绪会影响症状吗？' },
    { key: 'voice', stage: '闻', q: '说话声音有力还是懒洋洋？咳嗽吗、痰多不多、什么颜色？' },
    { key: 'tongue', stage: '望', q: '请对着镜子看舌头：舌色（淡白/正常/红/深红）、舌苔（薄白/白厚/黄/黄厚/没苔）、有没有裂纹和齿痕。拍照发我也行。' },
    { key: 'pulse', stage: '切', q: '脉象我这里摸不到，只能请你描述：手腕脉搏跳得快还是慢？轻按摸得到（浮）还是要用力按才摸到（沉）？有力还是无力？' },
    { key: 'history', stage: '问', q: '以前得过什么病？现在在吃什么药（中西药都算）？有没有手术或外伤？' },
    { key: 'female', stage: '问', q: '月经怎么样？周期准不准、经量多少、有无痛经和血块？带下正常吗？', only: 'female' },
  ];

  const CORE_KEYS = ['chief', 'cold_heat', 'stool', 'urine', 'diet', 'sleep', 'tongue'];

  // 字段识别关键词，顺序即优先级（越靠前越具体）
  const FIELD_KEYWORDS = {
    tongue: ['舌', '苔'],
    pulse: ['脉', '浮', '沉'],
    sweat: ['汗'],
    urine: ['小便', '尿'],
    stool: ['大便', '拉', '便', '屎'],
    sleep: ['睡', '失眠', '多梦'],
    emotion: ['心情', '情绪', '烦', '闷', '压力', '焦虑', '抑郁'],
    voice: ['声音', '说话', '咳', '痰'],
    female: ['月经', '经期', '痛经', '带下', '例假'],
    diet: ['胃口', '吃', '饭', '饮食', '不想吃'],
    chest_abdomen: ['胸口', '心口', '胸闷', '腹胀', '肚子胀', '胀痛'],
    history: ['以前', '病史', '吃药', '手术', '外伤', '过敏', '住院'],
    cold_heat: ['怕冷', '怕热', '手脚', '冷', '热', '凉', '不渴', '口渴', '畏寒'],
    head_body: ['头', '脑', '太阳穴', '疼', '痛', '腰', '关节', '身'],
  };

  function applicable(qs, profile) {
    profile = profile || {};
    return qs.filter((q) => !(q.only === 'female' && profile.sex !== 'female'));
  }

  function inferField(text, profile) {
    profile = profile || {};
    let best = null, bestN = 0;
    for (const key of Object.keys(FIELD_KEYWORDS)) {
      if (key === 'female' && profile.sex !== 'female') continue;
      let n = 0;
      for (const w of FIELD_KEYWORDS[key]) if (String(text).indexOf(w) >= 0) n++;
      if (n > bestN) { best = key; bestN = n; }
    }
    return best;
  }

  class FourDiagSession {
    constructor(profile) {
      this.profile = profile || {};
      this.collected = {};
    }

    completeness() {
      const qs = applicable(QUESTIONS, this.profile);
      const total = qs.length;
      const done = qs.filter((q) => this.collected[q.key] !== undefined).length;
      const missing = qs.filter((q) => this.collected[q.key] === undefined);
      return {
        done: done, total: total,
        percent: total ? Math.round(done / total * 100) : 0,
        missing: missing,
        core_missing: missing.filter((q) => CORE_KEYS.indexOf(q.key) >= 0).map((q) => q.key),
        ready: done >= Math.floor(total * 0.6),
      };
    }

    nextQuestions(n) {
      const pending = applicable(QUESTIONS, this.profile)
        .filter((q) => this.collected[q.key] === undefined);
      pending.sort((a, b) => (CORE_KEYS.indexOf(a.key) >= 0 ? 0 : 1) -
                             (CORE_KEYS.indexOf(b.key) >= 0 ? 0 : 1));
      return pending.slice(0, n || 2);
    }

    record(key, value) { this.collected[key] = value; }

    text() {
      return Object.keys(this.collected).map((k) => k + ' ' + this.collected[k]).join(' ');
    }

    stagesDone() {
      const got = new Set(applicable(QUESTIONS, this.profile)
        .filter((q) => this.collected[q.key] !== undefined).map((q) => q.stage));
      return { '望': got.has('望'), '闻': got.has('闻'), '问': got.has('问'), '切': got.has('切') };
    }
  }

  function inferEightPrinciples(text) {
    const t = String(text || '');
    const r = { '表里': '待补', '寒热': '待补', '虚实': '待补', '阴阳': '待补' };

    if (['怕冷', '恶寒', '喜热', '不渴', '舌淡'].some((k) => t.indexOf(k) >= 0)) r['寒热'] = '寒';
    if (['发热', '怕热', '口渴', '喜冷', '舌红', '便干', '便秘'].some((k) => t.indexOf(k) >= 0)) {
      r['寒热'] = r['寒热'] === '待补' ? '热' : '寒热错杂';
    }
    if (['乏力', '气短', '自汗', '盗汗', '舌淡', '脉弱', '脉细', '神疲']
        .some((k) => t.indexOf(k) >= 0)) r['虚实'] = '虚';
    if (['腹胀', '胀痛', '拒按', '痰多', '苔厚腻', '便秘'].some((k) => t.indexOf(k) >= 0)) {
      r['虚实'] = r['虚实'] === '待补' ? '实' : '虚实夹杂';
    }
    if (['感冒', '着凉', '受凉'].some((k) => t.indexOf(k) >= 0)) r['表里'] = '表';
    if (['久', '长期', '反复', '多年', '老毛病'].some((k) => t.indexOf(k) >= 0)) r['表里'] = '里';

    if (r['寒热'] === '寒' && r['虚实'] === '虚') r['阴阳'] = '阴证';
    else if (r['寒热'] === '热' && r['虚实'] === '实') r['阴阳'] = '阳证';
    return r;
  }

  function rankSyndromes(kb, session, diseaseName) {
    const text = session.text();
    const out = [];
    for (const s of kb.syndromes) {
      if (diseaseName && s.d !== diseaseName) continue;
      const hit = (s.sy || []).filter((w) => w && text.indexOf(w) >= 0);
      const score = hit.length * 2 +
        (diseaseName && s.d === diseaseName ? 1 : 0);
      out.push(Object.assign({}, s, { hit: hit, score: score }));
    }
    out.sort((a, b) => b.score - a.score);
    return out;
  }

  function confidenceOf(sx, session) {
    const c = session.completeness();
    const n = (sx.hit || []).length;
    if (n >= 4 && c.percent >= 75) return ['高', ''];
    if (n >= 3 || c.percent >= 60) return ['中', '尚缺核心项：' + c.core_missing.join('、')];
    if (n >= 1) {
      return ['低', '证据太少，只匹配到 ' + n + ' 项；还缺：' +
        c.missing.slice(0, 5).map((q) => q.key).join('、')];
    }
    return ['低', '尚无可用证据，无法定证'];
  }

  function buildPlan(kb, safety, sxId, session, profile) {
    profile = profile || {};
    const sx = kb.syndrome(sxId);
    if (!sx) return { error: '未找到证型 ' + sxId };

    const formulas = [];
    for (const fid of (sx.fx || [])) {
      const f = kb.formula(fid);
      if (!f) continue;
      const herbNames = extractHerbNames(String(f.herbs || ''));
      formulas.push({
        name: f.name, source: f.source_text || '',
        functions: f.functions || '', indications: f.indications || '',
        herbs: f.herbs || '', meaning: f.formula_meaning || '',
        similar_diff: f.similar_diff || '', modifications: f.modifications || '',
        verified: !!f.verified,
        warnings: safety.checkFormula(f, profile),
        toxicity: safety.herbToxicity(herbNames),
      });
    }

    const meridian = kb.pointsMeridian(sxId).map((p) => ({
      name: p.name, meridian: p.meridian || '',
      location: p.location || '', depth: p.depth_limit || '',
      indications: (p.indications || []).slice(0, 4),
      needling: p.needling || '', contra: p.contraindication || '',
      self_moxa: !!p.self_moxa_safe,
      anatomy: p.anatomy_note || '', channel: 'meridian',
    }));

    const screen = safety.screenProfile(profile);
    return {
      syndrome: {
        id: sxId, name: sx.n || '', disease: sx.d || '', system: sx.sys || '',
        mechanism: sx.me || '', treatment: sx.tx || '',
        tongue: sx.tg || '', pulse: sx.p || '',
        key_symptoms: sx.sy || [],
        home_ok: !!sx.home, severity: sx.sev || '',
      },
      confidence: confidenceOf(sx, session),
      eight: inferEightPrinciples(session.text()),
      formulas: formulas,
      acupoint_meridian: meridian,        // 通道一
      dongshi_channel: kb.pointsDongshi(sxId),  // 通道二（独立）
      tuina: kb.searchTuina(sx.d || '', 2),
      safety: {
        bans: screen.bans, cautions: screen.cautions,
        must_ask: screen.must_ask,
        refer: safety.referFlags(session.text()),
        needling_global: safety.needlingSafety,
      },
      warnings: [sx.wn, sx.nt].filter(Boolean),
    };
  }

  function renderPlan(plan) {
    if (plan.error) return plan.error;
    const s = plan.syndrome;
    const L = [];
    const lvl = plan.confidence[0], why = plan.confidence[1];
    L.push(`【证型】${s.disease} · ${s.name}（${s.system}）｜置信度：${lvl}`);
    if (why) L.push('  └─ ' + why);
    L.push('【八纲】' + JSON.stringify(plan.eight));
    L.push('【病机】' + s.mechanism);
    L.push('【治法】' + s.treatment);
    L.push('【舌脉】' + s.tongue + '｜' + s.pulse);

    if (plan.formulas.length) {
      L.push('\n【方药】');
      for (const f of plan.formulas) {
        const tag = f.verified ? '' : '（组成待核对教材）';
        L.push(`· ${f.name}${tag}　${f.functions}`);
        L.push('  出处：' + f.source);
        L.push('  主治：' + f.indications);
        L.push('  组成：' + f.herbs);
        L.push('  方义：' + f.meaning);
        if (f.similar_diff) L.push('  类方鉴别：' + f.similar_diff);
        for (const w of f.warnings) L.push('  ' + w);
        for (const w of f.toxicity) L.push('  ' + w);
      }
    }

    L.push('\n【针灸 · 通道一：十四经穴】');
    for (const p of plan.acupoint_meridian) {
      L.push(`· ${p.name}（${p.meridian}）`);
      L.push('  定位：' + p.location);
      L.push('  主治：' + p.indications.join('、'));
      L.push('  针刺：' + p.needling + '｜深度上限：' + p.depth);
      if (p.anatomy) L.push('  解剖：' + p.anatomy);
      if (p.contra) L.push('  ⚠️禁忌：' + p.contra);
      if (p.self_moxa) L.push('  🟢 此穴适合家庭艾灸/按揉（针刺仍须专业者）');
    }

    const d = plan.dongshi_channel;
    L.push(`\n【针灸 · 通道二：董氏奇穴（${d.lineage} 派）】`);
    L.push('  ⚠️以上十四经穴与下方董氏奇穴不是同一套体系，请分开理解，不可混为一表。');
    if (d.hint) L.push('  配穴思路：' + d.hint);
    if (d.matches && d.matches.length) {
      L.push('  可考虑穴（按主治方向匹配）：' +
        d.matches.map((m) => `${m.name}（${m.direction}）`).join('、'));
    }
    L.push('  已有定位可输出：' + ((d.location_ready || []).join('、') || '（无）'));
    L.push('  🔒 ' + d.note);
    L.push('  ⛔ 定位未经原书核对，系统不输出董氏奇穴的定位与针刺深度。');

    if (plan.tuina.length) {
      L.push('\n【推拿】');
      for (const t of plan.tuina) {
        L.push(`· ${t.condition}（${t.syndrome_pattern}）等级 ${t.level}`);
        L.push('  首步：' + (t.steps || [''])[0]);
        if (t.home_self_help) L.push('  🏠 家庭可做：' + t.home_self_help);
        L.push('  疗程：' + t.course);
        if (t.cautions) L.push('  注意：' + t.cautions.join('；'));
      }
    }

    if (plan.warnings.length) {
      L.push('\n【本证型安全提示】');
      for (const w of plan.warnings) L.push('  ' + w);
    }

    const sa = plan.safety;
    if (sa.bans.length) {
      L.push('\n【禁用（针对你的情况）】');
      for (const b of sa.bans) L.push('  ⛔ ' + b);
    }
    if (sa.cautions.length) {
      L.push('\n【注意】');
      for (const c of sa.cautions) L.push('  ⚠️ ' + c);
    }
    if (sa.refer.length) {
      L.push('\n【必须先排查的器质性病变】');
      for (const r of sa.refer) {
        L.push(`  ⚠️ ${r.cat}：命中「${r.hit.join('、')}」—— ${r.why}；${r.action}`);
      }
    }

    L.push('\n【免责】以上为中医辨证思路与健康建议，不构成处方，不能替代执业医师面诊。' +
           '用药前须经执业中医师复核签字。');
    return L.join('\n');
  }

  global.FourDiagSession = FourDiagSession;
  global.QUESTIONS = QUESTIONS;
  global.CORE_KEYS = CORE_KEYS;
  global.inferField = inferField;
  global.inferEightPrinciples = inferEightPrinciples;
  global.rankSyndromes = rankSyndromes;
  global.buildPlan = buildPlan;
  global.renderPlan = renderPlan;
})(typeof window !== 'undefined' ? window : globalThis);
