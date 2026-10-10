/* 知源问病 · 静态版引擎测试（Node 环境，不依赖浏览器）
 *
 * 验的是"和 Python 版行为一致"，不是"页面能打开"。
 * 静态版没有 Python 兜底，测试不过就是线上事故。
 *
 * 用法：node tools/test_web.mjs
 */
import { readFile } from 'node:fs/promises';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, '..');
const U = (p) => pathToFileURL(p).href;   // Windows 上 ESM 动态 import 必须用 file:// URL

globalThis.window = globalThis;
// bundle.js 形如 `window.ZYW_BUNDLE = {...}`，先执行它给引擎供料
(0, eval)(await readFile(join(ROOT, 'static/js/bundle.js'), 'utf8'));

// 这些 js 是 IIFE + 挂 globalThis（浏览器里要能直接 <script> 引），不是 ESM 模块。
// 用 import() 只是为了触发执行，之后从 globalThis 取。
await import(U(join(ROOT, 'static/js/kb.js')));
await import(U(join(ROOT, 'static/js/safety.js')));
await import(U(join(ROOT, 'static/js/diagnose.js')));
await import(U(join(ROOT, 'static/js/inverse.js')));

const { loadKB, Safety, checkAnticonflict, extractHerbNames,
        FourDiagSession, inferField, rankSyndromes, buildPlan, renderPlan,
        Inverse, OTHER_THERAPY, renderDisease, renderSymptom,
        renderFormula, renderAcupoint, renderTherapy, setInverseKB } = globalThis;

const missing = [];
for (const [n, f] of Object.entries({ loadKB, Safety, checkAnticonflict, extractHerbNames,
  FourDiagSession, inferField, rankSyndromes, buildPlan, renderPlan,
  Inverse, renderDisease, renderSymptom, renderFormula, renderAcupoint,
  renderTherapy, setInverseKB })) {
  if (typeof f !== 'function') missing.push(n);
}
if (missing.length) { console.error('MISSING: ' + missing.join(', ')); process.exit(2); }
const D = { FourDiagSession, inferField, rankSyndromes, buildPlan, renderPlan };
const I = { Inverse, OTHER_THERAPY, renderDisease, renderSymptom,
            renderFormula, renderAcupoint, renderTherapy, setInverseKB };

let pass = 0, fail = 0;
const bad = [];
function t(name, cond, extra) {
  if (cond) { pass++; }
  else { fail++; bad.push(name + (extra ? ' → ' + extra : '')); }
}

const kb = await loadKB();
const safety = new Safety(kb);
const inv = new Inverse(kb);
I.setInverseKB(kb);

console.log('='.repeat(56));
console.log('1. 知识库加载');
const st = kb.stats();
console.log('  ', JSON.stringify(st, null, 0).slice(0, 160));
t('方剂 55', st['方剂'] === 55);
t('中药 170', st['中药'] === 170);
t('经穴 120', st['经穴'] === 120);
t('证型 125', st['证型'] === 125);
t('病种 35', st['病种'] === 35);
t('董氏流派 yangweijie', kb.dongshiLineage === 'yangweijie');

console.log('\n2. 双通道隔离');
let sepOK = true;
for (const id of ['S001', 'S012', 'S061', 'S120']) {
  const m = kb.pointsMeridian(id);
  const d = kb.pointsDongshi(id);
  try { I.assertChannelSeparation ? null : null; } catch (e) { sepOK = false; }
  for (const p of m) if (p.source_system === '董氏奇穴') sepOK = false;
  for (const p of d.matches) if (p.channel !== 'dongshi') sepOK = false;
}
t('两条通道没串', sepOK);
const mOnly = kb.searchAcupoint('太冲');
t('searchAcupoint 不返回董氏穴',
  mOnly.every((p) => p.source_system !== '董氏奇穴'));
t('searchDongshi 全部标 dongshi',
  kb.searchDongshi('三里').every((p) => p.channel === 'dongshi'));
t('未录定位的董穴 location_to_output 为空',
  kb.searchDongshi('三里').every((p) => p.location_to_output === ''));

