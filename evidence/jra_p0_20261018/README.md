# 2026-10-18 JRA 36R — measured review and unmerged repairs

Production remains R51, resolved from main d1b711d63c50d7f14e2d2ab2a96f2b3ec7e72b8f. 34 signed FINAL/RESULT pairs; 2 AKI_NO_BET without Production FINAL. All 36 registrations are represented. The 2 NO_BET official observations are reused from the existing separate Candidate official acquisition; they are not Candidate Prediction results relabelled as Production. Their canonical Production zero-bet Learning is missing.

## Concrete outcomes

- KRS diagnostic repair: capture actual request Roles in summary, compare P3 using the same SSR-T3 criterion as the proposal producer, and bind historical evaluation to frozen Production Roles/ranking. No Engine, threshold, Role selection or ticket-policy change.
- Learning producer: new states can carry actual UTC observation time and explicit FAMILY-CANDIDATE scope. Existing states and reviews are immutable; corrected official results require a new review revision, not silent rewriting.
- Research sidecar: Winner re-audit, Head-local P2, Pair-third, existing actionable KRS, learning-on/off and CORE/PROTECTION comparisons. Same positive-feature logic applies to all qualifying runners. Nonblocking calls in existing Formal and RESULT workflows freeze/persist/settle sidecars and maintain a distinct-race tracker.
- Existing formal paths continue unchanged if a Shadow fails; failure reasons are retained in summaries. No new workflow dispatcher, paid API, external notifier or automatic promotion.

## Artifacts (combined to avoid duplicate reports)

| Requested outcome | Existing placement / field |
|---|---|
| JRA_20261018_36R_FORMAL_REVIEW | JRA_20261018_36R_FORMAL_REVIEW.json.gz |
| PREDICTION_FAILURE_MATRIX | PREDICTION_FAILURE_MATRIX.csv + JSON races |
| STATIC_AKI_EVIDENCE_AUDIT | JSON races[].runner_audit / aki / model_market_disagreement |
| KRS_INCREMENTAL_UTILITY | JSON krs_role_comparison_totals / races[].krs_recomputed / shadow_comparison |
| VENUE_DAILY_REVIEW | JSON venues / venue_canon |
| CAPITAL_ROBUST_PFS | JSON summary / bet_type_pfs / tier_pfs / shadow_comparison |
| LEARNING_CONSUMPTION_PROOF | JSON learning + temporal regression tests; actual consumption remains zero verified |
| CORRECTNESS_REPAIR | runtime/jra_krs_measurement.py, runtime/post_result_learning.py, both existing workflows, tests/test_jra_role_learning_repair.py |
| FORWARD_OOS_SHADOW | runtime/jra_role_learning_shadow.py; proposed existing workflow connections |
| NEXT_RACE_READINESS | EXECUTION_CONTEXT.json, RUNTIME_READINESS.json, limitations below |

SIGNED_RESULT_VERIFICATION.json preserves the unchanged envelopes downloaded from 34 canonical Actions checkpoints and binds each to the canonical request hash. Signatures were checked locally using the live Runtime Ed25519 public key. All 34 frozen FINAL signatures and signed ticket payloads were independently verified with jra_delivery.verify_signed_final. No historical FINAL/RESULT/learning file was modified.

## Measured results

Frozen recommendation only: Tokyo 17,500/19,670 yen (112.40%); Kyoto 14,400/10,830 (75.2083%); Niigata 25,000/0 (0%). Total 56,900/30,500, PFS 53.6028%, loss 26,400. 31 positive-investment races, 3 zero-stake FINALs, 2 non-FINAL AKI_NO_BET. Actual purchases unknown.

Role denominators are 34 FINALs: W17, P2=13, P3=19, semantic ordered pair6, semantic exact3. A role capture is not necessarily a purchased correct ticket. Missing W is split into 8 role-migration and 9 discovery-or-role cases; the latter are not fully causally separated. Canon revision=NO at this stage, Promotion=HOLD for TKY/KYO/NGT. Venue mechanism measurements remain incomplete; course geometry grouping is not full canon implementation.

Largest return Tokyo11 accounts for 62.2951% of all returns. Removing it and its stake gives PFS21.2569%; top2 removed11.7202%, top3 removed6.5619%. Median race PFS0, maximum chronological drawdown35,300 yen, longest zero-return streak12. Ordering is official post then race ID, not verified actual purchase cash flow.

