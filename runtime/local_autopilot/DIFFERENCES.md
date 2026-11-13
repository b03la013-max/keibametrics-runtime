# LOCAL autopilot: PAPER engine vs formal LOCAL numerical mapping (P1-3)

The autopilot runs two separate calculations on the same Rakuten card snapshot.
They are **not the same model** and must not be treated as one.

| | Claude v4.3 PAPER engine (`engine.py`) | Formal 29-index arithmetic, shadow (`shadow29.py`) |
|---|---|---|
| Code | new, this directory | existing `local_nar_evidence_candidate.compile_parsed_candidate_evidence` → `local_fullnumerical_candidate.materialize_candidate`, unchanged |
| Rule ids | none (inline formulas) | `LOCAL-EVIDENCE-FEATURE-RULE-REGISTRY-v1.1-PRODUCTION-NUMERICAL-20261008` / `LOCAL-FULL-NUMERICAL-MAPPING-v1.0-PRODUCTION-20261008` |
| Indices | 13 (HPI, CFI, RFI, EVI, NCI, JTI, CSI, BVI, BWI, CCI, TPI-L, SRI-L, T3I/F3S/OPI) + WCI, AKI | all 29 with CALCULATED / RULED-NEUTRAL terminal status and provenance |
| TPI-L / SRI-L / F3S-L weights | same canon weights as the mapping | canon weights |
| Base indices | simple aggregates of 5 past starts (see v4.4 §35.4) | 63 evidence components (rule registry) |
| **Fixed tables** | jockey scores (`JOCKEYS`), trainer scores (`TRAINERS`), sire sets (`SIRES`), venue front-bias (`FRONT_WEIGHT`), frame bonuses — **hand-set PAPER heuristics, not Production policy; must not be copied into the formal mapping** | none; jockey/trainer from observed rides; BVIg-L RULED-NEUTRAL without official population statistics |
| Body weight | 連対時馬体重レンジ (card) vs current | formal BWI-L components |
| Market | p_win = 50:50 softmax(F3S) / market; OPI from market vs model rank | PRI / OPI-V market-diagnostic only (mapping `market_separation`) |
| CCI / TRI | neutral 52 (no comment / training source) | RULED-NEUTRAL (same reason) |
| AKI | W/P/ASI/RSI simplified (§19) | W-AKI / P2-AKI / P3-AKI / ASI / RSI per mapping |
| Tickets | formation + two-axis quadrant (§12, §20) | none (ticket/capital consumption false) |
| Consumption authority | PAPER output only | `prediction/krs/ticket/capital_consumption_authorized = false` |
| KRS | not used | KRS input (5,000 runs, seed 1) built; **0 trials** — external Engine v1.1.0 sits behind the signed formal gateway and is not called |
| Source status | Rakuten public card, robots-checked | same; **formal SOURCE not established** |

Promotion of either path into Production requires, per the mapping's own
`promotion.required`: deterministic regression, walk-forward OOS,
venue/profile calibration and human (Owner) review. Nothing here flips a
consumer flag.
