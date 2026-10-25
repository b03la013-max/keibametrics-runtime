"""TEST_SYNTHETIC_ONLY: authored HTML and unsigned parser-contract fixtures.

Only factual table cells were retained. No original NAR HTML/CSS/JavaScript,
signed receipt, network fetch or live prediction is created here. The normal
snapshot builder parses our own minimal markup with explicitly synthetic clocks.
"""
from copy import deepcopy
from datetime import datetime
from functools import lru_cache
from html import escape
import gzip
import json
from pathlib import Path
import tempfile

from runtime.local_physical.nar_source_manifest import _race_card_source, _odds_source
from runtime.local_physical.nar_runner_universe import enrich_source_artifact
from runtime.local_physical.source_acquisition import (
    _merge_evidence, sha_obj, snapshot_from_bytes, SOURCE_SCHEMA, SOURCE_PROFILE,
)
from runtime.local_race_key_shadow_owner import compile_reference_prediction, render_reference_prediction
from runtime.local_race_entry import _reference_availability_report
from runtime.local_reference_day import one_race

FIXTURE = 'TEST_SYNTHETIC_ONLY'


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)+'\n')


def minimal_html(case, *, odds=False):
    """Our own simple markup around factual cells; no copied website markup."""
    if odds:
        return ('<html><body><p>'+FIXTURE+'</p><table><tr><td>発売前</td></tr></table></body></html>').encode()
    y,m,d = map(int, case['race_date'].split('-'))
    post = datetime.fromisoformat(case['scheduled_post_at']).strftime('%H:%M')
    heading = (f'{y}年{m}月{d}日 浦和 第{case["race_no"]}競走 {post}発走 '
               f'ダート{case["distance"]}m（左） {case["class"]} ')
    table = '<table>'+''.join('<tr>'+''.join('<td>'+escape(str(c))+'</td>' for c in row)+'</tr>'
                               for row in case['factual_table_cells'])+'</table>'
    return ('<html><body><p>'+FIXTURE+'</p><p>'+escape(heading)+'</p><h3>'+escape(case['title'])+
            '</h3><p>競走馬</p>'+table+'</body></html>').encode()


def synthetic_source(case, race_id):
    day, number = case['race_date'], case['race_no']
    specs = [_race_card_source('URW','18',day.replace('-','/'),number),
             _odds_source('URW','18',day.replace('-','/'),number,required=False)]
    snapshots = []
    for spec in specs:
        raw = minimal_html(case, odds=spec['source_class']=='OFFICIAL_ACTIVE_BETTING_UNIVERSE')
        snap, errors = snapshot_from_bytes(spec, raw, final_url=spec['url'], status_code=200,
            headers={'content-type':'text/html; charset=UTF-8'}, fetched_at=case['source_fetch_at'],
            prediction_cutoff=case['prediction_cutoff'])
        assert not errors, errors
        snap[FIXTURE] = True
        snap['snapshot_sha256'] = sha_obj({k:v for k,v in snap.items() if k!='snapshot_sha256'})
        snapshots.append(snap)
    normalized, conflicts, errors = _merge_evidence(snapshots)
    assert not errors, errors
    manifest = [{k:s[k] for k in ('source_id','url','source_class','authority','priority','official','required','extract')} for s in specs]
    raw_bundle = [{k:s[k] for k in ('source_id','raw_sha256','snapshot_sha256','fetched_at','final_url')} for s in snapshots]
    source = {FIXTURE:True, 'schema':SOURCE_SCHEMA, 'profile':SOURCE_PROFILE, 'race_id':race_id,
        'prediction_cutoff':case['prediction_cutoff'], 'scheduled_post_at':case['scheduled_post_at'],
        'source_freeze_at':case['source_freeze_at'],
        'source_fetch_execution':{'mode':FIXTURE,'source_count':len(snapshots),'network_executed':False,
            'prediction_authority':False,'production_transport_changed':False},
        'source_race_context':{'venue_id':'URW','race_date':day,'race_no':number},
        'required_source_manifest':manifest,'required_source_manifest_sha256':sha_obj(manifest),
        'sources':snapshots,'raw_source_bundle_sha256':sha_obj(raw_bundle),
        'normalized_evidence':normalized,'normalized_evidence_sha256':sha_obj(normalized),
        'conflicts':conflicts,'missing_required_sources':[],'stale_sources':[],'post_cutoff_sources':[],
        'formal_ready':True,'errors':[],'optional_source_errors':[],
        'research_only':True,'signed_source_claim':False,'production_authority':False}
    source = enrich_source_artifact(source)
    source['source_snapshot_sha256'] = sha_obj({k:v for k,v in source.items() if k!='source_snapshot_sha256'})
    return source


