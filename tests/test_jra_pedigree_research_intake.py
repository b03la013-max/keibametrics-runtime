import hashlib,json,sys,zipfile
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'runtime'))
from jra_pedigree_research_intake import normalize_checkpoint


def checkpoint(tmp_path,rows):
    files={'results.json':rows,'races.json':[{'race_id':'provider-race','condition_text':'test'}],
        'collection_state.json':{'requested_period':['2021-10-11','2026-10-10'],'status':'STOPPED'},
        'observed_races.json':[{'id':'provider-race'}]}
    raw={k:json.dumps(v).encode() for k,v in files.items()}
    p=tmp_path/'private.zip'
    with zipfile.ZipFile(p,'w') as z:
        for k,v in raw.items():z.writestr(k,v)
        z.writestr('sha256.json',json.dumps({k:hashlib.sha256(v).hexdigest() for k,v in raw.items()}))
    return p


def row(**updates):
    return {'race_id':'provider-race','horse_number':'1','horse_id':'provider-horse',
        'horse_name':'test','sire':'father','damsire':'maternal','race_date':'20211228',
        'observed_at':'2026-10-11T05:00:00Z','source_url':'https://www.blood-b.com/test',**updates}


def test_observation_time_is_not_backdated_and_official_identity_not_invented(tmp_path):
    p=checkpoint(tmp_path,[row()]);rows,a=normalize_checkpoint(p)
    assert rows[0]['horse_id']=='bloodb:provider-horse'
    assert rows[0]['official_horse_id'] is None and rows[0]['dam_name'] is None
    assert rows[0]['source_available_at'].startswith('2026-10-11')
    assert not rows[0]['production_authority']
    assert normalize_checkpoint(p,'2026-10-10T00:00:00Z')[0]==[]


def test_duplicate_rows_are_not_counted_twice_and_conflicts_are_quarantined(tmp_path):
    assert normalize_checkpoint(checkpoint(tmp_path,[row(),row()]))[1]['runner_rows']==1
    rows,a=normalize_checkpoint(checkpoint(tmp_path,[row(),row(sire='different')]))
    assert rows==[] and a['conflicting_runner_keys']==1


def test_changed_member_cannot_pass_checkpoint_integrity(tmp_path):
    p=checkpoint(tmp_path,[row()])
    with zipfile.ZipFile(p) as z:parts={n:z.read(n) for n in z.namelist()}
    parts['results.json']=b'[]'
    with zipfile.ZipFile(p,'w') as z:
        for k,v in parts.items():z.writestr(k,v)
    with pytest.raises(ValueError,match='HASH_MISMATCH'):normalize_checkpoint(p)
