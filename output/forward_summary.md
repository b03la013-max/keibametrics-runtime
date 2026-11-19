# LOCAL Forward OOS（PAPER・推薦試算・実購入なし）

- 精算Race 191（R30 達成／R100 達成／R500 未達）
- 実効投資 148,000円／払戻 102,090円／**PFS 69.0%**（最大払戻 21,490円を除くと 54.5%）
- 最大ドローダウン 45,910円／黒字Race率 0.162／Bet Coverage 1.0
- W的中 57／P2一致 24／P3一致 27
- 第一失敗の分布：{'WINNER_DISCOVERED_LOW': 40, 'P2_MISS': 25, 'W_WIDTH_OR_ROLE': 67, 'THIRD_MISS': 13, 'WINNER_NOT_DISCOVERED': 27, 'NONE': 16, 'TICKET_OR_CAPITAL': 3}

| 日付 | Race | 締切前 | 精算 | 実効投資 | 払戻 | PFS |
|---|---|---|---|---|---|---|
| 2026-11-13 | 46 | 14 | 14 | 10,900 | 2,920 | 26.8% |
| 2026-11-14 | 22 | 22 | 22 | 17,500 | 8,880 | 50.7% |
| 2026-11-15 | 44 | 44 | 44 | 31,600 | 31,340 | 99.2% |
| 2026-11-16 | 36 | 36 | 36 | 26,800 | 36,680 | 136.9% |
| 2026-11-17 | 36 | 36 | 36 | 29,900 | 11,110 | 37.2% |
| 2026-11-18 | 36 | 36 | 36 | 29,200 | 11,160 | 38.2% |
| 2026-11-19 | 36 | 36 | 3 | 2,100 | 0 | 0.0% |

## 全29指数の観測率（場別・CALCULATEDの比率。それ以外は全頭が規則中立）

| 場 | 頭数 | BVIg-L | CCI | CFIg-L | CSI-L | DRS | EVI/CEV | HCS | HPI-L | JTI-L | OPI-V | PRI | RFIg-L | TRI | URP |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| KNZ | 308 | 0% | 0% | 100% | 100% | 100% | 100% | 100% | 100% | 70% | 100% | 100% | 100% | 0% | 100% |
| KOC | 242 | 0% | 0% | 98% | 98% | 98% | 98% | 98% | 98% | 62% | 100% | 100% | 98% | 0% | 98% |
| KSM | 248 | 0% | 0% | 100% | 100% | 100% | 100% | 100% | 100% | 59% | 54% | 54% | 100% | 0% | 100% |
| MIZ | 383 | 0% | 0% | 99% | 99% | 99% | 99% | 99% | 99% | 61% | 100% | 100% | 99% | 0% | 99% |
| OHI | 591 | 0% | 0% | 93% | 93% | 93% | 93% | 93% | 93% | 65% | 75% | 75% | 93% | 0% | 93% |
| SAG | 234 | 0% | 0% | 100% | 100% | 100% | 100% | 100% | 100% | 65% | 100% | 100% | 100% | 0% | 100% |
| SON | 245 | 0% | 0% | 100% | 100% | 100% | 100% | 100% | 100% | 66% | 58% | 58% | 100% | 0% | 100% |

## 正式Production（署名FINAL・未知未来・推薦試算・実購入なし）

