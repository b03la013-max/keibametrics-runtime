"""Private historical SOURCE -> existing 29 indices -> fixed owners audit.

No SOURCE acquisition, KRS execution, signing, formal activation or purchase.
Result labels, when supplied, are used only after all prediction artifacts.
"""
from __future__ import annotations
import argparse, hashlib, json, sys, os
from pathlib import Path
from datetime import datetime


def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def run(index_path, original_root, output, compiler_root, model_path):
    index_path=Path(index_path).resolve();original_root=Path(original_root).resolve()
    compiler_root=Path(compiler_root).resolve();model_path=Path(model_path).resolve()
    sys.path[:0]=[str(compiler_root),str(Path(compiler_root)/'runtime')]
    from runtime import ohi_single_race_research as m
    for name,module in list(sys.modules.items()):
        if (name=='runtime' or name.startswith('runtime.')) and getattr(module,'__file__',None):
            if not Path(module.__file__).resolve().is_relative_to(compiler_root):
                raise ValueError('AUDIT_COMPILER_IMPORT_ROOT_MISMATCH:'+name)
    os.chdir(compiler_root)
    dest=m.private_root(output)
    if dest.exists():raise ValueError('IMMUTABLE_AUDIT_OUTPUT_ALREADY_EXISTS')
    dest.mkdir(parents=True,mode=0o700)
    index=json.loads(Path(index_path).read_text());base=Path(original_root)
    entries=index['rows']
    if (len(entries)!=12 or {e['race_no'] for e in entries}!=set(range(1,13))
            or len({e['race_id'] for e in entries})!=12 or len({e['revision'] for e in entries})!=12):
        raise ValueError('AUDIT_FIXED_12R_INDEX_UNIVERSE')
    model=json.loads(Path(model_path).read_text())
    if model['sha256']!=m.MODEL or digest({k:v for k,v in model.items() if k!='sha256'})!=m.MODEL:
        raise ValueError('FIXED_MODEL_MISMATCH')
    rows=[];calculated=neutral=unresolved=0;diffs=[];fixed_files={}
    for entry in index['rows']:
        folder=base/entry['revision'];source=folder.with_name(folder.name+'.source')
        immutable={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [*folder.rglob('*'),*source.rglob('*')] if p.is_file()}
        original,_=m.readback(folder)
        if original['sha256']!=entry['prediction_sha256']:raise ValueError('INDEX_PREDICTION_SHA')
        if (original['race']['provider_race_id']!=entry['race_id']
                or original['race']['race_no']!=entry['race_no']
                or original['race']['venue_id']!='OHI'
                or original['race']['race_date']!=index['race_date']):
            raise ValueError('AUDIT_INDEX_RACE_IDENTITY')
        if (entry['classification']!=original['classification']
                or original['classification']!=m.CLASS):
            raise ValueError('AUDIT_INDEX_CLASSIFICATION')
        observation=json.loads((folder/'observation.json').read_text())
        if (observation['race']!=original['race'] or observation['sha256']!=original['source_sha256']
                or entry['source_sha256']!=original['source_sha256']):
            raise ValueError('AUDIT_ORIGINAL_SOURCE_BINDING')
        frozen=datetime.fromisoformat(original['freeze_at']);cutoff=datetime.fromisoformat(original['race']['prediction_cutoff'])
        if frozen.tzinfo is None or cutoff.tzinfo is None or frozen>=cutoff:
            raise ValueError('AUDIT_ORIGINAL_FREEZE_CUTOFF')
        for receipt in observation['receipts']:
            stamp=datetime.fromisoformat(receipt['fetched_at'])
            if stamp.tzinfo is None or stamp>frozen or stamp>=cutoff:
                raise ValueError('AUDIT_SOURCE_AFTER_FREEZE_OR_CUTOFF')
        m.verify_observation(observation,source)
        n=m.numerical(observation,'OHI-'+entry['race_id']+'-PRIVATE-R1')
        summary=n['candidate_full_numerical_summary']
        calculated+=summary['calculated_count'];neutral+=summary['ruled_neutral_count'];unresolved+=summary['unresolved_count']
        for horse in n['runners']:
            rid=horse['runner_id']
            for key,cell in horse['canonical_components'].items():
                old=original['numerical_cells'][rid][key]
                if cell['value']!=old['value'] or cell['terminal_status']!=old['terminal_status']:
                    diffs.append({'race_no':entry['race_no'],'runner_id':rid,'name':horse['name'],'index':key,
                        'before':old['value'],'after':cell['value'],'before_status':old['terminal_status'],'after_status':cell['terminal_status'],
                        'source_sha256':observation['sha256'],'cell_evidence_refs':cell.get('evidence_refs'),
                        'cell_components':cell.get('components')})
        baseline=m.build_candidate_prediction_structure_derived(n)['candidate_static_prediction']
        pack=m.feature_pack(observation,n,baseline,model,'OHI-'+entry['race_id']+'-PRIVATE-R1')
        candidate=m.predict_conditioned_owner(model,pack,historical_replay=True)
        owners={'BASELINE':baseline,'OHI_FIXED_CANDIDATE':candidate}
        portfolios={owner:m.selection(observation,pred,'OHI-'+entry['race_id']+'-PRIVATE-R1') for owner,pred in owners.items()}
        race_dir=dest/f"r{entry['race_no']:02d}";race_dir.mkdir()
        for name,value in [('numerical',n),('features',pack),('owners',owners),('portfolios',portfolios)]:
            m.write(race_dir/(name+'.json'),value)
        rows.append({'race_no':entry['race_no'],'provider_race_id':entry['race_id'],'source_sha256':observation['sha256'],
            'original_prediction_sha256':original['sha256'],'original_freeze':original['freeze_at'],
            'original_cutoff':original['race']['prediction_cutoff'],'source_fetched_at':original['source_fetched_at'],
            'raw_reparsed':True,'runner_count':len(n['runners']),'summary':summary,
            'owner_changes':{owner:{'ranking_changed':pred['ranking']!=original['owners'][owner]['ranking'],
                'roles_changed':(pred.get('roles') or pred.get('role_columns'))!=(original['owners'][owner].get('roles') or original['owners'][owner].get('role_columns')),
                'selected_ticket_count':len(portfolios[owner]['tickets']),
                'original_selected_ticket_count':len(original['portfolios'][owner]['tickets']),
                'no_bet':portfolios[owner]['capital']['no_bet'],
                'selected_ticket_keys_sha256':digest(portfolios[owner]['tickets'])} for owner,pred in owners.items()}})
        if immutable!={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in immutable}:raise ValueError('FROZEN_ORIGINAL_MUTATED')
        fixed_files.update(immutable)
    paths=['runtime/local_nar_evidence_candidate.py','runtime/local_fullnumerical_candidate.py','runtime/local_fullnumerical_production.py',
        'mapping/local_evidence_feature_rule_registry_v0.1_candidate_20260923.json','mapping/local_full_numerical_mapping_v0.1_candidate_20260923.json']
    report={'classification':'HISTORICAL_INFORMATION_QUALITY_DIAGNOSTIC_NOT_FORWARD_NOT_FORMAL',
        'races':len(rows),'runners':sum(r['runner_count'] for r in rows),'calculated':calculated,'neutral':neutral,'unresolved':unresolved,
        'rows':rows,'numerical_differences_from_frozen':diffs,'production_authority':False,'registered_oos_credit':0,
        'source_acquisitions':0,'krs_reexecutions':0,'actual_investment':0,'new_model_or_policy':False,
        'fixed_model_sha256':m.MODEL,'compiler_file_sha256':{p:hashlib.sha256((Path(compiler_root)/p).read_bytes()).hexdigest() for p in paths},
        'original_files_unchanged':True,'original_file_count':len(fixed_files),'original_files_sha256':digest(fixed_files)}
    report['sha256']=digest(report);m.write(dest/'acceptance.json',report)
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('index','original-root','output','compiler-root','model'):p.add_argument('--'+name,required=True)
    a=p.parse_args();r=run(a.index,a.original_root,a.output,a.compiler_root,a.model)
    print(json.dumps({k:r[k] for k in ('sha256','races','runners','calculated','neutral','unresolved')}))

if __name__=='__main__':main()
