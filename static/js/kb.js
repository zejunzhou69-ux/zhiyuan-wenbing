/* 知源问病 · 知识库与检索（JS 版）
 *
 * 通道隔离是硬约束：
 *   经穴通道 bundle.acupoints          -> searchAcupoint / pointsMeridian
 *   董氏通道 bundle.dongshi            -> searchDongshi / pointsDongshi
 * 任何检索函数都不得跨通道返回条目。assertChannelSeparation() 自检，串了直接抛错。
 */
(function (global) {
  'use strict';

  class KnowledgeBase {
    constructor(bundle) {
      this.meta = bundle._meta || {};
      this.formulas = bundle.formulas || [];
      this.herbs = bundle.herbs || [];
      // 通道隔离：再清一次，任何董氏来源的条目都不许进经穴通道
      this.acupoints = (bundle.acupoints || []).filter(
        (a) => (a.source_system || '经穴') !== '董氏奇穴'
      );
      const ds = bundle.dongshi || {};
      this.dongshiPoints = ds.points || [];
      this.dongshiNames = (ds.names_hand || []).concat(ds.names_foot || []);
      this.dongshiTheory = ds.theory || [];
      this.dongshiUsagePatterns = ds.usage_patterns || [];
      this.dongshiLineage = ds.lineage || 'yangweijie';
      this.dongshiLocatorNote = ds.locator_note || '';

      const t = bundle.tuina || {};
      this.tuinaHand = t.handcrafts || [];
      this.tuinaProto = t.protocols || [];
      this.tuinaGlobalContra = t.global_contraindications || {};

      this.diseases = bundle.diseases || [];
      this.syndromes = bundle.syndromes || [];

      const rf = bundle.redflags || {};
      this.emergency = rf.emergency || [];
      this.mustRefer = rf.must_refer || [];
      this.special = rf.special_populations || {};
      this.drugRules = rf.drug_safety_rules || [];
      this.needlingSafety = rf.needling_safety || [];

      this._idx();
    }

    _idx() {
      this.fById = indexBy(this.formulas, 'id');
      this.hById = indexBy(this.herbs, 'id');
      this.aById = indexBy(this.acupoints, 'id');
      this.sById = indexBy(this.syndromes, 'id');
    }

    // ---------------------------------------------------------- 检索
    static score(item, text, fields) {
      const t = String(text || '').toLowerCase();
      let sc = 0;
      for (const f of fields) {
        let v = item[f];
        if (!v) continue;
        if (Array.isArray(v)) v = v.join(' ');
        v = String(v).toLowerCase();
        if (v && t.indexOf(v) >= 0) {
          sc += (v.length / Math.max(t.length, 1)) * 100 + Math.min(v.length, 8);
        }
      }
      return sc;
    }

    _rank(pool, text, fields, k) {
      const out = pool
        .map((x) => ({ x, s: KnowledgeBase.score(x, text, fields) }))
        .filter((r) => r.s > 0)
        .sort((a, b) => b.s - a.s)
        .slice(0, k || 8);
      return out.map((r) => r.x);
    }

    searchFormula(text, k) {
      return this._rank(this.formulas, text,
        ['name', 'indications', 'functions', 'similar_diff'], k || 5);
    }

    searchSyndrome(text, k) {
      return this._rank(this.syndromes, text,
        ['n', 'd', 'sy', 'me', 'tx'], k || 8);
    }

    searchTuina(text, k) {
      return this._rank(this.tuinaProto, text,
        ['condition', 'syndrome_pattern'], k || 5);
    }

    // ------------------------------------------------ 通道一：十四经穴
    searchAcupoint(text, k) {
      return this._rank(this.acupoints, text,
        ['name', 'indications', 'meridian'], k || 8);
    }

    pointsMeridian(syndromeId) {
      const sx = this.sById[syndromeId];
      if (!sx) return [];
      return (sx.ac || []).map((id) => this.aById[id]).filter(Boolean);
    }

    // ------------------------------------------------ 通道二：董氏奇穴
    searchDongshi(text, k) {
      const out = [];
      const t = String(text || '').toLowerCase();
      for (const p of this.dongshiPoints) {
        if (p.name && t.indexOf(p.name.slice(0, 2)) >= 0) {
          out.push(Object.assign({}, p, {
            channel: 'dongshi',
            // 只有 verified 的条目才允许输出定位
            location_to_output: p.verified ? (p.location || '') : '',
          }));
        }
      }
      for (const nm of this.dongshiNames) {
        if (nm.name && t.indexOf(nm.name.slice(0, 2)) >= 0) {
          out.push({
            name: nm.name, part: nm.part || '',
            direction: nm.direction || '', use_for: nm.use_for || [],
            lineage: this.dongshiLineage, channel: 'dongshi',
            verified: false, location_to_output: '',
            conflict_note: nm.conflict_note || '',
          });
        }
      }
      return out.slice(0, k || 8);
    }

    dongshiByUse(keywords) {
      const keys = [];
      for (const kw of keywords) {
        const s = String(kw || '').trim();
        if (s.length >= 2) { keys.push(s); keys.push(s.slice(0, 2)); }
      }
      const hit = [];
      const seen = new Set();
      for (const nm of this.dongshiNames) {
        if (seen.has(nm.name)) continue;
        const hay = (nm.direction || '') + ' ' + (nm.use_for || []).join(' ');
        for (const kw of keys) {
          if (kw && hay.indexOf(kw) >= 0) {
            hit.push(Object.assign({}, nm, {
              channel: 'dongshi', location_to_output: '',
              lineage: this.dongshiLineage, match_on: kw,
            }));
            seen.add(nm.name);
            break;
          }
        }
      }
      return hit;
    }

    pointsDongshi(syndromeId) {
      const sx = this.sById[syndromeId];
      if (!sx) {
        return { hint: '', matches: [], location_ready: [], lineage: this.dongshiLineage, note: '' };
      }
      // 只用证型名 + 主症做匹配；病名截断会造成假匹配（"小儿积食"->"小儿" 撞上 "小儿喘促"）
      const keys = [sx.n || ''].concat((sx.sy || []).slice(0, 4));
      return {
        hint: sx.ds || '',
        matches: this.dongshiByUse(keys).slice(0, 5),
        location_ready: this.dongshiPoints.filter((p) => p.verified).map((p) => p.name),
        lineage: this.dongshiLineage,
        note: '董氏奇穴定位待按原书补录；补录前系统只给配穴思路，不给定位。',
      };
    }

    // ---------------------------------------------------------- 主诉 -> 病
    // chief（主诉）里出现的症状权重更高：用户说"后脑勺疼"是主症，
    // "怕冷"是伴随症 —— 两者都命中时应判头痛，不能靠出现顺序决定。
    matchDisease(text, chiefText) {
      const t = String(text || '');
      const chief = String(chiefText || '');
      const res = [];
      for (const d of this.diseases) {
        let hit = 0, chiefHit = 0;
        for (const kw of (d.kw || [])) {
          if (t.indexOf(kw) >= 0) {
            hit++;
            if (chief && chief.indexOf(kw) >= 0) chiefHit++;
          }
        }
        if (hit) res.push({ d: d, hit: hit, chiefHit: chiefHit, score: hit + chiefHit * 2 });
      }
      res.sort((a, b) => (b.score - a.score) ||
        String(a.d.name).localeCompare(String(b.d.name)));   // 同分按名称，保证结果确定
      return res;
    }

    // ---------------------------------------------------------- 详情
    formula(id) { return this.fById[id]; }
    herb(id) { return this.hById[id]; }
    syndrome(id) { return this.sById[id]; }
    disease(name) { return this.diseases.find((d) => d.name === name) || null; }

    herbByName(name) {
      if (!name) return null;
      if (this.hById[name]) return this.hById[name];
      const hit = this.herbs.find((h) => h.name === name);
      if (hit) return hit;
      return this.herbs.find((h) =>
        name.indexOf(h.name) >= 0 || h.name.indexOf(name) >= 0) || null;
    }

    // ---------------------------------------------------------- 通道自检
    static assertChannelSeparation(meridian, dongshi) {
      for (const p of meridian) {
        if (p.source_system === '董氏奇穴') {
          throw new Error('经穴通道混入董氏条目：' + (p.name || ''));
        }
      }
      for (const p of dongshi) {
        if (p.channel !== 'dongshi') {
          throw new Error('董氏通道混入非董氏条目：' + (p.name || ''));
        }
      }
      return true;
    }

    stats() {
      return {
        '方剂': this.formulas.length,
        '中药': this.herbs.length,
        '经穴': this.acupoints.length,
        '董氏奇穴(定位已录)': this.dongshiPoints.filter((p) => p.verified).length,
        '董氏奇穴(穴名层)': this.dongshiNames.length,
        '推拿手法': this.tuinaHand.length,
        '推拿方案': this.tuinaProto.length,
        '证型': this.syndromes.length,
        '病种': this.diseases.length,
        '红旗': this.emergency.length,
      };
    }
  }

  function indexBy(arr, key) {
    const o = {};
    for (const x of arr) o[x[key]] = x;
    return o;
  }

  let KB = null;
  // bundle.js 用 <script> 直接注入（file:// 双击也能用，不受 CORS 限制）
  async function loadKB() {
    if (KB) return KB;
    const bundle = globalThis.ZYW_BUNDLE;
    if (!bundle) throw new Error('知识库未加载：请确认 js/bundle.js 已引入');
    KB = new KnowledgeBase(bundle);
    return KB;
  }

  global.KnowledgeBase = KnowledgeBase;
  global.loadKB = loadKB;
})(typeof window !== 'undefined' ? window : globalThis);
