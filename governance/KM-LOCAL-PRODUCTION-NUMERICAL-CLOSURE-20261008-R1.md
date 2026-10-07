# KM-LOCAL-PRODUCTION-NUMERICAL-CLOSURE-20261008-R1

## Status

ACTIVE / LOCAL / PRODUCTION-NUMERICAL-AUTHORITY / C1-EXECUTION-CLOSURE / FULL-63-RULE-BINDING / FULL-29-INDEX-NUMERICAL-CLOSURE / UNCALIBRATED-RULE-BASED / PREDICTION-CONSUMPTION-GATED

## 1. Purpose

LOCAL正式予測で長期間残っていた

`NOT_READY / 63 REQUIRED COMPONENT SCORE RULES UNBOUND / DEGRADED EXECUTION ONLY`

を終了する。

今後のR44以後のLOCAL FORMAL-PRE-RACEでは、Signed SOURCEとOfficial Runner Universeから全馬29 required indicesをProduction Numerical Authorityで数値Terminalへ閉じる。

## 2. Production numerical authority

Evidence rule registry:

`LOCAL-EVIDENCE-FEATURE-RULE-REGISTRY-v1.1-PRODUCTION-NUMERICAL-20261008`

Mapping:

`LOCAL-FULL-NUMERICAL-MAPPING-v1.0-PRODUCTION-20261008`

Materializer:

`runtime/local_fullnumerical_production.py`

Component rules:

63 / 63 bound.

Required indices:

29 / 29.

## 3. Strict numerical terminal policy

正式な数値Terminalは以下を区別する。

- CALCULATED
- RULED-NEUTRAL

R44 Ready pathでは以下を許さない。

- RULED-HOLD
- unresolved
- provenance missing
- finite value missing

`RULED-NEUTRAL` はCALCULATEDと偽装しない。

52等のneutral transport valueはUNKNOWN/incomparable evidenceのためのrule-bound transport valueであり、能力52点を意味しない。MissingnessとDCR consequenceを必ず保持する。

したがってR44のStrict Numerical Closureは、

`CALCULATED + RULED-NEUTRAL = required cells`

かつ

`RULED-HOLD = 0 / unresolved = 0`

で成立する。

## 4. Why v0.1 rules were promoted mechanically

既存v0.1 Candidateは63/63 component ruleをresult-blind deterministic transformとして既に実装していた。

R44ではそのtransformをC1 Numerical Execution ClosureとしてProductionへ昇格する。

これはCandidateの予測性能をProductionへ昇格する意味ではない。

v0.2はretrospective calibrated、v0.3はevidence-routing変更を含み、Forward OOS上でv0.1を明確に上回っていないため、R44のProduction Numerical execution ruleには採用しない。

## 5. Authority separation

### Numerical materialization authority
PRODUCTION / ACTIVE.

### Prediction consumption authority
NOT AUTHORIZED by R44.

Numerical rankingを理由にStatic Ranking、W/P2/P3、Pair/Thirdを自動変更しない。

### KRS consumption authority
NOT AUTHORIZED by R44.

Production KRSは当面、既存source-derived technical proxy経路を維持する。

### Ticket / Capital consumption authority
NOT AUTHORIZED by R44.

Numerical indexだけを理由にMEC/Ticket/Stakeを変更しない。

## 6. Forward validation

Numerical valuesはR44以後すべて正式保存する。

その上で、

- Numerical rank vs actual winner/top3
- Static Prediction vs Numerical rank
- KRS Technical Proxy vs Numerical-fed KRS Shadow
- Winner/P2/P3 capture
- Pair/Exact downstream utility
- PFS / Drawdown / Hit-but-Loss

を未知未来で比較する。

Numerical→Prediction/KRS/Ticket/Capitalの各接続は、別々のForward OOS GateとHuman Reviewを必要とする。

## 7. Temporal purity

R44 effective:

2026-10-08T00:15:00+09:00

2026-10-07大井R1-R12へR44を遡及適用しない。

過去Raceはmechanical replay/regressionに使用できるがProduction/OOS creditを与えない。

## 8. Final principle

「指数が未完成だからNarrativeだけで走る」状態を終了する。

同時に、

「指数を計算できるようになったから、その指数が予測的に正しいとみなす」

ことも禁止する。

Production Numerical CompletionとPredictive Promotionを分離し、前者を今完成させ、後者は未知未来で勝った場合だけ段階的に接続する。
