# ケイバメトリクスFamily 実行Architecture正式統合改定 R8

制定日：2026-09-28  
Profile：`KM-FAMILY-EXECUTION-ARCHITECTURE-20260928-R8`  
Predecessor：`KM-FAMILY-EXECUTION-ARCHITECTURE-20260928-R7`

## 0. 継承

R7のScope Ownership、Formal Lifecycle、Current Authority Guard、Family Isolation、Prediction Utility、Promotion Governanceを全面継承する。

**R8はFormal Stageを削除しない。**

R8が変更するのはWall-clock execution architectureのみである。

## 1. Race-Day Fast Path

`KM-FAMILY-RACE-DAY-FAST-PATH-20260928-R1` をProduction Execution Optimizationとして接続する。

初期対象はLOCAL、優先VenueはFNBとする。

```text
Full Formal Intelligence
+ Precompute
+ Exact Content Cache
+ Runner Parallelism
+ Delta Invalidation
+ Next-3 Prewarm
+ Fast Reflection
= Same Required Output / Shorter Wall Clock
```

## 2. Formal Lifecycle

R7のexecution_sequenceを完全維持する。

Precomputeされた値はFormal Stageそのものの完了を意味しない。Formal時点でCurrent Authority、Signed Source、Runner Universe、Current State、dependency SHA、implementation SHAを再確認した後にだけ再利用できる。

## 3. Cache

CacheはAuthorityではない。

`stage + exact dependency SHA256 + implementation SHA256 + profile` が一致する場合のみ利用できる。

不一致、破損、例外はすべてMISSとしてcanonical Full Pathへ戻す。

## 4. Parallelism

Runner単位等、依存関係が独立した純粋計算のみ並列化できる。

Temporal Stage、Signed Receipt verification、KRS handoff、MEC、Capital、FINALの依存順序は並列化を理由に逆転させない。

## 5. Prewarm

既に作成済みの同日未来requestについてn+1～n+3を先行計算できる。

未来requestを推測・捏造しない。

当日結果、取消、馬体重、Official Going等によりdependencyが変化した場合、該当cacheは自動失効する。

## 6. Reflection

Verified RESULT直後にFast Reflectionを生成する。

Fast ReflectionはPFS、W/P2/P3、Pair/Set/Exact、KRS分類、First Material Failure、Next Learning Stateを即時返す。

深いCandidate/OOS/Canon研究はCritical Path外へ送る。

## 7. SLO

- FINAL target：300秒
- Hard SLO：420秒
- Purchase reserve target：600秒
- Fast Reflection target：120秒

SLOは品質Gateより下位である。SLO達成のためにGateを省略してはならない。

## 8. Full/Fast Equivalence

同一入力についてFastとFullでPrediction/Selection/Execution behaviorが一致しなければFast PathをProduction利用しない。

Receipt timestamp、workflow id等の非行動差は同値性対象外とする。

## 9. Freeze

Prediction Model、指数式、Weight、KRS physics、parameter_map、MEC-R3、Capital Policy、FNB v2.1 Prediction Knowledgeは変更しない。
