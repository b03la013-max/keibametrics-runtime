# 2026-11-27 NGY_08 詳細反省（自動・実購入なし）

- 公式着順：12-5-6-8-1（上位3頭 [12, 5, 6]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 3／2着 2／3着 6；W False・P2 True・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 900／返還 0／払戻 0／損益 -900／PFS 0.0%
- 参照：{"revision": "NGY_08.r2", "ticket_sha256": "99eedb21c677f7cea9e3d7b4763de8947f2a65fe56d3682cf218a53656bfb265", "frozen_at": "2026-11-27T17:50:11.814761+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 4／2着 1／3着 3；W False・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 2670／損益 -3330／PFS 44.5%
- 参照：{"final_receipt_sha256": "1d346380379283708676cb112bec1a0f983a0feeb1d4a61c126fa0b59ce08c35", "result_receipt_sha256": "01d093e949f326d1e3c840267896d32b42eebd40bc749b344f2a08ab1fc33dbe", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "cd7c8d593250612f4327b42687a26df1a2e59df9ecf6ab44398bbdf799168ae7", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-27T09:25:14.303921+00:00", "source_receipt_sha256": "d63760b1bce7c4e80b42f0e2f9c7d7ede580ceec5fb15bd95d879eade086706e", "signed_final_at": "2026-11-27T09:25:27.071541+00:00", "delivered_ticket_sha256": "ad2d88b227789db5329cfc6406c1f4ab04cd8d43d05f6269daa717e56311b576", "settled_ticket_sha256": "1d346380379283708676cb112bec1a0f983a0feeb1d4a61c126fa0b59ce08c35"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 4, "TPI-L": 4, "SRI-L": 4, "T3I-L": 4, "HPI-L": 3}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補4頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 4, "second_pre_rank": 1, "third_pre_rank": 3, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [12, 5, 6], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CONFIRMED", "OR |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_cov |
| CAPITAL | ISSUE | {"pfs": 44.5, "profit_loss": -3330, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 4, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P1:HIT_BUT_LOSS | P1 | {"pfs": 44.5, "tickets": 60, "payout": 2670} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `7d77dba93fa2cf83`／Learning State `cf6e2a9ee15d`</sub>
