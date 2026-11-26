# 2026-11-26 URW_06 詳細反省（自動・実購入なし）

- 公式着順：1-5-8-3-6（上位3頭 [1, 5, 8]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 1／2着 4／3着 8；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 1740／損益 1040／PFS 248.6%
- 参照：{"revision": "URW_06.r2", "ticket_sha256": "c0bd326d9dd9495473a25c65d82e068afe8918ca6ba4b4bee7cd106be860d6c7", "frozen_at": "2026-11-26T14:05:12.279761+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 4／3着 6；W True・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 5920／損益 -80／PFS 98.7%
- 参照：{"final_receipt_sha256": "e1ec60d78b63935713e0cee9a2d1fd3de17bf4c400b6c36c745c586b0896eed4", "result_receipt_sha256": "65d1fa415c07de52f196aa181a6bc1ee915882821fc4a3313684f1da232bf374", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "f795a9fcf3950a6fe51246c739051f85f85c4b86c220b00b7357557efb025d70", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 11130, "pfs": 84.3}, "effective_revision": "REVISION_2", "source_at": "2026-11-26T05:41:18.479172+00:00", "source_receipt_sha256": "234c8f99635cdecc263cd48fa7db6387249bbee486ecd06c168f90c79a3f333d", "signed_final_at": "2026-11-26T05:41:30.326196+00:00", "delivered_ticket_sha256": "7600e1cd9a1fc8afe0fd77a2dc327e58fb0ce2d4bd32e694e6ec609ac3c98a49", "settled_ticket_sha256": "e1ec60d78b63935713e0cee9a2d1fd3de17bf4c400b6c36c745c586b0896eed4"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 1, "SRI-L": 3, "T3I-L": 5, "HPI-L": 1}, "ruled_neutral_share": 0.072} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 3, "second_pre_rank": 4, "third_pre_rank": 6, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [1, 5, 8], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "ORDERED_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 98.7, "profit_loss": -80, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 98.7, "tickets": 60, "payout": 5920} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `0bfdf652e0a0a8fb`／Learning State `360c0f52e498`</sub>
