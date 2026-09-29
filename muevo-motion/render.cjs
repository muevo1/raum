const { chromium } = require('playwright');
const { spawn } = require('child_process');
const [mode, ...rest] = process.argv.slice(2);
(async () => {
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--enable-webgl'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on('console', m => console.log('[page]', m.text()));
  page.on('pageerror', e => console.log('[err]', e.message));
  await page.goto('http://127.0.0.1:8765/index.html');
  await page.waitForFunction(() => window.READY === true, null, { timeout: 60000 });
  const stage = await page.$('#stage');
  if (mode === 'stills') {
    for (const t of rest) {
      await page.evaluate(t => window.seek(t), +t);
      await stage.screenshot({ path: `stills/t${(+t).toFixed(2)}.png` });
    }
  } else {
    const [fps, out] = rest; const N = Math.round(15 * fps); const t0 = Date.now();
    const ff = spawn('ffmpeg', ['-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', fps, '-c:v', 'png', '-i', '-', '-c:v', 'ffv1', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let i = 0; i < N; i++) {
      await page.evaluate(t => window.seek(t), i / fps);
      const buf = await stage.screenshot({ type: 'png' });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (i % 60 === 0) console.log(`frame ${i}/${N} ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }
  await browser.close();
})();
