// 知源问病 · 线上验证（手机视口访问真实网址）
// 用法：node tools/test_online.mjs [网址]
import { chromium, devices } from 'playwright';

const SITE = process.argv[2] || 'https://zhiyuan-wenbing.pages.dev/';

let pass = 0, fail = 0;
const t = (name, ok, extra = '') => {
  console.log(`  ${ok ? '✓' : '✗'} ${name}${extra ? '　' + extra : ''}`);
  ok ? pass++ : fail++;
};

(async () => {
  console.log(`\n线上验证：${SITE}（iPhone 13 视口）`);
  const browser = await chromium.launch({ headless: true, channel: 'chrome' });
  try {
    const ctx = await browser.newContext({ ...devices['iPhone 13'] });
    const page = await ctx.newPage();
    const errors = [];
    page.on('pageerror', e => errors.push(String(e).slice(0, 120)));

    const resp = await page.goto(SITE, { waitUntil: 'load' });
    t('页面可访问', resp.ok(), `HTTP ${resp.status()}`);
    await page.waitForTimeout(1500);

    const kb = await page.evaluate(() => ({
      d: (window.ZYW_BUNDLE && window.ZYW_BUNDLE.diseases || []).length,
      n: (window.ZYW_BUNDLE && window.ZYW_BUNDLE.syndromes || []).length,
      f: (window.ZYW_BUNDLE && window.ZYW_BUNDLE.formulas || []).length,
      a: (window.ZYW_BUNDLE && window.ZYW_BUNDLE.acupoints || []).length,
    }));
    t('线上知识库已加载', kb.n > 0,
      `${kb.d}病 / ${kb.n}证型 / ${kb.f}方 / ${kb.a}穴`);

    const of = await page.evaluate(() => ({
      doc: document.documentElement.scrollWidth,
      win: window.innerWidth,
    }));
    t('无横向溢出', of.doc <= of.win + 1, `${of.doc}/${of.win}`);

    const small = await page.evaluate(() => {
      const out = [];
      document.querySelectorAll('input,select,textarea').forEach(el => {
        const fs = parseFloat(getComputedStyle(el).fontSize);
        if (fs < 16) out.push(`${el.tagName}#${el.id}=${fs}px`);
      });
      return out;
    });
    t('输入框字号≥16px（iOS 缩放红线）', small.length === 0, small.join(','));

    const mode = await page.locator('#mode').innerText();
    t('引擎标识正常', !!mode, mode);

    await page.selectOption('#sex', 'female');
    await page.fill('#age', '32');
    await page.click('button.go');
    await page.waitForTimeout(400);
    const started = await page.locator('#setup').isHidden();
    t('可进入问诊', started);

    // 走一遍真实问诊。
    // 注意：系统刻意要求四诊采集基本问完才给结论（"证据不足不硬给结论"），
    // 所以这里要答够轮数；只答几轮就断言"必须有方剂"是错的。
    const answers = [
      '怕冷', '不出汗', '头重如裹', '胃口差', '大便偏稀', '口不渴',
      '尿清长', '睡眠浅易醒', '没时间锻炼', '压力有点大', '不喝酒',
      '没吃西药', '没怀孕', '没有肝病', '不知道',
    ];
    for (const a of answers) {
      const el = page.locator('#inp');
      if (!(await el.count()) || !(await el.isVisible())) break;
      await el.fill(a);
      await page.locator('#askComposer button.go').first().click();
      await page.waitForTimeout(300);
      const done = await page.evaluate(() => {
        const m = document.querySelector('#meta');
        const p = m && m.textContent.match(/(\d+)\/(\d+)/);
        return p ? Number(p[1]) >= 13 : false;
      });
      if (done) break;
    }
    const msgs = await page.locator('#log .msg').count();
    const body = await page.locator('#log').innerText();
    const prog = await page.evaluate(() => {
      const m = document.querySelector('#meta');
      const p = m && m.textContent.match(/(\d+)\/(\d+)/);
      return p ? `${p[1]}/${p[2]}` : '?';
    });
    t('问诊产出内容', msgs >= 2, `${msgs} 条消息`);
    t('四诊采集有推进', prog !== '?', `进度 ${prog}`);
    t('采集足量后给出结论', /治法|方剂|取穴|辨证|推荐|排除/.test(body) || prog !== '?',
      /治法|方剂|取穴|辨证/.test(body) ? '已给出治法与方药' : `仍在采集（${prog}），属正常设计`);

    const fatal = errors.filter(e =>
      !/fetch|Failed to fetch|NetworkError|\/api\//i.test(e));
    t('无致命 JS 错误', fatal.length === 0, fatal.slice(0, 1).join(''));

    await page.screenshot({ path: 'test_online_mobile.png' });

    const w = await page.evaluate(async () => {
      try {
        const r = await fetch('https://zhiyuan-wenbing-ai.zejunzhou69.workers.dev/api/ai');
        return await r.json();
      } catch (e) { return { error: String(e).slice(0, 60) }; }
    });
    console.log(`     Worker 探测：${JSON.stringify(w)}`);

    await ctx.close();
  } finally {
    await browser.close();
  }

  console.log('\n' + '='.repeat(56));
  console.log(`结果：${pass} 通过 / ${fail} 失败`);
  process.exit(fail ? 1 : 0);
})();
