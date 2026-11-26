# 2026-11-26 URW_09 詳細反省（自動・実購入なし）

- 公式着順：9-1-8-11-5（上位3頭 [9, 1, 8]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 1／2着 8／3着 5；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 False；Pair条件付き3着 None
- 投資 1600／返還 0／払戻 0／損益 -1600／PFS 0.0%
- 参照：{"revision": "URW_09.r2", "ticket_sha256": "757bc0ec372256b977061d1a54307f0f4ff7d41403a77bbc5cb27b5bd79c3748", "frozen_at": "2026-11-26T15:50:12.175663+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 11／3着 6；W True・P2 False・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "1cc8dc4f061c8aa796df46022f949b05ea92d56b6d60056b487d9693f9db562d", "result_receipt_sha256": "110d8b47daf793ed78d2209fedfbdd88860f656c56d85576e9f95114d97839dd", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "86df5d7aeedd108228e3e9931e6d27b233b4b8b2c2c25402fdd60e14c0b4c5be", "signed_final_ticket_count": 180, "signed_final_total_investment": 18000, "signed_final_settlement": {"invest": 18000, "refund": 0, "effective_invest": 18000, "payout": 1160, "pfs": 6.4}, "effective_revision": "REVISION_2", "source_at": "2026-11-26T07:26:26.556281+00:00", "source_receipt_sha256": "6bb4df9527f2242650dd44c57f17332f0e5b56b771d44124460444218288c2dd", "signed_final_at": "2026-11-26T07:26:40.129785+00:00", "delivered_ticket_sha256": "29bb805878c90a52ec59e90eb1d7a3be46518e99d84098ce3f22ab14450665fd", "settled_ticket_sha256": "1cc8dc4f061c8aa796df46022f949b05ea92d56b6d60056b487d9693f9db562d"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 5, "HPI-L": 1}, "ruled_neutral_share": 0.005} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補4頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 1, "second_pre_rank": 11, "third_pre_rank": 6, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [9, 1, 8], "rescues": ["P2_ROLE_RESCUE", "ORDERED_PAIR_RESCUE"], "support |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 11} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `98e1ae5fff318515`／Learning State `a8e69c709973`</sub>