21 correct-outcome role-zone rescues and 2 potential nonconfirmations are diagnostic counts, not 21 winning tickets or 2 actual harms. 10 races have an actionable post-result UNIQUE-RESCUE label. Full proposal width611 includes false pair194 and false exact322. Research cost is explicitly included: actionable KRS arm requires120,700 yen vs baseline56,900. It is not automatically purchasable or proven superior. Every new arm was designed after this day; all 2026-10-18 comparisons are exploration/regression and earn zero forward OOS credit.

## Verification and independent review

Combined targeted regression: 62 tests + 9 subtests PASS, then added backdated-commit negative regression: role/learning suite9 tests +4 subtests PASS. Both workflow inline Python and YAML PASS, git diff --check PASS. Actual Tokyo11 and Kyoto2/4/10 positive controls preserve frozen baseline payout; Tokyo8 remains a negative control. Existing immutable signed tickets were not changed.

A separate review agent independently reproduced KRS false-rescue counts, Source/digest and proposal omissions, leakage cases, costs, and a backdated Git timestamp vulnerability. All blocking code findings were addressed. Independent review final code verdict PASS; external human review is not claimed. Reviewer ran22 tests+4 subtests and workflow syntax checks independently. Future measurement remains pending.

## First blockers / next allowed actions

1. Existing PR306 is extended; its new HEAD needs Owner approval before Merge. PR305 approved HEAD is untouched and remains subject to its existing real Railway isolated deploy/rollback condition. No provider-deploy retry or bypass was attempted. PR307 remains separate.
2. Git committer dates are mutable and cannot independently prove pre-result persistence. Sidecars can freeze/settle, but OOS eligibility stays false until server-side receipt time plus matching frozen artifact bytes are verified. The tracker does not auto-promote at60 races/3days/2venues.
3. Today34 Learning states have no effective_time; verified actual next-input consumption=0. New producer plus mechanical binding test is not historical live consumption proof. SAME-DAY and meeting-specific numerical adaptation are not activated.
4. The2 NO_BET outcomes lack canonical Production zero-bet Learning; no signed RESULT was fabricated for them. Static-only pre-KRS ticket counterfactual is not identifiable from an independent frozen ticket set and remains UNKNOWN.
5. No notification/recipient ACK records were found. Canonical publication/readback is separate from user receipt. No external send was made.

Production Merge HOLD; Shadow forward OOS BLOCKED pending Merge and independent server witness; model quality/Robust PFS improvement FORWARD OOS PENDING. Revert this PR's code/workflow additions to roll back; do not rewrite signed artifacts. Production Railway deployment remains7c7eeb5e-3b5b-496a-b66f-82bd71897d53; Runtime READY; deployed Git SHA unknown. No deploy/restart/stop was done.

CI caught LOCAL preregistration coupling to the shared KRS file. Its exact main bytes were restored. The JRA-only adapter contains the measurement repair; LOCAL code, metrics and frozen definition hashes are unchanged.


## PR306 merge and next-race continuation — 2026-10-18

Owner approved exact HEAD `5f9165b81cc7a1ddb341af7c44f219a63a6523e0`.
Merged as `408def14c7e32515ccefbad8af6ae39f41b70f26`; approved and merged trees are identical. PR CI 9/9 and merge/main CI 19/19 succeeded. Main subsequently observed at `b6ca787d10b1984f303aabaa73965c9046bdb4cd`. No signed historical artifact, Production coefficient, Engine, parameter map, Signer, AKI, MEC or Capital policy changed. Production Deployment `7c7eeb5e-3b5b-496a-b66f-82bd71897d53` remains SUCCESS/READY; deployed Git SHA remains UNVERIFIED. No Deployment/Restart/stop was performed. Rollback for merged code: revert PR306 code/workflow changes while preserving immutable artifacts. PR305 provider isolation gate remains unresolved and was not bypassed.

Unmerged continuation is consolidated into existing PR307. The existing Actions upload now contains the exact Shadow sidecar. RESULT checks fixed repository/main workflow/run attempt/head/code bytes, immutable archive digest and exact content, with server creation and update times no later than Cutoff. Git dates alone never confer OOS eligibility. New fields separately record losing added-ticket stake (False-positive Cost), added winning stake and return. These changes do not generate purchase instructions or promote a Candidate.

