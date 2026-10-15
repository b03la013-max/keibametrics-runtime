# Weekend official BVI automatic intake

Owner instruction on 2026-10-11 authorizes automatic reflection for the 2026-10-10/11 JRA weekend. The observed Blood-B inventory is 48 races / 659 displayed runners (315 Saturday, 344 Sunday). These inventory counts are collection targets, not official-source acceptance claims.

## Active path

`runtime/pedigree_weekend_intake/20261010-11.json` → 16 bounded three-race windows → existing sequential JRA official collector → original `km-jra-pedigree-verified-backfill.yml` OIDC signer → `_verified_harvest` → unchanged `build_corpus` → unchanged future official feature compiler → unchanged BVI mapping.

The workflow commits only actual public JRA pedigree/history facts and admission receipts. Blood-B ratings, observed result rows, or subscriber HTML are never relabelled as official facts or posted to this repository. Same-day result acquisition is deferred until 19:00 JST; discovery still must succeed against JRA. One matrix job runs at a time, with a 1.3-second request delay. Existing immutable corpus artifacts are verified, never overwritten. Failed windows remain pending for the existing scheduled runs. Admission receipt presence is the restart cursor; no receipt is written before real OIDC and reader-consumption verification.

## Completion meaning

`OFFICIAL_BVI_CORPUS_ADMITTED` proves the official corpus reader consumes that verified window at a postcapture cutoff. It does not establish all 659 identities collected, complete national population coverage, calibrated bloodline effects, Full20 closure, or the numeric values of an unknown future race. Check the live run and all 16 files under `runtime/pedigree_intake_receipts/` for actual completion. Formula, weights, minimum coverage, source trust requirements and historical predictions remain unchanged. Past results are eligible only for later race dates and after their witnessed acquisition time.

## Validation

35 local tests passed: 7 weekend intake, 15 official BVI corpus, 6 historical harvest, 7 browser bridge. Workflow YAML parses. Actual GitHub orchestration initially skipped downstream jobs because a legacy ancestor was intentionally skipped; `always()` with explicit successful plan/pending gates corrects that. Active rerun: https://github.com/b03la013-max/keibametrics-runtime/actions/runs/38139650789
