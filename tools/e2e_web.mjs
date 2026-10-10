/* 知源问病 · 静态站端到端验证（模拟浏览器环境）
 *
 * engine 测试覆盖逻辑，这个补"页面能不能跑起来"这一层：
 * index.html 里 6 个脚本能否按序加载、引擎能否从 window.ZYW_BUNDLE 取到数据。
 *
 * 用法：node tools/e2e_web.mjs
 */
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, '..');

function makeEl(tag) {
  const el = {
    tagName: (tag || 'div').toUpperCase(),
    _html: '', value: '', dataset: {}, style: {}, children: [],
    className: '', placeholder: '',
    classList: {
      add(c) { if (!el.className.includes(c)) el.className = (el.className + ' ' + c).trim(); },
      remove(c) { el.className = el.className.split(/\s+/).filter((x) => x && x !== c).join(' '); },
      contains(c) { return el.className.split(/\s+/).includes(c); },
    },
    appendChild(c) { el.children.push(c); return c; },
    set innerHTML(v) { el._html = v; }, get innerHTML() { return el._html; },
    addEventListener() {}, focus() {},
    querySelectorAll(sel) {
      const cls = String(sel).replace('.', '');
      return el.children.filter((c) => String(c.className || '').includes(cls));
    },
  };
  return el;
}

const els = {};
for (const id of ['log', 'setup', 'lookup', 'askComposer', 'progWrap', 'meta', 'bar',
  'mode', 'modeDesc', 'tabAsk', 'tabLook', 'chips', 'q', 'kindTip', 'inp',
  'sex', 'age', 'preg', 'lk', 'meds', 'statsLine']) {
  els[id] = makeEl();
}
els.sex.value = 'female';
els.age.value = '30';
els.preg.value = '0';
els.lk.value = '0';

globalThis.window = globalThis;
globalThis.document = {
  getElementById: (id) => els[id] || makeEl(),
  querySelectorAll: () => [],
  createElement: (t) => makeEl(t),
};
globalThis.scrollTo = () => {};
// /api/ai 探测必须失败（本地没 Worker），验证会自动退回纯规则
globalThis.fetch = async () => { throw new Error('no worker'); };

let pass = 0, fail = 0;
const bad = [];
const t = (n, c, e) => { if (c) pass++; else { fail++; bad.push(n + (e ? ' → ' + e : '')); } };

console.log('1. 按 index.html 顺序加载脚本');
// bundle 文件名带内容指纹（bundle.<hash>.js），从 index.html 里读实际引用，
// 写死 'js/bundle.js' 会在启用指纹后失效。
const indexHtml = await readFile(join(ROOT, 'static', 'index.html'), 'utf8');
const bundleRef = (indexHtml.match(/js\/bundle(\.[0-9a-f]+)?\.js/) || [])[0];
if (!bundleRef) { console.log('✗ index.html 里找不到 bundle 引用'); process.exit(1); }
console.log(`   bundle 引用：${bundleRef}`);
const files = [bundleRef, 'js/kb.js', 'js/safety.js', 'js/diagnose.js',
               'js/inverse.js', 'js/app.js'];
for (const f of files) {
  const src = await readFile(join(ROOT, 'static', f), 'utf8');
  try { (0, eval)(src); t(`加载 ${f}`, true); }
  catch (e) { t(`加载 ${f}`, false, e.message); }
}

console.log('\n2. 全局导出');
for (const n of ['loadKB', 'Safety', 'FourDiagSession', 'inferField', 'Inverse',
                 'renderDisease', 'renderTherapy', 'start', 'send', 'lookup', 'setKind']) {
  t(`导出 ${n}`, typeof globalThis[n] === 'function');
}
t('bundle 已注入', !!globalThis.ZYW_BUNDLE);

console.log('\n3. UI 函数已挂载（init 执行过）');
for (const n of ['start', 'send', 'lookup', 'setKind', 'switchMode']) {
  t(`window.${n}`, typeof globalThis[n] === 'function');
}

console.log('\n4. AI 探测失败 → 退回纯规则（功能不受影响）');
const G = globalThis;
const kb = await G.loadKB();
const safety = new G.Safety(kb);
const inv = new G.Inverse(kb);
G.setInverseKB(kb);
// 用下限断言而不是写死具体数字：知识库会持续扩充，写死会让每次补录都误报失败。
// 下限取首批基线，保证「数据丢失」和「整体没加载」仍能被发现。
t('知识库已加载（>=55方/>=125证型）',
  kb.formulas.length >= 55 && kb.syndromes.length >= 125 && kb.diseases.length >= 35);

const sess = new G.FourDiagSession({ sex: 'female', age: 30 });
// 模拟 app.js 的真实归位逻辑：第一条无条件当主诉，其余按 inferField
for (const a of ['后脑勺疼三天了', '怕冷风，手脚凉', '不出汗', '后脑连着脖子一起疼',
                 '大便一天一次成形', '小便正常', '吃凉的胃里不舒服', '睡眠还行',
                 '舌淡红，苔薄白', '脉浮紧']) {
  const firstChief = !sess.collected.chief;
  if (firstChief) sess.record('chief', a);
  const f = G.inferField(a, sess.profile);
  if (f) sess.record(f, a);
  else if (!firstChief) sess.record('chief', (sess.collected.chief || '') + ' ' + a);
}
const c = sess.completeness();
t(`采集完成 ${c.percent}%`, c.percent >= 60);
const m = kb.matchDisease(sess.text(), sess.collected.chief || '');
t('判为头痛', m[0].d.name === '头痛', m[0].d.name);
const cands = G.rankSyndromes(kb, sess, m[0].d.name);
t('首选风寒头痛', cands[0].n === '风寒头痛', cands[0].n);
const txt = G.renderPlan(G.buildPlan(kb, safety, cands[0].id, sess, sess.profile));
t('方案含方药', txt.includes('【方药】'));
t('方案含双通道', txt.includes('通道一：十四经穴') && txt.includes('通道二：董氏奇穴'));
t('方案含免责', txt.includes('不能替代执业医师面诊'));

console.log('\n5. 查阅模式');
const d = inv.byDisease('咳嗽');
t('咳嗽 5 证型', d.syndromes.length === 5);
t('病谱含鉴别', G.renderDisease(d).includes('**鉴别**'));
t('中风带120警告', inv.byDisease('中风').syndromes.some((s) => (s.warn || '').includes('120')));
t('其他疗法 8 种', G.OTHER_THERAPY.length === 8);

console.log('\n6. HTML 引用完整性');
const html = await readFile(join(ROOT, 'static/index.html'), 'utf8');
for (const f of files) t(`index.html 引用 ${f}`, html.includes(f));
t('引用 css/app.css', html.includes('css/app.css'));
t('含免责声明', html.includes('不能替代执业医师面诊'));

console.log('\n' + '='.repeat(56));
console.log(`结果：${pass} 通过 / ${fail} 失败`);
if (bad.length) { console.log('\n失败项：'); for (const x of bad) console.log('  ✗ ' + x); }
process.exit(fail ? 1 : 0);
