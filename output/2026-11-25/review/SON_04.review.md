# 2026-11-25 SON_04 詳細反省（自動・実購入なし）

- 公式着順：3-8-1-4-6（上位3頭 [3, 8, 1]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 2／2着 7／3着 5；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 1600／返還 0／払戻 0／損益 -1600／PFS 0.0%
- 参照：{"revision": "SON_04.r2", "ticket_sha256": "adbc9deeb4b0a489617df22d6318aa9ab127b31e6b168a7f80c457933658eb4a", "frozen_at": "2026-11-25T11:25:17.593235+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 5／3着 6；W True・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 22460／損益 16460／PFS 374.3%
- 参照：{"final_receipt_sha256": "c58156d8a78268896bffb88e1a1f6d77d5224a045775d8733c4fc863cd82d4ff", "result_receipt_sha256": "32052343385152e4664f106e6c3c04e1f45e7fe8658bc470e390d5d83b454842", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "c71541a92e128cde0f906f71fb63666bd48aafd65ff83fa1b81bb433444cde94", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 70700, "pfs": 535.6}, "effective_revision": "REVISION_2", "source_at": "2026-11-25T03:02:08.672491+00:00", "source_receipt_sha256": "d6ef85e66910792c5819f5a1ac206f645c24c392b03757e1e1781d2c8599f95a", "signed_final_at": "2026-11-25T03:02:20.148969+00:00", "delivered_ticket_sha256": "f21ad6d30e948d6a6e184e13233f78247bcb9d3bfb93f017a2545feecbc17137", "settled_ticket_sha256": "c58156d8a78268896bffb88e1a1f6d77d5224a045775d8733c4fc863cd82d4ff"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 2, "SRI-L": 3, "T3I-L": 5, "HPI-L": 3}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 5, "third_pre_rank": 6, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [3, 8, 1], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P3_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | OK | {"pfs": 374.3, "profit_loss": 16460, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `74c1e59773b1de14`／Learning State `ef83e2f636bc`</sub>
