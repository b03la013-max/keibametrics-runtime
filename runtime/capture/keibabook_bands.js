// KeibaMetrics JRA — Keibabook workout / stable-comment band calculator (browser side).
// Runs in the Owner's logged-in Keibabook tab on compact captures; only bands leave the page.
// Rules: JRA-WORKOUT-CAPABILITY-COMMENT-v1, JRA-WORKOUT-FINAL1F-BAND-v1 (v2: U9 adds 美Ｗ and
// polytrack, Owner approved 2026-11-15 19:50), KM-JRA-STABLE-COMMENT-STATE-v1.
window.__kmBands = function (c) {
  const cb = t => { t = String(t);
    if (["絶好","抜群","文句なし","充実"].some(x => t.includes(x))) return "VERY_STRONG";
    if (["上向","良化","楽しみ","期待","順調","好調","仕上がり良好","動き良"].some(x => t.includes(x))) return "STRONG";
    if (["使いつつ","緩い","展開の助け","一変までは","様子","半信半疑","慣れ"].some(x => t.includes(x))) return "CAUTION";
    return "NEUTRAL"; };
  // final-1F thresholds (sec). WOOD = 栗ＣＷ・美Ｗ; POLY = 栗Ｐ・美Ｐ (0.2s tighter); SLOPE = 坂路.
  const T = { WOOD: [11.5, 11.8, 12.1, 12.5, 12.9], POLY: [11.3, 11.6, 11.9, 12.3, 12.7],
              SLOPE: [12.1, 12.4, 12.7, 13.0, 13.5] };
  const B = ["EXCEPTIONAL", "VERY_STRONG", "STRONG", "POSITIVE", "NEUTRAL"];
  const wb = (s, co) => { const t = T[co]; for (let i = 0; i < t.length; i++) if (s <= t[i]) return B[i]; return "CAUTION"; };
  const course = dc => /ＣＷ|CW/.test(dc) ? "WOOD" : /美Ｗ|美W/.test(dc) ? "WOOD"
                   : /[栗美]Ｐ|[栗美]P/.test(dc) ? "POLY" : dc.includes("坂") ? "SLOPE" : null;
  const y = +c.date8.slice(0, 4), rd = new Date(y, +c.date8.slice(4, 6) - 1, +c.date8.slice(6, 8));
  return c.races.map(r => { const S = Object.fromEntries(r.s); return { id: r.id, t: r.t,
    h: r.w.map(([no, name, ass, rows]) => { let sel = null;
      for (const [dc, f] of rows) { const m = dc.match(/(\d{1,2})\/(\d{1,2})/); if (!m) continue;
        const d = new Date(y, +m[1] - 1, +m[2]); const age = (rd - d) / 864e5; if (age <= 0 || age > 60) continue;
        const co = course(dc);
        if (co && typeof f === "number" && f >= 8 && f <= 20 && (!sel || d >= sel.d)) sel = { d, co, f }; }
      return { no, name, wcap: ass ? cb(ass) : null, wspd: sel ? wb(sel.f, sel.co) : null,
               wsrc: sel ? sel.co + ":" + sel.f : null, stab: S[no] ? cb(S[no]) : null }; }) }; });
};
if (typeof module !== "undefined") module.exports = { __kmBands: window.__kmBands };
