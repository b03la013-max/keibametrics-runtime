# 2026-11-27 NGY_07 詳細反省（自動・実購入なし）

- 公式着順：11-12-7-3-5（上位3頭 [11, 12, 7]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 1／2着 5／3着 9；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "NGY_07.r2", "ticket_sha256": "375eef6df8182644e3648c376dca8e052c7703d2179dacf5b0ef4682a095a77d", "frozen_at": "2026-11-27T17:23:46.293441+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 4／3着 11；W True・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 1820／損益 -4180／PFS 30.3%
- 参照：{"final_receipt_sha256": "c186bbd580a80a49487bd3bf3b27a9c50e3404e7439de9865fa80bc6b4dbff6f", "result_receipt_sha256": "de42b756c8b5124975ebade42ea81708a4af042c35731fe326c342f508573471", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "f74c231d1c4e5baa411c8596f9e38b2c61f5bb8b8f590a7423bf12e4e40b6036", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 16410, "pfs": 105.2}, "effective_revision": "REVISION_2", "source_at": "2026-11-27T08:55:17.082301+00:00", "source_receipt_sha256": "7715b1eec6e52d2c68a4c96ebc266a86ebe00796c9160a511a0dbd833d877e3f", "signed_final_at": "2026-11-27T08:55:30.364344+00:00", "delivered_ticket_sha256": "3dcb388f75351e6236ae5a7a4a758c35b3a19388acba829b91d9f550ab08bb46", "settled_ticket_sha256": "c186bbd580a80a49487bd3bf3b27a9c50e3404e7439de9865fa80bc6b4dbff6f"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 5, "HPI-L": 1}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 4, "third_pre_rank": 11, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [11, 12, 7], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROL |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 30.3, "profit_loss": -4180, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 30.3, "tickets": 60, "payout": 1820} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `576aaead5f8f4bd8`／Learning State `963f1359d857`</sub>
