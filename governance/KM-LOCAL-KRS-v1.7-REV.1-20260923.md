# LOCAL KRS v1.7-KRS Rev.1
Profile: `KM-LOCAL-KRS-v1.7-REV.1-20260923`
Status: ACTIVE / PRODUCTION KRS SPEC / NON-NUMERICAL / FULL-LIFECYCLE-CONNECTED
Predecessor: v1.6-KRS Rev.3
Compiled artifact SHA256: `3be5824dac713566f80436af27ae641f34e15bd9338247031206d3578990e6e6`

## Authority
- Common Canon: ケイバメトリクス地方版 v4.13 Rev.1
- Ops: v1.7 Rev.1
- Reflection: v1.4 Rev.1
- KMS: v1.4-KMS Rev.1
- CSL: v1.1-CSL Rev.1
- Engine: KRS-Engine v1.1.0 unchanged
- parameter_map: v0.1-provisional / PROVISIONAL_UNCALIBRATED unchanged
- Maximum authority: DIAGNOSTIC / SHADOW UTILITY / HANDOFF. No purchase or capital authority.

## Normative changes
1. KRS input must reference an immutable pre-result Static Freeze and identical race/revision identity.
2. PRE_KRS verifies runner universe, required-index state, actual numerical coverage, static freeze, input hash and revision.
3. Required runs use external runtime when executable and before deadline. SIM-STD >=5000; SIM-HIGH >=20000 when current authority requires it.
4. Attempt, completion, output capture, signed receipt issue and receipt verification are distinct states.
5. Every run stores race/prediction/revision IDs, Engine version/SHA, parameter_map version/SHA, mode, seed, requested/actual run count, input/output SHA and timestamp.
6. SSR/LSR/Z4R and occurrence support remain uncalibrated; they are not win/place probability, EV or Kelly inputs.
7. KRS Utility may produce confirmations/rescue proposals only as SHADOW/AUDIT. Production effect is NONE unless separately promoted by frozen OOS evidence.
8. KRS does not decide PURCHASED, NO-BET, stake, MEC width or capital.
9. Pre-compression Semantic Universe remains owned by Venue/Common prediction semantics before MEC.
10. LOW-DISCRIMINATION and NO-MATERIAL-KRS-UPDATE are valid outcomes.
11. Result-time calibration records Rank Gain, Unique Rescue/Harm and KRS support without rewriting Race_n.
12. Family isolation is mandatory: LOCAL must not silently reuse JRA/BAN numerical adapters or parameter maps.
13. Post-start execution is POST-START-REPLAY, never FORMAL-PRE-RACE.
14. RESULT calibration must reference the same Frozen FINAL lineage.
15. No numerical, Engine, parameter-map or probability change is introduced by this revision.