The existing zero-bet Workflow had five valid pending decisions but selected the oldest four; Kyoto R05 fell outside that batch. Selection now prioritizes the current meeting, and individual OIDC/decision-validation failures cannot block valid siblings. Regression executes the actual Workflow Python with official-network and attestation boundaries mocked, including the actual five pending terminal records. This is not proof of official capture: both Oct18 zero-bet canonical Learning records still await the existing OIDC Workflow's real execution. No unsigned observation was relabelled verified.

Focused regression: 53 tests + 32 subtests PASS. YAML and embedded Python compile, whitespace checks PASS. Separate technical reviewer independently passed 26 tests + 13 subtests, server-witness/NO-BET adversarial probes, and the combined Delivery wiring review; this is distinct from Owner authorization and from actual provider acceptance.

The 34 FINAL publication/readback records were audited; all 34 notification and recipient ACK states remain UNVERIFIED. No external message was sent. Actual next-race Learning consumption remains 0 verified; original 34 states are not backdated. New timestamped states can be bound only when actually available before the next Source freeze. True Forward OOS remains PENDING, not ACTIVE, until the unmerged code is approved and a future pre-cutoff artifact is independently verified. Prediction improvement is unproven.

Retrospective cost measurement, same 31 invested formal races (all arms designed after results; exploration only; not OOS or actual purchase):

| Arm | Added capital (yen) | Losing added-ticket stake (yen) | Added-ticket return (yen) |
|---|---:|---:|---:|
| Winner Re-Audit | 45,900 | 45,100 | 62,670 |
| Head-local P2 | 42,600 | 41,200 | 39,180 |
| Pair-conditioned Third | 11,500 | 11,100 | 3,190 |
| KRS Actionable | 60,700 | 59,400 | 94,700 |

Baseline is 56,900 yen / 30,500 yen return. Unequal-budget arms do not establish improvement; equal-budget/equal-ticket diagnostics and forward comparison remain separate. Full machine-readable observations are appended to existing EXECUTION_CONTEXT.json.


## Prediction quality continuation — 2026-10-18 (unmerged research)

Latest main base: 6a907d6e (PR306/307 merged, NO-BET Learning2 generated). Current Authority R51 and Production numerical policy remain unchanged. PR305 isolated provider/rollback gate remains independent and unresolved.

Full review: PREDICTION_QUALITY.json.gz; compact metrics: PREDICTION_QUALITY_SUMMARY.json. All36 races /450 runners /9000 index cells included, with actual NO-BET Full20 inputs separated from34 signed FINALs. Per-runner values, midranks, feature contributions and immutable input references are retained. Missing features and DCR-only values are not labelled weak ability.

| Index | Actual W mean rank | Actual P2 mean rank | Actual P3 mean rank |
|---|---:|---:|---:|
| BVI | 5.944 | 7.347 | 5.903 |
| BWI | 5.875 | 6.306 | 6.764 |
| CFI | 5.417 | 5.639 | 5.292 |
| CSI | 4.625 | 6.264 | 5.514 |
| DCR | 5.056 | 6.472 | 5.736 |
| F3S | 4.250 | 5.583 | 5.500 |
| GCI | 5.611 | 6.167 | 5.833 |
| HPI | 4.833 | 5.417 | 5.611 |
| JTI | 4.542 | 4.611 | 5.125 |
| KGI | 5.250 | 5.708 | 4.681 |
| PRI | 4.417 | 6.347 | 6.792 |
| RFI | 5.319 | 7.458 | 5.931 |
| SRI | 3.972 | 5.833 | 5.528 |
| SSI | 4.639 | 5.333 | 5.819 |
| T3I | 4.111 | 5.500 | 5.500 |
| TPI | 4.028 | 5.500 | 5.333 |
| TRI | 5.042 | 5.819 | 5.153 |
| VMI | 3.986 | 5.083 | 4.472 |
| ZAI_PLACE | 4.167 | 5.472 | 5.667 |
| ZAI_WIN | 4.250 | 5.444 | 5.611 |

Ranks use midranks for ties; normalized rank and target pairwise concordance are in JSON. Finish Spearman excludes races lacking full official finish order (NO-BET only has canonical top3 here). Correlation/dependency is association, not proof of an implementation defect or independent causal evidence. ZAI_WIN/ZAI_PLACE mean within-race rank correlation=0.9833. Low AKI<=20 descriptive subset:9/11 invested races excluded the actual Winner from W; this does not calibrate AKI as a probability.

