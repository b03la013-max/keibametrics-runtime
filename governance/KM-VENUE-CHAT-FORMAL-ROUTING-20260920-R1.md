# KeibaMetrics Venue Chat Formal Routing R1

Effective: 2026-09-20
Profile: KM-VENUE-CHAT-FORMAL-ROUTING-20260920-R1
Parent: KM-FAMILY-EXECUTION-ARCHITECTURE-20260920-R2
Status: ACTIVE / FAMILY-WIDE / NON-NUMERICAL / FAIL-CLOSED

## 1. Purpose
Every venue-specialized ChatGPT conversation becomes the operational entry point for that venue. Venue chats retain venue-specific prediction knowledge, but they do not own formal execution, KRS, ticket-construction authority, receipt authority, or post-hoc override authority.

## 2. Trigger
When the user requests a race prediction in a venue chat using wording such as:
- ケイバメトリクス調査願います
- ケイバメトリクスで予想
- 正式予測
- 完全フル規格
the venue chat must enter FORMAL-PRE-RACE mode unless the user explicitly asks for analysis-only or post-race review.

## 3. Mandatory route
VENUE_CHAT
-> VENUE_PROFILE_RESOLVE
-> SOURCE_SNAPSHOT
-> FULL_RUNNER_UNIVERSE
-> FAMILY_REQUIRED_INDEX_MANIFEST
-> BASE_INDEX_TERMINALIZATION
-> PRE_KRS
-> PRE_KRS_VERIFY
-> KRS
-> KRS_VERIFY
-> W/P2/P3
-> TICKET_CONSTRUCTION
-> CAPITAL
-> FINAL
-> FINAL_VERIFY
-> USER_VISIBLE_FORMAL_OUTPUT

No silent bypass.

## 4. Venue authority
Venue chat owns:
- venue-specific course interpretation
- distance/track/going interpretation
- evidence translation
- static semantic roles
- alternative winner / tail preservation
- venue-specific exclusion and caution rules

Venue chat does NOT own:
- substituting missing base-index formulas
- inventing numeric indices
- bypassing PRE_KRS
- claiming KRS executed without receipt
- constructing post-hoc FINAL after post time
- overriding shared Ticket/Capital/Receipt rules

## 5. Family routing
JRA venues -> JRA family route.
NAR/local venues -> LOCAL family route.
Banei Obihiro -> BAN family route.

Each family route must use its own canonical index manifest and parameter map. JRA/LOCAL/BAN formulas must never be cross-used.

## 6. Temporal rule
Pre-race formal output requires source freeze and FINAL freeze before scheduled post time.
If execution finishes after post time:
- preserve the frozen input if it existed pre-race,
- allow POST-START-REPLAY only,
- do not call it FORMAL-PRE-RACE,
- do not backfill tickets as if they were available before post.

## 7. Readiness
A route can be ACTIVE at the governance level while its family runtime is not fully deployed.
If a family-specific calculator/adapter/receipt path is unavailable, venue chats must return FINAL-BLOCKED / EXECUTION-NOT-PROVEN rather than fall back to hand scoring.

## 8. Ticket coverage
All offered bet types must be evaluated. Each is classified as PURCHASED, BUDGET-NONSELECTED, STRUCTURAL-INELIGIBLE, EVIDENCE-RANKED-LOWER, NOT-APPLICABLE, or NO-BET. "All bet types evaluated" does not mean all bet types purchased.

## 9. Venue inheritance
Venue-specific chats automatically inherit this policy. They should not duplicate the full execution constitution; they reference this routing profile and retain only venue-specific prediction rules.

## 10. Current venue registry
JRA:
Nakayama, Hanshin, Tokyo, Kyoto, Chukyo, Niigata, Fukushima, Kokura, Sapporo, Hakodate.

LOCAL:
Ohi, Kawasaki, Funabashi, Urawa, Sonoda, Himeji, Nagoya, Kasamatsu, Kanazawa, Kochi, Saga, Morioka, Mizusawa, Mombetsu.

BAN:
Obihiro.

Unknown/new venue IDs fall back to FAMILY-ROUTE-UNRESOLVED and must fail closed until explicitly registered.

## 11. Current readiness
JRA: FORMAL ROUTE ACTIVE. JRA Base Index Mapping Registry v0.1 + Railway base-index calculator + PRE_KRS compatibility + quorumprobe KRS/FINAL path verified in Hanshin R05 pre-race execution.
LOCAL: ROUTING POLICY ACTIVE; family-specific formal runtime readiness must be verified per current LOCAL production stack before FORMAL-FULL.
BAN: ROUTING POLICY ACTIVE; family-specific formal runtime readiness must be verified per current BAN production stack before FORMAL-FULL.

## 12. Invariant
A venue chat may analyze without the runtime, but it may not present that analysis as FORMAL-FULL, KRS-EXECUTED, FINAL-PASS, or official KeibaMetrics tickets unless the shared execution path proves those states.