def make_reference(case, output):
    day, no = case['race_date'], case['race_no']
    eid = f'KM-LOCAL-URW-{day.replace("-", "")}-R{no:02d}-REFERENCE-R1'
    intent = {FIXTURE:True,'family_id':'LOCAL','venue_id':'URW','race_date':day,'race_no':no,
              'prediction_mode':'REFERENCE','race_id':eid,'execution_id':eid}
    source = synthetic_source(case, eid)
    prediction = compile_reference_prediction(intent, source, now=datetime.fromisoformat(case['forecast_freeze_at']))
    prediction[FIXTURE] = True
    prediction['status'] += ' / '+FIXTURE
    prediction['source_signature_status'] = 'TEST_SYNTHETIC_ONLY_NOT_OFFICIAL_OBSERVATION'
    prediction['sha256'] = sha_obj({k:v for k,v in prediction.items() if k!='sha256'})
    for name, value in [('reference_intent.json',intent),('reference_source.json',source),('reference_prediction.json',prediction)]:
        write(output/name,value)
    (output/'reference_prediction.md').write_text(render_reference_prediction(prediction))
    report = _reference_availability_report(intent, output=output, run_id=FIXTURE, prediction=prediction, eid=eid)
    report[FIXTURE] = True
    write(output/'entry_report.json',report)
    return source, prediction


@lru_cache(maxsize=1)
def fixture_root():
    """Build a private temporary test tree; no data is written into Runtime."""
    facts = json.loads((Path(__file__).parent/'factual_cells.json').read_text())
    assert facts[FIXTURE] is True
    root = Path(tempfile.mkdtemp(prefix='km-urw-TEST_SYNTHETIC_ONLY-'))
    for key, case in facts['cases'].items():
        if key=='declared_capsule':
            continue
        day, label = key.split('/')
        if day=='2026-10-20':
            folder=root/'runtime/local_reference'/day/label
            attempt=folder/'attempts/001'
            make_reference(case,attempt)
            publication,_=one_race(folder,day,case['race_no'],generate=lambda *a, _p=attempt, **k:json.loads((_p/'entry_report.json').read_text()),
                                   clock=lambda _c=case:datetime.fromisoformat(_c['forecast_freeze_at']))
            publication[FIXTURE]=True
            publication['sha256']=sha_obj({k:v for k,v in publication.items() if k!='sha256'})
            write(folder/'publication.json',publication)
        else:
            make_reference(case,root/'research/urw_owner/20261019_prediction_availability/reference_repair'/label)
    # Legacy cache-layout regression uses the same explicitly synthetic source.
    import shutil
    shutil.copytree(root/'research/urw_owner/20261019_prediction_availability/reference_repair/R05',
                    root/'research/urw_owner/20261019_prediction_availability/chat_R05')
    plan=deepcopy(facts['plan_facts'])
    plan['official_snapshots']=[]
    plan['discovery_read_attempts']=[]
    for row in plan['races']:
        source=json.loads((root/f'runtime/local_reference/2026-10-20/R{row["fields"]["race_no"]:02d}/attempts/001/reference_source.json').read_text())
        row['source_basis_sha256']=source['source_snapshot_sha256']
    plan['plan_sha256']=sha_obj(plan)
    path=root/'runtime/local_reference/2026-10-20/official_plan.json.gz'
    path.write_bytes(gzip.compress(json.dumps(plan,ensure_ascii=False,sort_keys=True).encode(),mtime=0))
    # A declared-source materialization contract, never a signed SOURCE or OOS.
    from runtime.local_fullnumerical_candidate import materialize_candidate
    from runtime.local_nar_evidence_candidate import compile_candidate_evidence
    from runtime.local_krs_bridge_candidate import build_candidate_prediction_structure_derived
    c=facts['cases']['declared_capsule'];eid='KM-LOCAL-URW-20261019-R01-PUBLIC-SHADOW'
    source=synthetic_source(c,eid)
    req={'family_id':'LOCAL','venue_id':'URW','race_id':eid,'execution_id':eid,'race_date':c['race_date'],'race_no':1,
         'scheduled_post_at':c['scheduled_post_at'],'prediction_cutoff':c['prediction_cutoff'],
         'runners':source['declared_runner_universe']['runners'],
         'race':{'racecourse':'浦和','date':c['race_date'],'race_no':1,
                 'prediction_id':eid,'distance':c['distance'],'surface':'DIRT','class':c['class']}}
    numerical=build_candidate_prediction_structure_derived(materialize_candidate(compile_candidate_evidence(source,req)))
    capsule={FIXTURE:True,'source_artifact':source,'numerical':numerical,
        'report':{FIXTURE:True,'frozen_at':c['forecast_freeze_at'],'forward_oos_credit':0,
                  'fields':{k:req[k] for k in ('venue_id','race_date','race_no','scheduled_post_at','prediction_cutoff')}}}
    p=root/'declared_capsule.json.gz'
    p.write_bytes(gzip.compress(json.dumps(capsule,ensure_ascii=False,sort_keys=True).encode(),mtime=0))
    return root
