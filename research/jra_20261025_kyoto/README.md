# 京都2026-10-25：既存Candidateの全FINAL比較

結果判明後の診断。未知未来OOS、モデル再学習、Production変更ではない。

京都全12Rを分母に保持する。1R・2Rは真正AKI NO_BET、3Rは正式FINALなしで予測評価不能。4R〜12Rの9 FINAL・117頭を対象とし、PAPERの4R・5Rには資金を新設しない。3RのSOURCE取消障害は別PR #337の原本回帰で検収する。

既存PR #332の8方式をそのまま使用し、券種別点数・各掛金の集合・総予算をProductionと一致させた。予測関数へ結果・払戻を渡さず、候補を作成した後で精算する。全ての入力ファイルの生SHAとCandidate Code/PolicyのHashを保存している。

Production：推薦投資8,100円、払戻18,740円、推薦PFS231.358%、最大DD4,800円。ただし払戻の91.942%を京都8Rが占め、同Rの投資・払戻を除くPFSは25.167%。実購入は未確認。

|既存方式|同予算・券種構成の診断PFS|
|---|---:|
|STATIC_INDEX|18.395%|
|FROZEN_OCT18_RANK|18.395%|
|CONTEXT_HISTORY|18.642%|
|OBSERVED_ABILITY|0.000%|
|UNIQUE_EVIDENCE|37.037%|
|BVI_NEUTRAL_SENSITIVITY|18.395%|
|FROZEN_KRS_ROLE|28.272%|
|FROZEN_HEAD_P2|18.395%|

8方式とも今回のProductionを下回り、新規的中救済は0。既存的中を1件失う方式が5、2件失う方式が1。残り2方式も回収額を減らした。この比較からの採用・昇格は行わない。BVI除去、KRS全面採用、総合順位からの一括再構成は今回の解決にならなかった。

凍結済み特徴量の取得数、条件替わり、距離・馬場・同日先行傾向の分母、新馬調教資料、同源根拠の多重寄与、Role移行を`replay.json.gz`に保存した。資料にない調教負荷・併せ・反応や京都の下り加速を補完しない。血統適性の強さと確実さは別に研究する。

再現：

```bash
python scripts/jra_20261025_kyoto_compare.py --data-root /path/to/unchanged/runtime-checkout --output /tmp/kyoto-20261025/replay.json.gz
```

`summary.json`と圧縮詳細は今回の診断証拠。PR332の前向き登録はinactiveのまま。固定BVI-ENV 5e7f…の30 Raceと、この別研究モデルの既存60 Race・3日・2場条件を混ぜない。独立した発走前保存がない今回の再計算は、どちらのOOS台帳にも加えない。
