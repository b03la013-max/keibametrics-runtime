# 2026-11-22 KOC_10 詳細反省（自動・実購入なし）

- 公式着順：4-6-2-5-1（上位3頭 [4, 6, 2]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 2／2着 6／3着 1；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 240／損益 -460／PFS 34.3%
- 参照：{"revision": "KOC_10.r2", "ticket_sha256": "861b2fb1e6eb5d6a1f769606b407382408d62d81cb471b994de8d9e7862383fa", "frozen_at": "2026-11-22T19:35:14.071436+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 3／3着 1；W True・P2 True・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 1470／損益 -4530／PFS 24.5%
- 参照：{"final_receipt_sha256": "ca639c1af317b9e0f99dd02ea566ca2a8ee6dbf8b715ccb436ca7b1f2c437bff", "result_receipt_sha256": "ecfd2cba03556e03e66370d736015720aa2893cfd2b6f8507b2af9674eaa6415", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "362748b514ff26e6efc263efde7e459f67925be02dfece5ed1496c8feeb1fb0d", "signed_final_ticket_count": 90, "signed_final_total_investment": 9000, "signed_final_settlement": {"invest": 9000, "refund": 0, "effective_invest": 9000, "payout": 4060, "pfs": 45.1}, "effective_revision": "REVISION_1", "source_at": "2026-11-22T10:40:25.453193+00:00", "source_receipt_sha256": "8851c45f78487cd6b1c5800aa9dd8483428dca47fc4218463233ff6c7ab571cb", "signed_final_at": "2026-11-22T10:40:35.724690+00:00", "delivered_ticket_sha256": "1739655c66dd6c28e4c5b36890032055317bb6283ae67c0207ca59297438734a", "settled_ticket_sha256": "ca639c1af317b9e0f99dd02ea566ca2a8ee6dbf8b715ccb436ca7b1f2c437bff"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 3, "T3I-L": 4, "HPI-L": 3}, "ruled_neutral_share": 0.074} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補4頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 3, "third_pre_rank": 1, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [4, 6, 2], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CONFIRMED", "ORD |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 24.5, "profit_loss": -4530, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 24.5, "tickets": 60, "payout": 1470} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `f499f04a62650208`／Learning State `1b57917e9546`</sub>
