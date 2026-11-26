# 2026-11-26 SON_02 詳細反省（自動・実購入なし）

- 公式着順：5-1-2-8-3（上位3頭 [5, 1, 2]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 1／2着 3／3着 7；W True・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 5300／損益 4600／PFS 757.1%
- 参照：{"revision": "SON_02.r2", "ticket_sha256": "9e44e9370716ac47bd107956af32bac526b52677a37d984865ddad23d9f80dfd", "frozen_at": "2026-11-26T10:25:05.266533+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 3／3着 4；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 5740／損益 -260／PFS 95.7%
- 参照：{"final_receipt_sha256": "74c5c6ea5c1c4f9be40e87f0e2e98bf1004af2807faf42728c0f80dd4ec4ab76", "result_receipt_sha256": "f7efeed416416cbdf5e16c4f1e3a94bdb2a0f78db99c37e926fd998399e7c39d", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "20502b750ba2fa22ecb9e0191e99a0bec96cfbada7649b8339efa8e89c800227", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 12410, "pfs": 94.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-26T02:00:09.161866+00:00", "source_receipt_sha256": "bf28983bf77a3dcb7679d4eccb9def3c3481f5ff38e17b52a7b7bf68803d836b", "signed_final_at": "2026-11-26T02:00:20.651306+00:00", "delivered_ticket_sha256": "92cb0e567f165a473f43ac8be4d607bdf5a93d63e4aceba9186f78c7307286f2", "settled_ticket_sha256": "74c5c6ea5c1c4f9be40e87f0e2e98bf1004af2807faf42728c0f80dd4ec4ab76"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 5, "HPI-L": 1}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 3, "third_pre_rank": 4, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [5, 1, 2], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 95.7, "profit_loss": -260, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 95.7, "tickets": 60, "payout": 5740} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `0e2e5fe958a63288`／Learning State `a218a147ab1c`</sub>
