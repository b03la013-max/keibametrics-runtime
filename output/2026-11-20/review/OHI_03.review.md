# 2026-11-20 OHI_03 詳細反省（自動・実購入なし）

- 公式着順：2-5-4-1-8（上位3頭 [2, 5, 4]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 3／2着 2／3着 1；W False・P2 True・P3 False
- Top3捕捉 3／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 890／損益 190／PFS 127.1%
- 参照：{"revision": "OHI_03.r2", "ticket_sha256": "340babaf15bd82c8039bfa11754ca07860341e744788da5a23ef5136512ce20b", "frozen_at": "2026-11-20T14:51:22.205581+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 2／3着 1；W True・P2 True・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 6470／損益 470／PFS 107.8%
- 参照：{"final_receipt_sha256": "97039a0393487ac967d74cf30b7889a71bf104c7a0170008304c74bdc1b366a5", "result_receipt_sha256": "635002bffa9cca287a5f48baece9fb18e88d21d5dcdf3c399ef5cae80dcbb973", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "e6863d6cb9ceadd849e16cabdce13847009d4152189b51dc5b0987f123c39124", "signed_final_ticket_count": 105, "signed_final_total_investment": 10500, "signed_final_settlement": {"invest": 10500, "refund": 0, "effective_invest": 10500, "payout": 6470, "pfs": 61.6}, "effective_revision": "REVISION_1", "source_at": "2026-11-20T05:56:26.642184+00:00", "source_receipt_sha256": "1a4dbb0e34e939f7024d166aeabc6af3fe0e1fde40c0b5082c91511959782835", "signed_final_at": "2026-11-20T05:56:33.930073+00:00", "delivered_ticket_sha256": "ca3e0f9b663355c29e9976a1215668d251b7a3eaf62a6abbed1010472cc25ea8", "settled_ticket_sha256": "97039a0393487ac967d74cf30b7889a71bf104c7a0170008304c74bdc1b366a5"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 3, "SRI-L": 3, "T3I-L": 3, "HPI-L": 3}, "ruled_neutral_share": 0.108} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 3, "second_pre_rank": 2, "third_pre_rank": 1, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [2, 5, 4], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CONFIRMED", "ORD |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_cov |
| CAPITAL | OK | {"pfs": 107.8, "profit_loss": 470, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `723b566002bdbe0a`／Learning State `29204e12b5fa`</sub>
