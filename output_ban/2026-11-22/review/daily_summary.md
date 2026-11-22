# ばんえい 反省会 2026-11-22

- 精算 12R（締切超過 0R）／投資 34,200円・払戻 21,660円・PFS 63.3%（最高配当1本を除くと 26.7%）
- 三連複 的中 2R・PFS 84.4%／三連単 的中 1R・PFS 42.0%
- ◎ 1着 4・3着内 5／勝ち馬∈W 9・2着∈P2 8・3着∈P3 8
- 最初の断線: {'ROLE': 3, 'HEAD-P2-TERMINAL': 2, 'PAIR-P3-TERMINAL': 5, 'NONE': 1, 'EXACT': 1}／原因コード: {'C1': 1, 'C3': 7, 'C2': 2, 'C4': 1}
- 変換ファネル: 勝ち馬∈W 9 → 1-2着の組 8 → 三連複 2 → 三連単 1 → 収支プラス 2／的中したが投資割れ 0／一極集中 12・最多出現馬が3着外 7
- P0/P1: {'P1:ROLE_W_MISS': 3, 'P1:ROLE_P2_MISS': 4, 'P1:XDI_FINISHER': 3, 'P1:ROLE_P3_MISS': 4}
- 直前見直し（修正版のレース）: Rev1 21,660/19,700円 → Rev2 21,660/19,900円

| R | 着順 | ◎ | 結果 | PFS | 断線 | 原因 | P0/P1 |
|---|---|---|---|---|---|---|---|
| 1 | 1-2-6 | 3 |  | 0.0 | ROLE | C1 | P1:ROLE_W_MISS |
| 2 | 4-7-9 | 4 |  | 0.0 | HEAD-P2-TERMINAL | C3 | P1:ROLE_P2_MISS P1:XDI_FINISHER |
| 3 | 9-5-8 | 6 |  | 0.0 | HEAD-P2-TERMINAL | C3 | P1:ROLE_P2_MISS |
| 4 | 4-5-6 | 4 |  | 0.0 | PAIR-P3-TERMINAL | C3 | P1:ROLE_P3_MISS |
| 5 | 8-2-9 | 6 |  | 0.0 | PAIR-P3-TERMINAL | C3 | P1:ROLE_P3_MISS P1:XDI_FINISHER |
| 6 | 3-9-5 | 5 |  | 0.0 | ROLE | C2 | P1:ROLE_W_MISS P1:ROLE_P2_MISS |
| 7 | 5-7-2 | 10 |  | 0.0 | PAIR-P3-TERMINAL | C3 |  |
| 8 | 2-4-9 | 2 | 三連単 | 277.7 | NONE |  |  |
| 9 | 10-5-2 | 1 |  | 0.0 | PAIR-P3-TERMINAL | C3 | P1:ROLE_P3_MISS P1:XDI_FINISHER |
| 10 | 7-3-8 | 7 | 三連複 | 444.3 | EXACT | C4 | P1:ROLE_P2_MISS |
| 11 | 7-8-6 | 9 |  | 0.0 | PAIR-P3-TERMINAL | C3 | P1:ROLE_P3_MISS |
| 12 | 9-1-3 | 5 |  | 0.0 | ROLE | C2 | P1:ROLE_W_MISS |

数値の変更は単日では行わない（R30/R100の未来レース比較＋Owner承認）。P0のコード欠陥は夜間の自動作業で修正する。
