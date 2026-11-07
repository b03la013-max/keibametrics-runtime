# Delivery / Learning Consumption Review

Signed FINAL、GitHub Canonical availability、通知送信、ユーザー到達ACKは別状態。23件の発走前Canonical可用性は確認したが、通知送信・受領ACKは確認していない。観測した経路にはChatGPTへの自動Pushはない。既存Receiptの時刻を後から『Delivery済み』へ書き換えない。

RESULT/learning保存22件、署名原本19件を確認。次予測への正式消費は0件確認であり、存在しなかったとの断定ではない。次Raceは同Venueの次Rとして固定し、署名RESULT時刻と次Cutoffを比較した。署名時刻は生のLearning生成時刻ではない。署名がCutoff後なら、正式な署名証拠はCutoffに間に合わなかったと判定できる。

| 元Race | 次同Venue Race | Signed RESULT時刻 | 次Cutoff | 判定 |
|---|---|---|---|---|
| KM-JRA-NGT-20261017-R06 | KM-JRA-NGT-20261017-R07 | 2026-10-17T04:11:08.578071Z | 2026-10-17T13:00:00+09:00 | SIGNED_LEARNING_DELIVERY_MISS |
| KM-JRA-KYO-20261017-R06 | KM-JRA-KYO-20261017-R07 | 2026-10-17T04:11:04.051941Z | 2026-10-17T13:10:00+09:00 | SIGNED_LEARNING_DELIVERY_MISS |
| KM-JRA-NGT-20261017-R07 | KM-JRA-NGT-20261017-R08 | 2026-10-17T04:41:16.598202Z | 2026-10-17T13:30:00+09:00 | SIGNED_LEARNING_DELIVERY_MISS |
| KM-JRA-KYO-20261017-R07 | KM-JRA-KYO-20261017-R08 | 2026-10-17T04:41:05.596002Z | 2026-10-17T13:40:00+09:00 | SIGNED_LEARNING_DELIVERY_MISS |
| KM-JRA-NGT-20261017-R08 | KM-JRA-NGT-20261017-R09 | 2026-10-17T05:12:26.802288Z | 2026-10-17T14:00:00+09:00 | SIGNED_LEARNING_DELIVERY_MISS |
| KM-JRA-KYO-20261017-R08 | KM-JRA-KYO-20261017-R09 | 2026-10-17T05:12:21.624408Z | 2026-10-17T14:10:00+09:00 | SIGNED_LEARNING_DELIVERY_MISS |
| KM-JRA-NGT-20261017-R10 | KM-JRA-NGT-20261017-R11 | 2026-10-17T06:13:55.196083Z | 2026-10-17T15:10:00+09:00 | SIGNED_LEARNING_DELIVERY_MISS |

7件が上記の署名証拠遅延。9件は署名が次Cutoff前でもIntake未確認。残る20件は原本・次Cutoff・次開催情報等が足りずUNKNOWN。これらをPrediction不的中へ混入しない。

新規 `runtime/jra_learning_intake.py` はhash、Family/Venue、Effective Time、Source freeze、Cutoff、対象Race自身の結果、重複state_idを検証するShadow用Intake準備。Policy/指数への数値適用は一切しない。`runtime/learning_states/jra_day_review_20261017/` の36件は新しいEffective Time、前revision hash、追加レビューを持つunsigned context。元22件の正式Learning/署名原本は維持し、既に走ったRaceへ適用したことにはしない。

実閉ループの受入には、未知Raceで受信state hashとEffective TimeがSource/Prediction freezeより前であること、許可されたOwnerが実際に読んだBinding、下流Prediction/FINALへのLineage、Deliveryを確認する必要がある。現時点ではPENDING。
