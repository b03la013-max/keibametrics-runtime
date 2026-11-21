// KeibaMetrics JRA — Keibabook (中央) full per-race page collector (browser side).
// Owner approval 2026-11-21 10:57: collect every per-race page for JRA as well, RECORD ONLY.
// Prediction use stays as before (workout / stable-comment bands from __kmCapture + __kmBands).
// Port of keibabook_local_collect.js to /cyuou/: for each race of date8 it follows that race's own
// sub-menu (出馬表・オッズ・CPU予想・レース結果・対戦成績・調教・能力表・厩舎の話・パドック情報・
// ギリギリ情報・TM直前情報・血統表・過去一覧・前走インタビュー・当該成績・コースデータ・レイティング ...),
// so every page Keibabook offers at that moment is fetched. No download: the gzip JSON is kept in
// the page (window.__kmJraLast = {file, sha256, b64}) for Claude to read back and store in the
// PRIVATE evidence repo only (jra/<date>/keibabook_pages_<HHMM>.json.gz). Nothing goes public.
// Usage: window.__kmJraCollect('20261122',{gapMs:300}).then(r=>window.__kmJobRes=r)
//        paddock re-capture near post time: {only:['パドック情報','ギリギリ情報','ＴＭ直前情報']}
window.__kmJraCollect = async function (date8, opts) {
  opts = opts || {};
  const gap = Math.max(300, opts.gapMs == null ? 300 : opts.gapMs);
  const sleep = ms => new Promise(r => setTimeout(r, ms));
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
    const txt = d.body ? (d.body.innerText || d.body.textContent || "") : "";
    const a = txt.lastIndexOf("確定出馬"), b = txt.indexOf("中央競馬Topへ");
    return { text: clean(txt.slice(a >= 0 ? a + 4 : 0, b > a ? b : undefined)).slice(0, 20000) };
  };
  const top = await get("/cyuou/top");
  if (/login/.test(top.url)) throw new Error("KEIBABOOK_NOT_LOGGED_IN");
  // meeting pages are /cyuou/nittei/<date8><venue code 2 digits> (00 京都, 04 東京, 06 福島, ...)
  const meetings = [...new Set([...top.doc.querySelectorAll("a")].map(a => a.getAttribute("href"))
    .filter(h => h && new RegExp("^/cyuou/nittei/" + date8 + "\\d{2}$").test(h)))];
  const ids = [];
  for (const m of meetings) {
    await sleep(gap);
    const v = await get(m);
    [...v.doc.querySelectorAll("a")].map(a => a.getAttribute("href"))
      .filter(h => h && /^\/cyuou\/syutuba\/\d{12}$/.test(h)).forEach(h => { const id = h.split("/").pop();
        if (!ids.includes(id)) ids.push(id); });
  }
  const races = []; window.__kmJraProg = races;
  for (const id of ids.sort().slice(0, opts.limit || ids.length)) {   // limit: test runs only
    await sleep(gap);
    const s = await get("/cyuou/syutuba/" + id);
    const m = (s.doc.title || "").match(/(\d+)年(\d+)月(\d+)日(\D+?)(\d+)R/);
    if (!m) continue;
    if (opts.venues && !opts.venues.includes(m[4])) continue;
    const seen = new Set([s.url]);
    const links = [...s.doc.querySelectorAll("a")].map(a => [a.innerText.trim(), a.getAttribute("href")])
      .filter(([n, h]) => n && h && h.startsWith("/cyuou/") && h.endsWith(id));
    const pages = { "出馬表": { url: s.url, ...extract(s.doc) } };
    for (const [name, href] of links) {
      if (pages[name] || seen.has(href)) continue;
      seen.add(href);
      if (opts.only && !opts.only.includes(name)) continue;
      await sleep(gap);
      const p = await get(href);
      const body = p.doc.body ? (p.doc.body.innerText || p.doc.body.textContent || "") : "";
      if (p.status !== 200 || /表示できません|存在しません/.test(p.doc.title + body)) {
        pages[name] = { status: p.status, unavailable: true }; continue; }
      pages[name] = { url: p.url, ...extract(p.doc) };
    }
    races.push({ kb_id: id, venue: m[4], race_no: +m[5], title: s.doc.title, pages });
  }
  const out = { profile: "KM-JRA-KEIBABOOK-PAGES-v1", date: date8, record_only: true,
                source: "s.keibabook.co.jp (Owner session)", collected_at: new Date().toISOString(), races };
  const json = JSON.stringify(out);
  const sha = [...new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(json)))]
    .map(x => x.toString(16).padStart(2, "0")).join("");
  const gz = new Uint8Array(await new Response(new Blob([json]).stream()
    .pipeThrough(new CompressionStream("gzip"))).arrayBuffer());
  const hhmm = new Date().toLocaleTimeString("ja-JP", { timeZone: "Asia/Tokyo", hour: "2-digit", minute: "2-digit" }).replace(":", "");
  const name = `keibabook_pages_${opts.only ? "PD" : ""}${hhmm}.json.gz`;   // PD = paddock-only capture
  let bin = ""; for (let i = 0; i < gz.length; i += 0x8000) bin += String.fromCharCode(...gz.subarray(i, i + 0x8000));
  window.__kmJraLast = { file: name, sha256: sha, b64: btoa(bin) };
  return { file: name, sha256: sha, bytes_json: json.length, bytes_gz: gz.length, races: races.length,
           pages: races.reduce((n, r) => n + Object.keys(r.pages).length, 0),
           kinds: [...new Set(races.flatMap(r => Object.keys(r.pages)))] };
};
'defined';
