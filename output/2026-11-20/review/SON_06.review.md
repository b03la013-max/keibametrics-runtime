# 2026-11-20 SON_06 詳細反省（自動・実購入なし）

- 公式着順：12-4-8-7-5（上位3頭 [12, 4, 8]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 7／2着 4／3着 2；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "SON_06.r2", "ticket_sha256": "5f3211e938a1062343c405882dbd91c814541dc2b2f1f1de8904671e69f54ba0", "frozen_at": "2026-11-20T12:25:53.467596+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 3／3着 4；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 19370／損益 13370／PFS 322.8%
- 参照：{"final_receipt_sha256": "436da215cd4ff9547cb3b251b766cc2616f6b95404108dfa53207668a9a29eeb", "result_receipt_sha256": "50810cba0e151b4c06f84cf72a7a6df426e483a1f02d3e6f15e1609a57b75fdb", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "9d173ddc6f64fd56cc9f10a2040e1b5f03a623bfdd360e6bf00de7e4f89b05cd", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 19370, "pfs": 124.2}, "effective_revision": "REVISION_1", "source_at": "2026-11-20T03:28:14.809001+00:00", "source_receipt_sha256": "f6820d1b5c1a501e93dd419323ba9b104b8b4eeea28cf207e4958e4832a0f372", "signed_final_at": "2026-11-20T03:28:23.901925+00:00", "delivered_ticket_sha256": "9cb52627e2a4a6d762c32da4ab03cc62ec2983a471da82093a8c67f4d4baf3bf", "settled_ticket_sha256": "436da215cd4ff9547cb3b251b766cc2616f6b95404108dfa53207668a9a29eeb"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 1, "SRI-L": 1, "T3I-L": 3, "HPI-L": 2}, "ruled_neutral_share": 0.115} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補4頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 3, "third_pre_rank": 4, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [12, 4, 8], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_cov |
| CAPITAL | OK | {"pfs": 322.8, "profit_loss": 13370, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `7f0f0883a0eab7f6`／Learning State `bc073a1efcd2`</sub>