BVI measured414, measured+DCR12, DCR-only24. Existing registered Full20 formula replay is exact for9000 cells (max error0). In-memory BVI scalar=50 sensitivity leaves W/P2 ranks unchanged; actual P3 mean midrank5.500→5.5278. This is not a Corpus/Evidence, AKI/KRS, Ticket or PFS ablation and does not prove the whole pedigree channel useless. Raw offspring-count shrinkage sensitivity is labelled non-Bayesian, research-only; official IDs/independent samples and full hierarchical Bayesian fit remain HOLD. Unaccepted408 runs were not imported; Blood-B was not newly collected.

Candidate JRA-CONDITIONAL-RANK-20261018-R1 uses fixed strong L2 race-balanced pairwise loss, trained on41 completed canonical races fromOct11/12/17. No hyperparameter search onOct18. Mean actual W/P2/P3 midranks: Production indices4.25/5.4722/5.50; learned3.8889/4.9167/4.4167. Paired exploratory confidence intervals and every race are in JSON. Specification was designed after results; this is NOT authentic OOS, and historical RESULT signatures were not independently reverified for this training cohort. Head/Pair conditioning excludes already selected horses; it does not learn head/pair interactions. TKY12 P2 worsens9→12, KYO7 Winner remains6, NGT10 Winner remains12: the core failures are not solved by this fit.

The rank-only Candidate attaches to the existing Shadow sidecar, with independent ID/model/code/source/universe/cutoff binding and provider artifact checks. It creates no tickets and changes no Production Role, Capital, coefficients or KRS Physics. Model creation must precede Source freeze; target overlap or training-result times after model creation reject. Future NO-BET rank freezing is not connected by this successful-FINAL path. Existing R1 frozen arms are preserved. Future race freeze and actual next-race Learning consumption remain PENDING; no past states were backdated.

KRS31-invested-race diagnostic:20 potential Role-zone rescues,1 potential Static-correct Role non-confirmation (not Production deletion),585 Role proposals,185 false Pair and310 false Exact additions. Added Capital60700 yen, losing added-ticket stake59400 yen, added-ticket return94700 yen. These are post-result research conversions, not actual winning purchases.

Integer100-yen same-budget allocation preserves56900-yen total. Baseline and baseline-preserving rescue arms remain PFS53.6028% because retaining all existing100-yen tickets exhausts the budget. Equal-budget Static-top3 BOX224.2004% drops to36.9526% after largest-return race removal; Market-top3 BOX147.9438% drops to67.0425%. Baselines are diagnostics, not proposed Production BOX rules. Largest-return dependence and omitted baseline tickets are recorded; unknown future benefit is unproven.

Correctness changes: bind nested Candidate hashes to provider-verified dependencies; repair stale NO-BET audit missing label; make pending-batch regression independent of already completed live Learning records. Regression47 tests+25 subtests PASS; independent reviewer28 tests+25 subtests PASS and numerical convergence/positive-control checks. No unresolved High finding.

Rollback: revert new rank-only optional attachment, research module/model, audit/test/CI changes; preserve all signed histories and deployed Runtime. No Production deployment or promotion. Merge HOLD pending current HEAD Owner approval and CI. Forward OOS minimum60 distinct races/3 dates/2 venues, no automatic promotion.

Artifacts: model SHA c288ab90c0c855799e8b0ac22ba8fdb0a4392b258d4ce9369247082f26aa8674; full report SHA 2f3c05dba506645d86f949afca391d6af9ef49b37b846780c5d2530a99175cbe; summary SHA 89c628e579bc885c3dacbbd958366c8c72ab2dcc78e67ecc569e2d269069259e.

### PR308 integration and fixed-model conditional comparison (2026-10-18)

Owner-approved PR308 HEAD `a4badf34691e913227c2d330b5ec7252d72752af` merged as `8a3ff81108b23f6b7fa9ce9ad938ad381db094d3`; approved and merged Git trees are identical (`16687c7cc4fb5103966b59fe90360c34a50d61a2`). Main CI: 5/5 successful. No Production deployment or numerical-policy change. Railway deployment remains `7c7eeb5e-3b5b-496a-b66f-82bd71897d53`, live, no staged changes; health READY at `2026-10-18T10:31:39.180481Z`, existing engine/parameter/signer fingerprints unchanged. Deployment Git SHA remains unverified.

