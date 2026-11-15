// KeibaMetrics LOCAL — Keibabook (地方) workout / stable-comment band capture (browser side).
// Runs in the Owner's logged-in s.keibabook.co.jp tab (Owner instruction 2026-11-15 21:19 JST:
// automatic acquisition on the Owner's responsibility). Only BANDS leave the page: no comment
// text, no times, no raw HTML is returned or stored.
// Coverage: Keibabook provides 調教 / 厩舎の話 for 南関東 only (others: 提供外 -> no bands).
// Rules: KM-LOCAL-WORKOUT-COMMENT-v1 (短評 dictionary + trend arrow),
//        KM-LOCAL-STABLE-COMMENT-v1 (厩舎の話 dictionary + stable mark ◎/○/△).
// Usage (in the tab):  await window.__kmLocalBands('20261116')  -> {date, races:[...]}
window.__kmLocalBands = async function (date8, opts) {
  opts = opts || {};
  const gap = opts.gapMs || 2500;                       // polite spacing between page loads
  // hidden panes throttle timers heavily: gap 0 = paced by the network round-trip only
  const sleep = ms => ms > 0 ? new Promise(r => setTimeout(r, ms)) : Promise.resolve();
  const L = ["VERY_STRONG", "STRONG", "NEUTRAL", "CAUTION"];
  const shift = (b, d) => L[Math.max(0, Math.min(3, L.indexOf(b) - d))];
  const band = t => { t = String(t || "");
    if (["変わり身まで", "どうかな", "案外", "今ひと息", "今一息", "手控え", "平凡", "心配", "気難しい",
         "大きくは変わらない", "物足りない", "反応鈍", "重め", "太め残り", "様子見"].some(x => t.includes(x))) return "CAUTION";
    if (["絶好", "抜群", "文句なし", "充実", "期待大", "好調持続", "勝ち負け", "態勢万全"].some(x => t.includes(x))) return "VERY_STRONG";
    if (["上向", "良化", "楽しみ", "動き軽快", "素軽", "フットワーク軽快", "状態は良く", "具合はいい", "デキはいい",
         "前進", "上位争い", "期待", "好調", "仕上がり良好", "動き良", "伸び脚"].some(x => t.includes(x))) return "STRONG";
    return "NEUTRAL"; };
  const get = async p => { const r = await fetch(p, { credentials: "include" });
    return { ok: r.ok && !/\/syutuba\//.test(r.url) || /\/syutuba\//.test(p), url: r.url,
             doc: new DOMParser().parseFromString(await r.text(), "text/html") }; };
  const venues = new Set(opts.venues || ["大井", "川崎", "船橋", "浦和"]);
  const day = await get("/chihou/top");
  const ids = new Set();
  for (const code of [...new Set([...day.doc.querySelectorAll("a")].map(a => a.getAttribute("href"))
        .filter(h => h && h.startsWith("/chihou/nittei/" + date8)))]) {
    await sleep(gap);
    const v = await get(code);
    [...v.doc.querySelectorAll("a")].map(a => a.getAttribute("href"))
      .filter(h => h && /^\/chihou\/syutuba\/\d{16}$/.test(h)).forEach(h => ids.add(h.split("/").pop()));
  }
  const races = [], skipped = {};
  for (const id of [...ids].sort()) {
    const vk = id.slice(0, 10);                          // one meeting = one id prefix
    if (skipped[vk]) continue;
    await sleep(gap);
    const cy = await get("/chihou/cyokyo/1/" + id);
    const m = (cy.doc.title || "").match(/(\d+)年(\d+)月(\d+)日(\D+?)(\d+)R/);
    if (!m || !venues.has(m[4]) || !/^調教/.test(cy.doc.title)) {   // 提供外 -> redirected to 出馬表
      skipped[vk] = m ? m[4] : "?"; continue; }
    const horses = {};
    for (const tr of cy.doc.querySelectorAll("table.cyokyo > tbody > tr")) {
      const no = tr.querySelector("td.umaban"); if (!no) continue;
      const tp = tr.querySelector("td.tanpyo"), ar = tr.querySelector("td.yajirusi");
      let b = band(tp && tp.textContent);
      const a = ar ? ar.textContent.trim() : "";
      if (a.includes("↗")) b = shift(b, 1); else if (a.includes("↘")) b = shift(b, -1);
      horses[+no.textContent.trim()] = { tri: b };
    }
    await sleep(gap);
    const dw = await get("/chihou/danwa/1/" + id);
    if (/^厩舎の話/.test(dw.doc.title)) {
      for (const td of dw.doc.querySelectorAll("table.danwa td.umaban")) {
        const nx = td.closest("tr").nextElementSibling;
        const c = nx && nx.querySelector("td.danwa");
        if (!c) continue;
        const t = c.textContent.trim(), mk = t.charAt(0);
        let b = band(t.replace(/^.?【[^】]*】/, ""));
        if (mk === "◎") b = shift(b, 1); else if (mk === "△") b = shift(b, -1);
        (horses[+td.textContent.trim()] = horses[+td.textContent.trim()] || {}).cci = b;
      }
    }
    races.push({ kb_id: id, venue: m[4], race_no: +m[5], horses });
  }
  return { date: date8, source: "s.keibabook.co.jp (Owner session)", rules: ["KM-LOCAL-WORKOUT-COMMENT-v1",
           "KM-LOCAL-STABLE-COMMENT-v1"], captured_at: new Date().toISOString(),
           not_provided: Object.values(skipped), races };
};
