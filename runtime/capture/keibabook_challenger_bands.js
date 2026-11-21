// KeibaMetrics JRA — Keibabook challenger bands (browser side). CHALLENGER / RECORD ONLY.
// Owner instruction 2026-11-21 22:20: connect collected information to the indices and fill the
// features that were 0% observed on 11/21 (224 runners): workout_load, workout_partner_level,
// workout_consistency, stable_readiness. Runs in the Owner's logged-in Keibabook tab; only bands
// leave the page (no comment text, no times). Production features/weights are NOT fed from here;
// runtime/analysis/jra_index_research.py reads these as Challenger inputs.
// Rules: KM-JRA-KB-CHALLENGER-BANDS-v1
//   trend     : 調教欄の矢印  ↗/↑ UP, → FLAT, ↘/↓ DOWN
//   load      : 最新追い切りの強弱  一杯 HIGH, 強め MEDIUM_HIGH, 末強め/G前仕掛け MEDIUM, 馬なり LOW
//   partner   : 併せ馬の結果  先着 AHEAD, 同入 EVEN, 遅れ BEHIND, 単走 SOLO
//   readiness : 攻め解説＋厩舎の話の仕上がり語  READY / NOT_READY / NEUTRAL
// Usage: window.__kmChallenger('20261122', ['04','00']).then(r => window.__kmChRes = r)
window.__kmChallenger = async function (date8, codes, opts) {
  opts = opts || {};
  const gap = Math.max(300, opts.gapMs || 600);
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const T = n => n ? n.textContent.replace(/\s+/g, ' ').trim() : '';
  const doc = async p => new DOMParser().parseFromString(await (await fetch(p, { credentials: 'include' })).text(), 'text/html');
  const trend = s => /[↗↑]/.test(s) ? 'UP' : /[↘↓]/.test(s) ? 'DOWN' : /→/.test(s) ? 'FLAT' : null;
  const load = s => !s ? null : /一杯/.test(s) ? 'HIGH' : /末強め|G前|Ｇ前|仕掛/.test(s) ? 'MEDIUM'
                   : /強め/.test(s) ? 'MEDIUM_HIGH' : /馬なり/.test(s) ? 'LOW' : null;
  const partner = s => /先着/.test(s) ? 'AHEAD' : /同入/.test(s) ? 'EVEN' : /遅れ/.test(s) ? 'BEHIND' : 'SOLO';
  const POS = ['仕上がり良', '仕上がりは良', '好仕上がり', '態勢整', '態勢は整', '万全', '上々', 'スカッと', '具合良', '状態良', '絶好'];
  const NEG = ['太め', '余裕残し', '重め', '使いつつ', '良化途上', '叩いて', '一息', 'もう一つ', '本調子手前', '緩さ'];
  const ready = t => { const p = POS.some(x => t.includes(x)), n = NEG.some(x => t.includes(x));
    return p && !n ? 'READY' : n && !p ? 'NOT_READY' : 'NEUTRAL'; };
  const out = { profile: 'KM-JRA-KB-CHALLENGER-BANDS-v1', date8, captured_at: new Date().toISOString(),
                challenger_only: true, production_effect: 'NONE', races: [] };
  window.__kmChProg = out;
  for (const code of codes) {
    const day = await doc('/cyuou/nittei/' + date8 + code);
    const ids = [...new Set([...day.querySelectorAll('a[href*="/cyuou/syutuba/"]')]
      .map(a => a.getAttribute('href').split('/').pop()))].filter(x => /^\d{12}$/.test(x)).slice(0, opts.limit || 99);
    for (const id of ids) {
      await sleep(gap); const c = await doc('/cyuou/cyokyo/0/' + id);
      await sleep(gap); const d = await doc('/cyuou/danwa/0/' + id);
      const danwa = {};
      for (const row of d.querySelectorAll('tr')) { const no = row.querySelector('td.umaban'); if (!no) continue;
        const cell = row.nextElementSibling && row.nextElementSibling.querySelector('td.danwa'); danwa[T(no)] = T(cell); }
      const horses = [];
      for (const row of c.querySelectorAll('tr')) {
        if (!row.querySelector('td.kbamei')) continue;
        const no = T(row.querySelector('td.umaban')), det = row.nextElementSibling;
        let latest = null, n = 0;
        if (det) for (const dl of det.querySelectorAll('dl.dl-table')) {
          const dts = [...dl.children].filter(x => x.tagName === 'DT').map(T);
          if (dts.length < 3 || dts[0] === '(前回)') continue;
          n += 1; if (!latest) { let t = dl.nextElementSibling; while (t && t.tagName !== 'TABLE') t = t.nextElementSibling;
            latest = { gait: dts[2], data: T(t) }; }
        }
        const seme = det ? T(det.querySelector('.semekaisetu')) : '';
        horses.push({ no, trend: trend(T(row.querySelector('td.yajirusi'))), load: latest ? load(latest.gait) : null,
                      partner: latest ? partner(latest.data) : null, workouts_listed: n,
                      readiness: ready(seme + ' ' + (danwa[no] || '')) });
      }
      out.races.push({ kb_id: id, title: (c.title || '').split(' | ')[1] || c.title, horses });
    }
  }
  return out;
};
'defined';
