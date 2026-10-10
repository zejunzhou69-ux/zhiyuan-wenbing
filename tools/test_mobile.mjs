// 知源问病 · 移动端与 file:// 双击实测
//
// 这不是"应该能跑"，是真实开浏览器、点按钮、量像素。
// 验证三件事：
//   1) 手机尺寸下布局不横向溢出、输入框字号达标（iOS 缩放红线）
//   2) 触摸目标够大（>=40px）
//   3) file:// 双击打开时，问诊主流程仍能跑通（核心功能不依赖网络）
//
// 用法：node tools/test_mobile.mjs
import { chromium, devices } from 'playwright';
import { pathToFileURL } from 'url';
import path from 'path';

const ROOT = process.cwd();
const FILE_URL = pathToFileURL(path.join(ROOT, 'static', 'index.html')).href;

// 优先用 Playwright 自带的 chromium；没下载完就退回系统已装的 Chrome/Edge，
// 省掉 150MB 下载。systemChrome 变量在下方 launch 时传入。
const useSystem = process.env.USE_SYSTEM_BROWSER === '1';

let pass = 0, fail = 0;
const t = (name, ok, extra = '') => {
  console.log(`  ${ok ? '✓' : '✗'} ${name}${extra ? '　' + extra : ''}`);
  ok ? pass++ : fail++;
};

const IPHONE = devices['iPhone 13'];

async function checkLayout(page, label, isTouch = true) {
  // 1. 横向溢出：文档宽度不应超过视口
  const of = await page.evaluate(() => ({
    doc: document.documentElement.scrollWidth,
    win: window.innerWidth,
  }));
  t(`${label} 无横向溢出`, of.doc <= of.win + 1,
    `文档${of.doc}px / 视口${of.win}px`);

  if (of.doc > of.win + 1) {
    const bad = await page.evaluate((vw) => {
      const out = [];
      document.querySelectorAll('*').forEach(el => {
        const r = el.getBoundingClientRect();
        if (r.width > 0 && r.right > vw + 1) {
          out.push(`${el.tagName}.${el.className || '-'} 右边界${Math.round(r.right)}`);
        }
      });
      return out.slice(0, 5);
    }, of.win);
    if (bad.length) console.log('      溢出元素：' + bad.join(' / '));
  }

  // 2 & 3 只对触屏设备检查：
  //    ≥16px 是 iOS Safari 的聚焦缩放红线，≥40px 是手指点击下限。
  //    桌面用鼠标，14px 字号与 33px 按钮是合理设计，不该按触屏标准判失败。
  if (isTouch) {
    const small = await page.evaluate(() => {
      const out = [];
      document.querySelectorAll('input,select,textarea').forEach(el => {
        const fs = parseFloat(getComputedStyle(el).fontSize);
        if (fs < 16) out.push(`${el.tagName}#${el.id || '-'}=${fs}px`);
      });
      return out;
    });
    t(`${label} 输入框字号≥16px（iOS 缩放红线）`, small.length === 0, small.join(','));

    const smallTap = await page.evaluate(() => {
      const out = [];
      document.querySelectorAll('button,.chip,.kind').forEach(el => {
        const r = el.getBoundingClientRect();
        if (r.height > 0 && r.height < 40) {
          out.push(`${el.className || el.tagName}=${Math.round(r.height)}px`);
        }
      });
      return out;
    });
    t(`${label} 触摸目标≥40px`, smallTap.length === 0, smallTap.join(','));
  }
}

async function runDiagnosis(page, label) {
  await page.selectOption('#sex', 'female');
  await page.fill('#age', '32');
  await page.click('button.go');
  await page.waitForTimeout(300);

  const started = await page.locator('#setup').isHidden();
  t(`${label} 可进入问诊`, started);
  if (!started) return;

  const answers = ['怕冷', '不出汗', '头重如裹', '胃口差', '大便偏稀', '口不渴'];
  // 问诊模式的输入框是 #inp（#q 是查阅模式的，别搞混）
  const el = page.locator('#inp');
  let sent = 0;
  for (const a of answers) {
    if (!(await el.count())) break;
    if (!(await el.isVisible())) break;
    await el.fill(a);
    await page.locator('#askComposer button.go').first().click();
    sent++;
    await page.waitForTimeout(350);
    const body = await page.locator('#log').innerText();
    if (/治法|方剂|辨证|取穴|推荐/.test(body) && body.length > 300) break;
  }
  const msgs = await page.locator('#log .msg').count();
  t(`${label} 问诊可产出内容`, msgs >= 2, `${msgs} 条消息 / 已答 ${sent} 轮`);
}

