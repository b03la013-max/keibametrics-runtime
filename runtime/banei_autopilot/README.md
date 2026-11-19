# KeibaMetrics BAN autopilot (ばんえい・帯広) — v4.0-BAN

Spec: Project doc `ケイバメトリクスばんえい版_実装仕様_v4.0-BAN案_20261119.md` (Owner-approved 2026-11-19:
BSI 0.40/0.35/0.25 provisional, TPI adjustments = midpoints, 水分ボンバー 30%, 三連複+三連単, cap 30点, every race,
delivery to a dedicated ばんえい issue). Improve by racing: numbers change only after R30/R100 forward comparison + Owner OK.

| module | status |
|---|---|
| engine.py | Static core: indices (SBO first, own fallback), ISV/LIS, BTA/MPA/BRS, WDA/FLA (no double count), JBR/ADF/BWL/CPU/CCI, DCR, TPI, 3 rankings, roles, marks, F3S/S3H, AKI, ASI |
| tickets.py | universe -> terminals -> 三連複/三連単 shapes (BAN-CAP) -> hole links (BAN-HAC) -> closure -> compression to 30 -> gates/formality |
| render.py | tree text per 買い目表記規格 (LOCAL ticket_tree) |
| source.py | 楽天 帯広(baba 03) card parser (3-digit load, 4-digit body weight, past starts), own speed index (speed_model.json, NAR-fit), NAR ledger history (~/Downloads/KM_BAN_NAR), feed loader |
| kintaro.py | キンタロー qwYYYYMMDDRR.pdf download + layout parser: 区間秒 (障害まで/第2障害/障害後), 先行力・障害力・末脚・軽馬場・重馬場 grades |
| run.py | race-day tick: discover -> predict at post-35..6 -> deliver to issue #429 before post-5 -> settle after post+12 (PFS, First Failure Layer) -> README |
| workflow | runs inside km-local-race-day-autopilot.yml on the Owner's Mac (same worker, shared 楽天 throttle), output -> local-autopilot-data:output_ban |
| TODO | 水分ボンバー 帯広 page + 競馬ブック(場58) bands (browser-side collectors -> KM_BAN_FEED_DIR); circled positions meaning in キンタロー; MPA/BRS from segments |
