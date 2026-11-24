"""11/23 review P0: Challenger freezes must not depend on GitHub cron alone.

On 2026-11-23 the 15-minute cron of km-jra-index-research.yml fired in only 2 of 36
slots, so none of the 20 FINALs got a Challenger freeze before post. The workflow is
now also triggered by every completed JRA FORMAL run (the run that persists the FINAL),
and that trigger keeps the race-day guard so non-race days exit immediately.
"""
from pathlib import Path

WF = Path(__file__).resolve().parents[1] / '.github/workflows/km-jra-index-research.yml'


def _text():
    return WF.read_text()


def test_formal_runner_completion_triggers_freeze():
    s = _text()
    i = s.index('workflow_run:')
    block = s[i:s.index('schedule:', i)]
    assert '"KeibaMetrics Formal Request Runner"' in block
    assert '"JRA Candidate Automatic Official Postresult Closed Loop"' in block
    assert 'types: [completed]' in block


def test_formal_runner_name_matches_trigger():
    runner = WF.parent / 'km-formal-request-runner.yml'
    assert runner.read_text().splitlines()[0].strip() == 'name: KeibaMetrics Formal Request Runner'


def test_cron_backstop_and_race_day_guard_kept():
    s = _text()
    assert 'cron: "10,25,40,55 0-8 * * *"' in s
    assert 'github.event.workflow_run.name }}" = "KeibaMetrics Formal Request Runner"' in s
    assert 'NO_RACE_DAY_SCHEDULE' in s
    # the post-result trigger (which can run after midnight JST) is NOT guarded, so evaluation still runs
    guard = s[s.index('FREEZE_ONLY_TRIGGER=false'):s.index('NO_RACE_DAY_SCHEDULE')]
    assert 'Postresult' not in guard


def test_freeze_steps_unchanged():
    s = _text()
    for cmd in ('jra_role_candidate_replay.py freeze "$D"', 'jra_nobet_shadow.py freeze "$D"',
                'jra_feature_challenger.py freeze "$D"', 'jra_conversion_challenger.py freeze "$D"',
                'jra_info_gap_challenger.py freeze "$D"', 'jra_keibabook_forward_oos.py freeze "$D"'):
        assert cmd in s
