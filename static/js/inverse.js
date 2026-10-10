/* 知源问病 · 逆向检索（JS 版）
 * 同一套数据的另一个遍历方向：病→证→症→方→穴→其他疗法。
 * 与 Python 版 engine/inverse.py 保持一致。
 */
(function (global) {
  'use strict';

  // 其他疗法：知识陈述，不是处方
  const OTHER_THERAPY = [
    { name: '艾灸法', category: '温通类',
      principle: '以艾绒燃烧产生的温热刺激作用于腧穴，温通经络、行气活血、扶阳固本。',
      indications: ['虚寒证（畏寒肢冷、脘腹冷痛）', '阳虚证（阳痿、宫寒、五更泻）',
        '慢性虚损性疾病（久咳、久泻、疲劳）', '寒痹（关节冷痛、遇寒加重）',
        '气血不足（面色少华、易感冒、贫血辅助）'],
      methods: ['温和灸：艾条距皮肤2–3cm，局部温热不烫，每穴15–20分钟',
        '悬灸：艾条悬于穴上，灸感以温热为度',
        '隔姜灸：生姜切片扎孔置穴，上置艾炷，温中散寒力强',
        '隔盐灸（神阙）：食盐填脐，上置艾炷，温阳固脱，用于虚寒性腹痛腹泻',
        '隔附子饼灸：附子研末制饼，温阳力强，用于阳虚证，须医师指导'],
      cautions: ['⚠️实热证、阴虚火旺者禁灸（虚火上炎者灸之更甚，如口疮、咽痛、失眠宜灸涌泉引火归元）',
        '⚠️面部、大血管处、孕妇腰腹部禁灸',
        '⚠️施灸中防烫伤：艾条距皮肤不可过近，糖尿病周围神经病变者感觉迟钝，须格外小心',
        '灸后不立即洗澡、不吹冷风，饮温水',
        '施灸宜避开空腹、过饱、疲劳、醉酒时'],
      verified: true },
    { name: '拔罐法', category: '泻实类',
      principle: '以罐吸附于体表，造成局部负压与皮下瘀血，疏通经络、行气活血、消肿止痛。',
      indications: ['风寒湿痹（关节痛、腰肌劳损）', '肌肉紧张酸痛', '痤疮（背部）',
        '感冒受寒（背部拔罐）', '局部气血滞滞'],
      methods: ['走罐：在痛处往返移动，适合大面积肌肉酸痛',
        '闪罐：罐快速吸拔数次，适合受寒',
        '留罐：吸附5–10分钟，适合点状痛处',
        '刺络拔罐：先用三棱针点刺再拔罐，泻热活血（须专业者操作）'],
      cautions: ['⚠️皮肤破损、炎症、皮肤病处禁拔',
        '⚠️孕妇腰腹部禁拔',
        '⚠️大血管处（颈动脉窦、腋动脉、股动脉处）、关节骨突处禁拔',
        '⚠️发热、极度虚弱、严重贫血、血小板低、正在服抗凝药者禁拔',
        '罐后皮肤有瘀青属正常，但应逐渐消退；若起大水泡需处理',
        '空腹、饭后1小时内不宜'],
      verified: true },
    { name: '刮痧法', category: '泻实类',
      principle: '以刮板在皮肤表面反复刮拭，使局部皮下瘀血外排，疏通经络、祛邪外出。',
      indications: ['风寒感冒（颈肩背部）', '暑湿（胸腹）', '经络阻滞之酸痛', '头面胀痛（颈项侧）'],
      methods: ['项背刮：从颈后正中向两侧肩部刮拭，力度以出痧为度',
        '胸腹刮：沿肋间由内向外',
        '刮痧板边缘垂直皮肤，短距离反复刮，忌大面积重刮'],
      cautions: ['⚠️孕妇腰腹部禁刮', '⚠️经期、皮肤破损、急性传染病发热期禁刮',
        '⚠️刮后不立即洗澡、不吹冷风，喝温水',
        '⚠️「晕刮」（刮后头晕恶心）立即停止，平卧饮糖水',
        '⚠️糖尿病、皮肤病、静脉曲张处慎用'],
      verified: true },
    { name: '刺络放血（点刺）', category: '泻热类',
      principle: '点刺浅表血络挤出少量血液，泻热解毒、活血消肿。',
      indications: ['咽喉肿痛（少商、耳尖）', '高热（十宣、大椎）', '痤疮（耳尖、肺俞）',
        '丹毒、疔疮（局部）', '麦粒肿（耳尖）', '急性扁桃体炎'],
      methods: ['少商点刺：拇指外侧指甲角，点刺出血数滴',
        '耳尖点刺：耳廓最高点，点刺出血',
        '十宣点刺：十指尖端，用于高热、昏迷（急救为主）'],
      cautions: ['⚠️血友病、凝血功能障碍、正在服抗凝药、血小板低者禁',
        '⚠️孕妇、月经期、贫血者禁',
        '⚠️仅限浅表部位，不可深刺',
        '⚠️须由具备资质者操作'],
      verified: true },
    { name: '灯火灸', category: '古法灸',
      principle: '以灯芯草蘸麻油点燃，速点穴位，灯火灼热刺激，用于古法灸治。',
      indications: ['小儿疳积', '腮腺炎（灯火灸耳尖/角孙）', '小儿惊风、脐风',
        '扁桃体炎', '疮疡初起'],
      methods: ['灯火灸：灯芯草蘸油点燃，对准穴位速点即止，局部发出啪声',
        '常用穴：角孙、耳尖、印堂、神阙（脐风）、四缝（疳积）'],
      cautions: ['⚠️必须在家长看护与专业指导下进行',
        '⚠️面部与婴幼儿皮肤娇嫩，灼伤风险高，务必由专业者操作',
        '⚠️已列入部分医院的婴幼儿辅助疗法，非家庭自用'],
      verified: false },
    { name: '药膳食疗', category: '食治类',
      principle: '药食同源。以常用食材的性味归经调养，温和持久，适合慢性调理与病后调养。',
      indications: ['脾胃虚弱（山药、莲子、小米、南瓜）', '湿重（薏苡仁、赤小豆、冬瓜）',
        '肺燥咳嗽（百合、银耳、梨、冰糖）', '气血不足（红枣、当归炖鸡、桂圆）',
        '肝肾不足（枸杞、黑芝麻、桑葚）', '血瘀（山楂、黑木耳）',
        '肝阳上亢（菊花、决明子代茶）', '失眠（酸枣仁粥、莲子心）'],
      methods: ['代茶饮：菊花 3g 沸水泡饮（肝阳上亢、高血压辅助）',
        '山药粥：鲜山药 50g + 小米同煮（脾胃虚弱、儿童厌食）',
        '薏苡仁赤小豆粥：各 30g 煮粥（湿重、水肿）',
        '百合银耳羹：百合 15g 银耳 10g 炖（肺燥干咳）',
        '生姜红枣茶：生姜 3 片 + 红枣 4 枚（寒性腹痛、经期保暖）',
        '陈皮山楂饮：陈皮 3g 山楂 6g 煮水（食积腹胀）'],
      cautions: ['⚠️食疗是调理，不治病，不能替代药物与就医',
        '⚠️药膳也有禁忌：孕妇慎用活血类（山楂大量活血）、阳虚者慎用寒凉（苦瓜、绿茶）',
        '⚠️糖尿病、肾病、高尿酸者用代茶饮须咨询医师（含糖类）',
        '⚠️服药期间忌口：服温补药忌生冷萝卜茶；服清热药忌辛辣'],
      verified: false },
    { name: '足浴引火下行', category: '外治类',
      principle: '温热水泡脚使下肢血流通畅，引火下行、暖足助眠。',
      indications: ['失眠（尤虚火上炎者）', '手足不温', '头痛头晕（肝阳上亢辅助）',
        '口疮、咽喉肿痛（虚火所致）'],
      methods: ['温开水泡脚 15–20 分钟，水温 38–42℃，忌过烫',
        '可加艾叶、生姜（寒证）或盐（简单版）', '睡前1小时泡，配合揉涌泉'],
      cautions: ['⚠️水温不宜过高，糖尿病、下肢动脉硬化、感觉障碍者须先测温',
        '⚠️静脉曲张、皮肤破损、感染者不宜',
        '⚠️饭后立即不宜泡脚',
        '⚠️严重心衰、高血压未控者不宜久泡'],
      verified: true },
    { name: '功法导引（八段锦）', category: '导引类',
      principle: '以特定动作导引气血、通经络。动作柔和，适合慢性病与老人。',
      indications: ['慢性疲劳', '颈肩腰背慢性痛', '失眠', '高血压辅助（八段锦有证据支持）',
        '老年人平衡与柔韧'],
      methods: ['预备式 → 双手托天理三焦 → 左右开弓似射雕 → 调理脾胃须单举',
        '五劳七伤往后瞧 → 摇头摆尾去心火 → 两手攀足固肾腰 → 攒拳怒目增气力',
        '背后七颠百病消 → 收功'],
      cautions: ['⚠️量力而行，出现头晕胸闷立即停止',
        '⚠️颈椎病急性期、严重骨质疏松者不做「摇头摆尾」与「两手攀足」',
        '⚠️高血压未控者避免低头与憋气动作',
        '每次 10–20 分钟，每日 1–2 次，坚持才有效'],
      verified: false },
  ];

  const SYNONYMS = {
    '口苦': ['嘴里发苦', '嘴苦'],
    '咽干': ['嗓子干', '喉咙干', '口干'],
    '不思饮食': ['没胃口', '不想吃', '吃不下', '食欲不振', '厌食'],
    '五更泻': ['黎明泻', '鸡鸣泻', '早上腹泻'],
    '头重如裹': ['头重', '像裹了布', '头沉'],
    '自汗': ['爱出汗', '动不动出汗'],
    '盗汗': ['晚上出汗', '睡觉出汗'],
  };

  class Inverse {
    constructor(kb) {
      this.kb = kb;
      this._sym = null;
    }

    symIndex() {
      if (this._sym) return this._sym;
      const idx = {};
      for (const sx of this.kb.syndromes) {
        for (const w of (sx.sy || [])) {
          if (!idx[w]) idx[w] = [];
          idx[w].push({ id: sx.id, n: sx.n || '' });
        }
      }
      for (const canon of Object.keys(SYNONYMS)) {
        for (const alt of SYNONYMS[canon]) {
          if (!idx[alt]) idx[alt] = idx[canon] || [];
        }
      }
      this._sym = idx;
      return idx;
    }

    _expand(text) { return [text].concat(SYNONYMS[text] || []); }

    byDisease(name) {
      const kb = this.kb;
      let matched = kb.matchDisease(name);
      if (!matched.length) {
        const d = kb.disease(name);
        if (d) matched = [{ d: d, hit: 1 }];
      }
      if (!matched.length) return null;
      const d = matched[0].d;

      const syndromes = [];
      for (const sid of (d.sx || [])) {
        const sx = kb.syndrome(sid);
        if (!sx) continue;
        const formulas = [];
        for (const fid of (sx.fx || [])) {
          const f = kb.formula(fid);
          if (!f) continue;
          formulas.push({
            name: f.name, functions: f.functions || '',
            herbs: f.herbs || '', source: f.source_text || '',
            cautions: f.cautions || [],
          });
        }
        syndromes.push({
          id: sid, name: sx.n || '', system: sx.sys || '',
          severity: sx.sev || '', home_ok: !!sx.home,
          key_symptoms: sx.sy || [], tongue: sx.tg || '', pulse: sx.p || '',
          mechanism: sx.me || '', treatment: sx.tx || '',
          differential: sx.df || '', warn: sx.wn || '', note: sx.nt || '',
          formulas: formulas,
          acupoints_meridian: kb.pointsMeridian(sid).map((p) => ({
            name: p.name, meridian: p.meridian || '', location: p.location || '',
          })),
          dongshi: kb.pointsDongshi(sid),
          tuina: kb.searchTuina(sx.d || '', 1).map((t) => ({
            condition: t.condition, level: t.level, home: t.home_self_help || '',
          })),
        });
      }
      return {
        disease: d, syndromes: syndromes,
        must_exclude: d.ex || [], overview: d.ov || '',
        common_symptoms: d.cs || [],
      };
    }

    bySymptom(text, k) {
      const idx = this.symIndex();
      const hits = {};
      const seen = new Set();
      for (const w of this._expand(text)) {
        if (seen.has(w)) continue;      // 同义词展开会把原词再带一次，去重否则命中数虚高
        seen.add(w);
        for (const it of (idx[w] || [])) {
          if (!hits[it.id]) hits[it.id] = { id: it.id, name: it.n, match: [] };
          hits[it.id].match.push(w);
        }
      }
      const out = [];
      for (const key of Object.keys(hits)) {
        const e = hits[key];
        const sx = this.kb.syndrome(key);
        if (!sx) continue;
        e.disease = sx.d || '';
        e.tongue = sx.tg || ''; e.pulse = sx.p || '';
        e.mechanism = sx.me || ''; e.treatment = sx.tx || '';
        e.hit = e.match.length;
        e.formula = '';
        for (const fid of (sx.fx || [])) {
          const f = this.kb.formula(fid);
          if (f) { e.formula = f.name; break; }
        }
        e.acupoints = this.kb.pointsMeridian(key).slice(0, 4).map((p) => p.name);
        out.push(e);
      }
      out.sort((a, b) => (b.hit - a.hit) || String(a.disease).localeCompare(String(b.disease)));
      return { q: text, hits: out.slice(0, k || 12) };
    }

    byFormula(text, k) {
      const hits = this.kb.searchFormula(text, k || 8);
      return {
        hits: hits.map((f) => {
          const usedBy = this.kb.syndromes.filter((sx) => (sx.fx || []).indexOf(f.id) >= 0);
          const acupoints = [];
          for (const sx of usedBy) {
            for (const p of this.kb.pointsMeridian(sx.id)) {
              if (acupoints.indexOf(p.name) < 0) acupoints.push(p.name);
            }
          }
          return { formula: f, used_by: usedBy, acupoints: acupoints };
        }),
      };
    }

    byAcupoint(text, k) {
      const meridian = this.kb.searchAcupoint(text, k || 10).map((p) => ({
        point: p,
        used_by: this.kb.syndromes.filter((sx) => (sx.ac || []).indexOf(p.id) >= 0),
      }));
      return {
        meridian: meridian,
        dongshi: this.kb.searchDongshi(text, k || 10),
        lineage: this.kb.dongshiLineage,
      };
    }
  }

  // ------------------------------------------------------------ 渲染
  function renderDisease(data) {
    if (!data) {
      return '库中没有这个病。可查：' +
        ['感冒', '咳嗽', '哮病', '喘证', '胸痹', '头痛', '眩晕', '不寐', '心悸', '胃痛',
          '痞满', '呕吐', '泄泻', '痢疾', '便秘', '腹痛', '胁痛', '黄疸', '鼓胀', '痹证',
          '腰痛', '痉证', '痿证', '郁证', '血证', '痰饮', '水肿', '淋证', '癃闭', '关格',
          '消渴', '虚劳', '内伤发热', '自汗盗汗', '阳痿', '遗精', '中风', '瘿病', '疟疾',
          '月经不调', '痛经', '带下', '妊娠', '产后', '乳癖', '咽喉肿痛', '口疮', '鼻渊',
          '耳鸣耳聋', '牙痛', '小儿积食', '小儿腹泻', '小儿夜啼', '遗尿']
          .join('、');
    }
    const d = data.disease;
    const L = [`# ${d.name}（${d.cat}）`];
    if (data.overview) L.push(data.overview);
    if (data.common_symptoms && data.common_symptoms.length) {
      L.push('\n**常见症状**：\n' + data.common_symptoms.join('、'));
    }
    L.push(`\n**本病收录 ${data.syndromes.length} 个证型**`);

    data.syndromes.forEach((sx, i) => {
      L.push('\n' + '─'.repeat(50));
      L.push(`## ${i + 1}. ${sx.name}（${sx.system}｜${sx.severity}）`);
      L.push('**主症**：' + sx.key_symptoms.join('、'));
      L.push(`**舌**：${sx.tongue}　**脉**：${sx.pulse}`);
      L.push('**病机**：' + sx.mechanism);
      L.push('**治法**：' + sx.treatment);
      if (sx.differential) L.push('**鉴别**：' + sx.differential);
      L.push('\n**方药**');
      for (const f of sx.formulas) {
        L.push(`- **${f.name}**（${f.source}）${f.functions}`);
        L.push('  - 组成：' + f.herbs);
        if (f.cautions && f.cautions.length) {
          L.push('  - 注意：' + f.cautions.slice(0, 3).join('；'));
        }
      }
      L.push('\n**针灸 · 通道一 十四经穴**');
      L.push(sx.acupoints_meridian.map((p) => `${p.name}（${p.meridian}）`).join('、'));
      const ds = sx.dongshi;
      L.push(`\n**针灸 · 通道二 董氏奇穴（${ds.lineage} 派）**`);
      L.push('- 配穴思路：' + (ds.hint || '（本证型未预设董氏配穴思路）'));
      if (ds.matches && ds.matches.length) {
        L.push('- 可考虑：' + ds.matches.map((x) => x.name).join('、') + '（定位待原书核对）');
      }
      L.push('- ⛔ 定位未录入原书，系统不给定位');
      if (sx.tuina && sx.tuina.length) {
        L.push(`\n**推拿**（${sx.tuina[0].level}）：${sx.tuina[0].condition}`);
        if (sx.tuina[0].home) L.push('- 🏠 家庭可做：' + sx.tuina[0].home);
      }
      if (sx.warn) L.push(`\n⚠️ **安全提示**：${sx.warn}`);
      if (sx.note) L.push('ℹ️ ' + sx.note);
      if (sx.home_ok) L.push('✅ 本证型可先做家庭调理');
    });

    if (data.must_exclude && data.must_exclude.length) {
      L.push('\n' + '═'.repeat(50));
      L.push('## ⚠️ 出现以下情况必须先就医，不可只按本病处理');
      for (const m of data.must_exclude) L.push('- ' + m);
    }
    L.push('\n' + '─'.repeat(50));
    L.push('ℹ️ 本页为中医病证知识查阅，不构成处方。处方须经执业中医师复核签字。');
    return L.join('\n');
  }

  function renderSymptom(data) {
    const hits = data.hits || [];
    if (!hits.length) {
      return '没有匹配到含该症状的证型。可以换个说法试试，或直接查病名。';
    }
    const L = [`# 症状「${data.q}」反查（命中 ${hits.length} 个证型）`, ''];
    L.push('⚠️ 同一症状可见于多个病多种证，此处仅为知识对照，**不能据此自诊**。');
    L.push('');
    for (const e of hits) {
      L.push(`**${e.disease} · ${e.name}**（匹配 ${e.hit} 项：${e.match.join('、')}）`);
      L.push(`  - 舌脉：${e.tongue}｜${e.pulse}`);
      L.push('  - 病机：' + e.mechanism);
      L.push(`  - 治法：${e.treatment}　方：${e.formula || '—'}`);
      L.push('  - 穴：' + e.acupoints.join('、') + '\n');
    }
    return L.join('\n');
  }

  function renderFormula(data) {
    const hits = data.hits || [];
    if (!hits.length) return '没有匹配到这个方剂。';
    const L = ['# 方剂反查（方 → 证 → 症）', ''];
    for (const h of hits) {
      const f = h.formula;
      L.push('═'.repeat(50));
      L.push(`## ${f.name}（${f.source_text || ''}）　${f.functions || ''}`);
      L.push('**主治**：' + (f.indications || ''));
      L.push('**组成**：' + (f.herbs || ''));
      L.push('**方义**：' + (f.formula_meaning || ''));
      if (f.similar_diff) L.push('**类方鉴别**：' + f.similar_diff);
      if (f.modifications) L.push('**加减**：' + f.modifications);
      if (f.cautions && f.cautions.length) L.push('**禁忌**：' + f.cautions.join('；'));
      L.push('**剂量**：⚠️为教材参考值，须执业医师核定');
      if (h.used_by.length) {
        L.push(`\n**本库中用于这些证型**（共 ${h.used_by.length} 个）：`);
        for (const sx of h.used_by) {
          L.push(`- ${sx.d} · ${sx.n}｜主症：${(sx.sy || []).slice(0, 5).join('、')}`);
        }
      }
      if (h.acupoints.length) {
        L.push('\n**常配穴**：' + h.acupoints.slice(0, 10).join('、'));
      }
    }
    L.push('\n' + '─'.repeat(50));
    L.push('ℹ️ 知识查阅用，不构成处方。');
    return L.join('\n');
  }

  function renderAcupoint(data) {
    const L = ['# 穴位反查（穴 → 主治 → 证 → 方）', ''];
    L.push('## 通道一：十四经穴');
    if (!data.meridian.length) L.push('（无匹配）');
    for (const m of data.meridian) {
      const p = m.point;
      L.push('─'.repeat(40));
      L.push(`### ${p.name}（${p.meridian || ''}｜${p.code || ''}）`);
      L.push('- 定位：' + (p.location || ''));
      L.push('- 主治：' + (p.indications || []).slice(0, 8).join('、'));
      L.push('- 针刺：' + (p.needling || '') + '｜深度上限：' + (p.depth_limit || ''));
      if (p.anatomy_note) L.push('- 解剖：' + p.anatomy_note);
      if (p.contraindication) L.push('- ⚠️ 禁忌：' + p.contraindication);
      if (p.self_moxa_safe) L.push('- 🟢 适合家庭艾灸/按揉');
      if (m.used_by.length) {
        L.push(`- **本库用于这些证型**（${m.used_by.length}）：`);
        for (const sx of m.used_by) {
          let fn = '';
          for (const fid of (sx.fx || [])) {
            const f = this_global_kb.formula(fid);
            if (f) { fn = f.name; break; }
          }
          L.push(`  - ${sx.d} · ${sx.n}　方：${fn || '—'}`);
        }
      }
    }
    L.push(`\n## 通道二：董氏奇穴（${data.lineage} 派）`);
    L.push('⚠️ 与上方十四经穴不是同一套体系。');
    if (!data.dongshi.length) L.push('（无匹配）');
    for (const p of data.dongshi) {
      L.push('─'.repeat(40));
      L.push('### ' + p.name + (p.part ? `（${p.part}）` : ''));
      L.push('- 主治方向：' + (p.direction || ''));
      if (p.use_for && p.use_for.length) L.push('- 适用：' + p.use_for.join('、'));
      L.push('- 定位：🔒 未按原书录入，系统不提供（' + (p.lineage || '') + ' 派）');
      if (p.conflict_note) L.push('- ⚠️ 与经穴冲突：' + p.conflict_note);
    }
    L.push('\n' + '─'.repeat(50));
    L.push('ℹ️ 针刺仅限具备执业资格者。知识查阅用，不构成处方。');
    return L.join('\n');
  }

  function renderTherapy() {
    const L = ['# 其他疗法（传统中医非药物与非方药方法）', '',
      '本库已有的方药、针灸、推拿之外，以下方法按「传统中医」收录。',
      '**这些是知识查阅，不构成处方。**', ''];
    for (const t of OTHER_THERAPY) {
      L.push('═'.repeat(50));
      L.push(`## ${t.name}（${t.category}）`);
      L.push('**原理**：' + t.principle);
      L.push('**适用**：' + t.indications.join('、'));
      L.push('**操作**：');
      for (const m of t.methods) L.push('- ' + m);
      L.push('**注意**：');
      for (const c of t.cautions) L.push('- ' + c);
      if (!t.verified) L.push('- ℹ️ 本条待对照教材核对');
    }
    return L.join('\n');
  }

  // renderAcupoint 需要访问 kb 查方名，用模块级引用避免层层传参
  let this_global_kb = null;
  function setKB(kb) { this_global_kb = kb; }

  global.Inverse = Inverse;
  global.OTHER_THERAPY = OTHER_THERAPY;
  global.renderDisease = renderDisease;
  global.renderSymptom = renderSymptom;
  global.renderFormula = renderFormula;
  global.renderAcupoint = renderAcupoint;
  global.renderTherapy = renderTherapy;
  global.setInverseKB = setKB;
})(typeof window !== 'undefined' ? window : globalThis);
