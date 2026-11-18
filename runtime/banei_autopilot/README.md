# KeibaMetrics BAN autopilot (ばんえい・帯広) — v4.0-BAN

Spec: Project doc `ケイバメトリクスばんえい版_実装仕様_v4.0-BAN案_20261119.md` (Owner-approved 2026-11-19:
BSI 0.40/0.35/0.25 provisional, TPI adjustments = midpoints, 水分ボンバー 30%, 三連複+三連単, cap 30点, every race,
delivery to a dedicated ばんえい issue). Improve by racing: numbers change only after R30/R100 forward comparison + Owner OK.

| module | status |
|---|---|
| engine.py | Static core: indices (SBO first, own fallback), ISV/LIS, BTA/MPA/BRS, WDA/FLA (no double count), JBR/ADF/BWL/CPU/CCI, DCR, TPI, 3 rankings, roles, marks, F3S/S3H, AKI, ASI |
| tickets.py | universe -> terminals -> 三連複/三連単 shapes (BAN-CAP) -> hole links (BAN-HAC) -> closure -> compression to 30 -> gates/formality |
| render.py | tree text per 買い目表記規格 (LOCAL ticket_tree) |
| collectors | TODO: 楽天(場03) card/odds/result, キンタロー qwYYYYMMDDRR.pdf layout parser, 競馬ブック(場58) bands, 水分ボンバー 帯広 |
| run / delivery / settle / review | TODO: reuse LOCAL autopilot loop; dedicated BAN issue; C0-C6 + First Failure Layer |
