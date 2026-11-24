// cancel keeps the sheet + stream; stop then restart within 30 min continues the same sheet with the hole counted
import { chromium } from "playwright-core"; import fs from "fs";
const exe = fs.readdirSync(process.env.HOME + "/Library/Caches/ms-playwright").filter(d => d.startsWith("chromium-")).map(d => process.env.HOME + `/Library/Caches/ms-playwright/${d}/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing`).find(fs.existsSync);
const b = await chromium.launch({ executablePath: exe, headless: true, args: ["--use-angle=metal", "--enable-gpu"] }); const p = await b.newPage({ viewport: { width: 1600, height: 1000 } }); const errs = [];
p.on("pageerror", e => errs.push(e.message)); const res = {};
await p.addInitScript(() => { Object.defineProperty(navigator, "bluetooth", { value: { requestDevice: () => Promise.reject(Object.assign(new Error("User cancelled the requestDevice() chooser."), { name: "NotFoundError" })) } }); });
await p.goto("http://127.0.0.1:8765/web/app.html?speed=0&src=sim&simspeed=1"); await p.waitForTimeout(5000);
const before = await p.evaluate(() => ({ id: __app.S.id, n: __app.E.n }));
await p.click("#connect"); await p.waitForTimeout(2500);
const after = await p.evaluate(() => ({ id: __app.S.id, n: __app.E.n, live: !!__app.live, state: document.querySelector("#state").textContent }));
res.cancel = { pass: after.id === before.id && after.n > before.n && after.live && /No Muse chosen/.test(after.state), before, after };
await p.click("#sim"); await p.waitForTimeout(4000); await p.click("#sim"); await p.waitForTimeout(3500);
const rc = await p.evaluate(() => ({ id: __app.S.id, absent: __app.S.absent, state: document.querySelector("#state").textContent, count: document.querySelector("#count").textContent }));
res.reconnect = { pass: rc.id === before.id && rc.absent >= 3 && rc.absent <= 6, rc };
res.errs = errs; console.log(JSON.stringify(res, null, 1)); await b.close();