"""Availability must include independent verification and must not be backdated."""
import copy
import json
from pathlib import Path
import sys

import pytest
sys.path.insert(0,str(Path(__file__).parent))
from identity_label_times import derive,sha_obj


def seal(obj):
    obj['sha256']=sha_obj({k:v for k,v in obj.items() if k!='sha256'});return obj


def fixture(root):
    corpus='runtime/pedigree_corpus/unit.json';p=root/corpus;p.parent.mkdir(parents=True)
    run={'date':'2026-09-27','venue':'中山','race_name':'2歳未勝利','surface':'芝',
         'distance_m':1600,'finish':2,'field_size':12}
    horse={'horse_name':'UNIT','sire':'SIRE','dam':'DAM','damsire':'DAMSIRE','runs':[run]}
    p.write_text(json.dumps({'horses':[horse]}))
    r=seal({'target_cutoff':'2026-10-24T09:00:00+09:00',
        'raw_proofs':{'unit':{'source_envelope':'source.json','fetched_at':'2026-10-21T00:00:00Z'}},
        'resolved':[{'corpus_file':corpus,'observation_index':0,'proof':'unit','chronology_before_target':True,
            'original_observation_at':'2026-10-20T00:00:00Z',
            'run_bindings':[{'proof':'unit','run_index':0,'chronology_before_target':True}]}]})
    q=seal({'recovery_sha256':r['sha256'],'file_verifications':{
        name:{'qualified':True,'checks':[{'verified':True,'verified_timestamps':[time]}]}
        for name,time in [(corpus,'2026-10-20T00:01:00Z'),('source.json','2026-10-21T00:01:00Z'),
                          ('result.json','2026-10-23T05:00:00Z')]}})
    a=seal({'source_recovery_sha256':r['sha256'],'source_qualification_sha256':q['sha256'],
        'matched_direct_result_labels':[{'composite_identity':['UNIT','SIRE','DAM','DAMSIRE'],
            'run':run,'official_race_id':'KM-JRA-NKY-20260927-R02',
            'direct_result_evidence':[{'file':'result.json','observed_at':'2026-10-23T04:00:00Z',
                                       'snapshot_sha256':'a'*64}]}]})
    return r,q,a


def test_independent_result_verification_controls_available_label_time(tmp_path):
    r,q,a=fixture(tmp_path);out=derive(r,q,a,tmp_path)
    assert out['matched_labels_with_independent_availability']==1
    row=out['labels'][0]
    assert row['label_date']=='2026-09-27'
    assert row['label_available_at']=='2026-10-23T05:00:00+00:00'
    assert row['permanent_horse_id'] is None and not row['production_training_eligible']
    assert out['oos_increment']==0


@pytest.mark.parametrize('mutation',['late_witness','unqualified','changed_input'])
def test_missing_or_late_independent_clock_cannot_be_filled(tmp_path,mutation):
    r,q,a=fixture(tmp_path)
    if mutation=='late_witness':
        q['file_verifications']['result.json']['checks'][0]['verified_timestamps']=['2026-10-25T00:00:00Z']
        seal(q);a['source_qualification_sha256']=q['sha256'];seal(a)
    elif mutation=='unqualified':
        q['file_verifications']['result.json']['qualified']=False
        seal(q);a['source_qualification_sha256']=q['sha256'];seal(a)
    else:r['target_cutoff']='2099-01-01T00:00:00Z'
    with pytest.raises(ValueError):derive(r,q,a,tmp_path)
