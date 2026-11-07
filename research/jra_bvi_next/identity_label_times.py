"""Derive conservative label-availability clocks from an offline bound audit.

This consumes only that audit's matched direct-result records and the original
CI qualification. It neither requalifies OIDC nor backdates acquisition clocks.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
from datetime import timezone

from identity_label_audit import stamp, sha_obj, signature, surface


def verified_time(qualification, name):
    record=qualification['file_verifications'].get(name) or {}
    stamps=[stamp(t) for c in record.get('checks') or [] if c.get('verified') is True
            for t in c.get('verified_timestamps') or []]
    if not record.get('qualified') or not stamps:
        raise ValueError('IDENTITY_LABEL_TIME_FILE_NOT_QUALIFIED')
    return min(stamps)


def derive(recovery, qualification, audit, root):
    for obj in (recovery,qualification,audit):
        if obj.get('sha256')!=sha_obj({k:v for k,v in obj.items() if k!='sha256'}):
            raise ValueError('IDENTITY_LABEL_TIME_INPUT_HASH')
    if (audit['source_recovery_sha256']!=recovery['sha256']
            or audit['source_qualification_sha256']!=qualification['sha256']
            or qualification['recovery_sha256']!=recovery['sha256']):
        raise ValueError('IDENTITY_LABEL_TIME_INPUT_BINDING')
    cutoff=stamp(recovery['target_cutoff']);root=Path(root)
    original_times=defaultdict(list);corpora={}
    for row in recovery['resolved']:
        name=row['corpus_file'];source=recovery['raw_proofs'][row['proof']]['source_envelope']
        if not row['chronology_before_target']:continue
        if (not qualification['file_verifications'].get(name,{}).get('qualified')
                or not qualification['file_verifications'].get(source,{}).get('qualified')):continue
        if name not in corpora:corpora[name]=json.loads((root/name).read_text())
        horse=corpora[name]['horses'][row['observation_index']]
        for run in row['run_bindings']:
            proof=recovery['raw_proofs'][run['proof']]
            if not run['chronology_before_target'] or not qualification['file_verifications'].get(proof['source_envelope'],{}).get('qualified'):continue
            item=horse['runs'][run['run_index']]
            key=(signature(horse),item['date'],item['venue'],item['race_name'],surface(item['surface']),
                 item['distance_m'],item['finish'],item['field_size'])
            components={'original_harvested_at':stamp(row['original_observation_at']),
                'original_profile_fetched_at':stamp(proof['fetched_at']),
                'harvest_independent_verified_at':verified_time(qualification,name),
                'profile_independent_verified_at':verified_time(qualification,proof['source_envelope'])}
            original_times[key].append({'available_at':max(components.values()),
                'components':components,'corpus_file':name,'profile_source_file':proof['source_envelope']})
    rows=[]
    for match in audit['matched_direct_result_labels']:
        run=match['run'];key=(tuple(match['composite_identity']),run['date'],run['venue'],run['race_name'],
            surface(run['surface']),run['distance_m'],run['finish'],run['field_size'])
        earlier=original_times.get(key)
        if not earlier:raise ValueError('IDENTITY_LABEL_TIME_ORIGINAL_HISTORY_UNBOUND')
        history=min(earlier,key=lambda x:x['available_at'])
        alternatives=[]
        for result in match['direct_result_evidence']:
            components={**history['components'],
                'direct_result_fetched_at':stamp(result['observed_at']),
                'direct_result_independent_verified_at':verified_time(qualification,result['file'])}
            alternatives.append({'available_at':max(components.values()),'components':components,
                'direct_result_source_file':result['file'],'direct_result_snapshot_sha256':result['snapshot_sha256']})
        chosen=min(alternatives,key=lambda x:x['available_at'])
        if chosen['available_at']>=cutoff:raise ValueError('IDENTITY_LABEL_TIME_POST_CUTOFF')
        rows.append({'composite_identity':match['composite_identity'],'official_race_id':match['official_race_id'],
            'label_date':run['date'],'label_available_at':chosen['available_at'].astimezone(timezone.utc).isoformat(),
            'clock_components':{k:v.astimezone(timezone.utc).isoformat() for k,v in chosen['components'].items()},
            'corpus_file':history['corpus_file'],'profile_source_file':history['profile_source_file'],
            'direct_result_source_file':chosen['direct_result_source_file'],
            'direct_result_snapshot_sha256':chosen['direct_result_snapshot_sha256'],
            'permanent_horse_id':None,'production_training_eligible':False})
    out={'profile':'KM-JRA-OFFLINE-INDEPENDENT-LABEL-AVAILABILITY-AUDIT-v1',
        'classification':'INHERITED_CI_QUALIFICATION / NO_NEW_OIDC / NOT_FORWARD_OOS',
        'source_identity_audit_sha256':audit['sha256'],'source_recovery_sha256':recovery['sha256'],
        'source_qualification_sha256':qualification['sha256'],'target_cutoff':recovery['target_cutoff'],
        'matched_labels_with_independent_availability':len(rows),
        'earliest_label_available_at':min((r['label_available_at'] for r in rows),default=None),
        'latest_label_available_at':max((r['label_available_at'] for r in rows),default=None),
        'availability_is_not_label_date':True,'permanent_id_training_eligible':0,
        'production_effect':'NONE','oos_increment':0,'labels':rows,
        'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    out['sha256']=sha_obj(out);return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True)
    for name in ('recovery','qualification','audit','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();out=derive(json.loads(a.recovery.read_text()),json.loads(a.qualification.read_text()),json.loads(a.audit.read_text()),a.root)
    if a.output.exists():raise ValueError('IDENTITY_LABEL_TIME_OUTPUT_IMMUTABLE')
    a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='labels'},ensure_ascii=False))
