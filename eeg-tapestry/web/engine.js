// Incremental tapestry engine. Same maths as Tapestry.geometry() (batch reference) but O(new points) per update:
// per-band sorted log-power arrays (binary insert), minute stats frozen once their prefix is complete,
// so only the current minute (or the first 300 s) is ever recomputed. Supports window=0, per-band / lin modes.
(function (root) {
  const T = root.Tapestry, BANDS = T.BANDS, NB = 8;
  function Engine(opts) {
    const o = T.merge(opts);
    if (o.window > 0 || o.norm || (o.smooth && Object.values(o.smooth).some(Boolean))) throw new Error("engine: unsupported opts (window/norm/smooth)");
    const gq = o.giantQ ?? 0.9995, linQ = o.linQ ?? 0.6, lin = o.lin || {}, sep = o.giantSep ?? 1800, minN = o.giantMinN ?? 300;
    let cap = 4096, n = 0;
    let L = new Float64Array(cap * NB);           // log10 power per point/band
    const sorted = BANDS.map(() => new Float64Array(cap)); // sorted logs per band (all points so far)
    let R = new Float32Array(cap * NB), U = new Float32Array(cap * NB); // radius (world px), normalised u
    const final = [];   // final[c] = Float64Array(NB*3) [lo, span, gq] per band
    let cur = null;      // provisional stats for non-final chunks
    let giantPicks = [], gState = { last: -1e9, upto: minN }; // final picks + scan state (points < gState.upto decided)
    let provGiants = [];
    const listeners = [];
    // live settle mode (live sessions only; replay/poster maths unchanged): the provisional scale is refreshed only at
    // n = 10, 20, 30, 45, 60 and then each whole minute, and circles are capped at full size (no burst) until 120 s,
    // so early landings don't re-size the whole sheet every second and the first seconds can't fake a burst.
    const settle = !!opts.liveSettle, REFRESH = new Set([10, 20, 30, 45]); let lastRefresh = 0;
    const isRefresh = m => m < 10 || REFRESH.has(m) || m % 60 === 0;

    function q(arr, m, qq) { return arr[Math.min(m - 1, Math.max(0, Math.floor(qq * (m - 1))))]; }
    function snap(m) { const s = new Float64Array(NB * 3); for (let k = 0; k < NB; k++) { const a = q(sorted[k], m, 0.05), c = q(sorted[k], m, 0.95); s[k * 3] = a; s[k * 3 + 1] = Math.max(c - a, 1e-6); s[k * 3 + 2] = q(sorted[k], m, gq); } return s; }
    const need = c => Math.max(60 * c + 60, 300);
    function statsFor(i) { const c = (i / 60) | 0; return c < final.length ? final[c] : cur; }
    function uOf(i, k, s) { const x = L[i * NB + k]; const lo = s[k * 3], sp = s[k * 3 + 1];
      const b = BANDS[k]; let u = lin[b] ? Math.pow(Math.pow(10, x - (lo + sp * linQ)), lin[b]) : Math.max(0, (x - lo) / sp); if (settle && n < 120) u = Math.min(u, 1); return u; }
    function radius(u, k) { const b = BANDS[k], p = o.pitch, g = (o.gammaB && o.gammaB[b]) || o.gamma;
      const base = o.floor[b] + (o.rmax[b] - o.floor[b]) * Math.pow(Math.min(u, 1), g); const bc = (o.burstB && o.burstB[b]) ?? o.burst;
      const extra = u > 1 ? o.rmax[b] * Math.min(bc - 1, Math.pow(u - 1, 1.3) * 2.2) : 0; return (base + extra) * p; }
    function gz(i, k, s) { return (L[i * NB + k] - s[k * 3 + 2]) / s[k * 3 + 1]; }
    function compute(i) { const s = statsFor(i); for (let k = 0; k < NB; k++) { const u = uOf(i, k, s); U[i * NB + k] = u; R[i * NB + k] = radius(u, k); } }
    function scanGiants(from, to, st, out) { for (let i = Math.max(from, minN); i < to; i++) { if (i - st.last < sep) continue; let best = -1, bk = -1; const s = statsFor(i);
        for (let k = 0; k < NB; k++) { const z = gz(i, k, s); if (z > best) { best = z; bk = k; } } if (best > 0) { out.push([i, bk, best]); st.last = i; } } }
    function grow() { cap *= 2; const nL = new Float64Array(cap * NB); nL.set(L); L = nL; const nR = new Float32Array(cap * NB); nR.set(R); R = nR; const nU = new Float32Array(cap * NB); nU.set(U); U = nU;
      for (let k = 0; k < NB; k++) { const a = new Float64Array(cap); a.set(sorted[k]); sorted[k] = a; } }

    // push one or many points; returns {dirtyFrom} = first point whose geometry changed
    function push(pts) {
      if (!Array.isArray(pts)) pts = [pts]; let dirtyFrom = Math.min(n, final.length * 60);
      for (const p of pts) {
        if (n >= cap) grow();
        for (let k = 0; k < NB; k++) { const x = p.bands[BANDS[k]]; const v = Math.log10(x > 0 ? x : 1e-9); L[n * NB + k] = v;
          const a = sorted[k]; let lo = 0, hi = n; while (lo < hi) { const m = (lo + hi) >> 1; if (a[m] < v) lo = m + 1; else hi = m; } a.copyWithin(lo + 1, lo, n); a[lo] = v; }
        n++;
        while (n === need(final.length)) final.push(snap(n)); // freeze chunk(s) whose prefix just completed (chunks 0-4 all at n=300)
      }
      if (!settle || final.length || !cur) cur = snap(n);
      else { let hit = false; for (let m = n - pts.length + 1; m <= n; m++) if (isRefresh(m)) hit = true; if (hit) { cur = snap(n); lastRefresh = n; } else dirtyFrom = n - pts.length; }
      const firstProv = final.length * 60;
      // recompute: points that were provisional before this batch (stats changed or froze) and all new points
      for (let i = dirtyFrom; i < n; i++) compute(i);
      // giants: finalise picks for points inside frozen chunks, provisional beyond
      const fin = Math.min(firstProv, n); if (gState.upto < fin) { scanGiants(gState.upto, fin, gState, giantPicks); gState.upto = fin; }
      const st = { last: gState.last }; provGiants = []; scanGiants(gState.upto, n, st, provGiants);
      for (const f of listeners) f(dirtyFrom);
      return dirtyFrom;
    }
    function giants() { return giantPicks.concat(provGiants); }
    // nested giant rings: [i, x, y, r, band]
    function giantRings() { const out = []; for (const [i, k, z] of giants()) { const x = (i % o.cols) * o.pitch + o.pitch / 2, y = ((i / o.cols) | 0) * o.pitch + o.pitch / 2;
        const Rg = o.giant * o.pitch * (0.5 + 0.5 * Math.min(1, z * 4)); for (let j = k; j < NB; j++) out.push(i, x, y, Rg * Math.pow(o.giantShrink ?? 0.78, j - k) * (0.6 + 0.4 * Math.min(1, U[i * NB + j])), j); } return out; }
    function refresh() { cur = snap(n); lastRefresh = n; for (let i = final.length * 60; i < n; i++) compute(i); }
    return { o, push, giants, giantRings, refresh, get scaleBasis() { return final.length ? n : lastRefresh; }, get settling() { return settle && n < 300; }, onChange: f => listeners.push(f), get n() { return n; }, get R() { return R; }, get U() { return U; }, get L() { return L; } };
  }
  root.TapestryEngine = { Engine };
})(typeof window !== "undefined" ? window : globalThis);
