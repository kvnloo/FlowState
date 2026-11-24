// node tools/shots.mjs OUTDIR t1,t2 "label=query" ...   -> canvas screenshots of identical camera states per arm
import { chromium } from "playwright-core"; import fs from "fs";
const [out, ts, ...arms] = process.argv.slice(2); fs.mkdirSync(out, { recursive: true });
const exe = fs.readdirSync(process.env.HOME + "/Library/Caches/ms-playwright").filter(d => d.startsWith("chromium-")).map(d => process.env.HOME + `/Library/Caches/ms-playwright/${d}/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing`).find(fs.existsSync);
const b = await chromium.launch({ executablePath: exe, headless: true, args: ["--use-angle=metal", "--enable-gpu", "--ignore-gpu-blocklist"] });
for (const t of ts.split(",")) for (const a of arms) { const [lab, q] = a.split("=", 2).length === 2 ? [a.slice(0, a.indexOf("=")), a.slice(a.indexOf("=") + 1)] : [a, a];
  const p = await b.newPage({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 2 }); await p.goto(`http://127.0.0.1:8765/web/app.html?bench=1&shot=${t}&${q}`);
  await p.waitForFunction(() => window.__bench, null, { timeout: 120000 }); await p.locator("#stage").screenshot({ path: `${out}/t${t}_${lab}.png` }); await p.close(); console.log(`${out}/t${t}_${lab}.png`); }
await b.close();