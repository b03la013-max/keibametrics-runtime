// KeibaMetrics JRA — 統計ショッカーリミテッド (jra.k-ba.net) full capture (browser side).
// Owner approval 2026-11-21 10:56. RECORD ONLY except the 印, which keeps feeding VMI as before.
// Per race: 印, 単勝/複勝/馬連 得票率 and their colour classes, odds trend, 断層・拮抗・異常 signs,
// 推奨買い目 (波乱度・軸・本線・次点・おさえ), odds time. Full result goes to the private repo only.
// Usage: window.__tslFull('20261122', ['0520260505','0820260506'], 'last').then(r=>window.__tslFullRes=r)
//        r.marks = "venue/RR|印列;..." for tsl_update.py; window.__tslFullLast.b64 = gzip+base64 JSON.
window.__tslFull = async function (date8, venues, kind, opts) {
  kind = kind || 'last'; opts = opts || {};
  const gap = Math.max(300, opts.gapMs || 400);
  const tx = c => c.innerText.trim();
  const parse = d => {
    const tb = [...d.querySelectorAll('table')].sort((a, b) => b.rows.length - a.rows.length)[0];
    const H = []; let cur = null;
    if (tb) for (const r of tb.rows) { const c = [...r.cells];
      if (c.length === 9 && /^\d+$/.test(tx(c[0]))) {
        cur = { no: +tx(c[0]), mark: tx(c[1]) || null, vote_win: +tx(c[3]) || null, vote_place: +tx(c[4]) || null,
                vote_quinella: +tx(c[5]) || null, dansou: tx(c[6]) || null, kikkou: tx(c[7]) || null, ijou: tx(c[8]) || null,
                color: [c[3].className, c[4].className, c[5].className] };
        H.push(cur);
      } else if (c.length === 3 && cur && !cur.trend) cur.trend = c.map(x => +tx(x)); }
    const t = d.body ? d.body.innerText : '';
    // The page repeats 推奨買い目 in a help line; the block that matters starts at 波乱度.
    const i = t.indexOf('波乱度'); const j = t.indexOf('(1)', i);
    const rec = i >= 0 ? t.slice(i, j > i ? j : i + 300).trim() : null;
    // odds_at is the page's own label, e.g. 最終オッズ.
    const g = k => { const m = rec && rec.match(new RegExp(k + ':[ \\t]*([^\\n]*)')); return m ? m[1].trim() : null; };
    return { title: d.title, odds_at: (t.match(/\d+日\s+(\S*オッズ)/) || [])[1] || null, horses: H,
             rec: rec ? { volatility: g('波乱度'), axis: g('軸'), main: g('本線'), second: g('次点'), cover: g('おさえ'), raw: rec } : null };
  };
  const out = { profile: 'KM-JRA-TSL-FULL-CAPTURE-v1', date8, kind, captured_at: new Date().toISOString(),
                record_only_except_marks: true, races: [] };
  for (const v of venues) for (let n = 1; n <= 12; n++) {
    const u = `/${date8}/${v}/${String(n).padStart(2, '0')}/${kind}.html`;
    try { const r = await fetch(u, { cache: 'no-store' });
      const p = parse(new DOMParser().parseFromString(await r.text(), 'text/html'));
      if (p.horses.length) out.races.push({ key: `${v}/${String(n).padStart(2, '0')}`, url: u, ...p });
    } catch (e) { out.races.push({ key: `${v}/${String(n).padStart(2, '0')}`, url: u, error: String(e) }); }
    await new Promise(r => setTimeout(r, gap));
  }
  const json = JSON.stringify(out);
  const buf = await new Response(new Blob([json]).stream().pipeThrough(new CompressionStream('gzip'))).arrayBuffer();
  const hash = [...new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(json)))]
    .map(b => b.toString(16).padStart(2, '0')).join('');
  let bin = ''; const u8 = new Uint8Array(buf); for (let i = 0; i < u8.length; i += 0x8000) bin += String.fromCharCode(...u8.subarray(i, i + 0x8000));
  window.__tslFullLast = { b64: btoa(bin), sha256: hash };
  const marks = out.races.filter(r => r.horses && r.horses.length).map(r => r.key + '|' + r.horses.map(h => h.mark || '_').join('')).join(';');
  return { races: out.races.length, gz: u8.length, sha256: hash, marks, done: true };
};
'defined';
