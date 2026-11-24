import { chromium } from "playwright-core"; import fs from "fs";
const exe = fs.readdirSync(process.env.HOME + "/Library/Caches/ms-playwright").filter(d => d.startsWith("chromium-")).map(d => process.env.HOME + `/Library/Caches/ms-playwright/${d}/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing`).find(fs.existsSync);
const b = await chromium.launch({ executablePath: exe, headless: true, args: ["--use-angle=metal", "--enable-gpu"] });
const p = await b.newPage({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 2 });
await p.addInitScript(() => { window.__raf = 0; const r = window.requestAnimationFrame; window.requestAnimationFrame = f => { window.__raf++; return r(f); }; });
await p.goto("http://127.0.0.1:8765/web/app.html?speed=0"); await p.waitForTimeout(6000);
const a = await p.evaluate(() => window.__raf); await p.waitForTimeout(3000); const c = await p.evaluate(() => window.__raf);
console.log(JSON.stringify({ rafCallsDuring3sIdle: c - a })); await b.close();
