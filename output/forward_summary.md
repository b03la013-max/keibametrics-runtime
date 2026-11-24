# LOCAL Forward OOS（PAPER・推薦試算・実購入なし）

- 精算Race 377（R30 達成／R100 達成／R500 未達）
- 実効投資 298,900円／払戻 181,870円／**PFS 60.8%**（最大払戻 21,490円を除くと 53.7%）
- 最大ドローダウン 117,030円／黒字Race率 0.167／Bet Coverage 1.0
- W的中 124／P2一致 50／P3一致 52
- 頑健性（影の計測）：上位2/3払戻を除くPFS 49.2%／47.1%・最長連敗 23R（偶然でこれ以上が起きる確率 0.6143）・累計PFS100%以上だった割合 0.0・Race別PFS中央値 0.0%・的中なのに収支マイナス率 0.526
- 第一失敗の分布：{'WINNER_DISCOVERED_LOW': 76, 'P2_MISS': 61, 'W_WIDTH_OR_ROLE': 131, 'THIRD_MISS': 22, 'WINNER_NOT_DISCOVERED': 46, 'NONE': 35, 'TICKET_OR_CAPITAL': 6}

| 日付 | Race | 締切前 | 精算 | 実効投資 | 払戻 | PFS |
|---|---|---|---|---|---|---|
| 2026-11-13 | 46 | 14 | 14 | 10,900 | 2,920 | 26.8% |
| 2026-11-14 | 22 | 22 | 22 | 17,500 | 8,880 | 50.7% |
| 2026-11-15 | 44 | 44 | 44 | 31,600 | 31,340 | 99.2% |
| 2026-11-16 | 36 | 36 | 36 | 26,800 | 36,680 | 136.9% |
| 2026-11-17 | 36 | 36 | 36 | 29,900 | 11,110 | 37.2% |
| 2026-11-18 | 36 | 36 | 36 | 29,200 | 11,160 | 38.2% |
| 2026-11-19 | 36 | 36 | 36 | 31,600 | 10,440 | 33.0% |
| 2026-11-20 | 36 | 36 | 36 | 30,300 | 15,130 | 49.9% |
| 2026-11-21 | 23 | 23 | 23 | 18,200 | 5,790 | 31.8% |
| 2026-11-22 | 34 | 34 | 34 | 25,300 | 24,800 | 98.0% |
| 2026-11-23 | 33 | 33 | 33 | 26,400 | 10,350 | 39.2% |
| 2026-11-24 | 36 | 36 | 27 | 21,200 | 13,270 | 62.6% |

## 全29指数の観測率（場別・CALCULATEDの比率。それ以外は全頭が規則中立）

| 場 | 頭数 | BVIg-L | CCI | CFIg-L | CSI-L | DRS | EVI/CEV | HCS | HPI-L | JTI-L | OPI-V | PRI | RFIg-L | TRI | URP |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| KNZ | 401 | 0% | 0% | 100% | 100% | 100% | 100% | 100% | 100% | 67% | 100% | 100% | 100% | 0% | 100% |
| KOC | 474 | 0% | 0% | 99% | 99% | 99% | 99% | 99% | 99% | 61% | 94% | 94% | 99% | 0% | 99% |
| KSM | 363 | 0% | 0% | 100% | 100% | 100% | 100% | 100% | 100% | 59% | 88% | 88% | 100% | 0% | 100% |
| MIZ | 755 | 0% | 0% | 99% | 99% | 99% | 99% | 99% | 99% | 63% | 100% | 100% | 99% | 0% | 99% |
| NGY | 140 | 0% | 0% | 100% | 100% | 100% | 100% | 100% | 100% | 46% | 66% | 66% | 100% | 0% | 100% |
| OHI | 733 | 0% | 0% | 95% | 95% | 95% | 95% | 95% | 95% | 67% | 100% | 100% | 95% | 0% | 95% |
| SAG | 584 | 0% | 0% | 100% | 100% | 100% | 100% | 100% | 100% | 64% | 96% | 96% | 100% | 0% | 100% |
| SON | 365 | 0% | 0% | 98% | 98% | 98% | 98% | 98% | 98% | 66% | 92% | 92% | 98% | 0% | 98% |
| URW | 131 | 0% | 0% | 89% | 89% | 66% | 89% | 89% | 89% | 56% | 100% | 100% | 89% | 0% | 66% |

