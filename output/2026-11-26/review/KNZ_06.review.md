# 2026-11-26 KNZ_06 詳細反省（自動・実購入なし）

- 公式着順：8-2-5-6-1（上位3頭 [8, 2, 5]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 2／2着 1／3着 3；W False・P2 False・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 480／損益 -220／PFS 68.6%
- 参照：{"revision": "KNZ_06.r2", "ticket_sha256": "37d06b85113e6f1dc2139b5628f1eb512414f4106dee41ce359432ce933c9c95", "frozen_at": "2026-11-26T16:20:21.788223+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 3／3着 4；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 1460／損益 -4540／PFS 24.3%
- 参照：{"final_receipt_sha256": "faa493f67befbfb2e11865fe5c191aa009f0ad3773eb4a0f0f0c39605fb41680", "result_receipt_sha256": "8a76659dc38f322c7366b2e99d25bbe90aa5ba639d4b3791e399378174e1db6a", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "44cbbd8be8c9e2f9de359c4b938df1e8ad7ea9db02563d6ff6679d6a3aff745a", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 4810, "pfs": 36.4}, "effective_revision": "REVISION_2", "source_at": "2026-11-26T07:57:11.221122+00:00", "source_receipt_sha256": "fc184183967327e9e0456f1901573d4bd3c91dbe7167c1b15da128840c542164", "signed_final_at": "2026-11-26T07:57:23.287319+00:00", "delivered_ticket_sha256": "ad8adf91f9e7c7c80c45632afcd44b91e1bc64109d80b221467eb7ea21f90314", "settled_ticket_sha256": "faa493f67befbfb2e11865fe5c191aa009f0ad3773eb4a0f0f0c39605fb41680"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 2, "HPI-L": 1}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 3, "third_pre_rank": 4, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [8, 2, 5], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 24.3, "profit_loss": -4540, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 24.3, "tickets": 60, "payout": 1460} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `d85bfa9133eece94`／Learning State `7bcab1ee3744`</sub>
