# 2026-11-23 SAG_08 詳細反省（自動・実購入なし）

- 公式着順：5-2-1-8-7（上位3頭 [5, 2, 1]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 3／2着 2／3着 1；W False・P2 True・P3 False
- Top3捕捉 3／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 500／損益 -200／PFS 71.4%
- 参照：{"revision": "SAG_08.r2", "ticket_sha256": "b3c6f4a1bbbfc5bc0a4928c2d8189216a3c3d22ba08445d2ce939288295d2b12", "frozen_at": "2026-11-23T18:30:15.454662+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 3／3着 1；W True・P2 True・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 1480／損益 -4520／PFS 24.7%
- 参照：{"final_receipt_sha256": "b79430103234c1493fcefb615a280ed6c39c69b4804c2b286be0b8274e3c2786", "result_receipt_sha256": "805f72a6e5c0e2add9d0446ae2acb3d91f9f7e799c4b8475b7c51b95a5e2e359", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "467d1c804a2d6b5f962d645e389bf7ed60a656c45a945074c584669b42a6f2a5", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 3430, "pfs": 26.0}, "effective_revision": "REVISION_1", "source_at": "2026-11-23T09:33:47.179500+00:00", "source_receipt_sha256": "ed496770c3f8b441b857f417baba09443e02b8d80001a8d41a415f6294274462", "signed_final_at": "2026-11-23T09:34:00.804799+00:00", "delivered_ticket_sha256": "8a7b6f4828ae0ccc812bb4e81039cc90efa0670c433f3becaa769934c79b266e", "settled_ticket_sha256": "b79430103234c1493fcefb615a280ed6c39c69b4804c2b286be0b8274e3c2786"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 2, "T3I-L": 3, "HPI-L": 2}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（ドライカプチーノ）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 3, "third_pre_rank": 1, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [5, 2, 1], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_CONFIRMED",  |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 24.7, "profit_loss": -4520, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 24.7, "tickets": 60, "payout": 1480} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `afa8d1c9e60ddfae`／Learning State `9adca954254a`</sub>