(async () => {
  const browser = await chromium.launch({
    headless: true,
    ...(useSystem ? { channel: 'chrome' } : {}),
  });
  try {
    // ---------- 场景1：手机 + file:// 双击打开 ----------
    console.log('\n【场景1】手机浏览器（iPhone 13）+ file:// 双击打开');
    const c1 = await browser.newContext({ ...IPHONE });
    const p1 = await c1.newPage();
    const errors = [];
    p1.on('pageerror', e => errors.push(String(e)));
    await p1.goto(FILE_URL, { waitUntil: 'load' });
    await p1.waitForTimeout(900);

    // 知识库是否真的加载了（这是 file:// 能不能用的关键）
    const kb = await p1.evaluate(() => ({
      ok: !!(window.ZYW_BUNDLE && window.ZYW_BUNDLE.syndromes),
      n: (window.ZYW_BUNDLE && window.ZYW_BUNDLE.syndromes || []).length,
    }));
    t('file:// 下知识库已加载', kb.ok, `${kb.n} 个证型`);

    await checkLayout(p1, 'file://');
    await runDiagnosis(p1, 'file://');

    // 致命错误才算失败（fetch /api/ai 的失败是预期降级）
    const fatal = errors.filter(e => !/api|fetch|Failed to fetch|NetworkError/i.test(e));
    t('file:// 无致命 JS 错误', fatal.length === 0, fatal.slice(0, 2).join(' | '));

    await p1.screenshot({ path: 'test_mobile_file.png' });
    await c1.close();

    // ---------- 场景2：手机 + 本地 http（模拟线上） ----------
    console.log('\n【场景2】手机 + 本地 http（模拟线上环境）');
    const { createServer } = await import('http');
    const { readFile } = await import('fs/promises');
    const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css' };
    const srv = createServer(async (req, res) => {
      let f = decodeURIComponent(req.url.split('?')[0]);
      if (f === '/') f = '/index.html';
      try {
        const buf = await readFile(path.join(ROOT, 'static', f));
        res.writeHead(200, { 'Content-Type': (MIME[path.extname(f)] || 'text/plain') + '; charset=utf-8' });
        res.end(buf);
      } catch { res.writeHead(404); res.end('nf'); }
    });
    await new Promise(r => srv.listen(8791, r));

    const c2 = await browser.newContext({ ...IPHONE });
    const p2 = await c2.newPage();
    await p2.goto('http://127.0.0.1:8791/', { waitUntil: 'load' });
    await p2.waitForTimeout(900);
    await checkLayout(p2, 'http');
    await p2.screenshot({ path: 'test_mobile_http.png' });
    await c2.close();
    srv.close();

    // ---------- 场景3：小屏手机 ----------
    console.log('\n【场景3】小屏手机 320×568');
    const c3 = await browser.newContext({
      viewport: { width: 320, height: 568 }, isMobile: true, hasTouch: true,
      userAgent: IPHONE.userAgent,
    });
    const p3 = await c3.newPage();
    await p3.goto(FILE_URL, { waitUntil: 'load' });
    await p3.waitForTimeout(900);
    await checkLayout(p3, '320px');
    await p3.screenshot({ path: 'test_mobile_small.png' });
    await c3.close();

    // ---------- 场景4：桌面回归 ----------
    console.log('\n【场景4】桌面 1280×800 回归');
    const c4 = await browser.newContext({ viewport: { width: 1280, height: 800 } });
    const p4 = await c4.newPage();
    await p4.goto(FILE_URL, { waitUntil: 'load' });
    await p4.waitForTimeout(900);
    await checkLayout(p4, '桌面', false);   // 桌面非触屏，跳过触屏专项断言
    await runDiagnosis(p4, '桌面');
    await p4.screenshot({ path: 'test_desktop.png' });
    await c4.close();
  } finally {
    await browser.close();
  }

  console.log('\n' + '='.repeat(60));
  console.log(`结果：${pass} 通过 / ${fail} 失败`);
  console.log('截图：test_mobile_file / test_mobile_http / test_mobile_small / test_desktop (.png)');
  process.exit(fail ? 1 : 0);
})();