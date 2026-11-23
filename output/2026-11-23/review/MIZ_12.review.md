# 2026-11-23 MIZ_12 詳細反省（自動・実購入なし）

- 公式着順：11-3-1-2-4（上位3頭 [11, 3, 1]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 1／2着 6／3着 5；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 False；Pair条件付き3着 None
- 投資 1600／返還 0／払戻 0／損益 -1600／PFS 0.0%
- 参照：{"revision": "MIZ_12.r2", "ticket_sha256": "9c9e90a06697b520349c629f517646272149b01e3456ab77d8242e5f70305f2f", "frozen_at": "2026-11-23T17:20:05.906614+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 6／3着 1；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 470／損益 -5530／PFS 7.8%
- 参照：{"final_receipt_sha256": "0362f3dbc1d63fc8363414f66e31c05d62b793da39db65ea6924ed15fc366780", "result_receipt_sha256": "5cb1b6538ca715198d88b9c4ab24a2dff632ed83dfe4883a62b4b1ffa913fe9e", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "37d0bbdc79be3f9c435ea3f1f85bf1a6e75ae8df372a0c6d8dab95a52ceaedb0", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 700, "pfs": 5.3}, "effective_revision": "REVISION_2", "source_at": "2026-11-23T08:56:18.724424+00:00", "source_receipt_sha256": "54ba6af2e370f9bcee40bdadc4ccd65e2d84236f792ba951fccc93f6d1ca18c9", "signed_final_at": "2026-11-23T08:56:31.105087+00:00", "delivered_ticket_sha256": "7763f98d2e436e1fb536aa4e1cb9f4ff25939f7d54d07bc33def7b252d68177e", "settled_ticket_sha256": "0362f3dbc1d63fc8363414f66e31c05d62b793da39db65ea6924ed15fc366780"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 5, "TPI-L": 5, "SRI-L": 4, "T3I-L": 9, "HPI-L": 5}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（ヒロシクン）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 3, "second_pre_rank": 6, "third_pre_rank": 1, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [11, 3, 1], "rescues": [], "supports": ["P3_ROLE_CONFIRMED"], "misses": [ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 7.8, "profit_loss": -5530, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 7.8, "tickets": 60, "payout": 470} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `55e6723d3b099f01`／Learning State `671d287c6168`</sub>
