"""Offline opt-in paired comparison; stored captures only, never HTTP."""
from __future__ import annotations
import csv
import hashlib
import json
import os
import shutil
import tempfile
from collections import Counter
from dataclasses import replace
from datetime import datetime, time
from pathlib import Path
import numpy as np
try:
    from . import _benter_second_stage_legacy as b
    from . import closing_odds_reader as reader
except ImportError:
    import _benter_second_stage_legacy as b
    import closing_odds_reader as reader


def compare(root, start, end, asof, *, bootstrap_reps=1000, shuffle_reps=200, seed=b.SEED):
    inputs = b.Inputs(root)
    series, _, _ = inputs.load(start, end, asof)
    paired, closing, ledger, excluded = [], [], [], []
    limit = datetime.combine(asof, time.max, tzinfo=b.JST)
    for race in series["pre_signature"]:
        path = Path(root) / "runtime/closing_odds" / (race.race_id + ".json")
        if not path.exists():
            excluded.append({"race_id": race.race_id, "reason": "CLOSING_NOT_STORED"})
            continue
        try:
            capture = inputs.read(path)
            result = inputs.read(Path(root) / "runtime/results" / (race.race_id + ".json"))["official_result"]
            _, nonstarters, finishes = b.result_outcome(result)
            reader.validate_capture(capture, race_id=race.race_id, expected_active=race.ids, expected_nonstarters=nonstarters)
            observed = reader.timestamp(capture["captured_at"])
            if observed > limit:
                raise ValueError("CLOSING_CAPTURE_AFTER_ASOF")
            if observed < b.timestamp(race.post_at):
                raise ValueError("CLOSING_CAPTURE_BEFORE_POST")
            rows = {r["runner_id"]: r for r in capture["parsed"]["runners"] if r["status"] == "ACTIVE"}
            odds = np.array([rows[i]["win_odds"] for i in race.ids])
            market = (1 / odds) / (1 / odds).sum()
            closing.append(replace(race, m=market))
            paired.append(race)
            for j, horse in enumerate(race.ids):
                ledger.append({"race_id": race.race_id, "post_at": race.post_at, "runner_id": horse,
                               "horse_no": int(horse), "zai_win": float(race.zai[j]), "z": float(race.z[j]),
                               "win_odds": rows[horse]["win_odds"], "m": float(market[j]),
                               "odds_observed_at": observed.isoformat(),
                               "minutes_to_post": (b.timestamp(race.post_at) - observed).total_seconds() / 60,
                               "finish_pos": finishes.get(horse), "winner_weight": float(race.y[j]),
                               "excluded_reason": None, "segment": "JRA", "series": "closing",
                               "source_path": path.relative_to(Path(root)).as_posix(),
                               "time_basis": "RETROSPECTIVE_CAPTURE_NOT_MARKET_CLOSE_TIME"})
        except (KeyError, ValueError, TypeError) as exc:
            excluded.append({"race_id": race.race_id, "reason": str(exc)})
    options = dict(bootstrap_reps=bootstrap_reps, shuffle_reps=shuffle_reps, seed=seed)
    report = {"schema": "BENTER_CLOSING_COMPARISON_V1", "classification": "OFFLINE_UNSIGNED_RESEARCH",
              "period": {"from": start.isoformat(), "to": end.isoformat(), "asof": asof.isoformat()},
              "n_primary_races": len(series["pre_signature"]), "n_closing_races": len(closing),
              "n_runners": sum(len(r.ids) for r in closing), "comparison_population": "SAME_PAIRED_RACES_ONLY",
              "pre_signature_paired": b.analyze(paired, **options), "closing": b.analyze(closing, **options),
              "excluded_races": excluded, "exclusion_counts": dict(sorted(Counter(r["reason"] for r in excluded).items())),
              "input_files_sha256": dict(sorted(inputs.manifest.items())),
              "software": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
                           (Path(__file__), Path(reader.__file__), Path(b.__file__))},
              "notes": ["Only paired races are compared; closing never replaces pre-signature observations.",
                        "Capture time is not the historical market-close time; post time remains the frozen scheduled time.",
                        "FINAL signatures are not cryptographically reverified by this research calculator.",
                        "No closing captures means 0R; the original summary/ledger remain unchanged."]}
    for path, expected in inputs.manifest.items():
        if hashlib.sha256((Path(root) / path).read_bytes()).hexdigest() != expected:
            raise ValueError("INPUT_CHANGED_DURING_ANALYSIS:" + path)
    return report, ledger


