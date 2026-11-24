// node tools/ux.mjs OUTDIR  -> drive the real app like a user; screenshot each state; report console errors
import { chromium } from "playwright-core"; import fs from "fs";
const out = process.argv[2]; fs.mkdirSync(out, { recursive: true });
const exe = fs.readdirSync(process.env.HOME + "/Library/Caches/ms-playwright").filter(d => d.startsWith("chromium-")).map(d => process.env.HOME + `/Library/Caches/ms-playwright/${d}/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing`).find(fs.existsSync);
const b = await chromium.launch({ executablePath: exe, headless: true, args: ["--use-angle=metal", "--enable-gpu", "--ignore-gpu-blocklist"] });
const p = await b.newPage({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 2 }); const errs = [];
p.on("pageerror", e => errs.push(e.message)); p.on("console", m => { if (m.type() === "error") errs.push(m.text()); });
await p.goto("http://127.0.0.1:8765/web/app.html?speed=600"); await p.waitForTimeout(9000); await p.screenshot({ path: out + "/1-replay.png" });
await p.mouse.move(560, 420); await p.waitForTimeout(400); await p.screenshot({ path: out + "/2-hover.png" });
for (let i = 0; i < 8; i++) { await p.mouse.wheel(0, -120); await p.keyboard.down("Meta"); await p.mouse.wheel(0, -60); await p.keyboard.up("Meta"); await p.waitForTimeout(60); }
await p.waitForTimeout(700); await p.mouse.move(600, 500); await p.waitForTimeout(300); await p.screenshot({ path: out + "/3-zoomed.png" });
await p.hover("#legend button:nth-child(6)"); await p.waitForTimeout(500); await p.screenshot({ path: out + "/4-isolate-blue.png" });
await p.mouse.move(300, 900); await p.waitForTimeout(300);
const notes = await p.$$(".note"); if (notes.length) { await notes[Math.min(1, notes.length - 1)].hover(); await notes[Math.min(1, notes.length - 1)].click(); await p.waitForTimeout(1200); await p.screenshot({ path: out + "/5-note-fly.png" }); }
await p.keyboard.press("0"); await p.waitForTimeout(1200); await p.screenshot({ path: out + "/6-fit-all.png" });
await p.keyboard.press("t"); await p.waitForTimeout(300); await p.keyboard.type("coffee"); await p.screenshot({ path: out + "/7-tag.png" }); await p.keyboard.press("Enter");
console.log(JSON.stringify({ notes: notes.length, errs: errs.slice(0, 8) })); await b.close();
