# JRA cancelled runner, Kyoto 2026-10-25 R03

Historical offline regression only; no Forward/OOS or live acceptance credit.

Original SOURCE run: https://github.com/b03la013-max/keibametrics-runtime/actions/runs/40149439237

- Run code SHA: `5d43535f22151ed9c5dad76da90ca74855ee998a`
- Artifact ID: `12581592816`
- Parent-verified original ZIP SHA256: `f77dd21d83c9e6b98eaea6bb1d274018d53e08517abfa0bff8d38bffb80b357c`
- Original detail fetched at `2026-10-25T01:10:10.651485+00:00`, PRE_CUTOFF.
- Original complete CP932 HTML: 136226 bytes; SHA256 `c896c6468a98a490307755982f29bb0c04e41f34dc3edfd222df40823fa71a1e` (provenance only; not the excerpt hash).
- Original detail snapshot SHA256: `0e00782e05c3f722cdb56ff35432f424b23c15776e29d3de351a528f60b6e352`.

`current_rows.html` is a parent-supplied real extracted fixture: 12499 UTF-8 bytes,
SHA256 `177cf1380ffdac6a0bbb2ece9062acd4950bc59d5e830a473e59654cb958d278`.
The regression checks this exact length/hash. Extraction decoded the original
CP932 bytes and normalized newlines via Python read_text, retained the original
thead and first four current cells of all nine rows, removed only the jockey
cloth-image paragraph, replaced four historical cells with empty td, and wrapped
table/tbody. The original race header is absent. Context-binding unit tests add
an explicitly synthetic race-header harness and generate a derived snapshot/hash;
they never label the excerpt as the original complete SOURCE bytes.

The executor's original artifact downloads returned HTTP403. Full-payload text
transfer was incomplete and was not used. The parent then explicitly authorized
this extracted fixture. This executor did not independently download or verify
the ZIP or full original HTML. Independent full-original validation remains a
separate parent-side check.

`evidence.json` retains parent-supplied original source metadata and parsed PDF
universe. Its original universe digest is checked in the regression. PDF bytes
are not included: this tests detail parsing and reconciliation with preserved
parsed PDF evidence, not a fresh independent PDF extraction.

The current number cell is `取消`; name シュプレヒコール and profile
`pw01dud002024105437/B2` remain present. Frame 5 and row order are never number
evidence. Before the source patch, the real-excerpt regression failed `8 != 9`:
only numbers 1,2,3,4,6,7,8,9 survived. The PDF declares all nine with this horse at
number 5. The candidate preserves unresolved identity then requires complete,
unique same-race official identity binding before applying existing status logic.
Unresolved/ambiguous evidence stays fail-closed; original historical evidence is
unchanged.

Reproduce locally using stdlib unittest (no dependency installation):

    PYTHONDONTWRITEBYTECODE=1 python tests/test_jra_source_observed_fact_retention.py -v

The existing JRA Single Entry Repair Regression workflow already runs this module.