- 署名FINAL 84R／精算 80R／署名RESULT検証 80R
- 実効投資 519,600円／払戻 228,680円／PFS 44.0%／正式◎1着 26
- 正式29指数（Production計算器・未消費）のF3S-L順：78R中 1着的中 23／上位3頭の3着内捕捉 104（正式Static 97）
- 数値Consumer昇格ゲート：精算 78/100R・Ownerレビュー OWNER_APPROVED (2026-11-16)・承認 True

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
| 2026-11-17 | KNZ_11 | `ab762b86e15078e6` | 済 | 6000 | 13550 | True | CAPITAL_EFFICIENCY |
| 2026-11-17 | OHI_11 | `62169db2beabe927` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-17 | KNZ_12 | `a9161dc863580e9b` | 済 | 6000 | 8850 | True | CAPITAL_EFFICIENCY |
| 2026-11-17 | OHI_12 | `57ffb8d2f4440e64` | 済 | 6000 | 5840 | True | NONE |
| 2026-11-18 | KSM_01 | `7fe483276e1e7dc0` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-18 | SON_01 | `107a001ec679ae11` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-18 | KSM_02 | `7995a5543bc6ce3c` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-18 | SON_02 | `a09a9051ce043c04` | 済 | 6000 | 240 | True | CAPITAL_EFFICIENCY |
| 2026-11-18 | KSM_03 | `e38d991869a17cd2` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-18 | SON_03 | `07bcc637cf28ca2b` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-18 | KSM_04 | `1f1d280da8630b38` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-18 | SON_04 | `bf0388e6f1507fdb` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-18 | KSM_05 | `624b4b8f2e790724` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-18 | SON_05 | `a12ae0d58d3eb5be` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-18 | KSM_06 | `1d7a3a661b55b566` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-18 | SON_06 | `f7325dc0b7ea165a` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-18 | KSM_07 | `2d2df54820ef48b1` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-18 | SON_07 | `b26e0ab746d7f5e8` | 済 | 6000 | 2590 | True | CAPITAL_EFFICIENCY |
| 2026-11-18 | KSM_08 | `f9f6e9e672f67553` | 済 | 6000 | 2530 | True | CAPITAL_EFFICIENCY |
| 2026-11-18 | SON_08 | `1e5fabe27d4fe744` | 済 | 6000 | 2470 | True | CAPITAL_EFFICIENCY |
| 2026-11-18 | OHI_01 | `f273901b7e1a6e90` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-18 | KSM_09 | `23d6ec3237f590cc` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-18 | SON_09 | `92f1fbc37a781fbd` | 済 | 6000 | 57270 | True | NONE |
| 2026-11-18 | OHI_02 | `aca39cf5012880b1` | 済 | 6000 | 5110 | True | CAPITAL_EFFICIENCY |
| 2026-11-18 | KSM_10 | `97e701f7d95d97dd` | 済 | 6000 | 2010 | True | NONE |
| 2026-11-18 | SON_10 | `eac9ba4d692c6e60` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-18 | OHI_03 | `cb3e5978e14040b8` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-18 | KSM_11 | `419f8f58ede96fee` | 済 | 6000 | 1090 | True | CAPITAL_EFFICIENCY |
| 2026-11-18 | SON_11 | `0074a662e748717e` | 済 | 6000 | 6200 | True | CAPITAL_EFFICIENCY |
| 2026-11-18 | OHI_04 | `445e8fddf78e990b` | 済 | 6000 | 740 | True | EXACT_ORIENTATION |
| 2026-11-18 | KSM_12 | `6a8b0714ffa8f26e` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-18 | SON_12 | `e0ebae4282642871` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-18 | OHI_05 | `0088ed4ee8c21809` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-18 | OHI_06 | `538a197f1f353cb5` | 済 | 6000 | 1110 | True | CAPITAL_EFFICIENCY |
| 2026-11-18 | OHI_07 | `795529a81d2d425f` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-18 | OHI_08 | `546df00271c2d96b` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-18 | OHI_09 | `fdb18fde9280b2ab` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-18 | OHI_10 | `d1a3d87c051a8d1c` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-18 | OHI_11 | `a4982fc9a7427f7d` | 済 | 6000 | 16110 | True | NONE |
| 2026-11-18 | OHI_12 | `511087e36e3c3438` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-19 | KSM_01 | `52b926247408a69d` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-19 | SON_01 | `d7e06de8c8463e72` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-19 | KSM_02 | `822ef6c557bea4c6` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-19 | SON_02 | `7a372d34b9c11af8` | 待 | – | – | – | – |
| 2026-11-19 | KSM_03 | `e77cf0ed9f6d4f46` | 待 | – | – | – | – |
| 2026-11-19 | SON_03 | `65262f6145ebad67` | 待 | – | – | – | – |
| 2026-11-19 | KSM_04 | `5fd0f9d68745f3ce` | 待 | – | – | – | – |