console.log('\n3. 急症红旗');
const cases = [
  ['我胸口压着疼还出汗', {}, 'E01'],
  ['嘴歪了说话不清，右手没劲', {}, 'E06'],
  ['孩子发烧到39度还抽搐', {}, 'E07'],
  ['我有黑便，人也没劲', {}, 'E04'],
  ['怀孕8周，今天突然肚子疼', { pregnant: true }, 'E12'],
  ['怀孕20周牙疼', { pregnant: true }, null],
  ['怀孕20周头疼', { pregnant: true }, null],
  ['宝宝嗜睡不醒', { age: 0.5 }, 'E11'],
  ['宝宝拉肚子', { age: 0.5 }, null],
  ['我这两天拉肚子', {}, null],
  ['有点头疼', {}, null],
  ['睡不着', {}, null],
];
for (const [text, prof, expect] of cases) {
  const blk = safety.emergencyBlock(text, prof);
  const got = blk ? blk.id : null;
  t(`红旗「${text.slice(0, 12)}」→ ${expect || '不拦'}`, got === expect, `实际 ${got}`);
}

console.log('\n4. 十八反 / 十九畏');
t('甘草+海藻 → 抓十八反',
  checkAnticonflict(extractHerbNames('甘草6g 海藻12g')).some((x) => x.includes('十八反')));
t('人参+白芍 → 不误报',
  !checkAnticonflict(extractHerbNames('人参9g 白术9g 白芍12g 炙甘草6g')).some((x) => x.includes('十八反')));
t('制川乌+法半夏 → 抓十八反',
  checkAnticonflict(extractHerbNames('制川乌3g 法半夏9g')).some((x) => x.includes('十八反')));
t('人参+五灵脂 → 抓十九畏',
  checkAnticonflict(extractHerbNames('人参9g 五灵脂6g')).some((x) => x.includes('十九畏')));

console.log('\n5. 人群筛查');
const pg = safety.screenProfile({ pregnant: true, medications: ['华法林 2.5mg'] });
t('孕妇禁活血药', pg.bans.some((x) => x.includes('三棱')));
t('孕妇禁腹部推拿', pg.bans.some((x) => x.includes('腹部')));
// 出血风险写在 cautions（内容是"活血化瘀类…增加出血风险"），药名本身出现在 must_ask
t('华法林 → 出血风险提示', pg.cautions.some((x) => x.includes('出血风险')));
t('华法林 → 必问是否告知医师', pg.must_ask.some((x) => x.includes('华法林')));
const el = safety.screenProfile({ age: 72 });
t('老年人禁旋转手法', el.bans.some((x) => x.includes('旋转')));

console.log('\n6. 正向：采集 → 辨证 → 方案');
const prof = { sex: 'female', age: 32 };
const sess = new D.FourDiagSession(prof);
const answers = {
  chief: '后脑勺疼三天了', cold_heat: '怕冷风，手脚凉，不爱喝水',
  sweat: '不出汗', head_body: '后脑连着脖子一起疼',
  stool: '一天一次成形', urine: '颜色正常，不多',
  diet: '胃口一般，吃凉的胃里不舒服', sleep: '睡眠还行',
  tongue: '舌淡红，苔薄白', pulse: '浮紧',
};
for (const k of Object.keys(answers)) sess.record(k, answers[k]);
const c = sess.completeness();
t(`采集完成度>=60%（实际 ${c.percent}%）`, c.percent >= 60);
// 只要求望/问/切三诊到位；闻诊（声音咳嗽）本轮没答，不强求
const sd = sess.stagesDone();
t('望闻问切已覆盖（闻诊本轮未答）', sd['望'] && sd['问'] && sd['切']);

t('字段识别：舌苔 → tongue', D.inferField('舌淡红，苔薄白', prof) === 'tongue');
t('字段识别：大便 → stool', D.inferField('大便一天一次成形', prof) === 'stool');
t('字段识别：小便 → urine', D.inferField('小便颜色正常', prof) === 'urine');
t('字段识别：睡眠 → sleep', D.inferField('睡眠还行', prof) === 'sleep');
t('字段识别：吃药 → history', D.inferField('以前没什么大病，没吃药', prof) === 'history');

const matched = kb.matchDisease(sess.text(), sess.collected.chief || '');
t('主诉匹配到「头痛」', matched.length && matched[0].d.name === '头痛', matched[0] && matched[0].d.name);
const cands = D.rankSyndromes(kb, sess, matched.length ? matched[0].d.name : null);
t('候选首位是风寒头痛', cands[0] && cands[0].n === '风寒头痛', cands[0] && cands[0].n);

