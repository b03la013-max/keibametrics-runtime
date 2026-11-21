# KeibaMetrics development-agent coordination

This applies to **LOCAL development edits** only. It does not alter the
Production owner, JRA/BAN isolation, SOURCE permissions, numeric policy,
real purchases, or Merge/Deploy approvals.

**Before every LOCAL code change from any scheduled agent or ad-hoc Work session:**

1. Resolve current `main`, open PRs and their changed paths, and the intended
   workstream (`SOURCE`, `BASE9`, `CONSUMER`, `KRS`, `DELIVERY`, `RESULT`,
   or `COMMON`). Check for semantically overlapping PRs, not only file conflicts.
2. Read `coordination/local_work_claims.json` from the separate
   `coord/local-edit-claims` branch. Use the file's current GitHub **blob SHA
   compare-and-swap** when updating it. Do not write to `main`.
3. Ad-hoc/manual sessions get first priority. They **reserve** the workstream
   and file/directory scope, then **acquire** after any in-progress claim
   releases or expires. They must not forcibly take an in-flight claim.
4. Automatic sessions must acquire a different UUID for their own specific
   scope, and must yield to any overlapping manual reservation before their
   next write. They may continue on a genuinely disjoint workstream.
5. Before **every** GitHub file edit, commit, PR update or write-capable
   test, verify the same UUID is still active and that no priority reservation
   conflicts. Commit to a separate branch, use the newest branch HEAD/file SHA
   as appropriate, and never force-push another agent's work.
6. Release only your own UUID when finished or stopped. Claims expire;
   renew before expiry when needed. On permission, network, CAS or ownership
   uncertainty, do not modify the contested scope. Continue safe read-only or
   disjoint work.

The helper `tools/local_change_claim.py` implements `status`, `reserve`,
`acquire`, `verify`, `renew`, and `release` with the existing GitHub
token. The client itself can be used only where available and authorized;
connected Work sessions may perform the same atomic file updates using
their GitHub connector. No new credentials or paid services are requested.

**Completion evidence:** claim UUID, workstream and paths; branch and before
and after HEAD; actual code diff; real CI; independent delivery/Full29
and consumer results when achieved. Code commits are not a substitute for
prediction, pre-start user Delivery, or PFS.

This is a cooperative development coordination protocol, **not** a GitHub
permission boundary. External writers that ignore the protocol must still
be handled by normal GitHub branch protection, HEAD checks, PR review and
the owner's existing approvals.
