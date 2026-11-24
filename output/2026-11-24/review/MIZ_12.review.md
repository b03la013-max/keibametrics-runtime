# 2026-11-24 MIZ_12 詳細反省（自動・実購入なし）

- 公式着順：4-3-5-2-1（上位3頭 [4, 3, 5]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 7／2着 3／3着 10；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "MIZ_12.r2", "ticket_sha256": "8c04618953a24c1de62a92ffcb4ad0143b2f4002280f97908cc5745516e0eab4", "frozen_at": "2026-11-24T17:20:17.215290+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 9／2着 4／3着 10；W False・P2 True・P3 True
- Top3捕捉 0／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "02d44a458a3f338cea15e92e32e44be312f39b20bc2cd17ae38d9f799ff328bb", "result_receipt_sha256": "9cb8f551acf3730f474c22d1e3c9cfca8afdf361d283eafea2454403860d3a9c", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "b8cf602e3467bb5a1617e93c2c562e25ef046bc70cc3ef96b64bd14a23c0e946", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-24T08:55:14.681616+00:00", "source_receipt_sha256": "471d960462a6f500ac25dab9bba6e3be33230d4fc862c427547610c9a94b8027", "signed_final_at": "2026-11-24T08:55:30.776210+00:00", "delivered_ticket_sha256": "b5a732fe7287575cfb4fb24892ccb80de3c81211adc3b7944baef4f19e831127", "settled_ticket_sha256": "02d44a458a3f338cea15e92e32e44be312f39b20bc2cd17ae38d9f799ff328bb"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 8, "TPI-L": 8, "SRI-L": 8, "T3I-L": 9, "HPI-L": 9}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 9, "second_pre_rank": 4, "third_pre_rank": 10, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [4, 3, 5], "rescues": [], "supports": ["P2_ROLE_CONFIRMED"], "misses": [" |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 9, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `8ff4cf0b5f8e66f4`／Learning State `8a80803b1f1e`</sub>