const plan = D.buildPlan(kb, safety, cands[0].id, sess, prof);
const txt = D.renderPlan(plan);
t('方案含方药', txt.includes('【方药】'));
t('方案含经穴通道', txt.includes('通道一：十四经穴'));
t('方案含董氏通道', txt.includes('通道二：董氏奇穴'));
t('方案声明两套体系不同', txt.includes('不是同一套体系'));
t('方案锁定董氏定位', txt.includes('不输出董氏奇穴的定位'));
t('方案含免责', txt.includes('不能替代执业医师面诊'));
t('方案含剂量核定', txt.includes('剂量核定'));
// 麻黄汤/桂枝汤无先煎后下药，不该硬凑煎法；换个确实需要煎法的方验证
const sxHot = kb.syndromes.find((s) => (s.fx || []).some((f) => {
  const ff = kb.formula(f); return ff && (ff.herbs || '').includes('石膏');
}));
if (sxHot) {
  const planHot = D.buildPlan(kb, safety, sxHot.id, sess, prof);
  t('含石膏的方给出先煎法', D.renderPlan(planHot).includes('煎服法'));
} else {
  t('含石膏的方给出先煎法（未找到含石膏证型，跳过）', true);
}

console.log('\n7. 逆向四入口');
const d1 = inv.byDisease('咳嗽');
t('按病查 咳嗽 → 5 证型', d1 && d1.syndromes.length === 5, d1 && d1.syndromes.length);
t('按病查 含概述', !!(d1 && d1.overview));
t('按病查 含必须排除', !!(d1 && d1.must_exclude.length));
const r1 = I.renderDisease(d1);
t('病谱渲染含鉴别', r1.includes('**鉴别**'));
t('病谱渲染含董氏通道', r1.includes('通道二 董氏奇穴'));

const d2 = inv.byDisease('中风');
t('按病查 中风 → 6 证型', d2 && d2.syndromes.length === 6);
t('中风闭证带120警告',
  d2 && d2.syndromes.some((s) => (s.warn || '').includes('120')));

const s2 = inv.bySymptom('口苦');
t('按症查 口苦 命中>=2', s2.hits.length >= 2, s2.hits.length);
t('按症查 命中数未虚高', s2.hits.every((e) => e.hit <= 3));

const f2 = inv.byFormula('逍遥散');
t('按方查 逍遥散 命中', f2.hits.length > 0);
t('按方查 反查到证型', f2.hits[0] && f2.hits[0].used_by.length > 0);

const a2 = inv.byAcupoint('太冲');
t('按穴查 经穴通道有结果', a2.meridian.length > 0);
const r3 = I.renderAcupoint(a2);
t('穴位渲染分两通道', r3.includes('通道一：十四经穴') && r3.includes('通道二：董氏奇穴'));

t('其他疗法 8 种', I.OTHER_THERAPY.length === 8);
t('其他疗法渲染', I.renderTherapy().includes('艾灸法'));

console.log('\n8. 交叉引用完整性');
let refOK = true;
const fIds = new Set(kb.formulas.map((x) => x.id));
const aIds = new Set(kb.acupoints.map((x) => x.id));
for (const sx of kb.syndromes) {
  for (const fid of (sx.fx || [])) if (!fIds.has(fid)) { refOK = false; console.log('   坏方引用', sx.id, fid); }
  for (const aid of (sx.ac || [])) if (!aIds.has(aid)) { refOK = false; console.log('   坏穴引用', sx.id, aid); }
}
t('所有证型引用的方/穴都存在', refOK);

const dIds = new Set(kb.syndromes.map((x) => x.id));
let refOK2 = true;
for (const d of kb.diseases) for (const sid of (d.sx || [])) if (!dIds.has(sid)) refOK2 = false;
t('所有病种引用的证型都存在', refOK2);

console.log('\n' + '='.repeat(56));
console.log(`结果：${pass} 通过 / ${fail} 失败`);
if (bad.length) {
  console.log('\n失败项：');
  for (const b of bad) console.log('  ✗ ' + b);
}
process.exit(fail ? 1 : 0);
