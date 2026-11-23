# 2026-11-23 KNZ_08 詳細反省（自動・実購入なし）

- 公式着順：9-1-3-2-7（上位3頭 [9, 1, 3]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 6／2着 2／3着 4；W False・P2 True・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "KNZ_08.r2", "ticket_sha256": "8be38aa6002722202f06693973622d7a23cc7129097a164b13e34907f0537ca7", "frozen_at": "2026-11-23T16:55:28.794221+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 5／2着 1／3着 6；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 970／損益 -5030／PFS 16.2%
- 参照：{"final_receipt_sha256": "affa60b17a02ce9a7dd4a9440d639960f7f062e8b5ca86b2fdcab807efc0e4fe", "result_receipt_sha256": "d8b24fea678aa42dd67a3add9a0520c32621ae784113d2ca96e8fd2407f5b989", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "10afd00b38ef8647784bdcaaa16822a7815a573b2263a26d278bc50ac2d0b4bc", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-23T08:32:35.592392+00:00", "source_receipt_sha256": "228ec7f2de204dbb333ae527897ef00edd83748c6f560dcf43e181974220e35d", "signed_final_at": "2026-11-23T08:32:48.339577+00:00", "delivered_ticket_sha256": "962b8111c5ec30a8560f7aca9159c22ab117dd5b0e8828650e2340af7ae0fa66", "settled_ticket_sha256": "affa60b17a02ce9a7dd4a9440d639960f7f062e8b5ca86b2fdcab807efc0e4fe"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 5, "TPI-L": 5, "SRI-L": 5, "T3I-L": 7, "HPI-L": 7}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（レイオーバー）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 5, "second_pre_rank": 1, "third_pre_rank": 6, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [9, 1, 3], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CONFIRMED", "ORD |
| TICKET | OK | {"head_local_p2": null, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cov |
| CAPITAL | ISSUE | {"pfs": 16.2, "profit_loss": -5030, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 5, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P1:HIT_BUT_LOSS | P1 | {"pfs": 16.2, "tickets": 60, "payout": 970} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `8279d6ea19156a59`／Learning State `c70634b4f7d5`</sub>
