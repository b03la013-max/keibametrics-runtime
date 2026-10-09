# LOCAL Formal Execution — practical recovery runbook

This is an operator guide, not a new Production Authority, prediction model, KRS policy, MEC or Capital policy.

## Verified blockers (2026-10-09)

- Current LOCAL authority: KM-FAMILY-CURRENT-AUTHORITY-20261008-R44.
- ChatGPT-to-GitHub Formal Intent content submission was blocked before reaching GitHub; never evade that tool safety decision.
- GitHub's existing Single Entry runs when an independently authorized owner commits a valid, result-blind Intent before the cutoff.
- C2 PR #124 is SHADOW and NOT Production. GitHub run 37895628668 returned OPENAI_API_429_CREDIT_BALANCE_EXHAUSTED_HOLD.

## 1. OpenAI API billing (authorized billing owner only)

Open https://platform.openai.com/settings/organization/billing/overview for the organization owning the already-configured C2 Project/Service Account. Restore prepaid credits through the Platform UI. Do not put payment details or API keys in chat or repository. Do not swap in a different unapproved key. Billing actions are performed only by the authorized owner.

## 2. Verify C2 Shadow with one manual staging run

After credits become usable, open:
https://github.com/b03la013-max/keibametrics-runtime/actions/workflows/km-local-c2-staging-real-api-manual.yml

Run workflow on main. The workflow checks out the fixed C2 Candidate commit 1033c818bf2451ccb9496ae017c7aea0c35ad13e and uses the existing keibametrics-staging secret only inside the run. Inspect the sanitized PASS/HOLD artifact. This historical R07/R08/R12 comparison is NOT forward OOS. API authentication and model output must be established by receipts; a workflow run does not itself prove success. Do not repeatedly retry billing holds.

## 3. Restart authorized production execution for a future race

Prepare a full 29-index LOCAL result-blind Formal Intent, verified official active Runner Universe, Venue Canon, Static ranking/roles, Pair/Third and a cutoff in the future. The submitter does not invent or backdate a Prediction.

Use a locally authenticated GitHub CLI session on a trusted operator workstation:

~~~bash
gh auth login
gh auth status
git clone https://github.com/b03la013-max/keibametrics-runtime.git
cd keibametrics-runtime
python tools/submit_local_formal_intent.py --intent /path/to/future-race.json --dry-run
python tools/submit_local_formal_intent.py --intent /path/to/future-race.json
~~~

If the repo was cloned already, use git pull --ff-only rather than clone.

After SUBMITTED_PUSH_TRIGGER_PENDING, verify actual execution from:
https://github.com/b03la013-max/keibametrics-runtime/actions/workflows/km-formal-single-entry.yml

Official SOURCE / FORMAL Signed FINAL / RESULT receipts in runtime/executions/<execution_id> must each be checked. Submission or CI PASS is not FINAL-PASS. Distinguish Frozen Recommendation PFS from Actual Purchase PFS and do not reclassify historical or post-start races as forward OOS.

## Operational maturity boundary

The owner-operated transport restores a legitimate primary entry independent of ChatGPT's file-write capability. It is not a workaround for a refused ChatGPT tool action. C2 remains Shadow until genuine forward validation and explicit approval. Autonomous one-trigger end-to-end is still NO; do not claim completion from a green CI or a historical run.

Keep all GitHub and OpenAI API secrets out of Intent, commits and chat.
