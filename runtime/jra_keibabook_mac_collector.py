"""Mac-only, personally authenticated Keibabook capture -> existing private intake.

This collector does not defeat authentication, paywalls or access restrictions.
It requires the subscriber to be logged in through their OWN dedicated browser
profile, plus the provider's permission for the intended automated use. No
cookies, paid pages or paid-derived detail are sent to GitHub by this module.

Collector output is local and diagnostic only; it is not a signed JRA SOURCE,
FULL20 Production evidence, or any type of formal FINAL.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import plistlib
import re
import shutil
import subprocess
import sys
import tempfile
import fcntl
from urllib.parse import urlparse

try:
    from .jra_keibabook_private_intake import ingest
    from .jra_keibabook_evaluator_conformance import evaluate
except ImportError:
    from jra_keibabook_private_intake import ingest
    from jra_keibabook_evaluator_conformance import evaluate

HOME = Path.home() / ".keibametrics"
DEFAULT_PROFILE = HOME / "browser_keibabook"
DEFAULT_PRIVATE = HOME / "private_book"
DEFAULT_QUEUE = HOME / "book_queue.json"
LABEL = "jp.keibametrics.book-collector"
KIND_PATHS = {
    "ability": "nouryoku_html_detail/{race}.html",
    "workout": "cyokyo/0/{race}",
    "stable": "danwa/0/{race}",
}


class BookCollectorError(ValueError):
    pass


def _private_dir(path: Path) -> Path:
    path = path.expanduser().resolve()
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    if path.is_symlink() or path.stat().st_mode & 0o077:
        raise BookCollectorError("PRIVATE_DIRECTORY_PERMISSIONS_UNSAFE:" + str(path))
    return path


def _write_private(path: Path, data: bytes) -> None:
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    fd = os.open(path, flags, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def _json_bytes(data: object) -> bytes:
    return (json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def _time(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise BookCollectorError("TIME_INVALID") from exc
    if parsed.tzinfo is None:
        raise BookCollectorError("TIMEZONE_REQUIRED")
    return parsed.astimezone(timezone.utc)


def _race_id(value: str, race_date: str) -> str:
    if not re.fullmatch(r"\d{12}", str(value)) or str(value)[:4] != str(race_date)[:4]:
        raise BookCollectorError("BOOK_RACE_ID_INVALID")
    _time(race_date + "T00:00:00+09:00")
    return value


def _url(kind: str, book_race_id: str) -> str:
    return "https://s.keibabook.co.jp/cyuou/" + KIND_PATHS[kind].format(race=book_race_id)


def _assert_expected_url(actual: str, expected: str) -> None:
    source = urlparse(actual)
    expected_url = urlparse(expected)
    if (source.scheme, source.hostname, source.path, source.query, source.fragment) != (
            expected_url.scheme, expected_url.hostname, expected_url.path, "", ""):
        # A login/paywall redirect cannot count as collected subscriber data.
        raise BookCollectorError("PROVIDER_AUTHENTICATION_OR_PAGE_MISMATCH")


def _get_page_html(context, kind: str, book_race_id: str, cutoff: datetime, *, replay: bool):
    expected = _url(kind, book_race_id)
    page = context.new_page()
    try:
        response = page.goto(expected, wait_until="domcontentloaded", timeout=30000)
        if response is None or response.status != 200:
            raise BookCollectorError("PROVIDER_HTTP_NOT_SUCCESS:" + str(response.status if response else None))
        page.wait_for_selector("td.umaban", state="attached", timeout=15000)
        _assert_expected_url(page.url, expected)
        captured = datetime.now(timezone.utc)
        if captured >= cutoff and not replay:
            raise BookCollectorError("BOOK_CAPTURE_CUTOFF_EXPIRED")
        raw = page.content().encode("utf-8")
        if len(raw) > 3_000_000:
            raise BookCollectorError("BOOK_CAPTURE_TOO_LARGE")
        return {
            "file": kind + ".html",
            "url": expected,
            "sha256": hashlib.sha256(raw).hexdigest(),
            "captured_at": captured.isoformat(),
            "capture_method": "PLAYWRIGHT_AUTHENTICATED_RENDERED_DOM",
        }, raw
    finally:
        page.close()


def _validate_official(official: object) -> list[dict]:
    if not isinstance(official, list) or not 2 <= len(official) <= 18:
        raise BookCollectorError("OFFICIAL_RUNNER_UNIVERSE_REQUIRED")
    ids = [str(x.get("runner_id") or x.get("horse_no") or "") for x in official if isinstance(x, dict)]
    if len(ids) != len(official) or len(set(ids)) != len(ids) or not all(ids):
        raise BookCollectorError("OFFICIAL_RUNNER_UNIVERSE_INVALID")
    if not all(str(x.get("name") or "").strip() for x in official):
        raise BookCollectorError("OFFICIAL_RUNNER_NAMES_REQUIRED")
    return official


def capture_race(context, *, book_race_id: str, race_date: str, prediction_cutoff: str,
                 official: list[dict], output_dir: str | Path = DEFAULT_PRIVATE,
                 replay: bool = False) -> dict:
    race = _race_id(book_race_id, race_date)
    official = _validate_official(official)
    cutoff = _time(prediction_cutoff)
    if datetime.now(timezone.utc) >= cutoff and not replay:
        raise BookCollectorError("BOOK_CAPTURE_CUTOFF_EXPIRED")
    root = _private_dir(Path(output_dir))
    destination = root / race
    if destination.exists():
        raise BookCollectorError("BOOK_CAPTURE_IMMUTABLE_ALREADY_EXISTS")
    staging = Path(tempfile.mkdtemp(prefix=".pending-" + race + "-", dir=root))
    try:
        os.chmod(staging, 0o700)
        manifest = []
        for kind in KIND_PATHS:
            meta, raw = _get_page_html(context, kind, race, cutoff, replay=replay)
            _write_private(staging / meta["file"], raw)
            manifest.append(meta)
        _write_private(staging / "manifest.json", _json_bytes(manifest))
        private = ingest(
            staging / "manifest.json", official=official, race_date=race,
            book_race_id=race, prediction_cutoff=prediction_cutoff,
        )
        assessed = evaluate(private)
        # A successful fetch from Book is NOT automatically Production evidence.
        assert assessed["production_authority"] is False
        assert assessed["signed_final_issued"] is False
        _write_private(staging / "intake.json", _json_bytes(private))
        _write_private(staging / "diagnostic_evaluations.json", _json_bytes(assessed))
        counts = Counter(name for feats in assessed["observations"].values() for name in feats)
        result = {
            "book_race_id": race, "race_date": race_date,
            "runner_count": private["runner_count"],
            "prediction_cutoff": prediction_cutoff,
            "capture_temporal_mode": private["temporal_mode"],
            "capture_hashes": {x["kind"]: x["raw_sha256"] for x in private["sources"]},
            "available_feature_counts": dict(sorted(counts.items())),
            "feature_gaps": len(assessed["blocked"]),
            "production_authority": False, "signed_source": False,
            "signed_final_issued": False, "oos_increment": 0,
            "private_on_mac": True, "automated_purchase": False,
        }
        _write_private(staging / "local_summary.json", _json_bytes(result))
        # Same filesystem atomic publish; nothing incomplete is advertised.
        if destination.exists():
            raise BookCollectorError("BOOK_CAPTURE_IMMUTABLE_ALREADY_EXISTS")
        staging.rename(destination)
        return result
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def _playwright():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise BookCollectorError("PLAYWRIGHT_NOT_INSTALLED_ON_MAC") from exc
    return sync_playwright


def browser_login(*, profile: str | Path = DEFAULT_PROFILE):
    profile = _private_dir(Path(profile))
    with _playwright()() as playwright:
        context = playwright.chromium.launch_persistent_context(
            str(profile), headless=False, accept_downloads=False,
        )
        try:
            page = context.new_page()
            page.goto("https://s.keibabook.co.jp/", wait_until="domcontentloaded")
            print("Complete the normal subscriber login in this dedicated browser.")
            print("Do not enter passwords, cookies, recovery codes or session tokens into ChatGPT.")
            input("Once access works, press Enter here to close and preserve the local session: ")
        finally:
            context.close()


def run_capture(spec: dict, *, profile: Path = DEFAULT_PROFILE,
                private_dir: Path = DEFAULT_PRIVATE, replay: bool = False) -> dict:
    official_path = Path(spec["official_runners_path"]).expanduser().resolve()
    official = _validate_official(json.loads(official_path.read_text(encoding="utf-8")))
    profile = _private_dir(profile)
    with _playwright()() as playwright:
        context = playwright.chromium.launch_persistent_context(
            str(profile), headless=True, accept_downloads=False,
        )
        try:
            return capture_race(
                context, book_race_id=spec["book_race_id"],
                race_date=spec["race_date"],
                prediction_cutoff=spec["prediction_cutoff"],
                official=official, output_dir=private_dir, replay=replay,
            )
        finally:
            context.close()


def process_queue(queue_path: Path, *, profile: Path = DEFAULT_PROFILE,
                  private_dir: Path = DEFAULT_PRIVATE, lookahead_minutes: int = 65) -> dict:
    """Launchd entry: only pre-cutoff queued races, never invent Book race IDs."""
    queue_path = queue_path.expanduser().resolve()
    if not queue_path.is_file():
        raise BookCollectorError("BOOK_QUEUE_MISSING:" + str(queue_path))
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    if not isinstance(queue, list):
        raise BookCollectorError("BOOK_QUEUE_LIST_REQUIRED")
    output = _private_dir(private_dir)
    lock_path = output / ".queue.lock"
    lock_fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    results = {"completed": [], "not_due": [], "past_cutoff": [], "already_collected": [], "failed": []}
    with os.fdopen(lock_fd, "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        for spec in queue:
            if not isinstance(spec, dict):
                raise BookCollectorError("BOOK_QUEUE_SPEC_INVALID")
            race = _race_id(spec.get("book_race_id"), spec.get("race_date"))
            remain = (_time(spec.get("prediction_cutoff")) - datetime.now(timezone.utc)).total_seconds()
            if (output / race).exists():
                results["already_collected"].append(race)
            elif remain <= 0:
                results["past_cutoff"].append(race)
            elif remain > lookahead_minutes * 60:
                results["not_due"].append(race)
            else:
                try:
                    observed = run_capture(spec, profile=profile, private_dir=private_dir)
                    results["completed"].append({
                        "book_race_id":race, "observed_feature_counts":observed["available_feature_counts"]
                    })
                except Exception as exc:
                    # Never continue as if a failed authenticated fetch succeeded.
                    results["failed"].append({"book_race_id": race, "reason": str(exc)})
        fcntl.flock(lock, fcntl.LOCK_UN)
    return results


def make_launchd_plist(*, repo_root: Path, queue_path: Path, profile: Path,
                      private_dir: Path, interval_seconds: int = 300) -> dict:
    if not 120 <= interval_seconds <= 3600:
        raise BookCollectorError("LAUNCHD_INTERVAL_INVALID")
    root = repo_root.expanduser().resolve()
    module = root / "runtime/jra_keibabook_mac_collector.py"
    if not module.is_file():
        raise BookCollectorError("LOCAL_REPOSITORY_COLLECTOR_NOT_FOUND")
    private = _private_dir(private_dir)
    return {
        "Label": LABEL, "RunAtLoad": True, "StartInterval": interval_seconds,
        "WorkingDirectory": str(root),
        "ProgramArguments": [
            sys.executable, str(module), "queue",
            "--queue", str(queue_path.expanduser().resolve()),
            "--profile", str(profile.expanduser().resolve()),
            "--private-dir", str(private),
        ],
        "StandardOutPath": str(private / "collector.stdout.log"),
        "StandardErrorPath": str(private / "collector.stderr.log"),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    login = sub.add_parser("login")
    login.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    capture = sub.add_parser("capture")
    capture.add_argument("--spec", type=Path, required=True)
    capture.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    capture.add_argument("--private-dir", type=Path, default=DEFAULT_PRIVATE)
    capture.add_argument("--replay", action="store_true")
    queue = sub.add_parser("queue")
    queue.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    queue.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    queue.add_argument("--private-dir", type=Path, default=DEFAULT_PRIVATE)
    install = sub.add_parser("install-launchd")
    install.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    install.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    install.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    install.add_argument("--private-dir", type=Path, default=DEFAULT_PRIVATE)
    install.add_argument("--interval-seconds", type=int, default=300)
    install.add_argument("--activate", action="store_true")
    args = parser.parse_args(argv)
    if args.action == "login":
        browser_login(profile=args.profile)
        return 0
    if args.action == "capture":
        spec = json.loads(args.spec.expanduser().read_text(encoding="utf-8"))
        result = run_capture(spec, profile=args.profile,
                             private_dir=args.private_dir, replay=args.replay)
    elif args.action == "queue":
        result = process_queue(args.queue, profile=args.profile, private_dir=args.private_dir)
    else:
        if sys.platform != "darwin":
            raise BookCollectorError("LAUNCHD_ONLY_ON_MACOS")
        launch_dir = _private_dir(HOME)
        plist = make_launchd_plist(
            repo_root=args.repo, queue_path=args.queue, profile=args.profile,
            private_dir=args.private_dir, interval_seconds=args.interval_seconds,
        )
        agents = Path.home() / "Library/LaunchAgents"
        agents.mkdir(parents=True, exist_ok=True)
        target = agents / (LABEL + ".plist")
        with target.open("wb") as stream:
            plistlib.dump(plist, stream)
        os.chmod(target, 0o600)
        if args.activate:
            result_activation = subprocess.run(
                ["launchctl", "bootstrap", "gui/" + str(os.getuid()), str(target)],
                capture_output=True, text=True, check=False,
            )
            if result_activation.returncode:
                raise BookCollectorError("LAUNCHD_ACTIVATION_FAILED:" + result_activation.stderr)
        result = {"launch_agent_path": str(target), "activated":args.activate,
                  "session_saved_locally":True, "queue_path":str(args.queue)}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if not result.get("failed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
