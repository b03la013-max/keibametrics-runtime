# JRA C4 Shadow Requests

This directory is **NON-PRODUCTION**.

Each request must be frozen before the race result and contain:
- race_id
- runners[]
- runner_id / name / newcomer
- evidence_features{}

Each evidence feature must contain:
- category from the candidate finite scale
- evidence_refs[]
- source_fact

Do not enter freehand 0-100 base-index values.

The workflow materializes:
Evidence -> 13 base indices -> existing JRA v1.0 derived formulas -> 20 canonical components.

A successful SHADOW artifact is not Production authority and must not be used to retroactively change any race's Formal Grade.