`CONDITIONAL_FAILURE_ANALYSIS.json` is reproducible with `python scripts/jra_conditional_failure_audit.py`. It binds its own SHA, audit/runtime code, unchanged model, and per-race request/Source/FINAL/RESULT references. The 2 NO-BET prepared requests do not contain a Signed Source SHA: those fields remain null; their canonical zero-investment Learning hashes are retained. They are excluded from formal-FINAL capture and funded PFS denominators.

The follow-up adds a separate **non-Production** equal-exposure research policy `JRA-RANK-EQUAL-EXPOSURE-20261018-R1`: for every frozen bet type it retains exactly the count and stake multiset, enumerates all distinct orientations, orders by role ordinal sum, and canonicalizes TRIO. No results, payouts or known winning horses enter construction. All-horse P3-to-W/P2 migrations, literal top1 chain, matched-width potential capture and oracle conditional rank are reported separately. R1 still has exclusion-only conditioning, not learned head/pair interactions.

On 31 funded Oct18 races, both portfolios invest 56,900 yen. Production returns 30,500 (53.60%); research returns 53,370 (93.80%). Excluding each portfolio's largest return: 21.26% vs 63.53%. Shadow reassigns 27,200 yen; 26,400 yen of increased allocations lose. Decreased winning allocations remove 670 yen of original returns (Tokyo10), while new allocations there return 1,150; the net gain does not erase the lost baseline ticket. The four designated Positive Controls retain their baseline payouts in this replay. Results are **post-result exploration, never Forward OOS or actual purchases**, and do not authorize promotion. The KRS additive negative control remains 60,700 yen additional capital / 59,400 yen losing added stake, measured separately.

34 formal FINALs: original W/P2/P3 captures 17/13/19; same-width rank diagnostics 18/14/23. Literal Shadow top1 Ordered Pair: 1/34; Exact: 0/34. Candidate width, oracle-conditioned recall, paid ticket capture and actual exact order are not interchangeable. Niigata's mean Winner midrank remains 5.83; Tokyo12 actual P2 falls from index midrank 9 to learned rank 12. Fixed-weight contribution margins identify negative BVI/VMI/JTI contributions for Tokyo12 and low VMI/HPI/RFI/SSI for Niigata10; these are associations, not causal verdicts or grounds to tune coefficients after results.

AKI <=20: 11 funded races, 9 winners outside W. Separation/density/axis support/rank-discordance share Full20 inputs, so agreement cannot certify external coverage. Existing SOURCE conflict is not a model-market conflict. All-horse positive-Evidence groups and market rank gaps are diagnostic only; their independence is not proven. No AKI threshold or candidate admission rule changed.

Forward OOS eligible freezes: **0**. Verified new-Learning next-race consumption: **0**. Existing provider archive-time/content/code/model proof is extended with model Policy SHA and a separately bound portfolio policy. Actual future Source/runner/cutoff and independent pre-cutoff server persistence are still required. Learning remains Shadow-only. The 34 historic Learning records lack verified effective_time and are not backdated; 2 zero-investment NO-BET Learning completions are inherited from PR307. No new activation, notification, deploy, purchase, fee or Production coefficient change is performed.

BVI: measured414 / mixed12 / DCR-only24. Hierarchical Bayes is not implemented: official pedigree IDs, independent sample counts and time-eligible labels must first be verified. Existing partial pooling is a sensitivity check, not a posterior or proof of pedigree utility. Unaccepted408 runs stay excluded.

Rollback for the unmerged follow-up is to leave main at the merged308 tree; after a separately authorized integration, revert its focused commit. Frozen Production artifacts/model are not rewritten. No provider rollback/restart/deploy action is required for these GitHub-run Shadow changes.

Follow-up validation: full affected regression suite **51 tests / 37 subtests PASS**; independent technical agent review **34 tests / 37 subtests PASS**, plus independent recalculation of all34 formal portfolios. The rehashed out-of-universe horse regression now fails closed. No unresolved high findings. This is a separate-agent technical review, not a GitHub human approval. New follow-up Merge remains **HOLD pending exact-HEAD Owner approval**; PR308 approval does not cover new code.

### Pre-race predictive structure audit (2026-10-18; unmerged research)

`PREDICTIVE_STRUCTURE_AUDIT.json` is reproduced by `python scripts/jra_probability_readiness_audit.py`. The research adapter reuses the existing rank fitter and vectors; it does not attach to the formal Request/Result Runner, change the frozen R1 model, or activate a new 72-race arm. The 10/24 and 10/25 plans and original model remain byte-identical. Main base: f64b0fbf6fd6e95a14d3c0b173a8e44c0ccb9e3e.

