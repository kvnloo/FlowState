// Live sources. Both the real Muse (Web Bluetooth via vendored muse-js) and the TEST simulator feed the same
// SecondAssembler: 12-sample packets per electrode -> whole seconds on a true clock, with absent seconds for gaps
// and a per-second contact verdict. The simulator replays real EEGMAT raw EEG with injected faults; it is labelled.
(function (root) {
  const FS = 256, NCH = 4, CH = ["TP9", "AF7", "AF8", "TP10"];
  function SecondAssembler(h) { // h: {second({t, bands, quality, valid}), absent(tSec), progress(f), raw(ch, samples)}
    let buf = [[], [], [], []], secStart = null, got0 = 0, t0 = null, expected = null; const stats = { seconds: 0, absent: 0, lateMs: 0 };
    const exp = [null, null, null, null], PKT_MS = 12 / FS * 1000;
    function closeInvalid(reason) { // the current second lost samples: it lands as not measured, never stitched across the hole
      h.second({ t: secStart / 1000, bands: null, quality: ["dropped", "dropped", "dropped", "dropped"], valid: false, reason }); stats.seconds++; stats.dropped = (stats.dropped || 0) + 1; secStart += 1000; buf = [[], [], [], []]; }
    function packet(ch, samples, ts) {
      if (ch >= NCH) return;
      if (secStart === null) { secStart = Math.ceil(ts / 1000) * 1000; t0 = ts; }
      if (exp[ch] !== null && ts - exp[ch] > PKT_MS * 0.9) { // samples missing on this channel
        const until = Math.floor(ts / 1000) * 1000;
        if (ts - exp[ch] > 600) { if (buf.some(b => b.length)) closeInvalid("gap"); for (let s2 = secStart; s2 < until; s2 += 1000) { h.absent(s2 / 1000); stats.absent++; } secStart = Math.max(secStart, until); buf = [[], [], [], []]; }
        else if (secStart <= ts) closeInvalid("dropped samples");
        for (let c = 0; c < NCH; c++) exp[c] = null; }
      exp[ch] = ts + samples.length / FS * 1000;
      const sampleMs = i => ts + i / FS * 1000; let k = 0; while (k < samples.length && sampleMs(k) < secStart + buf[ch].length / FS * 1000 - 2) k++;
      for (; k < samples.length; k++) buf[ch].push(samples[k]);
      h.raw && h.raw(ch, samples);
      const minLen = Math.min(buf[0].length, buf[1].length, buf[2].length, buf[3].length); h.progress && h.progress(Math.min(1, minLen / FS));
      if (minLen >= FS) { const chans = buf.map(b => b.splice(0, FS)); const { bands, quality } = EEGBands.bandPowers(chans, FS);
        const valid = quality.every(q => q === "good" || q === "blink"); stats.seconds++; stats.lateMs = Math.max(0, Date.now() - (secStart + 1000));
        h.second({ t: secStart / 1000, bands, quality, valid }); secStart += 1000; }
    }
    return { packet, stats, get t0() { return t0; } };
  }

  // TEST stream: real raw EEG (EEGMAT, T5/F7/F8/T6 as TP9/AF7/AF8/TP10) with scheduled faults.
  async function SimSource(h, { speed = 1, url = "../data/sim_raw.f32" } = {}) {
    const raw = new Float32Array(await fetch(url).then(r => r.arrayBuffer())); const N = raw.length / NCH;
    const asm = SecondAssembler(h); let idx = 0, timer = 0, stopped = false; const start = Date.now(); // true clock: sample 0 is now
    const faults = t => ({ // seconds since start -> per-electrode fault
      flat: [0, 1, 2, 3].map(k => t < 1.2 + k * 1.3 || (k === 3 && t >= 70 && t < 82)), noisy: [false, t >= 200 && t < 206, false, false], gap: (t >= 150 && t < 162) || (t >= 110 && t < 110.04) });
    const blink = t => { const ph = (t % 4.1) - 2.0; return ph >= 0 && ph < 0.25 ? 400 * Math.sin(Math.PI * ph / 0.25) : 0; }; // test blink: AF7+AF8 same sign
    const PK = 12;
    // wall-clock scheduled: every tick sends all packets that are due (catch-up after timer throttling), like a device whose clock never stops
    const t0w = Date.now(); let sent = 0;
    function tick() { if (stopped) return; const due = Math.floor((Date.now() - t0w) * speed / (PK / FS * 1000)); let budget = 400;
      while (sent < due && budget-- > 0) { const t = idx / FS, f = faults(t), ts = start + t * 1000;
        if (!f.gap) for (let ch = 0; ch < NCH; ch++) { const s = new Array(PK); for (let i = 0; i < PK; i++) { const v = raw[((idx + i) % N) * NCH + ch];
              const bl = (ch === 1 || ch === 2) && t > 30 ? blink((idx + i) / FS) : 0;
              s[i] = f.flat[ch] ? 0.2 * Math.sin(idx + i) : f.noisy[ch] ? v + (Math.random() - 0.5) * 900 : v + bl; }
            asm.packet(ch, s, ts); }
        idx += PK; sent++; }
      timer = setTimeout(tick, 20); }
    tick();
    return { kind: "sim", label: `simulated Muse · EEGMAT raw${speed !== 1 ? " · " + speed + "×" : ""}`, stop() { stopped = true; clearTimeout(timer); }, stats: asm.stats };
  }

  async function MuseSource(h) { // must be called synchronously inside a click (requestDevice needs the user gesture)
    const { MuseClient } = root.__museJs; const m = new MuseClient(); const asm = SecondAssembler(h);
    await m.connect(); await m.start();
    m.eegReadings.subscribe(r => asm.packet(r.electrode, r.samples, r.timestamp));
    let onDrop = null; m.connectionStatus.subscribe(ok => { if (!ok && onDrop) onDrop(); });
    return { kind: "muse", label: "muse s", stop() { try { m.disconnect(); } catch (e) {} }, stats: asm.stats, set ondisconnect(f) { onDrop = f; } };
  }
  root.EEGSources = { FS, CH, SecondAssembler, SimSource, MuseSource };
})(typeof window !== "undefined" ? window : globalThis);
