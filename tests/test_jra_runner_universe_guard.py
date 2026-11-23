"""11/23 review P0: a PDF parse bound to another race must not cost the race."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime/jra_source_runtime'))
from jra_runner_universe_guard import pdf_is_other_race  # noqa: E402

# FKS 2026-11-23 R03: the PDF parse returned R02's runners (names from the SOURCE receipt).
PDF_R02 = {1: 'サクラパステル', 2: 'ピラニアキッス', 3: 'メリーサウンド', 4: 'ミヤジテン', 5: 'ルージュボニート', 6: 'ベルソテイラ'}
DETAIL_R03 = {1: 'ロンドンオービタル', 2: 'ソナタン', 3: 'ニコ', 4: 'ケイエイト', 5: 'サムシングニュー', 6: 'ムーランオランジュ'}


def test_disjoint_names_mean_other_race():
    assert pdf_is_other_race(PDF_R02, DETAIL_R03)


def test_any_common_name_still_fails_source():
    partial = {**DETAIL_R03, 1: 'サクラパステル'}  # one shared name: partial mismatch
    assert not pdf_is_other_race(PDF_R02, partial)
    shuffled = {i + 1: n for i, n in enumerate(reversed(list(DETAIL_R03.values())))}
    assert not pdf_is_other_race(shuffled, DETAIL_R03)  # same horses, numbers differ


def test_small_or_blank_fields_are_not_provable():
    assert not pdf_is_other_race({1: 'A', 2: 'B'}, {1: 'C', 2: 'D'})
    blank = {**PDF_R02, 6: ''}
    assert not pdf_is_other_race(blank, DETAIL_R03)
    assert not pdf_is_other_race({}, DETAIL_R03)


def test_whitespace_and_width_normalised():
    spaced = {k: ' '.join(v) for k, v in DETAIL_R03.items()}
    assert not pdf_is_other_race(spaced, DETAIL_R03)


def test_app_uses_detail_fallback_only_in_guarded_branch():
    s = (ROOT / 'runtime/jra_source_runtime/app.py').read_text()
    i = s.index('if pdf_is_other_race(p,h):')
    block = s[i:i + 2000]
    assert 'JRA_OFFICIAL_JRADB_DETAIL_FALLBACK_PDF_OTHER_RACE' in block
    assert 'JRA_OFFICIAL_RUNNER_UNIVERSE_PDF_DETAIL_MISMATCH' in block.split('else:', 1)[1]
    assert s.index('reconcile_pdf_column_with_detail(') < i  # strict recovery is tried first
