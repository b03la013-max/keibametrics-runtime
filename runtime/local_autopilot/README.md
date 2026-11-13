# LOCAL race-day autopilot (PAPER)

- Workflow: `.github/workflows/km-local-race-day-autopilot.yml` (07:07 JST start, worker until done / 23:30)
- **Output since 2026-11-13 19:30 JST: branch `local-autopilot-data`, `output/<date>/README.md`.**
  `runtime/local_autopilot/output/` on main is the frozen first-day copy, kept for history.
- `rakuten.py` source (robots RFC 9309, >=61 s spacing, 403/429 hold) · `engine.py` v4.3 PAPER ·
  `shadow29.py` formal 29-index arithmetic (shadow, no consumption) · `settle.py` result + PAPER settlement ·
  `run.py` queue / states / completion gate · `DIFFERENCES.md` PAPER vs formal mapping.
