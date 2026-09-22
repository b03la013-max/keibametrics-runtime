# LOCAL Input / Source Operations v1.5

Profile: `KM-LOCAL-INPUT-SOURCE-OPS-v1.5-20260923`  
Predecessor: `KM-LOCAL-INPUT-SOURCE-OPS-v1.4-20260923`  
Status: ACTIVE / LOCAL-WIDE / NON-NUMERICAL / AUTOMATIC-NAR-MANIFEST / OFFICIAL-RUNNER-UNIVERSE-HARD-GATE / FAIL-CLOSED

## Formal Source-to-Universe Route

```text
Race Metadata
→ NAR Official Source Manifest
→ NAR DebaTable Raw Snapshot
→ Structured race_card_tables
→ Official Runner Universe
→ Runner Universe SHA256
→ SOURCE Freeze / Signed SOURCE Receipt
→ Request Runner Universe Match
→ Numerical Materialization
→ KRS Input
→ External PRE_KRS Official Universe Match
→ KRS
```

## Official Runner Universe

Profile: `KM-LOCAL-NAR-RUNNER-UNIVERSE-v1.0-20260923`

DebaTableから最低限以下を正規化する。

- runner_id / horse_no
- horse name
- canonical horse name (NFKC / whitespace normalized)
- frame number when explicitly represented
- body weight when published
- body weight change when published
- source snapshot lineage

Official Universeはhash化しSOURCE artifactへ含める。

## Hard Gates

NAR automatic source routeでは以下をFail-Closedする。

- OFFICIAL_RUNNER_UNIVERSE_MISSING
- REQUEST_RUNNERS_MISSING_OFFICIAL
- REQUEST_RUNNERS_NOT_OFFICIAL
- REQUEST_RUNNER_NAME_MISMATCH
- SOURCE_RUNNER_UNIVERSE_MISMATCH

Formal RunnerでSource artifactとrequest runnersを照合し、さらに外部署名RuntimeのPRE_KRSでKRS horsesと同じOfficial Universeを独立照合する。

## Live Acceptance

Runner Universe direct live run: `35769508360` SUCCESS

- official runner count: 12
- official universe SHA256: `6919b4bd5e5cb54c85adafba755c92be0556e7984a67604ecca697ede21ea09a`
- 3-runner incomplete KRS input: rejected as expected
- 12-runner complete KRS input: PRE_KRS PASS
- KRS actual_run_count: 5,000

Formal Runner full-universe run: `35769640173` SUCCESS

- automatic NAR source manifest: YES
- official request runner universe: 12/12
- required numerical cells: 348
- calculated: 348
- unresolved: 0
- SOURCE receipt: `a6137791ec1d50235535c3de5c603412e08c408a52a6bc2ba5939de83681cadd`
- PRE_KRS receipt: `3ce7d59d8e53443beb9930a4db94851695fc5f50099d378e401fbdf2fe6873d0`
- KRS receipt: `e1155307ceaa5bead395122c33d0c05af67b88e4657e4325c150ed1127208b08`
- FINAL receipt: `4a878e98bea2549ce519927c5a1f623ac0cf01b817de1dd66c3d973b337f91d4`
- KRS actual_run_count: 5,000
- MEC material coverage: 1.0

## Boundary

これはSource/Runner Universe/Executionの機械的Acceptanceである。
Archived NAR source fixture + synthetic numerical evidenceを使用しているため、未知未来Prediction Accuracyの実証ではない。
Production numerical formula、KRS Engine、parameter_map、MEC/Capital Authorityは変更しない。
