# 2026-11-23 MIZ_01 詳細反省（自動・実購入なし）

- 公式着順：10-2-1-6-7（上位3頭 [10, 2, 1]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 2／2着 4／3着 6；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "MIZ_01.r2", "ticket_sha256": "20117bf29bf19e495ac3f366a9917f776d91abfd20dec7098e127296efe3d6b0", "frozen_at": "2026-11-23T10:55:13.812184+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 5／2着 4／3着 10；W False・P2 True・P3 True
- Top3捕捉 0／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "dbb237efb3327c137d38d73f64818710f63f399f845b104e26349fa32fd057a2", "result_receipt_sha256": "e1df4bf26268f393f683ac185c04061ec61d5ea6cdaf4b5cc8a8fbd92b8af14c", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "7baee25487343058dd33c7a4f5c20591fb5b444cc20a7964c140af51002a7d3b", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_1", "source_at": "2026-11-23T01:58:21.671859+00:00", "source_receipt_sha256": "bdc4e326c1cc602337cacbe61e61b59894ca0c471de0eb9a9a2e0ab1a8b84cf4", "signed_final_at": "2026-11-23T01:58:33.411159+00:00", "delivered_ticket_sha256": "c6f56f8a57343b1a023518b17af15911b38b155f2ae0661659bf700ff30c6fc8", "settled_ticket_sha256": "dbb237efb3327c137d38d73f64818710f63f399f845b104e26349fa32fd057a2"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 5, "TPI-L": 5, "SRI-L": 4, "T3I-L": 7, "HPI-L": 3}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 5, "second_pre_rank": 4, "third_pre_rank": 10, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [10, 2, 1], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CON |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 5, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `f72c281bf184f039`／Learning State `174c1183bd06`</sub>
