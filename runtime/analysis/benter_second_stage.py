"""Phase 0 CLI; opt-in closing series reads stored evidence and never fetches."""
from __future__ import annotations
import argparse
import sys
from datetime import date
from pathlib import Path
try:
    from . import _benter_second_stage_legacy as _legacy
except ImportError:
    import _benter_second_stage_legacy as _legacy
# Re-export #362's API; its calculator bytes, hashes and default run are intact.
globals().update({n: getattr(_legacy, n) for n in dir(_legacy) if not n.startswith("_")})
CALCULATOR_SOURCE = Path(_legacy.__file__)

def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    probe = argparse.ArgumentParser(add_help=False)
    probe.add_argument("--series", choices=["pre_signature", "closing"], default="pre_signature")
    selection, remaining = probe.parse_known_args(argv)
    if selection.series == "pre_signature" and not any(x in argv for x in ("-h", "--help")):
        return _legacy.main(remaining)
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--series", choices=["pre_signature", "closing"], default="pre_signature")
    p.add_argument("--from", dest="start", type=date.fromisoformat, required=True)
    p.add_argument("--to", dest="end", type=date.fromisoformat, required=True)
    p.add_argument("--asof", type=date.fromisoformat, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    p.add_argument("--bootstrap-reps", type=int, default=1000)
    p.add_argument("--shuffle-reps", type=int, default=200)
    p.add_argument("--seed", type=int, default=SEED)
    a = p.parse_args(argv)
    if a.series == "pre_signature":
        return _legacy.main(remaining)
    try:
        from . import closing_odds_analysis as closing
    except ImportError:
        import closing_odds_analysis as closing
    result = closing.run(a.root, a.start, a.end, a.asof, a.out,
                         bootstrap_reps=a.bootstrap_reps, shuffle_reps=a.shuffle_reps, seed=a.seed)
    print(canonical({"n_closing_races": result["n_closing_races"], "output": str(a.out)}))

if __name__ == "__main__":
    main()
