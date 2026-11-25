## 自動改善の判定（2026-11-25）

昇格中の C13-FORMAL-MIX-P2BOX20 を監視中（139R）

- C15-FORMAL-MIX-WAXIS-TRIO：139R／PFS 42.65% 対 MIX_P2BOX20 42.65%／最大払戻除く 37.18% 対 37.18%／的中 74 対 74／未達：pfs・pfs_ex_top1・venues_better
- C22-KEEP-MEC-TRIO20：139R／PFS 36.88% 対 MIX_P2BOX20 42.65%／最大払戻除く 34.28% 対 37.18%／的中 65 対 74／未達：pfs・pfs_ex_top1・hits・venues_better
- C24-W-PLUS-TOP2POP-SAME-BUDGET：139R／PFS 39.56% 対 MIX_P2BOX20 42.65%／最大払戻除く 32.9% 対 37.18%／的中 74 対 74／未達：pfs・pfs_ex_top1・no_venue_much_worse
- C28-CORE-LAYER-60：139R／PFS 96.48% 対 MIX_P2BOX20 42.65%／最大払戻除く 46.65% 対 37.18%／的中 44 対 74／未達：hits
- C29-KRS-CAP-60：0R／PFS 0.0% 対 MIX_P2BOX20 0.0%／最大払戻除く 0.0% 対 0.0%／的中 0 対 0／未達：races・pfs・pfs_ex_top1・venues_better
- G001-P2PLUS-add1：105R／PFS 33.93% 対 MIX_P2BOX20 41.59%／最大払戻除く 30.46% 対 34.33%／的中 51 対 55／未達：pfs・pfs_ex_top1・hits・venues_better・no_venue_much_worse
- G002-CORE-n2：105R／PFS 47.87% 対 MIX_P2BOX20 41.59%／最大払戻除く 35.75% 対 34.33%／的中 40 対 55／未達：hits・no_venue_much_worse
- G003-PAIRFULL-pairs6：105R／PFS 33.73% 対 MIX_P2BOX20 41.59%／最大払戻除く 23.48% 対 34.33%／的中 34 対 55／未達：pfs・pfs_ex_top1・hits・no_venue_much_worse
- G004-PAIRFULL-pairs4：72R／PFS 56.2% 対 MIX_P2BOX20 43.18%／最大払戻除く 38.56% 対 38.52%／的中 30 対 40／未達：races・hits・no_venue_much_worse
- G005-WPLUS-add1：72R／PFS 49.26% 対 MIX_P2BOX20 43.18%／最大払戻除く 37.72% 対 38.52%／的中 36 対 40／未達：races・pfs_ex_top1・hits
- G006-MKTP2-blend50：72R／PFS 31.51% 対 MIX_P2BOX20 43.18%／最大払戻除く 27.53% 対 38.52%／的中 24 対 40／未達：races・pfs・pfs_ex_top1・hits・venues_better・no_venue_much_worse

### 自動で作った改善案

- 新規登録：G007-KRSCAP-mode2（GEN:KRSCAP:mode=2）← 反省 P1:CAP_LOST_HIT（12件・229,540円）、2026-11-26 から比較
- 新規登録：G008-WPLUS-add3（GEN:WPLUS:add=3）← 反省 P1:ROLE_W_MISS（18件・90,860円）、2026-11-26 から比較
- 引退：G001-P2PLUS-add1（105R：PFS 33.93% 対 41.59%、最大払戻除く 30.46% 対 34.33%）
- 引退：G003-PAIRFULL-pairs6（105R：PFS 33.73% 対 41.59%、最大払戻除く 23.48% 対 34.33%）
- 比較中の自動案：6／6（G002-CORE-n2・G004-PAIRFULL-pairs4・G005-WPLUS-add1・G006-MKTP2-blend50・G007-KRSCAP-mode2・G008-WPLUS-add3）
