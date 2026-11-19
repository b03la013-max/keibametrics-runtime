# BAN × NAR official monthly data (2023-01 .. 2026-10)

Input: Owner-downloaded NAR monthly ZIPs on the Owner's Mac (no automated NAR retrieval; Owner 2026-11-19).
Extracted 帯広 only -> ~/Downloads/KM_BAN_NAR/ban_{racelist,horselist,payback}.csv (raw stays on the Mac, not committed).
6,744 races / 63,331 runners. 馬場 column = 馬場水分(%). No barrier/section times in NAR files.

- build.py: runner ledger + own speed index (OLS on load, moisture, moisture^2, 2歳, month, class; fit < 2026 only),
  per-horse 近走 / 同水分帯(馬場) / 近5走平均 computed from strictly earlier runs (no leakage).
- evaluate.py: 2026-01..10 OOS readout (market baseline, BSI, relative load, body-weight change, engine+compiler backtest).
- variant.py: RESEARCH ONLY market-rank blend. Not adopted (needs forward OOS + Owner review; k chosen on the test window).
