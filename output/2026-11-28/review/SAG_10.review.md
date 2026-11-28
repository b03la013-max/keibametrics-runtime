# 2026-11-28 SAG_10 詳細反省（自動・実購入なし）

- 公式着順：2-6-10-4-5（上位3頭 [2, 6, 10]）
- 距離帯：MIDDLE(1701-2100)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2

## PAPER

- 1着の事前順位 8／2着 5／3着 9；W False・P2 False・P3 False
- Top3捕捉 0／Top4捕捉 0；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "SAG_10.r2", "ticket_sha256": "113075be87210dec8b959ea42f45f47f54824cc159ea6fa61382553bd5d1df09", "frozen_at": "2026-11-28T18:50:02.943837+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 8／2着 5／3着 6；W False・P2 True・P3 True
- Top3捕捉 0／Top4捕捉 0；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "3513dc90402b06e413de3e86f572f4b43073c9b58cf486621ef5da6dc54fc77b", "result_receipt_sha256": "af3807549d84d1d89c5ca60ba2e3f2aff4a4385e1f0cbd5e790db1420bcd9a83", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "2494714ff8929f040a92df1bac2dfd9e082b80109221c567e6c7d2ffe2f8318c", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-28T10:27:13.955147+00:00", "source_receipt_sha256": "bce02a44f074ce98c6ecac50692f665a2aa3fa526043dd9903c435f9cde9afa3", "signed_final_at": "2026-11-28T10:27:26.713223+00:00", "delivered_ticket_sha256": "5ae128a3edf2d60490500e0761d2f99bf63f477fd0c44e3a23bdba2cdbe0c553", "settled_ticket_sha256": "3513dc90402b06e413de3e86f572f4b43073c9b58cf486621ef5da6dc54fc77b"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 7, "TPI-L": 7, "SRI-L": 8, "T3I-L": 11, "HPI-L": 3}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（カナデルエア）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 8, "second_pre_rank": 5, "third_pre_rank": 6, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [2, 6, 10], "rescues": [], "supports": ["P3_ROLE_CONFIRMED"], "misses": [ |
| TICKET | ISSUE | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 8, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `05877a9b109af646`／Learning State `8c8f69705fb8`</sub>