Training uses19 Oct11/12 races, temperature calibration22 Oct17 races, evaluation34 Oct18 formal FINALs plus2 separately reported NO-BETs. Strict cross-split result/source chronology is checked. The design was made after Oct18 results: this is chronological exploration, NOT genuine Forward OOS. Fixed temperature grid selects W2/P2=1/P3=.5 on calibration only; no test-driven retuning is applied. Against unit temperature on the same19-race refit, formal evaluation Log Loss changes W2.11420→2.24685, P2 2.46737→2.47496, P3 2.31030→2.27033. P3 calibration error and top1 accuracy worsen despite better Log Loss. Probability calibration is UNVALIDATED, not successful. The original41-race frozen model is a separate unchanged candidate.

The joint distribution enumerates all distinct ordered triples and marginalizes unknown heads/pairs. Actual-winner/P2-conditioned diagnostics are explicitly oracle exclusions, not learned head/pair interactions or deployable measured gains. Log Loss, multiclass Brier, fixed-bin top1 ECE, ranks, pair/exact likelihoods and capture are recorded. No KRS SSR is treated as probability. EV/Kelly, automatic promotion and ticket construction are disabled.

Among31 funded races, actual Winner-outside-W is17: Evidence flags TP17/FP14/FN0/TN0 (specificity0); market-disagreement flags TP14/FP4/FN3/TN10; OOD flags TP0/FP0/FN17/TN14 (sensitivity0). The AKI<=20 subset has9 failures among11, but market's apparent perfect separation there is tiny, post-result-designed exploration. None changes AKI thresholds or proves independent Evidence. Train19 has no Niigata; OOD is an unvalidated diagonal feature-envelope diagnostic.

Selection audit finds43 prior planned races without eligible canonical labels across Oct11/12/17. Missing execution, PAPER, NO-BET and funded populations are separated. Horse-name overlap is recorded, but permanent Horse IDs and cross-race independence are UNVERIFIED. Current frozen BVI aggregates overlap and expose normalized-finish summaries, not deduplicated Bernoulli success counts. Hierarchical fitting is blocked pending eligible horse/race/parent IDs, raw labels and condition/sample lineage; no fractional pseudo-successes, LOCAL policy or unaccepted408 runs are used. EV/portfolio optimization is ineligible without calibrated probabilities and verified pre-cutoff market inputs.

Existing Learning intake and provider time/hash binding are reused as inventory evidence. Verified new-Learning next-race consumption remains0. This audit does not equate file reads with numerical prediction impact or retrospective replay with future consumption. Future evaluation requires a separately approved and frozen candidate arm, same Source/universe/cutoff, pre-cutoff independent persistence, immutable model/policy/code SHA and no target/result overlap. New candidate is callable research only; automatic execution and genuine OOS are not active. Existing72-race Production and previously approved Shadow execution are unaffected.

Independent separate-agent technical review PASS:11 tests+22 subtests, joint/marginal and distinct-horse constraints checked on36 real races (maximum normalization error1.11e-16), protected model/plans exact-byte checks, nested artifact/code SHA checks. Off-grid temperatures and malformed/reversed/overlapping manifests now fail closed. No unresolved High finding. This is not a GitHub human approval. CI status belongs to the Draft PR exact HEAD. Merge/Deploy remain HOLD without new exact-HEAD approval. Rollback is removal/revert of this isolated research adapter, its candidate/audit/tests and CI path additions; no Runtime restart or signed artifact rewrite is required.

### PR311 authorized integration and head/P2 recheck (2026-10-18)

Exact Owner-approved HEAD `cf24befbc8ab466e30fcc73e3affa5a95697d8c4` merged as `39a86b7e1fa3bc4874d78619a9194fd4c2cdf7f1`; main CI5/5 PASS. The seven-file research-only scope and prior independent review were retained. No Runtime deployment, Production numerical change or automatic new research arm was included. Railway quorumprobe remains live at deployment7c7eeb5e-3b5b-496a-b66f-82bd71897d53, SUCCESS, no staged changes, no volumes. Its saved start command now invokes uvicorn with hash checks; actual saved-command/process generation binding and Deployment Git SHA remain unverified. PR305 isolated startup/restart/rollback conditions remain unresolved; no rejected operation was retried.

