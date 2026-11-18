import io
import json
import zipfile

from runtime.local_autopilot import nar_ingest
import importlib.util, pathlib
_spec = importlib.util.spec_from_file_location('hs_t', pathlib.Path(__file__).with_name('test_local_hist_stats.py'))
_m = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_m)
RL, HL, PB = _m.RL, _m.HL, _m.PB


def test_ingest_owner_zip(tmp_path):
    z = tmp_path / '202610_1795000000_race.zip'
    with zipfile.ZipFile(z, 'w') as zf:
        zf.writestr('202610_racelist.csv', RL.encode('cp932'))
        zf.writestr('202610_horselist.csv', HL.encode('cp932'))
        zf.writestr('202610_payback.csv', PB.encode('cp932'))
    done, st = nar_ingest.ingest(tmp_path / 'out', [z])
    assert done == ['202610'] and st['races'] == 2 and 'NAR_OFFICIAL_CSV:202610' in st['source']
    man = json.loads((tmp_path / 'out' / 'hist' / 'nar' / '202610' / 'manifest.json').read_text())
    assert len(man['files']) == 3 and 'Owner' in man['source']
    assert (tmp_path / 'out' / 'hist_stats.md').exists()
