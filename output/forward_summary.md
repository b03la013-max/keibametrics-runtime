# LOCAL Forward OOS（PAPER・推薦試算・実購入なし）

- 精算Race 148（R30 達成／R100 達成／R500 未達）
- 実効投資 113,500円／払戻 88,530円／**PFS 78.0%**（最大払戻 21,490円を除くと 59.1%）
- 最大ドローダウン 24,970円／黒字Race率 0.182／Bet Coverage 1.0
- W的中 44／P2一致 18／P3一致 26
- 第一失敗の分布：{'WINNER_DISCOVERED_LOW': 29, 'P2_MISS': 19, 'W_WIDTH_OR_ROLE': 52, 'THIRD_MISS': 11, 'WINNER_NOT_DISCOVERED': 23, 'NONE': 13, 'TICKET_OR_CAPITAL': 1}

| 日付 | Race | 締切前 | 精算 | 実効投資 | 払戻 | PFS |
|---|---|---|---|---|---|---|
| 2026-11-13 | 46 | 14 | 14 | 10,900 | 2,920 | 26.8% |
| 2026-11-14 | 22 | 22 | 22 | 17,500 | 8,880 | 50.7% |
| 2026-11-15 | 44 | 44 | 44 | 31,600 | 31,340 | 99.2% |
| 2026-11-16 | 36 | 36 | 36 | 26,800 | 36,680 | 136.9% |
| 2026-11-17 | 36 | 36 | 32 | 26,700 | 8,710 | 32.6% |

## 全29指数の観測率（場別・CALCULATEDの比率。それ以外は全頭が規則中立）

| 場 | 頭数 | BVIg-L | CCI | CFIg-L | CSI-L | DRS | EVI/CEV | HCS | HPI-L | JTI-L | OPI-V | PRI | RFIg-L | TRI | URP |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| KNZ | 308 | 0% | 0% | 100% | 100% | 100% | 100% | 100% | 100% | 70% | 100% | 100% | 100% | 0% | 100% |
| KOC | 242 | 0% | 0% | 98% | 98% | 98% | 98% | 98% | 98% | 62% | 100% | 100% | 98% | 0% | 98% |
| MIZ | 383 | 0% | 0% | 99% | 99% | 99% | 99% | 99% | 99% | 61% | 100% | 100% | 99% | 0% | 99% |
| OHI | 296 | 0% | 0% | 87% | 87% | 87% | 87% | 87% | 87% | 59% | 100% | 100% | 87% | 0% | 87% |
| SAG | 234 | 0% | 0% | 100% | 100% | 100% | 100% | 100% | 100% | 65% | 100% | 100% | 100% | 0% | 100% |

## 正式Production（署名FINAL・未知未来・推薦試算・実購入なし）

- 署名FINAL 40R／精算 37R／署名RESULT検証 37R
- 実効投資 261,600円／払戻 102,970円／PFS 39.4%／正式◎1着 13
- 正式29指数（Production計算器・未消費）のF3S-L順：35R中 1着的中 9／上位3頭の3着内捕捉 49（正式Static 43）
- 数値Consumer昇格ゲート：精算 35/100R・Ownerレビュー OWNER_APPROVED (2026-11-16)・承認 True

| 日付 | Race | FINAL | 精算 | 投資 | 払戻 | RESULT署名 | 第一失敗 |
|---|---|---|---|---|---|---|---|
| 2026-11-16 | KNZ_12 | `bacbed68d4f75ef5` | 済 | 4800 | 780 | True | CAPITAL_EFFICIENCY |
| 2026-11-16 | OHI_09 | `5d17b4e931826c8a` | 済 | 16800 | 3040 | True | PREDICTION_ROLE_P2 |
| 2026-11-16 | OHI_10 | `c5241d7249545b06` | 済 | 18000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-16 | OHI_11 | `c97004d7b930454b` | 済 | 12000 | 16570 | True | NONE |
| 2026-11-16 | OHI_12 | `5ba4e0d3393223fe` | 済 | 18000 | 5610 | True | CAPITAL_EFFICIENCY |
| 2026-11-17 | MIZ_01 | `0d912c8b32f8def1` | 済 | 6000 | 440 | True | CAPITAL_EFFICIENCY |
| 2026-11-17 | MIZ_02 | `31c0dd5ae0098bdd` | 済 | 6000 | 2100 | True | CAPITAL_EFFICIENCY |
| 2026-11-17 | MIZ_03 | `f1491fea14c5890d` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-17 | MIZ_04 | `2c121f66b6466038` | 済 | 6000 | 790 | True | CAPITAL_EFFICIENCY |
| 2026-11-17 | MIZ_05 | `a647e02dac90728e` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-17 | KNZ_01 | `df08f368247d7556` | 済 | 6000 | 2600 | True | CAPITAL_EFFICIENCY |
| 2026-11-17 | OHI_01 | `4afdb63397ede685` | 済 | 6000 | 45730 | True | NONE |
| 2026-11-17 | MIZ_06 | `a06dc56635e00e83` | 済 | 6000 | 11660 | True | CAPITAL_EFFICIENCY |
| 2026-11-17 | KNZ_02 | `d2fee1a602734ff7` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-17 | OHI_02 | `e9a37afa2b91e8e7` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-17 | MIZ_07 | `2a7c39eb2932fa75` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-17 | KNZ_03 | `98fd48f2b5530451` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-17 | OHI_03 | `810f01c9b63fb4ac` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-17 | MIZ_08 | `1480e269215f542c` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-17 | KNZ_04 | `25969d2aa418cba8` | 済 | 6000 | 4480 | True | CAPITAL_EFFICIENCY |
| 2026-11-17 | OHI_04 | `5fdf930db41bb3a2` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-17 | MIZ_09 | `e8a63ae130f4655d` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-17 | KNZ_05 | `be5cb5399e2457e0` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-17 | OHI_05 | `4294c290daa80dd2` | 済 | 6000 | 2640 | True | CAPITAL_EFFICIENCY |
| 2026-11-17 | MIZ_10 | `c3e45f7526a09244` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-17 | KNZ_06 | `34ca2085c3df84d2` | 済 | 6000 | 480 | True | EXACT_ORIENTATION |
| 2026-11-17 | OHI_06 | `97c16fc7f72db956` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-17 | MIZ_11 | `060139cb7421987c` | 済 | 6000 | 770 | True | EXACT_ORIENTATION |
| 2026-11-17 | KNZ_07 | `a42d06b5f862b306` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-17 | OHI_07 | `e2559818c9144f4c` | 済 | 6000 | 2100 | True | EXACT_ORIENTATION |
| 2026-11-17 | MIZ_12 | `e9a9b719b61bd420` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-17 | KNZ_08 | `53a128bcfd314e70` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-17 | OHI_08 | `e45409048e792369` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-17 | KNZ_09 | `92ac700f470f584f` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-17 | OHI_09 | `65369cdff64b598b` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-17 | KNZ_10 | `0980ce3813c8d9ad` | 済 | 6000 | 3180 | True | NONE |
| 2026-11-17 | OHI_10 | `184289bbae3f36cf` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-17 | KNZ_11 | `ab762b86e15078e6` | 待 | – | – | – | – |
| 2026-11-17 | OHI_11 | `62169db2beabe927` | 待 | – | – | – | – |
| 2026-11-17 | KNZ_12 | `a9161dc863580e9b` | 待 | – | – | – | – |