`CONDITIONAL_P2_RECHECK.json` and `scripts/jra_conditional_p2_recheck.py` preserve the311 base candidate and recheck chronological calibration/evaluation, Venue metrics and complete per-race comparisons. Winner temperature2 improves calibration-day NLL2.60696→2.54410 but worsens formal test2.11420→2.24685: day/venue distribution shift and small calibration support are limitations, not proof of causality. It lowers actual Winner probability in25/34 formal tests. P2 temperature remains1: its full marginal NLL deterioration is exactly reproduced by changing W temperature alone (maximum difference0), because uncertain heads are marginalized. P2/P3 temperature selection used actual-head/pair conditional NLL, which is different from marginal evaluation. P3's aggregate NLL improvement hides worse ECE/top1 and Niigata NLL2.54933→2.69381. No new calibration family or test-tuned temperature is introduced. Temperature mapping promotion is rejected; existing uncalibrated rank model remains unchanged.

A separate callable head/P2 residual reuses the fixed19-race base and adds only four strongly regularized interaction coefficients from registered, result-blind position/pace-resilience/closing/course categories. These are Evidence proxies, not raw running-style or simulated-pace observations. Missing/UNKNOWN contributes no interaction and is logged. Model training is bound to the exact prior19-race Source/FINAL/RESULT manifest; no Oct17/18 labels fit it. Inference enumerates every hypothetical head and never accepts actual results. Unit-temperature exclusion is the baseline; P3 context logits stay unchanged. Formal test oracle-head P2 NLL2.33290→2.33015, mean rank4.79412→4.73529, ECE worsens. Full top1 Pair1/34 and Exact1/34 are unchanged. This tiny post-result exploratory difference is not proven improvement, not future OOS and not a ticket/Capital recommendation.

AKI diagnostics remain diagnostic only. Evidence flags all31 funded races, so specificity0 reflects a broad/shared-information design, not a confusion-matrix calculation error. OOD's fixed calibration threshold10.7233 exceeds all test scores0.5985..3.7587; a race-mean envelope is not a Winner-error classifier. No threshold was retuned after results. Market flags TP14/FP4/FN3/TN10 remain exploratory.

BVI structural inventory:65 stored harvest files, all65 content hashes valid,2670 horse observations/2380 pedigree-triple identities,26365 historical run observations.26005 have valid finish/field labels; surrogate grouping yields23668 horse-run groups,2337 duplicate observations and0 label/going conflicts. All2670 horse observations lack explicit permanent horse/sire/damsire IDs; all26365 run observations lack official race IDs.198 lack venue/surface/distance/going. These are stored-file counts, NOT newly verified attested eligible training samples: OIDC attestations were not reverified and surrogate identity is not an official ID. Identity-complete verified hierarchical samples remain0. No fake integer labels, unaccepted408 runs or Production admission. Recovery requires official permanent IDs, deduplicated time-eligible horse×race labels/conditions and attestation verification before cell/offspring counts and a hierarchical fit.

Both planned36-race cohorts and original model remain byte-identical. New head/P2 and probability models are not registered into the72-race cohort. Existing approved arms only; genuine future freezes0 and verified new-Learning next-race consumption0 as of this work. Official numbered cards and fresh Source/universe/cutoff, independent pre-cutoff provider persistence, actual ON/OFF Learning input and output differences, and result-time equal-exposure settlement are still required. Existing schedules are preserved. No retrospective OOS eligibility, notification or actual purchase is claimed.

Follow-up code is separate from merged311 approval; Merge HOLD pending its exact-HEAD Owner approval. Rollback is reverting only the new research adapter/model/audit/test and CI-trigger additions. No signed artifacts, Production policies or day plans are rewritten.

Follow-up validation:69 tests+71 subtests PASS. Separate-agent independent review18 tests+34 subtests PASS and independent real36-race recalculation (joint normalization maximum error2.22e-16); no unresolved High finding. The review reproduced detached Top3 training with unchanged RESULT bytes; repair now checks actual RESULT labels, FINAL selfhash/Race/Source binding, request-runner equality, existing Frozen FINAL compiler attestation and all20 Frozen replay values. Per-training-request SHA/compiler references are recorded. Mutation regressions reject changed Top3, Evidence, Full20, FINAL body, RaceID, model policy/weights/mapping and late freeze. This is technical separate-agent review, not a GitHub human approval. Exact follow-up HEAD CI is reported on its Draft PR.
