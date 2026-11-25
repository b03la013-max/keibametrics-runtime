# 地方 統計表の期間分割（HISTORICAL_BACKFILL_LEARNING (not Forward OOS)）

発見 ['2023-01-01', '2025-06-30']（340814出走）／ 検証 ['2025-07-01', '2026-11-24']（197445出走）。境目 2025-07-01。BH の q 値は発見側だけ（q≤0.1、30出走以上を「手がかり」）。検証側で A/E が同じ向きなら HOLDS、逆なら FAILS、検証側が少数・無しなら UNTESTED。証拠のみ。

| 表 | 区分 | 手がかり | HOLDS | FAILS | UNTESTED |
|---|---|---|---|---|---|
| T10_CRZ | 2371 | 859 | 699 | 11 | 149 |
| T11_MPA | 168 | 3 | 3 | 0 | 0 |
| T12_DIRECT | 555 | 1 | 1 | 0 | 0 |
| T15_RETURNEE | 126 | 22 | 20 | 1 | 1 |
| T16_URW_FROM_FNB | 8 | 0 | 0 | 0 | 0 |
| T17_AGED_FRONT_FAV | 135 | 0 | 0 | 0 | 0 |
| T18_FAV_FRAME | 745 | 0 | 0 | 0 | 0 |
| T3_GATE | 5779 | 1 | 0 | 0 | 1 |
| T4_FRONT_FINISH | 252 | 205 | 188 | 4 | 13 |
| T5_DIST_CHANGE | 123 | 0 | 0 | 0 | 0 |
| T5_INTERVAL | 56 | 2 | 2 | 0 | 0 |
| T5_MON_COURSE | 4 | 0 | 0 | 0 | 0 |
| T5_OHI_COURSE | 9 | 0 | 0 | 0 | 0 |
| T5_VENUE_CHANGE | 196 | 1 | 0 | 1 | 0 |
| T6_JOCKEY | 6430 | 1 | 1 | 0 | 0 |
| T7_LAST3F | 593 | 372 | 327 | 2 | 43 |

## 検証期間でも同じ向きだった手がかり（q の小さい順、上位30）

| 表 | 条件 | 発見 出走 / A/E / q | 検証 出走 / A/E |
|---|---|---|---|
| T10_CRZ | venue=FNB / band=M / class=3YO / last_corner_pos(6=6+)=2 | 128 / 1.47 / 0.0 | 38 / 1.34 |
| T10_CRZ | venue=FNB / band=M / class=3YO / last_corner_pos(6=6+)=6 | 587 / 0.53 / 0.0 | 261 / 0.76 |
| T10_CRZ | venue=FNB / band=M / class=C1 / last_corner_pos(6=6+)=1 | 123 / 1.50 / 0.0 | 64 / 1.48 |
| T10_CRZ | venue=FNB / band=M / class=C1 / last_corner_pos(6=6+)=6 | 702 / 0.55 / 0.0 | 319 / 0.63 |
| T10_CRZ | venue=FNB / band=M / class=C2 / last_corner_pos(6=6+)=6 | 930 / 0.58 / 0.0 | 385 / 0.60 |
| T10_CRZ | venue=FNB / band=S / class=2YO / last_corner_pos(6=6+)=1 | 128 / 1.42 / 0.0 | 107 / 1.40 |
| T10_CRZ | venue=FNB / band=S / class=2YO / last_corner_pos(6=6+)=6 | 294 / 0.43 / 0.0 | 215 / 0.42 |
| T10_CRZ | venue=FNB / band=S / class=3YO / last_corner_pos(6=6+)=1 | 223 / 1.37 / 0.0 | 165 / 1.33 |
| T10_CRZ | venue=FNB / band=S / class=3YO / last_corner_pos(6=6+)=2 | 223 / 1.40 / 0.0 | 124 / 1.29 |
| T10_CRZ | venue=FNB / band=S / class=3YO / last_corner_pos(6=6+)=6 | 1229 / 0.54 / 0.0 | 651 / 0.62 |
| T10_CRZ | venue=FNB / band=S / class=C1 / last_corner_pos(6=6+)=6 | 815 / 0.63 / 0.0 | 471 / 0.70 |
| T10_CRZ | venue=FNB / band=S / class=C2 / last_corner_pos(6=6+)=6 | 1169 / 0.65 / 0.0 | 571 / 0.62 |
| T10_CRZ | venue=FNB / band=S / class=C3 / last_corner_pos(6=6+)=6 | 916 / 0.57 / 0.0 | 369 / 0.59 |
| T10_CRZ | venue=HMJ / band=M / class=3YO / last_corner_pos(6=6+)=6 | 195 / 0.30 / 0.0 | 64 / 0.57 |
| T10_CRZ | venue=HMJ / band=M / class=C1 / last_corner_pos(6=6+)=1 | 110 / 1.55 / 0.0 | 35 / 1.36 |
| T10_CRZ | venue=HMJ / band=M / class=C1 / last_corner_pos(6=6+)=6 | 565 / 0.33 / 0.0 | 158 / 0.68 |
| T10_CRZ | venue=HMJ / band=M / class=C2 / last_corner_pos(6=6+)=1 | 242 / 1.55 / 0.0 | 82 / 1.44 |
| T10_CRZ | venue=HMJ / band=M / class=C2 / last_corner_pos(6=6+)=2 | 222 / 1.38 / 0.0 | 69 / 1.20 |
| T10_CRZ | venue=HMJ / band=M / class=C2 / last_corner_pos(6=6+)=6 | 1012 / 0.35 / 0.0 | 346 / 0.32 |
| T10_CRZ | venue=HMJ / band=M / class=C3 / last_corner_pos(6=6+)=1 | 278 / 1.60 / 0.0 | 77 / 1.66 |
| T10_CRZ | venue=HMJ / band=M / class=C3 / last_corner_pos(6=6+)=2 | 232 / 1.54 / 0.0 | 66 / 1.34 |
| T10_CRZ | venue=HMJ / band=M / class=C3 / last_corner_pos(6=6+)=6 | 1217 / 0.34 / 0.0 | 332 / 0.48 |
| T10_CRZ | venue=KAW / band=M / class=2YO / last_corner_pos(6=6+)=1 | 167 / 1.44 / 0.0 | 142 / 1.39 |
| T10_CRZ | venue=KAW / band=M / class=2YO / last_corner_pos(6=6+)=6 | 448 / 0.31 / 0.0 | 336 / 0.30 |
| T10_CRZ | venue=KAW / band=M / class=3YO / last_corner_pos(6=6+)=1 | 348 / 1.56 / 0.0 | 169 / 1.46 |
| T10_CRZ | venue=KAW / band=M / class=3YO / last_corner_pos(6=6+)=2 | 293 / 1.40 / 0.0 | 143 / 1.25 |
| T10_CRZ | venue=KAW / band=M / class=3YO / last_corner_pos(6=6+)=3 | 317 / 1.35 / 0.0 | 136 / 1.40 |
| T10_CRZ | venue=KAW / band=M / class=3YO / last_corner_pos(6=6+)=6 | 1655 / 0.37 / 0.0 | 743 / 0.38 |
| T10_CRZ | venue=KAW / band=M / class=B3 / last_corner_pos(6=6+)=1 | 82 / 1.67 / 0.0 | 67 / 1.43 |
| T10_CRZ | venue=KAW / band=M / class=B3 / last_corner_pos(6=6+)=6 | 504 / 0.54 / 0.0 | 362 / 0.63 |
