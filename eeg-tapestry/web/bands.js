// Raw EEG -> NeuroSky-style band powers for one 1-second window (no deps).
(function (root) {
  const EDGES = { delta: [0.5, 2.75], theta: [3.5, 6.75], low_alpha: [7.5, 9.25], high_alpha: [10, 11.75],
    low_beta: [13, 16.75], high_beta: [18, 29.75], low_gamma: [31, 39.75], high_gamma: [41, 49.75] };
  function fftMag2(x) { // radix-2 real FFT via complex in-place; x.length must be a power of two
    const n = x.length, re = Float64Array.from(x), im = new Float64Array(n);
    for (let i = 1, j = 0; i < n; i++) { let bit = n >> 1; for (; j & bit; bit >>= 1) j ^= bit; j ^= bit; if (i < j) { [re[i], re[j]] = [re[j], re[i]]; } }
    for (let len = 2; len <= n; len <<= 1) { const a = -2 * Math.PI / len, wr = Math.cos(a), wi = Math.sin(a);
      for (let i = 0; i < n; i += len) { let cr = 1, ci = 0;
        for (let k = 0; k < len / 2; k++) { const ur = re[i + k], ui = im[i + k], vr = re[i + k + len / 2] * cr - im[i + k + len / 2] * ci, vi = re[i + k + len / 2] * ci + im[i + k + len / 2] * cr;
          re[i + k] = ur + vr; im[i + k] = ui + vi; re[i + k + len / 2] = ur - vr; im[i + k + len / 2] = ui - vi; const t = cr * wr - ci * wi; ci = cr * wi + ci * wr; cr = t; } } }
    const p = new Float64Array(n / 2 + 1); for (let k = 0; k <= n / 2; k++) p[k] = re[k] * re[k] + im[k] * im[k]; return p;
  }
  // samples: array of channels, each Float array of length fs (1 s). Returns {bands, quality[]}.
  function bandPowers(channels, fs) {
    let n = 1; while (n < fs) n <<= 1; const out = {}; for (const b in EDGES) out[b] = 0; const quality = [];
    for (const ch of channels) {
      const m = ch.reduce((a, b) => a + b, 0) / ch.length; const sd = Math.sqrt(ch.reduce((a, b) => a + (b - m) ** 2, 0) / ch.length);
      quality.push(sd < 1 ? "flat" : sd > 120 ? "noisy" : "good"); // µV: dry electrodes off-skin read flat or huge
      ch._m = m;
      const x = new Float64Array(n); let wsum = 0;
      for (let i = 0; i < ch.length; i++) { const w = 0.5 - 0.5 * Math.cos(2 * Math.PI * i / ch.length); /* periodic Hann, as scipy */ x[i] = (ch[i] - m) * w; wsum += w * w; }
      const p = fftMag2(x), df = fs / n;
      // one-sided PSD density (as scipy.signal.welch, Hann, nperseg = 1 s), trapezoid-integrated over bins in [lo, hi] (as np.trapezoid)
      for (const b in EDGES) { const [lo, hi] = EDGES[b]; let s = 0, prev = -1; for (let k = Math.ceil(lo / df); k * df <= hi && k < p.length; k++) { const d = p[k] * (k === 0 || k === n / 2 ? 1 : 2) / (wsum * fs); if (prev >= 0) s += (prev + d) / 2 * df; prev = d; } out[b] += s / channels.length; }
    }
    // a blink/eye movement swings both forehead channels (AF7, AF8 = 1, 2) together; that is signal, not bad contact
    if (channels.length === 4 && quality[1] === "noisy" && quality[2] === "noisy" && quality[0] !== "noisy" && quality[3] !== "noisy") {
      const a = channels[1], b = channels[2], ma = a._m, mb = b._m; let sab = 0, saa = 0, sbb = 0, peak = 0;
      for (let i = 0; i < a.length; i++) { const x = a[i] - ma, y = b[i] - mb; sab += x * y; saa += x * x; sbb += y * y; peak = Math.max(peak, Math.abs(x), Math.abs(y)); }
      if (sab / Math.sqrt(saa * sbb + 1e-9) > 0.8 && peak < 600) { quality[1] = quality[2] = "blink"; } }
    if (channels.length === 4 && (quality[1] === "noisy") !== (quality[2] === "noisy")) { // one forehead channel high: check if it's a blink seen mostly on that side
      const i1 = quality[1] === "noisy" ? 1 : 2, a = channels[1], b = channels[2]; let sab = 0, saa = 0, sbb = 0;
      for (let i = 0; i < a.length; i++) { const x = a[i] - a._m, y = b[i] - b._m; sab += x * y; saa += x * x; sbb += y * y; }
      if (sab / Math.sqrt(saa * sbb + 1e-9) > 0.8) quality[i1] = "blink"; }
    return { bands: out, quality };
  }
  root.EEGBands = { EDGES, bandPowers };
})(typeof window !== "undefined" ? window : globalThis);
