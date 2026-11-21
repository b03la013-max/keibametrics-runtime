// KeibaMetrics JRA — BLOOD BIAS deep capture (browser side, Owner approval 2026-11-21 10:54).
// Runs in the Owner's logged-in blood-b.com tab. RECORD ONLY: the result goes to the
// private evidence repo; nothing from it is published or used in predictions.
// Per race: 詳細データ, 傾向集計, BBコース, BB当日, BB前日, BB前週, 亀谷Point.
// Site-wide: 馬場コラム (/babacol?dt=&sm=0..2), 重賞コラム (/jyu1col, /jyu2col), ドル箱 (/dorubako).
// Usage: window.__bbDeep('20261122',{only:['bbtoday']}).then(r=>window.__bbDeepRes=r)
//        then read window.__bbDeepLast.b64 (gzip+base64 JSON) once.
window.__bbDeep = async function (date8, opts) {
  opts = opts || {};
  const gap = Math.max(700, opts.gapMs || 700);
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const T = s => String(s || '').replace(/[ \t　]+/g, ' ').replace(/\n\s*\n+/g, '\n').trim();
  const PAGES = { kjouhou: '/kjouhou.php', keikou: '/keikou.php', bbcourse: '/bbcourse.php',
                  bbtoday: '/bbtoday.php', bbyesterday: '/bbyesterday.php', bblweek: '/bblweek.php',
                  kpoint: '/kpoint.php' };
  const want = opts.only || Object.keys(PAGES);
  const get = async u => { const r = await fetch(u, { credentials: 'include', cache: 'no-store' });
    return { status: r.status, url: r.url, doc: new DOMParser().parseFromString(await r.text(), 'text/html') }; };
  const page = g => ({ status: g.status, url: g.url, title: g.doc.title,
    tables: [...g.doc.querySelectorAll('table')].filter(t => t.rows.length > 1).map(t =>
      [...t.rows].map(r => [...r.cells].map(c => T(c.innerText)))),
    text: T(g.doc.body ? g.doc.body.innerText : '').slice(0, 20000) });
  const sel = await get('/racesel?rdate=' + date8);
  if (/login/.test(sel.url)) throw new Error('BLOODB_NOT_LOGGED_IN');
  const codes = [...new Set([...sel.doc.querySelectorAll('a[href*="main.php?rcode="]')]
    .map(a => a.getAttribute('href').match(/rcode=(\d+)/)[1]))];
  const out = { profile: 'KM-JRA-BLOODB-DEEP-CAPTURE-v1', date8, captured_at: new Date().toISOString(),
                record_only: true, races: {}, site: {} };
  window.__bbDeepProg = out;
  for (const rc of codes) {
    out.races[rc] = {};
    for (const k of want) { if (!PAGES[k]) continue; await sleep(gap);
      try { out.races[rc][k] = page(await get(PAGES[k] + '?rcode=' + rc)); }
      catch (e) { out.races[rc][k] = { error: String(e) }; } }
  }
  if (!opts.only) {
    // 馬場コラム (per venue tab sm=0..2), 重賞コラム, 重賞コラム(平日版), ドル箱ホースリスト.
    const site = [['babacol_0', '/babacol?dt=' + date8 + '&sm=0'], ['babacol_1', '/babacol?dt=' + date8 + '&sm=1'],
                  ['babacol_2', '/babacol?dt=' + date8 + '&sm=2'], ['jyu1col', '/jyu1col'], ['jyu2col', '/jyu2col'],
                  ['dorubako', '/dorubako']];
    for (const [k, u] of site) { await sleep(gap);
      try { out.site[k] = page(await get(u)); } catch (e) { out.site[k] = { error: String(e) }; } }
  }
  const json = JSON.stringify(out);
  const buf = await new Response(new Blob([json]).stream().pipeThrough(new CompressionStream('gzip'))).arrayBuffer();
  const hash = [...new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(json)))]
    .map(b => b.toString(16).padStart(2, '0')).join('');
  let bin = ''; const u8 = new Uint8Array(buf); for (let i = 0; i < u8.length; i += 0x8000) bin += String.fromCharCode(...u8.subarray(i, i + 0x8000));
  window.__bbDeepLast = { b64: btoa(bin), sha256: hash };
  return { races: codes.length, pages: want.length, bytes: json.length, gz: u8.length, sha256: hash, done: true };
};
'defined';
