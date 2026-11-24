// node tools/live_ux.mjs OUT -> user journey on the test stream: hold-T range tag, hover excluded + gap seconds, poster export
import { chromium } from "playwright-core"; import fs from "fs";
const out = process.argv[2]; fs.mkdirSync(out, { recursive: true });
const exe = fs.readdirSync(process.env.HOME + "/Library/Caches/ms-playwright").filter(d => d.startsWith("chromium-")).map(d => process.env.HOME + `/Library/Caches/ms-playwright/${d}/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing`).find(fs.existsSync);
const b = await chromium.launch({ executablePath: exe, headless: true, args: ["--use-angle=metal", "--enable-gpu", "--ignore-gpu-blocklist"] });
const ctx = await b.newContext({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 2, acceptDownloads: true }); const p = await ctx.newPage(); const errs = [], res = {};
p.on("pageerror", e => errs.push(e.message)); p.on("console", m => { if (m.type() === "error") errs.push(m.text()); });
await p.goto("http://127.0.0.1:8765/web/app.html?speed=600&src=sim&simspeed=20"); await p.waitForTimeout(3000);
// Tag button (critic: passed the click event as a range)
await p.click("#tag"); await p.waitForTimeout(150); res.tagButtonRange = await p.evaluate(() => document.querySelector("#tagrange").textContent); await p.keyboard.type("standup"); await p.keyboard.press("Enter");
// hold T 600 ms -> range opens, box appears while held; name it; 2.5 s later press T to close
await p.keyboard.down("t"); await p.waitForTimeout(250); await p.screenshot({ path: out + "/1-arming.png" }); await p.waitForTimeout(350); await p.keyboard.up("t");
res.tagbox = await p.evaluate(() => [document.querySelector("#tagbox").classList.contains("show"), document.querySelector("#tagrange").textContent]);
await p.keyboard.type("coffee"); await p.screenshot({ path: out + "/2-tagbox.png" }); await p.keyboard.press("Enter"); await p.waitForTimeout(2500);
await p.screenshot({ path: out + "/2b-open-range.png" }); await p.keyboard.press("t"); await p.waitForTimeout(300);
res.tags = await p.evaluate(() => __app.tags()); const cf = res.tags.find(x => x.title === "coffee"); res.tagRangeSec = cf && cf.c1 !== null ? cf.c1 - cf.c0 : null;
// wait for faults to pass
for (let i = 0; i < 40; i++) { const k = await p.evaluate(() => { const S = __app.S; let n = 0; for (let c = S.firstCell; c < __app.cells(); c++) n++; return n; }); if (k > 230) break; await p.waitForTimeout(700); }
await p.click("#sim"); await p.waitForTimeout(200); const before = await p.evaluate(() => __app.E.n); await p.waitForTimeout(2500); // stop stream; nothing may be added after stop
res.noLeakAfterStop = await p.evaluate(b => ({ added: __app.E.n - b, state: document.querySelector("#state").textContent, follow: document.querySelector("#follow").classList.contains("show") }), before);
const cellXY = async c => p.evaluate(c => { const r = document.querySelector("#stage").getBoundingClientRect(); return null; }, c);
// zoom in on the gap row via keyboard fit then programmatic hover using pick coords
const pos = await p.evaluate(() => { const S = __app.S; let g = -1, m = -1; for (let c = S.firstCell; c < __app.cells(); c++) { if (g < 0 && S.state[c] === 0) g = c; if (m < 0 && S.state[c] === 2 && c > S.firstCell + 30) m = c; } return { g, m }; });
res.pos = pos;
await p.keyboard.press("0"); await p.waitForTimeout(900);
// zoom toward the excluded cell row
const toScreen = c => p.evaluate(c => window.__cellToClient(c), c);
await p.evaluate(() => {}); 
for (const [name, c] of [["3-hover-excluded", pos.m], ["4-hover-gap", pos.g]]) { if (c < 0) continue; const xy = await toScreen(c); if (!xy) continue;
  for (let z = 0; z < 6; z++) { await p.mouse.move(xy[0], xy[1]); await p.keyboard.down("Meta"); await p.mouse.wheel(0, -120); await p.keyboard.up("Meta"); await p.waitForTimeout(80); }
  await p.waitForTimeout(700); const xy2 = await toScreen(c); await p.mouse.move(xy2[0], xy2[1]); await p.waitForTimeout(400);
  res[name] = await p.evaluate(() => document.querySelector("#card").innerText.replace(/\n/g, " | ")); await p.screenshot({ path: `${out}/${name}.png` }); await p.keyboard.press("0"); await p.waitForTimeout(900); }
const [dl] = await Promise.all([p.waitForEvent("download", { timeout: 15000 }).catch(() => null), p.click("#save")]);
if (dl) { await dl.saveAs(out + "/poster.png"); res.poster = fs.statSync(out + "/poster.png").size; }
res.errs = errs.slice(0, 5); console.log(JSON.stringify(res, null, 1)); await b.close();