def render(report):
    lines = ["# 確定オッズ系列（保存済みデータのみ）", "",
             f"主系列 {report['n_primary_races']}R、確定オッズ {report['n_closing_races']}R。比較は同一Race集合。", "",
             "| 系列 | 後半M ρ² | 後半Δρ² | 95%区間 | シャッフル95%点 |", "|---|---:|---:|---|---:|"]
    for name, key in [("署名前・同一集合", "pre_signature_paired"), ("確定オッズ", "closing")]:
        data = report[key]
        if "evaluation" not in data.get("chronological", {}):
            lines.append(f"| {name} | N/A | N/A | 0R又は評価不足 | N/A |")
            continue
        score = data["chronological"]["evaluation"]
        interval = data["bootstrap"]["conditional_holdout"]["ci95"]
        control = data["shuffle_control"]["chronological_out_of_sample"]["p95"]
        lines.append(f"| {name} | {score['models']['M']['rho2']:.6f} | {score['delta_rho2']:+.6f} | {interval} | {control:.6f} |")
    lines += ["", "取得時刻は過去の市場締切時刻ではありません。人気や払戻から単勝価格を補完しません。",
              "通常のsummary.jsonは変更せず、比較結果を別ファイルへ出力します。", ""]
    return "\n".join(lines)


def run(root, start, end, asof, out, *, bootstrap_reps=1000, shuffle_reps=200, seed=b.SEED):
    root, out = Path(root).resolve(), Path(out).resolve()
    if out.exists():
        raise FileExistsError("OUTPUT_MUST_BE_NEW_DIRECTORY")
    if out.is_relative_to(root) and not out.is_relative_to(root / "runtime/reports/benter_second_stage"):
        raise ValueError("OUTPUT_IN_INPUT_OR_PRODUCTION_TREE_FORBIDDEN")
    if not start <= end <= asof:
        raise ValueError("REQUIRE_FROM_LE_TO_LE_ASOF")
    report, rows = compare(root, start, end, asof, bootstrap_reps=bootstrap_reps, shuffle_reps=shuffle_reps, seed=seed)
    out.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=".closing-analysis-", dir=out.parent))
    try:
        staging = temporary / "result"
        primary = b.run(root, start, end, asof, staging, bootstrap_reps=bootstrap_reps, shuffle_reps=shuffle_reps, seed=seed)
        expected = {p: s for p, s in report["input_files_sha256"].items() if not p.startswith("runtime/closing_odds/")}
        if primary["input_files_sha256"] != expected:
            raise ValueError("INPUT_COHORT_CHANGED_BETWEEN_PAIRED_AND_PRIMARY_ANALYSIS")
        (staging / "closing_comparison.json").write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        (staging / "closing_comparison.md").write_text(render(report), encoding="utf-8")
        fields = ["race_id", "post_at", "runner_id", "horse_no", "zai_win", "z", "win_odds", "m", "odds_observed_at",
                  "minutes_to_post", "finish_pos", "winner_weight", "excluded_reason", "segment", "series", "source_path", "time_basis"]
        with (staging / "ledger_closing.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        out.mkdir(exist_ok=False)
        for file in staging.iterdir():
            os.link(file, out / file.name)
    finally:
        shutil.rmtree(temporary)
    return report
