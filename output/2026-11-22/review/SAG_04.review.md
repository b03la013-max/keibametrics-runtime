# 2026-11-22 SAG_04 詳細反省（自動・実購入なし）

- 公式着順：10-3-8-4-6（上位3頭 [10, 3, 8]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 4／2着 1／3着 8；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 3240／損益 2540／PFS 462.9%
- 参照：{"revision": "SAG_04.r2", "ticket_sha256": "0f58821b18e1f194ee391f27484c272d558a112d4f25a119c52eac7b36cfcae1", "frozen_at": "2026-11-22T16:15:18.493252+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 1／3着 9；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 1030／損益 -4970／PFS 17.2%
- 参照：{"final_receipt_sha256": "470480861046523ea35b1c2c8b2fc4fc4d6884c184dc3ba830c04eb77f6850a5", "result_receipt_sha256": "7f74badb6567c10ec7007604439f59dbaf2611e60ae91309b1ad46c92bf95318", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "f2c2826dfb43f0d023b6909b90f913112499798d429c84599c0ed9ab5f9f68fe", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 38780, "pfs": 269.3}, "effective_revision": "REVISION_1", "source_at": "2026-11-22T07:18:20.233856+00:00", "source_receipt_sha256": "afa5f6b9fb5d658ec1b048e626b38882144eb412a488c4c00132cda0dfedfb35", "signed_final_at": "2026-11-22T07:18:32.191176+00:00", "delivered_ticket_sha256": "3e8c379bcffb28754871f52b0202046714e1073d7d9fd9c6cd7000a227231b88", "settled_ticket_sha256": "470480861046523ea35b1c2c8b2fc4fc4d6884c184dc3ba830c04eb77f6850a5"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 2, "HPI-L": 1}, "ruled_neutral_share": 0.072} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補4頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 3, "second_pre_rank": 1, "third_pre_rank": 9, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [10, 3, 8], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_CONFIRMED", |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 17.2, "profit_loss": -4970, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 17.2, "tickets": 60, "payout": 1030} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `b4dc3dcbd0625801`／Learning State `9fae34cf57d9`</sub>