## 正式Production（署名FINAL・未知未来・推薦試算・実購入なし）

- 署名FINAL 264R／精算 259R／署名RESULT検証 259R
- 実効投資 1,593,600円／払戻 1,337,370円／PFS 83.9%／正式◎1着 89
- 正式29指数（Production計算器・未消費）のF3S-L順：257R中 1着的中 80／上位3頭の3着内捕捉 366（正式Static 367）
- 数値Consumer昇格ゲート：精算 257/100R・Ownerレビュー OWNER_APPROVED (2026-11-16)・承認 True

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
| 2026-11-19 | SON_02 | `7a372d34b9c11af8` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-19 | KSM_03 | `e77cf0ed9f6d4f46` | 済 | 6000 | 12910 | True | NONE |
| 2026-11-19 | SON_03 | `03a31afa4455435d` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-19 | KSM_04 | `d3ca48548f71b6c4` | 済 | 6000 | 586840 | True | NONE |
| 2026-11-19 | SON_04 | `a314b337aa63d62c` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-19 | KSM_05 | `cb34d1395859a45a` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-19 | SON_05 | `32bfdd91bb0e7f80` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-19 | KSM_06 | `30cec064096d8609` | 済 | 6000 | 19100 | True | NONE |
| 2026-11-19 | SON_06 | `790bca3f79b87989` | 済 | 6000 | 320 | True | CAPITAL_EFFICIENCY |
| 2026-11-19 | KSM_07 | `01e75fc5dc7b3b07` | 済 | 6000 | 9880 | True | CAPITAL_EFFICIENCY |
| 2026-11-19 | SON_07 | `a5a1a9461f0fcbd2` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-19 | KSM_08 | `f8e1ef26d14e5627` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-19 | SON_08 | `f0727f974dffef4f` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-19 | OHI_01 | `524b8ab532e5ca6b` | 済 | 6000 | 3580 | True | CAPITAL_EFFICIENCY |
| 2026-11-19 | KSM_09 | `d6a2d7fc78644a18` | 済 | 6000 | 640 | True | CAPITAL_EFFICIENCY |
| 2026-11-19 | SON_09 | `b18056f331fcad10` | 済 | 6000 | 5340 | True | CAPITAL_EFFICIENCY |
| 2026-11-19 | OHI_02 | `20e8c9653e068b7a` | 済 | 6000 | 3060 | True | CAPITAL_EFFICIENCY |
| 2026-11-19 | KSM_10 | `a5a1fcc65b9d9a41` | 済 | 6000 | 27710 | True | NONE |
| 2026-11-19 | SON_10 | `b7954d010a6bd52c` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-19 | OHI_03 | `f3a6f58658f339b0` | 済 | 6000 | 4310 | True | NONE |
| 2026-11-19 | KSM_11 | `ae8a9b7f7ce3b1bb` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-19 | SON_11 | `c1f6785e455482ed` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-19 | OHI_04 | `50f0192b238298fa` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-19 | KSM_12 | `5b4665fd87abf225` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-19 | SON_12 | `18f13ca0bee1640b` | 済 | 6000 | 2440 | True | CAPITAL_EFFICIENCY |
| 2026-11-19 | OHI_05 | `cb0020f498f4e7be` | 済 | 6000 | 7420 | True | CAPITAL_EFFICIENCY |
| 2026-11-19 | OHI_06 | `cb0ae65101a5976d` | 済 | 6000 | 520 | True | EXACT_ORIENTATION |
| 2026-11-19 | OHI_07 | `fe96af83de02c89a` | 済 | 6000 | 5290 | True | CAPITAL_EFFICIENCY |
| 2026-11-19 | OHI_08 | `85bb166ec8b47f03` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-19 | OHI_09 | `efd2d592a2bad2d2` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-19 | OHI_10 | `f4134d46c2b6303a` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-19 | OHI_11 | `e182d0bcc8614bf9` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-19 | OHI_12 | `c99cb7f4d46c69c1` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-20 | KSM_01 | `3e8acf47ac60bf28` | 済 | 6000 | 1160 | True | CAPITAL_EFFICIENCY |
| 2026-11-20 | SON_01 | `c6dc96d85190a1f7` | 済 | 6000 | 760 | True | NONE |
| 2026-11-20 | KSM_02 | `b726f4419697bc46` | 済 | 6000 | 3220 | True | CAPITAL_EFFICIENCY |
| 2026-11-20 | SON_02 | `a8decd483e815bf9` | 済 | 6000 | 430 | True | CAPITAL_EFFICIENCY |
| 2026-11-20 | KSM_03 | `7b225c058db4f282` | 済 | 6000 | 12340 | True | NONE |
| 2026-11-20 | SON_03 | `18f7867d3bf2891b` | 済 | 6000 | 3450 | True | NONE |
| 2026-11-20 | KSM_04 | `4e0ae1f45af721a7` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-20 | SON_04 | `9234d3a97176f3df` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-20 | KSM_05 | `c37ccb2d8f4d5b99` | 済 | 6000 | 1890 | True | CAPITAL_EFFICIENCY |
| 2026-11-20 | SON_05 | `7f9b26b5d4f57220` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-20 | KSM_06 | `4e50ad8ac19696ad` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-20 | SON_06 | `436da215cd4ff954` | 済 | 6000 | 19370 | True | NONE |
| 2026-11-20 | KSM_07 | `7696cf5ab38cbe3d` | 済 | 6000 | 1250 | True | CAPITAL_EFFICIENCY |
| 2026-11-20 | SON_07 | `c5a0114782167c5e` | 済 | 6000 | 11050 | True | NONE |
| 2026-11-20 | KSM_08 | `1225e1a5cd0eb403` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-20 | SON_08 | `1e26669e59af236b` | 済 | 6000 | 10890 | True | CAPITAL_EFFICIENCY |
| 2026-11-20 | OHI_01 | `6bde0e990871db3a` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-20 | KSM_09 | `69734133966d6018` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-20 | SON_09 | `e87ab987f83775fb` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-20 | OHI_02 | `778b789eb5a0aebb` | 済 | 6000 | 33400 | True | NONE |
| 2026-11-20 | KSM_10 | `f1018206055014c4` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-20 | SON_10 | `9348551224b5b3a1` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-20 | OHI_03 | `97039a0393487ac9` | 済 | 6000 | 6470 | True | CAPITAL_EFFICIENCY |
| 2026-11-20 | KSM_11 | `1c0cee05184d7c00` | 済 | 6000 | 3440 | True | CAPITAL_EFFICIENCY |
| 2026-11-20 | SON_11 | `9cfc446c26d7e658` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-20 | OHI_04 | `b71a6da80e57804e` | 済 | 6000 | 1810 | True | CAPITAL_EFFICIENCY |
| 2026-11-20 | KSM_12 | `bf2ead336b62cd06` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-20 | SON_12 | `149fa3221242905c` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-20 | OHI_05 | `128b7b063366ee89` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-20 | OHI_06 | `b44f19537a98840b` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-20 | OHI_07 | `7360e0f191c966bc` | 済 | 6000 | 15630 | True | NONE |
| 2026-11-20 | OHI_08 | `9ef2cff532ae0e30` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-20 | OHI_09 | `53ac2e0dab058812` | 済 | 6000 | 210 | True | CAPITAL_EFFICIENCY |
| 2026-11-20 | OHI_10 | `694bd7ec99408f87` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-20 | OHI_11 | `f4123834ff6b914a` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-20 | OHI_12 | `c674faa38bc18f7d` | 済 | 6000 | 9130 | True | CAPITAL_EFFICIENCY |
| 2026-11-21 | SAG_04 | `2801c158a120fed5` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-21 | KOC_05 | `f74dd9f232965a45` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-21 | SAG_05 | `da6148665b1a2f01` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-21 | KOC_06 | `8bd5755bbe0f6216` | 済 | 6000 | 7010 | True | CAPITAL_EFFICIENCY |
| 2026-11-21 | SAG_06 | `539b60007881419e` | 済 | 6000 | 1580 | True | CAPITAL_EFFICIENCY |
| 2026-11-21 | KOC_07 | `71583e3c553dda9b` | 済 | 6000 | 440 | True | CAPITAL_EFFICIENCY |
| 2026-11-21 | SAG_07 | `ea3d93ce87345147` | 済 | 6000 | 620 | True | CAPITAL_EFFICIENCY |
| 2026-11-21 | KOC_08 | `fd31406971cdd0e5` | 済 | 6000 | 160 | True | CAPITAL_EFFICIENCY |
| 2026-11-21 | SAG_08 | `4f6293dc61a2a2fd` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-21 | KOC_09 | `490fc0326c3d8fed` | 済 | 6000 | 9610 | True | CAPITAL_EFFICIENCY |
| 2026-11-21 | SAG_09 | `b533fb3e0a03b1ce` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-21 | KOC_10 | `183dad15f37e4830` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-21 | SAG_10 | `9375369661500b7b` | 済 | 6000 | 2150 | True | NONE |
| 2026-11-21 | KOC_11 | `6acc0053c86cf329` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-21 | SAG_11 | `5d6b4aa66a53c002` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-21 | KOC_12 | `62289e6024f10f43` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-22 | MIZ_01 | `dd39eaa92f3a6386` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-22 | MIZ_02 | `84e12bddea95c406` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-22 | MIZ_03 | `ca88d09e8af49a14` | 済 | 6000 | 9150 | True | CAPITAL_EFFICIENCY |
| 2026-11-22 | MIZ_04 | `f5ecde526bdd6299` | 済 | 6000 | 3050 | True | CAPITAL_EFFICIENCY |
| 2026-11-22 | MIZ_05 | `2be8eb21db57c206` | 済 | 6000 | 2430 | True | CAPITAL_EFFICIENCY |
| 2026-11-22 | MIZ_06 | `4414960029d5a322` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-22 | SAG_01 | `c375ca6cf7e9fc88` | 済 | 6000 | 600 | True | PREDICTION_ROLE_W |
| 2026-11-22 | MIZ_07 | `e98d15085bbcfd65` | 済 | 6000 | 6230 | True | CAPITAL_EFFICIENCY |
| 2026-11-22 | KOC_01 | `cf184e2925468881` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-22 | SAG_02 | `793b02ab46c7a679` | 済 | 6000 | 9870 | True | NONE |
| 2026-11-22 | KOC_02 | `f1be25b2544496d3` | 済 | 6000 | 5590 | True | CAPITAL_EFFICIENCY |
| 2026-11-22 | MIZ_08 | `a00db139c0bdbc4d` | 済 | 6000 | 6650 | True | CAPITAL_EFFICIENCY |
| 2026-11-22 | SAG_03 | `f1f84bd6239187ac` | 済 | 6000 | 20060 | True | NONE |
| 2026-11-22 | KOC_03 | `891556219c35c3ed` | 済 | 6000 | 5800 | True | CAPITAL_EFFICIENCY |
| 2026-11-22 | MIZ_09 | `19665cf1a04e24b6` | 済 | 6000 | 490 | True | EXACT_ORIENTATION |
| 2026-11-22 | SAG_04 | `470480861046523e` | 済 | 6000 | 1030 | True | NONE |
| 2026-11-22 | KOC_04 | `0680435a4fd5a474` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-22 | MIZ_10 | `5dbcc0b94afcba1a` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-22 | SAG_05 | `8ae506f0dc663f22` | 済 | 6000 | 2650 | True | CAPITAL_EFFICIENCY |
| 2026-11-22 | KOC_05 | `8e0151f320b7b4bb` | 済 | 6000 | 3970 | True | CAPITAL_EFFICIENCY |
| 2026-11-22 | MIZ_11 | `9666694caee399f7` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-22 | SAG_06 | `9995396c360ae1d4` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-22 | KOC_06 | `be9b40efde919083` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-22 | MIZ_12 | `7c18942c4d8ed85a` | 済 | 6000 | 8150 | True | NONE |
| 2026-11-22 | SAG_07 | `2c8aee579b280906` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-22 | KOC_07 | `a19f1eeb5a023d7e` | 済 | 6000 | 2200 | True | CAPITAL_EFFICIENCY |
| 2026-11-22 | SAG_08 | `0bd7d9ef937d3c87` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-22 | KOC_08 | `af681130fb3ecb3e` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-22 | SAG_09 | `6c839f37ba723b44` | 済 | 6000 | 3470 | True | CAPITAL_EFFICIENCY |
| 2026-11-22 | KOC_09 | `6b2e355d38e0a111` | 済 | 6000 | 800 | True | PREDICTION_ROLE_W |
| 2026-11-22 | SAG_10 | `bde95758de18ba1a` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-22 | KOC_10 | `ca639c1af317b9e0` | 済 | 6000 | 1470 | True | CAPITAL_EFFICIENCY |
| 2026-11-22 | SAG_11 | `26f320969e1da2b6` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-22 | KOC_11 | `2f03fb622dbcdced` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-23 | MIZ_01 | `dbb237efb3327c13` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-23 | MIZ_02 | `226fe55731c02f65` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-23 | MIZ_03 | `4bb7818e213a497a` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-23 | KNZ_01 | `9303212f44c664ed` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-23 | MIZ_04 | `14148610e1c4372c` | 済 | 6000 | 2660 | True | CAPITAL_EFFICIENCY |
| 2026-11-23 | KNZ_02 | `e67d2120aff3ff78` | 済 | 6000 | 1350 | True | CAPITAL_EFFICIENCY |
| 2026-11-23 | MIZ_05 | `4274af31364f5cff` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-23 | KNZ_03 | `36fe33be389c8ce6` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-23 | MIZ_06 | `17def28d4a5bdc3f` | 済 | 6000 | 3220 | True | CAPITAL_EFFICIENCY |
| 2026-11-23 | KNZ_04 | `162ad9b6becdc9ca` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-23 | MIZ_07 | `18bcf05596bf6e69` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-23 | SAG_01 | `bad7c5e1b44e61e0` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-23 | MIZ_08 | `55bd5f8d35e5aeb8` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-23 | KNZ_05 | `ef8976a2ff5a57a6` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-23 | SAG_02 | `222c15eaa7796558` | 済 | 6000 | 4360 | True | CAPITAL_EFFICIENCY |
| 2026-11-23 | MIZ_09 | `63f185ef05187046` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-23 | KNZ_06 | `3d0e071776c1ed96` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-23 | SAG_03 | `ded98680e75b07e0` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-23 | MIZ_10 | `abe7860c57cce4f4` | 済 | 6000 | 1510 | True | PREDICTION_ROLE_W |
| 2026-11-23 | KNZ_07 | `e677337d7679f989` | 済 | 6000 | 2310 | True | CAPITAL_EFFICIENCY |
| 2026-11-23 | SAG_04 | `c1a92571f89415e9` | 済 | 6000 | 1150 | True | CAPITAL_EFFICIENCY |
| 2026-11-23 | MIZ_11 | `945beab3b4b05805` | 済 | 6000 | 240 | True | PREDICTION_ROLE_W |
| 2026-11-23 | SAG_05 | `756679e5c0a48b0a` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-23 | KNZ_08 | `affa60b17a02ce9a` | 済 | 6000 | 970 | True | PREDICTION_ROLE_W |
| 2026-11-23 | MIZ_12 | `0362f3dbc1d63fc8` | 済 | 6000 | 470 | True | CAPITAL_EFFICIENCY |
| 2026-11-23 | SAG_06 | `301573cc9440c196` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-23 | KNZ_09 | `8a88c36a1debff76` | 済 | 6000 | 4200 | True | CAPITAL_EFFICIENCY |
| 2026-11-23 | SAG_07 | `c766ef0bd8fdac90` | 済 | 6000 | 1980 | True | CAPITAL_EFFICIENCY |
| 2026-11-23 | KNZ_10 | `65ef958fc4ab9fae` | 済 | 6000 | 47770 | True | NONE |
| 2026-11-23 | SAG_08 | `b79430103234c149` | 済 | 6000 | 1480 | True | CAPITAL_EFFICIENCY |
| 2026-11-23 | SAG_09 | `b882470af77112a8` | 済 | 6000 | 1790 | True | CAPITAL_EFFICIENCY |
| 2026-11-23 | SAG_10 | `ef0f67d5e3037a52` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-23 | SAG_11 | `c09191281147c577` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-24 | MIZ_01 | `fd975af1b62d35bf` | 済 | 6000 | 780 | True | CAPITAL_EFFICIENCY |
| 2026-11-24 | MIZ_02 | `9f0d0d6a2befdf47` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-24 | URW_01 | `66d0f5b5618c25bb` | 済 | 6000 | 940 | True | CAPITAL_EFFICIENCY |
| 2026-11-24 | MIZ_03 | `906c7ec85f64a46d` | 済 | 6000 | 2090 | True | CAPITAL_EFFICIENCY |
| 2026-11-24 | URW_02 | `71e41df0aeaba8cb` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-24 | URW_03 | `303ff7340b1bae38` | 済 | 6000 | 1860 | True | CAPITAL_EFFICIENCY |
| 2026-11-24 | MIZ_04 | `a703baa29914de1f` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-24 | URW_04 | `2d01a73c773c8832` | 済 | 6000 | 8660 | True | NONE |
| 2026-11-24 | MIZ_05 | `ecc231f3732d1907` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-24 | URW_05 | `b2a82e8162508512` | 済 | 6000 | 8430 | True | PREDICTION_ROLE_W |
| 2026-11-24 | NGY_01 | `726d9bfc32c8deee` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-24 | MIZ_06 | `973e19e08e7ff6ef` | 済 | 6000 | 4290 | True | CAPITAL_EFFICIENCY |
| 2026-11-24 | URW_06 | `ad4d66c286d548f3` | 済 | 6000 | 5320 | True | CAPITAL_EFFICIENCY |
| 2026-11-24 | NGY_02 | `96a458b5de4a3c0d` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-24 | MIZ_07 | `0876b7d96904aadc` | 済 | 6000 | 8210 | True | NONE |
| 2026-11-24 | URW_07 | `3866b3b45b4763ff` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-24 | NGY_03 | `f5cf7bf81f50aaa5` | 済 | 6000 | 1290 | True | PREDICTION_ROLE_W |
| 2026-11-24 | MIZ_08 | `4ee787d31cf09bac` | 済 | 6000 | 2950 | True | CAPITAL_EFFICIENCY |
| 2026-11-24 | URW_08 | `af5cf7c64b4e1078` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-24 | NGY_04 | `bbd45226b5bb4773` | 済 | 6000 | 5050 | True | PREDICTION_ROLE_W |
| 2026-11-24 | MIZ_09 | `c909203e149d3cf1` | 済 | 6000 | 2420 | True | PREDICTION_ROLE_W |
| 2026-11-24 | URW_09 | `c9f6c2c325f61755` | 済 | 6000 | 15320 | True | CAPITAL_EFFICIENCY |
| 2026-11-24 | NGY_05 | `db9ace94c28c4cd5` | 済 | 6000 | 1750 | True | CAPITAL_EFFICIENCY |
| 2026-11-24 | MIZ_10 | `ddc87548eb82229c` | 済 | 6000 | 1100 | True | CAPITAL_EFFICIENCY |
| 2026-11-24 | URW_10 | `bcb91b6fac6ed09d` | 済 | 6000 | 0 | True | PREDICTION_ROLE_P2 |
| 2026-11-24 | NGY_06 | `12661c2812e40ba5` | 済 | 6000 | 0 | True | PREDICTION_ROLE_W |
| 2026-11-24 | MIZ_11 | `81e44070711e01e2` | 済 | 6000 | 22280 | True | NONE |
| 2026-11-24 | URW_11 | `4a824c75bc3add97` | 待 | – | – | – | – |
| 2026-11-24 | NGY_07 | `61ac53e37985e688` | 待 | – | – | – | – |
| 2026-11-24 | MIZ_12 | `02d44a458a3f338c` | 待 | – | – | – | – |
| 2026-11-24 | URW_12 | `0994fd88f90811dc` | 待 | – | – | – | – |
| 2026-11-24 | NGY_08 | `1ce84744a34e48ff` | 待 | – | – | – | – |
