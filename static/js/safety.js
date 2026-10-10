/* 知源问病 · 安全层（JS 版）
 *
 * 独立于任何 AI。静态版没有 AI，这一层就是唯一防线，更不能简化。
 * 与 Python 版 engine/safety.py 保持一致，改一处必须改两处。
 */
(function (global) {
  'use strict';

  // 西药 -> 风险提示
  const WESTERN_DRUG_RISK = {
    '华法林': ['活血化瘀类中药（丹参、当归、川芎、红花、桃仁）会显著增加出血风险，须查 INR 调整'],
    '利伐沙班': ['与抗血小板药同用时活血药出血风险显著升高'],
    '阿司匹林': ['与活血化瘀药同用增加出血风险'],
    '氯吡格雷': ['与活血化瘀药同用增加出血风险'],
    '二甲双胍': ['须监测血糖，中药不可替代降糖药'],
    '胰岛素': ['须监测血糖，不可自行加减量'],
    '降压药': ['含麻黄制剂（麻黄、桂枝类）可能升高血压与心率，反向抵消降压效果'],
    '地高辛': ['⚠️甘草大量长期用可致低钾，地高辛与低钾并用易致洋地黄中毒（心律失常）'],
    '利尿剂': ['⚠️甘草与利尿剂并用致低钾、水肿、血压异常'],
    '胺碘酮': ['存在相互作用，须咨询心内科与药师'],
    '激素': ['长期使用致骨质疏松，推拿禁暴力手法'],
    '抗抑郁药': ['酸枣仁、柏子仁、远志等安神药可能叠加镇静，须防嗜睡'],
    '镇静催眠药': ['与安神药叠加可致过度镇静'],
    '他汀': ['何首乌、女贞子等有肝损伤报告，须监测肝功能'],
    '化疗药': ['与化疗相互作用复杂，须咨询肿瘤科，禁止自行服用'],
  };

  // 十八反 / 十九畏 显式配对表（含炮制品别名）
  const ANTI_ALIAS = {
    '甘草': ['甘草', '炙甘草', '生甘草', '粉甘草', '甘草梢'],
    '海藻': ['海藻'],
    '甘遂': ['甘遂', '醋甘遂'],
    '大戟': ['大戟', '京大戟', '红大戟', '醋大戟'],
    '芫花': ['芫花', '醋芫花'],
    '乌头': ['乌头', '川乌', '制川乌', '生川乌', '草乌', '制草乌', '附子', '黑顺片',
             '白附片', '淡附片', '炮附片', '附片'],
    '半夏': ['半夏', '法半夏', '姜半夏', '清半夏', '生半夏'],
    '瓜蒌': ['瓜蒌', '全瓜蒌', '瓜蒌皮', '瓜蒌仁', '天花粉'],
    '贝母': ['川贝母', '浙贝母', '平贝母', '贝母', '土贝母'],
    '白蔹': ['白蔹'],
    '白及': ['白及', '白及粉'],
    '藜芦': ['藜芦'],
    '人参': ['人参', '生晒参', '红参', '白参', '人参须'],
    '沙参': ['南沙参', '北沙参', '沙参'],
    '丹参': ['丹参'],
    '玄参': ['玄参'],
    '苦参': ['苦参'],
    '细辛': ['细辛'],
    '芍药': ['白芍', '赤芍', '炒白芍', '酒白芍', '白芍炭', '赤芍炭'],
    '硫黄': ['硫黄'],
    '朴硝': ['朴硝', '芒硝', '玄明粉', '牙硝'],
    '水银': ['水银'],
    '砒霜': ['砒霜', '砒石'],
    '狼毒': ['狼毒'],
    '密陀僧': ['密陀僧'],
    '巴豆': ['巴豆', '巴豆霜'],
    '牵牛': ['牵牛子', '黑丑', '白丑', '牵牛'],
    '丁香': ['丁香', '公丁香', '母丁香'],
    '郁金': ['郁金'],
    '犀角': ['犀角', '水牛角'],
    '三棱': ['三棱', '醋三棱', '荆三棱'],
    '官桂': ['肉桂', '桂皮', '官桂'],
    '赤石脂': ['赤石脂', '煅赤石脂'],
    '五灵脂': ['五灵脂', '醋五灵脂'],
  };

  const ANTI_18 = [['甘草', '海藻'], ['甘草', '甘遂'], ['甘草', '大戟'], ['甘草', '芫花'],
    ['乌头', '半夏'], ['乌头', '瓜蒌'], ['乌头', '贝母'], ['乌头', '白蔹'], ['乌头', '白及'],
    ['藜芦', '人参'], ['藜芦', '沙参'], ['藜芦', '丹参'], ['藜芦', '玄参'],
    ['藜芦', '苦参'], ['藜芦', '细辛'], ['藜芦', '芍药']];

  const ANTI_19 = [['硫黄', '朴硝'], ['水银', '砒霜'], ['狼毒', '密陀僧'], ['巴豆', '牵牛'],
    ['丁香', '郁金'], ['乌头', '犀角'], ['朴硝', '三棱'], ['官桂', '赤石脂'],
    ['人参', '五灵脂']];

  const NOT_HERB = new Set(['先煎', '后下', '包煎', '另煎', '烊化', '冲服', '研末', '吞服',
    '水煎', '各', '等分', '分', '酒', '醋', '姜', '蜜', '米', '朱砂为衣', '为衣']);

  function extractHerbNames(herbsStr) {
    const s = String(herbsStr || '')
      .replace(/（/g, ' ').replace(/）/g, ' ').replace(/，/g, ' ').replace(/、/g, ' ');
    const out = [];
    for (let tok of s.split(/\s+/)) {
      tok = tok.trim();
      if (!tok) continue;
      let name = tok.replace(/[×xX].*$/, '');
      name = name.replace(/[\d.]+\s*[gGmM克]*$/, '');
      name = name.trim();
      if (!name || NOT_HERB.has(name)) continue;
      if (/\d/.test(name)) continue;
      out.push(name);
    }
    return out;
  }

  function matchedGroups(herbNames) {
    const hit = new Set();
    for (const g of Object.keys(ANTI_ALIAS)) {
      if (ANTI_ALIAS[g].some((n) => herbNames.indexOf(n) >= 0)) hit.add(g);
    }
    return hit;
  }

  function checkAnticonflict(herbNames) {
    const hit = matchedGroups(herbNames);
    const out = [];
    const real = (g) => {
      for (const n of ANTI_ALIAS[g]) if (herbNames.indexOf(n) >= 0) return n;
      return g;
    };
    for (const [a, b] of ANTI_18) {
      if (hit.has(a) && hit.has(b)) {
        out.push('⚠️⚠️【十八反】本方含「' + real(a) + '」与「' + real(b) +
                 '」，属十八反配伍禁忌，须医师复核后方可使用');
      }
    }
    for (const [a, b] of ANTI_19) {
      if (hit.has(a) && hit.has(b)) {
        out.push('⚠️【十九畏】本方含「' + real(a) + '」与「' + real(b) + '」，属十九畏，须医师复核');
      }
    }
    return out;
  }

  const DECOCTION = [
    ['石膏', '生石膏先煎'], ['牡蛎', '牡蛎先煎'], ['龙骨', '龙骨先煎'],
    ['附子', '附子先煎久煎30–60分钟以上'], ['川乌', '川乌先煎久煎1–2小时'],
    ['草乌', '草乌先煎久煎1–2小时'], ['薄荷', '薄荷后下'],
    ['钩藤', '钩藤后下（超20分钟失效）'], ['砂仁', '砂仁后下'],
    ['豆蔻', '豆蔻后下'], ['沉香', '沉香后下'], ['车前子', '车前子包煎'],
    ['旋覆花', '旋覆花包煎'], ['人参', '人参另煎兑服'],
  ];

  class Safety {
    constructor(kb) {
      this.kb = kb;
      this.emergency = kb.emergency || [];
      this.mustRefer = kb.mustRefer || [];
      this.special = kb.special || {};
      this.needlingSafety = kb.needlingSafety || [];
    }

    scan(text) {
      if (!text) return [];
      const hits = [];
      for (const e of this.emergency) {
        const hit = (e.kw || []).filter((k) => String(text).indexOf(k) >= 0);
        if (hit.length) hits.push(Object.assign({}, e, { hit: hit }));
      }
      return hits;
    }

    // 孕妇腹痛的硬规则：不依赖关键词，靠 profile + 腹部疼痛词
    emergencyBlock(text, profile) {
      profile = profile || {};
      const t = String(text || '');

      if (profile.pregnant) {
        const belly = ['腹痛', '肚子痛', '肚子疼', '小腹痛', '下腹痛',
                       '小肚子疼', '坠痛', '腹部痛', '上腹痛', '胃脘痛'];
        if (belly.some((k) => t.indexOf(k) >= 0)) {
          const e12 = this.emergency.find((x) => x.id === 'E12');
          return Object.assign({}, e12, { hit: ['孕期腹痛（硬规则拦截）'] });
        }
      }

      const age = profile.age;
      if (typeof age === 'number' && age < 1) {
        if (['嗜睡', '叫不醒', '拒奶', '哭声尖', '囟门'].some((k) => t.indexOf(k) >= 0)) {
          const e11 = this.emergency.find((x) => x.id === 'E11');
          return Object.assign({}, e11, { hit: ['婴儿精神状态改变（硬规则拦截）'] });
        }
      }

      const hits = this.scan(t);
      if (!hits.length) return null;
      // 优先级：疑似中风最易被误当面瘫而延误，其次自伤
      const order = ['E06', 'E15', 'E01', 'E12', 'E08', 'E07', 'E11', 'E05',
                     'E04', 'E02', 'E03', 'E14', 'E13', 'E10', 'E09'];
      for (const id of order) {
        const h = hits.find((x) => x.id === id);
        if (h) return h;
      }
      return hits[0];
    }

    referFlags(text) {
      const out = [];
      for (const r of this.mustRefer) {
        const hit = (r.items || []).filter((i) => String(text).indexOf(i) >= 0);
        if (hit.length) out.push(Object.assign({}, r, { hit: hit }));
      }
      return out;
    }

    screenProfile(profile) {
      profile = profile || {};
      const out = { bans: [], cautions: [], must_ask: [] };
      const age = profile.age;

      if (profile.pregnant) {
        const pg = this.special.pregnancy || {};
        out.bans = out.bans.concat(pg.drug_absolutely_ban || []);
        out.bans = out.bans.concat(pg.acupoint_ban_needle || []);
        out.bans.push('腹部与腰骶部推拿按摩');
        out.cautions = out.cautions.concat(pg.drug_caution || []);
      }
      if (profile.breastfeeding) out.bans.push('回乳药（麦芽、大量山楂）');

      if (typeof age === 'number') {
        if (age < 1) {
          const inf = this.special.infant || {};
          out.bans = out.bans.concat(inf.massage_ban || []);
          out.must_ask.push('是否高热、拒奶、精神状态、尿量');
        } else if (age < 6) {
          out.must_ask.push('⚠️6个月以下婴儿发热属急诊指征');
        } else if (age >= 70) {
          const el = this.special.elderly || {};
          out.bans = out.bans.concat(el.avoid || []);
          out.must_ask.push('是否有骨质疏松、近期跌倒、新发疼痛');
        }
      }
      if (profile.liver_kidney) {
        const lk = this.special.liver_kidney_impairment || {};
        if (lk.note) out.cautions.push(lk.note);
        out.must_ask = out.must_ask.concat(lk.must_ask || []);
      }
      for (const med of (profile.medications || [])) {
        const s = String(med);
        for (const key of Object.keys(WESTERN_DRUG_RISK)) {
          if (s.indexOf(key) >= 0) {
            out.cautions = out.cautions.concat(WESTERN_DRUG_RISK[key]);
            out.must_ask.push('正在服用' + key + '，是否已告知开方医师');
          }
        }
      }
      out.bans = Array.from(new Set(out.bans)).sort();
      out.cautions = Array.from(new Set(out.cautions.filter(Boolean))).sort();
      return out;
    }

    checkFormula(formula, profile) {
      const warns = [];
      profile = profile || {};
      const herbsStr = String(formula.herbs || '');
      const cautions = String(formula.cautions || '');

      if (profile.pregnant) {
        const pg = this.special.pregnancy || {};
        const hitB = (pg.drug_absolutely_ban || []).filter((h) => herbsStr.indexOf(h) >= 0);
        const hitC = (pg.drug_caution || []).filter((h) => herbsStr.indexOf(h) >= 0);
        const hitP = (pg.acupoint_ban_needle || []).filter((h) => herbsStr.indexOf(h) >= 0);
        if (hitB.length) {
          warns.push('⚠️⚠️【妊娠禁用】本方含绝对禁用药 ' + hitB.join('、') + ' —— 孕妇禁用，须换方');
        }
        if (hitC.length) {
          warns.push('⚠️【妊娠慎用】本方含慎用药 ' + hitC.join('、') + ' —— 须医师评估');
        }
        if (hitP.length) {
          warns.push('⚠️【配伍与取穴禁忌】涉及 ' + hitP.join('、'));
        }
      }

      const herbNames = extractHerbNames(herbsStr);
      warns.push.apply(warns, checkAnticonflict(herbNames));

      if (cautions) warns.push('【原方注意】' + cautions);
      warns.push('【剂量核定】上方剂量为教材参考值，须经执业医师按体质、病情、剂量习惯核定后方可使用。');

      const deco = DECOCTION.filter(([kw]) => herbsStr.indexOf(kw) >= 0).map(([, how]) => how);
      if (deco.length) warns.push('【煎服法】' + deco.join('；'));
      return warns;
    }

    herbToxicity(herbNames) {
      const out = [];
      for (const hn of herbNames) {
        const h = this.kb.herbByName(hn);
        if (h && h.toxicity && h.toxicity.indexOf('无毒') < 0) {
          const ci = (h.contraindications || []).join('；').slice(0, 90);
          out.push('⚠️【' + hn + '】' + h.toxicity + '｜常用量 ' + (h.dosage || '') +
                   '｜禁忌：' + ci);
        }
      }
      return out;
    }
  }

  function emergencyReply(blk) {
    const L = ['🛑 **命中急症红旗：' + blk.cat + '**', '', '**' + blk.action + '**', ''];
    if (blk.note) L.push(blk.note, '');
    L.push('本次不进行辨证、不给方、不给穴。远程问诊无法排除这类急症，');
    L.push('任何中医处置（含推拿、针灸、服中药）都会延误抢救。');
    L.push('');
    L.push('⚠️ 心理援助热线：12356（全国 24 小时）');
    return L.join('\n');
  }

  global.Safety = Safety;
  global.emergencyReply = emergencyReply;
  global.extractHerbNames = extractHerbNames;
  global.checkAnticonflict = checkAnticonflict;
})(typeof window !== 'undefined' ? window : globalThis);
