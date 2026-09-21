# ケイバメトリクスFamily Minimum Efficient Coverage Mandatory Overlay R3

制定日：2026-09-21
Profile：KM-FAMILY-MINIMUM-EFFICIENT-COVERAGE-20260921-R3
Predecessor：KM-FAMILY-MINIMUM-EFFICIENT-COVERAGE-20260921-R2
Status：ACTIVE / FAMILY-WIDE / PRODUCTION-EXECUTION-OVERLAY / NON-NUMERICAL / PRECOMPRESSION-SEMANTIC-COVERAGE / NO-FIXED-TICKET-CAP / FAIL-CLOSED

## 1. 中心修復
R2の「100% Material Coverage」を、Pair-local圧縮後のUniverseではなく、
Global W/P2/P3から始まるPre-Compression Semantic Universeに対して定義する。

## 2. P3 Tail Floor
Material Ordered Pair（PURCHASE又は非手続的PROTECT）に対し、Global P3 Active馬は、
hard structural exclusionがない限りMEC前に消してはならない。

Pair-local:
- PURCHASE -> CORE Exact Third
- PROTECT -> PROTECTION Set Third
- EXCLUDE + hard structural reason -> HARD EXCLUSION
- EXCLUDE + lower materiality/budget/soft reason -> TAIL Set Protection
- disposition missing -> synthesized TAIL Set Protection

TAILは原則TRIOで低資本保護し、Exact Orientationを自動主張しない。

## 3. Hard Exclusion
SCRATCH / WITHDRAWN / NOT_APPLICABLE / IMPOSSIBLE / ROLE_INELIGIBLE /
FORMAL_OUT_OF_SCOPE等の構造的理由のみMEC前の除外を許可する。

LOWER_PAIR_LOCAL_MATERIALITYはHard Exclusionではない。

## 4. 目的
min Capital subject to Pre-Compression Semantic Coverage = 100%.

R2の固定点数禁止、STOP BUYING、STOP COMPRESSING、Budget非削除原則を全面継承する。
