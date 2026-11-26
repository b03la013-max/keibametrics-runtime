# 2026-11-26 KNZ_04 詳細反省（自動・実購入なし）

- 公式着順：1-4-9-7-3（上位3頭 [1, 4, 9]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 3／2着 1／3着 2；W False・P2 False・P3 False
- Top3捕捉 3／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 510／損益 -190／PFS 72.9%
- 参照：{"revision": "KNZ_04.r2", "ticket_sha256": "9b725f5a9851da239dc97dc09d810fad7826c9d25d5654d4297aa3546b8234fc", "frozen_at": "2026-11-26T15:10:18.807139+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 6／3着 1；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 3330／損益 -2670／PFS 55.5%
- 参照：{"final_receipt_sha256": "c73eb58eb7c5737706bcf776639ded3d8df1bff6609993dc2fdd9ee9aacea950", "result_receipt_sha256": "1b1274f2f8e62ba4d76da648c9511ef5132a3988f208df226a095d9b976e3af5", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "10505d09d2f49971d7f8928c0abcc4198bf0de3cd12cac241cd3eb193084f600", "signed_final_ticket_count": 120, "signed_final_total_investment": 12000, "signed_final_settlement": {"invest": 12000, "refund": 0, "effective_invest": 12000, "payout": 2990, "pfs": 24.9}, "effective_revision": "REVISION_2", "source_at": "2026-11-26T06:46:14.026445+00:00", "source_receipt_sha256": "17aee5f589f141456ea5bdea05f595254c51b2aaaea3e386c958d17682e0258a", "signed_final_at": "2026-11-26T06:46:25.057416+00:00", "delivered_ticket_sha256": "b59f283654de6f1c09a9d2bd1001c325e244cf11e9b3c197d5c382ac36abc5e3", "settled_ticket_sha256": "c73eb58eb7c5737706bcf776639ded3d8df1bff6609993dc2fdd9ee9aacea950"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 2, "SRI-L": 1, "T3I-L": 5, "HPI-L": 2}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 6, "third_pre_rank": 1, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [1, 4, 9], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P3_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 55.5, "profit_loss": -2670, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 55.5, "tickets": 60, "payout": 3330} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `d16c5c6423aa3065`／Learning State `b690f42b9324`</sub>
