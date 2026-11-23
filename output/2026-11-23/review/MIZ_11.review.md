# 2026-11-23 MIZ_11 詳細反省（自動・実購入なし）

- 公式着順：6-2-4-9-1（上位3頭 [6, 2, 4]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 2／2着 1／3着 3；W False・P2 False・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 360／損益 -340／PFS 51.4%
- 参照：{"revision": "MIZ_11.r2", "ticket_sha256": "246a24a7f745958e73754b32d0136160417b4f30914e9cc8adcdc93f260370ff", "frozen_at": "2026-11-23T16:45:07.332845+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 4／2着 1／3着 2；W False・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 240／損益 -5760／PFS 4.0%
- 参照：{"final_receipt_sha256": "945beab3b4b0580513d4ed3419f38aaf09de5471666677e344869b562b95f46c", "result_receipt_sha256": "78faa1523e0f42eb61dea5413b3e43154afcc45c2606ce39310d61dceb5fc060", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "d319abb59a72df6a47a91648d6c8c57c70316a721097649ceed810c59f7b10b1", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-23T08:22:08.517104+00:00", "source_receipt_sha256": "e248fdda6553f040810c2eaea14d713146263928d6e8dbc381a3f2406452042e", "signed_final_at": "2026-11-23T08:22:23.314446+00:00", "delivered_ticket_sha256": "077001ae3c6a9cf0c958dc45927a075a0cc5e589c2705f067136deb96e7c258e", "settled_ticket_sha256": "945beab3b4b0580513d4ed3419f38aaf09de5471666677e344869b562b95f46c"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 4, "TPI-L": 5, "SRI-L": 4, "T3I-L": 7, "HPI-L": 8}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（ポジティブスピン）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 4, "second_pre_rank": 1, "third_pre_rank": 2, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [6, 2, 4], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CONF |
| TICKET | OK | {"head_local_p2": null, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cov |
| CAPITAL | ISSUE | {"pfs": 4.0, "profit_loss": -5760, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 4, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P1:HIT_BUT_LOSS | P1 | {"pfs": 4.0, "tickets": 60, "payout": 240} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `bef14011e4cb739a`／Learning State `09de70591f3d`</sub>
