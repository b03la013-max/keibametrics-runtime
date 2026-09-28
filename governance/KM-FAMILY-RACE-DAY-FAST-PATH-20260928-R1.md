# ケイバメトリクス Race-Day Fast Path R1

制定日：2026-09-28  
Profile：`KM-FAMILY-RACE-DAY-FAST-PATH-20260928-R1`

## 0. 目的

30分間隔の地方開催で、正式予測・購入・結果照合・次走準備を現実的に完遂できるよう、Full Formal品質を維持したままWall-clock latencyを縮める。

Fast Pathは簡易版Predictionではない。同一入力ではFull Pathと同じPrediction/Selection/Execution結果を要求する。

## 1. 絶対原則

```text
FAST != FEWER REQUIRED STAGES
FAST = PRECOMPUTE + PARALLELIZE + EXACT-CACHE + DELTA-INVALIDATE + DEFER NON-CRITICAL RESEARCH
```

省略による高速化は禁止する。

## 2. SLO

- Production FINAL critical-path target：300秒
- Hard SLO：420秒
- 購入余裕 target：発走600秒前
- Race-Day Reflection target：120秒
- Next-race prewarm：n+1～n+3

SLO超過は診断対象であり、Formal Gateを無視する理由にはならない。

## 3. Cache Authority

キャッシュにはPrediction Authorityを与えない。

再利用条件は、

1. Stage一致
2. dependency SHA256一致
3. 実装コードSHA256一致
4. profile一致

の全て。

一つでも異なればMISSとし、Production canonical calculationを実行する。

## 4. 現在高速化するProduction工程

LOCAL Numerical MaterializationをRunner単位へ分解し、最大8 worker、通常4 workerで並列処理する。

キャッシュするのはDerived canonical componentsのみであり、Runner名、SOURCE receipt、Current State等の無関係又は時変fieldをキャッシュから復元しない。

## 5. Ahead-of-Race Preparation

既に正式requestが作成されている未来Raceについてn+1～n+3をprewarmする。

Prewarmは非権威。Formal時点でdependencyが変われば自動再計算する。

## 6. Dynamic Invalidation

取消、馬体重、Current Market、Official Going、Same-day Track State、Venue Context等の変更は、影響するdependency SHAを変化させる。

その結果、該当Stageだけcache MISSとなる。無関係Stageは再利用できる。

## 7. Race-Day Reflection

結果後は最初に、

```text
Settlement/PFS
→ W/P2/P3 Capture
→ Pair/Set/Exact Conversion
→ KRS Evaluation
→ First Material Failure
→ Next-Race Learning State
```

をFast Reflectionとして確定する。

Candidate numerical research、MEC Shadow詳細、Canon改定研究等はその後段へ置く。

## 8. Full/Fast Equivalence

AcceptanceではCold cacheとWarm cacheの両方でcanonical Full materializationとFast materializationがdict-equivalentであることを要求する。

最終成果物比較ではReceipt timestamp等を除き、Prediction、MEC、Capital、Ticket、StakeのBehavior projection一致を要求する。

## 9. Fallback

Fast Path内部で例外・cache corruption・hash不一致・equivalence failureが起きた場合、Fast結果を採用せずcanonical Full Pathへ戻る。

`FAST-PATH-ERROR -> FULL-PATH`

であり、`FAST-PATH-ERROR -> PARTIAL-PREDICTION`ではない。

## 10. Production Freeze

本R1は数値式、Weight、KRS physics、parameter_map、MEC-R3、Capital Policy、Venue Prediction Knowledgeを変更しない。
