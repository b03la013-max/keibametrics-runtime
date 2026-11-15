// KeibaMetrics LOCAL — Keibabook (地方) full per-race page collector (browser side).
// Owner instructions 2026-11-15 21:19 / 21:27 JST: collect every per-race page automatically
// (出馬表・オッズ・能力表HTML・レース結果・対戦成績・調教・厩舎の話・パドック情報・ポイント・
// 当該成績・血統表 ...) on the Owner's responsibility, in the Owner's logged-in session.
//
// For each race of date8 it follows that race's own sub-menu, so every page Keibabook
// offers at that moment is fetched (パドック情報 / レース結果 appear only on race day /
// after the race; venues where Keibabook does not offer a page simply have no link).
// Per page it keeps the data tables as rows of cell text (site chrome removed) or, for
// table-less pages, the content text. Output is downloaded as a gzip JSON file
// (km_local_kb_<date8>_<HHMM>.json.gz) into the Owner's Downloads folder; it is for the
// PRIVATE evidence repository only. The public repository receives bands only
// (window.__kmLocalBands in keibabook_local_bands.js computes them from the same pages).
window.__kmLocalCollect = async function (date8, opts) {
  opts = opts || {};
  const gap = opts.gapMs == null ? 300 : opts.gapMs;
  // hidden panes throttle timers heavily: gap 0 = paced by the network round-trip only
  const sleep = ms => ms > 0 ? new Promise(r => setTimeout(r, ms)) : Promise.resolve();
  const chrome = /^(default ?|open|open sub|syokin)$/;
  const clean = s => String(s || "").replace(/[ \t　]+/g, " ").replace(/\n\s*\n+/g, "\n").trim();
  const get = async p => { const r = await fetch(p, { credentials: "include" });
    return { status: r.status, url: r.url.replace(location.origin, ""),
             doc: new DOMParser().parseFromString(await r.text(), "text/html") }; };
  const extract = d => {
    const tables = [...d.querySelectorAll("table")].filter(t => !chrome.test(t.className.trim())
      && !t.parentElement.closest("table"));
    if (tables.length) return { tables: tables.map(t => ({ cls: t.className.trim(),
      rows: [...t.rows].map(tr => [...tr.cells].map(c => clean(c.innerText || c.textContent))) })) };
    const txt = d.body.innerText || d.body.textContent || "";
    const a = txt.lastIndexOf("血統表"), b = txt.indexOf("地方競馬Topへ");
    return { text: clean(txt.slice(a >= 0 ? a + 3 : 0, b > a ? b : undefined)).slice(0, 20000) };
  };
  const top = await get("/chihou/top");
  const meetings = [...new Set([...top.doc.querySelectorAll("a")].map(a => a.getAttribute("href"))
    .filter(h => h && h.startsWith("/chihou/nittei/" + date8)))];
  const ids = [];
  for (const m of meetings) {
    await sleep(gap);
    const v = await get(m);
    [...v.doc.querySelectorAll("a")].map(a => a.getAttribute("href"))
      .filter(h => h && /^\/chihou\/syutuba\/\d{16}$/.test(h)).forEach(h => { const id = h.split("/").pop();
        if (!ids.includes(id)) ids.push(id); });
  }
  const races = [];
  for (const id of ids.sort()) {
    await sleep(gap);
    const s = await get("/chihou/syutuba/" + id);
    const m = (s.doc.title || "").match(/(\d+)年(\d+)月(\d+)日(\D+?)(\d+)R/);
    if (!m) continue;
    if (opts.venues && !opts.venues.includes(m[4])) continue;
    if ((opts.exclude || ["帯広"]).includes(m[4])) continue;   // ばんえい is a separate system
    const links = [...s.doc.querySelectorAll("table.open.sub a")]
      .map(a => [a.innerText.trim(), a.getAttribute("href")]).filter(([, h]) => h && h.includes(id));
    const pages = { "出馬表": { url: s.url, ...extract(s.doc) } };
    for (const [name, href] of links) {
      if (pages[name]) continue;
      await sleep(gap);
      const p = await get(href);
      if (p.status !== 200 || /表示できません|存在しません/.test(p.doc.title + (p.doc.body.innerText || p.doc.body.textContent || ""))) {
        pages[name] = { status: p.status, unavailable: true }; continue; }
      pages[name] = { url: p.url, ...extract(p.doc) };
    }
    races.push({ kb_id: id, venue: m[4], race_no: +m[5], title: s.doc.title, pages });
  }
  const bands = window.__kmLocalBands ? await window.__kmLocalBands(date8, { gapMs: gap }) : null;
  const out = { date: date8, source: "s.keibabook.co.jp (Owner session)", collected_at: new Date().toISOString(),
                races, bands };
  const json = JSON.stringify(out);
  const sha = [...new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(json)))]
    .map(x => x.toString(16).padStart(2, "0")).join("");
  const gz = await new Response(new Blob([json]).stream().pipeThrough(new CompressionStream("gzip"))).blob();
  const hhmm = new Date().toLocaleTimeString("ja-JP", { timeZone: "Asia/Tokyo", hour: "2-digit", minute: "2-digit" }).replace(":", "");
  const name = `km_local_kb_${date8}_${hhmm}.json.gz`;
  if (opts.download !== false) {
    const a = document.createElement("a"); a.href = URL.createObjectURL(gz); a.download = name;
    document.body.appendChild(a); a.click(); a.remove();
  }
  return { file: name, sha256: sha, bytes_json: json.length, bytes_gz: gz.size, races: races.length,
           pages: races.reduce((n, r) => n + Object.keys(r.pages).length, 0),
           kinds: [...new Set(races.flatMap(r => Object.keys(r.pages)))],
           bands_races: bands ? bands.races.length : 0 };
};
