"""Run the research-only continuous audit from existing scheduled workflows."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
from jra_bvi_research_cycle import main

if __name__ == "__main__":
    raise SystemExit(main())
