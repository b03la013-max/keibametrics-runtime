// KeibaMetrics JRA — BLOOD BIAS compact capture for Production (browser side, Owner's member session).
// Owner decision 2026-11-14 15:16 (BLOOD BIAS primary, BVI 15% in ZAI); automated 2026-11-28 22:1x
// (「作成する（推奨）」: race-day collection scheduled task). Output is the compact the pack builder reads
// (jra_external_pack_builder.py --bloodb): {captured_at, races:[[rcode, course, "no:CR:GR:W:P:S:T:eval,..."]]}.
// The raw result stays in the PRIVATE evidence repo; the public pack carries only bands (eval marks off).
// Usage (on https://www.blood-b.com, logged in):
//   window.__bbCompact('20261129').then(r => window.__bbCompactRes = r)   // then JSON.stringify(...)
window.__bbCompact = async function (date8, opts) {
  opts = opts || {};
  const gap = Math.max(700, opts.gapMs || 700);
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const T = s => String(s || '').replace(/\s+/g, ' ').trim();
  const get = async u => { const r = await fetch(u, { credentials: 'include', cache: 'no-store' });
    return { url: r.url, doc: new DOMParser().parseFromString(await r.text(), 'text/html') }; };
  const sel = await get('/racesel?rdate=' + date8);
  if (/login/.test(sel.url)) throw new Error('BLOODB_NOT_LOGGED_IN');
  const codes = [...new Set([...sel.doc.querySelectorAll('a[href*="main.php?rcode="]')]
    .map(a => a.getAttribute('href').match(/rcode=(\d+)/)[1]))].filter(c => c.startsWith(date8));
  const races = [];
  for (const rc of codes) {
    await sleep(gap);
    const p = await get('/main.php?rcode=' + rc);
    if (/login/.test(p.url)) throw new Error('BLOODB_NOT_LOGGED_IN');
    const t = p.doc.querySelector('table.tplgrid');
    if (!t) throw new Error('BLOODB_GRID_MISSING ' + rc);
    // header rows: 馬番 馬名 人気ランク 推定人気 相対指数 血統評価 CR GR 血統タイプ(W P S T) ...
    const rows = [...t.rows].slice(2).map(r => [...r.cells].map(c => T(c.innerText))).filter(c => /^\d+/.test(c[0] || ''));
    const cm = T(p.doc.body.innerText).match(/(芝|ダ|障)\s*(\d{3,4})/) || [];
    races.push([rc, cm.length ? cm[1] + cm[2] : '',
      rows.map(c => [parseInt(c[0]), c[6], c[7], c[8], c[9], c[10], c[11], c[5]].join(':')).join(',')]);
  }
  return { captured_at: new Date().toISOString(), races };
};
'defined';
