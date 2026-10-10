import hashlib
import json
from pathlib import Path
import pytest
from runtime.jra_keibabook_private_intake import ingest, parse_ability, parse_pedigree, validate_universe

ABILITY = '''<table><tr><td class="umaban">1</td><td class="bamei"><p><a>父</a></p><p><a>テスト馬</a></p><p><span>母</span></p><p><span>母父</span></p></td><td class="zensou"><div class="inner"><p><a href="/cyuou/seiseki/202604000101">9･20</a></p><p>1400芝</p><p>S72</p><p>記録</p></div></td></tr></table>'''
WORKOUT = '<table><tr><td class="umaban">1</td><td class="kbamei">テスト馬</td></tr><tr></tr></table>'
STABLE = '<table><tr><td class="umaban">1</td><td><a href="/db/uma/1234567">テスト馬</a></td></tr><tr><td class="danwa">好調</td></tr></table>'
OFFICIAL = [{'runner_id':'1','name':'テスト馬'}]

def capture(tmp_path):
    entries=[]
    for kind, raw, suffix in [('ability',ABILITY,'nouryoku_html_detail/202604000309.html'),('workout',WORKOUT,'cyokyo/0/202604000309'),('stable',STABLE,'danwa/0/202604000309')]:
        (tmp_path / (kind+'.html')).write_text(raw)
        entries.append({'file':kind+'.html','url':'https://s.keibabook.co.jp/cyuou/'+suffix,'sha256':hashlib.sha256(raw.encode()).hexdigest(),'captured_at':'2026-01-02T00:00:00+00:00'})
    path=tmp_path/'manifest.json';path.write_text(json.dumps(entries));return path

def run(path):
    return ingest(path,official=OFFICIAL,race_date='2026-10-10',book_race_id='202604000309',prediction_cutoff='2026-01-01T00:00:00+00:00')

def test_prior_speed_and_future_rejection():
    assert parse_ability(ABILITY,'2026-10-10')[0]['prior_runs'][0]['speed_index']==72
    with pytest.raises(ValueError,match='FUTURE_RESULT'):
        parse_ability(ABILITY,'2026-09-20')

def test_replay_never_signed_or_promoted(tmp_path):
    result=run(capture(tmp_path))
    assert result['temporal_mode']=='REPLAY'
    assert not result['signed_source'] and not result['production_authority']
    assert result['oos_increment']==0 and not result['signed_final_issued']

def test_tampered_capture_rejected(tmp_path):
    path=capture(tmp_path);(tmp_path/'ability.html').write_text('changed')
    with pytest.raises(ValueError,match='HASH_MISMATCH'):run(path)

def test_universe_duplicates_and_wrong_name():
    with pytest.raises(ValueError,match='UNIVERSE'):validate_universe(OFFICIAL*2,OFFICIAL)
    with pytest.raises(ValueError,match='UNIVERSE'):validate_universe([{'runner_id':'1','name':'別馬'}],OFFICIAL)

def test_pedigree_zero_starts_unknown_and_rates_verified():
    raw='<p>馬場種類別</p><table><tr><th>1着</th><th>2着</th><th>3着</th><th>着外</th></tr><tr><td>芝</td>'+''.join('<td>'+str(v)+'</td>' for v in [0,0,0,0,'0.000','0.000','0.000'])+'</tr></table>'
    assert parse_pedigree(raw)[0]['rates']==[None,None,None]
    with pytest.raises(ValueError,match='RATE_MISMATCH'):
        parse_pedigree(raw.replace('<td>0</td>','<td>1</td>',1))
