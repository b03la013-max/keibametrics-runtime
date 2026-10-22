"""Private Work transport for the existing registered URW calculation path.

No model, selector, Engine, capital policy, registration or ledger is rewritten.
The ordinary entry can prepare an artifact, but only actual private byte
readback admits its publication. A local completion is never delivery proof.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import fcntl
import gzip
import hashlib
from itertools import combinations, permutations
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from types import SimpleNamespace
from zipfile import ZipFile, ZIP_DEFLATED

from runtime.urw_nankan_reference_source import (
    parse_card, parse_program, verify_history_asof, private_directory,
    private_lock, save_json, immutable)
from runtime.urw_paper_selection import POLICY, sha, _check_sha, canonical_tickets, select_portfolio
from runtime.local_nar_evidence_candidate import compile_parsed_candidate_evidence
from runtime.local_fullnumerical_candidate import materialize_candidate
from runtime.local_race_key_shadow_owner import predict_conditioned_owner, URW_CANON
from runtime.local_krs_bridge_candidate import build_candidate_krs
from runtime.krs_prediction_utility import build_krs_prediction_utility
from runtime.jra_ticket_tree_renderer import render_ticket_tree
from scripts.urw_candidate_krs_replay import parsed_owner_feature_pack, freeze_owner_forward_comparison
from scripts import urw_paper_selection_replay as registered

ENGINE='9929df994aa7964173edef9af7e9a705628ce377babf22df3af4e280fc275421'
PARAMETERS='d8c027ee5bcc8fd3d2c248e8059b341776be38910e833d7589f09ab817c161f5'
ARMS=('BASELINE','CANDIDATE')
METHODS=('P0S1','P0S1_NO_KRS','TOP4_BOX_DIAGNOSTIC')
ROOT=Path(__file__).resolve().parents[1]

def read(path): return json.loads(Path(path).read_text())
def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def now(): return datetime.now(timezone.utc)
def seal(value):
    body={k:v for k,v in value.items() if k!='sha256'}
    return {**body,'sha256':sha(body)}

def configuration(path):
    path=Path(path);private_directory(path.parent)
    if path.is_symlink() or path.stat().st_mode&0o077:raise ValueError('PAPER_CONNECTION_PRIVATE_CONFIG')
    c=read(path);reg=read(c['registration']);_check_sha(reg)
    if (type(c.get('seed')) is not int or type(c.get('runs')) is not int
            or c['runs']!=5000 or c['seed']<0):raise ValueError('PAPER_EXISTING_SIMULATION_CONTRACT')
    if (reg['code_sha256']!=registered.code_pins() or reg['policy']!=POLICY
            or reg['policy_sha256']!=sha(POLICY)):raise ValueError('PAPER_REGISTERED_CODE_OR_POLICY_CHANGED')
    if digest(c['engine'])!=ENGINE or digest(c['parameters'])!=PARAMETERS:
        raise ValueError('PAPER_PINNED_ENGINE_OR_PARAMETERS')
    models=read(c['model_bundle'])['models']
    for arm in ARMS:
        _check_sha(models[arm])
        if models[arm]['sha256']!=reg['models'][arm]:raise ValueError('PAPER_REGISTERED_MODEL_CHANGED')
    private_directory(c['store'])
    return c,reg,models

def source_observation(source_root, day, number):
    root=Path(source_root);folder=root/f'sources/R{number:02}'
    evidence=read(folder/'reference_evidence.json');_check_sha(evidence)
    race=evidence['race'];receipt=read(folder/'card.receipt.json');raw=(folder/'card.raw.html').read_bytes()
    provider_id=race.get('provider_race_id','')
    observed=datetime.fromisoformat(receipt['fetched_at'])
    if (observed.tzinfo is None or observed>now()
            or observed>=datetime.fromisoformat(race['prediction_cutoff'])):
        raise ValueError('PAPER_SOURCE_NOT_AVAILABLE_BEFORE_CUTOFF')
    if (race.get('race_date')!=day or race.get('race_no')!=number or race.get('venue_id')!='URW'
            or not provider_id.startswith(day.replace('-','')+'18') or not provider_id.endswith(f'{number:02}')
            or receipt['raw_sha256']!=hashlib.sha256(raw).hexdigest()
            or receipt not in evidence['sources'] or receipt.get('http_status')!=200
            or receipt.get('source_policy',{}).get('usage_scope')!='USER_PERSONAL_NONCOMMERCIAL_PRIVATE_ONLY_NOT_PUBLIC_REDISTRIBUTION'):
        raise ValueError('PAPER_SOURCE_RAW_RECEIPT_OR_RACE_IDENTITY')
    facts=parse_card(raw,race,receipt['url']);verify_history_asof(facts,receipt['fetched_at'])
    if facts!=evidence['runners']:raise ValueError('PAPER_RAW_PARSE_DIFFERS_FROM_SAVED_FACTS')
    ids=[f['runner_id'] for f in facts]
    if len(ids)!=len(set(ids)):raise ValueError('PAPER_DUPLICATE_DECLARED_RUNNER')
    program=(root/'program/program.raw.html').read_bytes();pr=read(root/'program/program.receipt.json')
    if hashlib.sha256(program).hexdigest()!=pr['raw_sha256']:raise ValueError('PAPER_PROGRAM_RAW_RECEIPT')
    rows=parse_program(program,pr['url'],day)
    expected=next((r for r in rows if r['race_no']==number),None)
    if expected is None or any(expected[k]!=race[k] for k in ('provider_race_id','distance','program_runner_count','scheduled_post_at','prediction_cutoff')):
        raise ValueError('PAPER_PROGRAM_CARD_CONTEXT')
    return {'race':race,'facts':facts,'source':receipt,'active_verified':False,'signed_source_claim':False}

def numerical(observation, race_id):
    """Thin fact transport into the byte-unchanged, shared 63-rule compiler."""
    o=observation;race={**o['race'],'class':o['race']['race_name'],'venue':'URW'}
    facts=[]
    for fact in o['facts']:
        if fact['status']!='ACTIVE_DECLARED':continue
        row=copy.deepcopy(fact)
        row.update(race_card_source_id='NANKAN-CARD:'+race['provider_race_id'],
            race_card_snapshot_sha256=o['source']['raw_sha256'],race_card_fetched_at=o['source']['fetched_at'])
        facts.append(row)
    if len(facts)<3:raise ValueError('PAPER_INSUFFICIENT_DECLARED_RUNNERS')
    req={'family_id':'LOCAL','venue_id':'URW','provider':'NANKAN_OFFICIAL','race_id':race_id,'race':race,
        'runners':[{'runner_id':f['runner_id'],'name':f['name']} for f in facts],
        'production_authority':False,'signed_source_claim':False,'formal_source_claim':False,'active_verified':False,
        'input_observation':{'raw_sha256':o['source']['raw_sha256'],'source_fetched_at':o['source']['fetched_at'],'source_url':o['source']['url']}}
    source={'source_snapshot_sha256':o['source']['raw_sha256'],'source_freeze_at':o['source']['fetched_at'],'normalized_evidence':{}}
    n=materialize_candidate(compile_parsed_candidate_evidence(source,req,{f['runner_id']:f for f in facts}))
    n=seal({k:v for k,v in n.items() if k!='sha256'})
    s=n['candidate_full_numerical_summary']
    if not s['numeric_transport_complete'] or s['terminalized_count']!=len(facts)*29 or s['unresolved_count']:
        raise ValueError('PAPER_FULL29_NOT_TERMINAL')
    return n

def original_portfolio(pred):
    template={'semantic_request':{'family_id':'LOCAL','race_id':pred['race_id'],
        'runners':[{'runner_id':x} for x in pred['ranking']],
        'capital_policy':{'mode':'HARD_RACE_BUDGET','max_race_capital':0,'insufficient_action':'PAPER'}}}
    return registered._research_mec(pred,template)

def krs_input(n,pred,*,seed,runs):
    rows=copy.deepcopy(n['runners'])
    for row in rows:row['candidate_static_roles']=pred['role_columns'][str(row['runner_id'])]
    race={**n['race'],'prediction_id':n['race_id'],'racecourse':'浦和','date':n['race']['race_date'],
          'course_rule_version':URW_CANON,'surface':'dirt','course':'left'}
    return build_candidate_krs({**n,'race':race,'runners':rows,'seed':seed,'run_count':runs})['candidate_krs_input_data']

def simulate(folder, c, data, race_id, number, day):
    inp=folder/'krs.input.json';out=folder/'krs.output.json';receipt=folder/'engine.receipt.json'
    save_json(inp,data)
    if receipt.exists():
        r=read(receipt);_check_sha(r)
        if r['input_sha256']!=sha(data) or r['output_file_sha256']!=digest(out):raise ValueError('PAPER_ENGINE_REUSE_BINDING')
        return read(out),r
    if any((folder/name).exists() for name in ('engine.log','krs.output.json','krs.csv')):
        raise ValueError('PAPER_INTERRUPTED_ENGINE_ATTEMPT_PRESERVED_NO_DUPLICATE_RUN')
    start=now();wall=time.monotonic()
    with (folder/'engine.log').open('x') as log:
        subprocess.run([sys.executable,c['engine'],str(inp),'--output',str(out),'--csv',str(folder/'krs.csv'),
            '--params',c['parameters'],'--runs',str(c['runs']),'--seed',str(c['seed']),'--short'],
            stdout=log,stderr=subprocess.STDOUT,timeout=300,check=True)
    output=read(out);s=output['snapshot']
    if (s.get('prediction_id')!=race_id or s.get('date')!=day or s.get('race_no')!=number
            or s.get('run_count')!=c['runs'] or s.get('master_seed')!=c['seed']
            or {str(r['horse_no']) for r in output['summary']}!={str(r['horse_no']) for r in data['horses']}):
        raise ValueError('PAPER_ENGINE_SNAPSHOT_OR_UNIVERSE')
    r=seal({'started_at':start.isoformat(),'completed_at':now().isoformat(),'wall_seconds':time.monotonic()-wall,
        'engine_sha256':ENGINE,'parameter_map_sha256':PARAMETERS,'input_sha256':sha(data),
        'output_file_sha256':digest(out),'run_count':c['runs'],'master_seed':c['seed'],
        'external_signed_receipt':False,'actual_engine_executed':True})
    save_json(receipt,r);return output,r

def tree(pred,tickets):
    result=render_ticket_tree({'static_prediction':{'ranking':pred['ranking']},
        'final_ticket':{'tickets':tickets,'no_bet':not tickets},'capital_policy_decision':{'decision':'PAPER'}})
    if canonical_tickets(result['reflattened_tickets'])!=canonical_tickets(tickets):raise ValueError('PAPER_DELIVERY_TREE_MISMATCH')
    return result

def prepare(config_path, intent):
    os.umask(0o077)
    c,reg,models=configuration(config_path);day=intent['race_date'];number=intent['race_no']
    obs=source_observation(c['source_root'],day,number)
    cutoff=datetime.fromisoformat(obs['race']['prediction_cutoff']);diagnostic=now()>=cutoff
    if diagnostic and not c.get('allow_postcutoff_diagnostic'):raise ValueError('PAPER_PAST_CUTOFF_NO_NEW_FORWARD')
    # Live operation cannot skip the existing whole-day/checkpoint admission.
    if not diagnostic:
        if c.get('current_v2_live_ledger_latestness')!='INDEPENDENT_PRIVATE_READBACK_VERIFIED':
            raise ValueError('PAPER_CURRENT_LIVE_LEDGER_LATESTNESS_NOT_VERIFIED')
        if not Path(reg['canonical_ledger_path']).is_dir():
            raise ValueError('PAPER_CURRENT_CANONICAL_LEDGER_NOT_RESTORED')
        ledger=registered._registered_context(reg)
        registered._verify_checkpoint(reg,ledger,SimpleNamespace(ledger_checkpoint=Path(c['checkpoint']),expected_checkpoint_sha256=c['checkpoint_sha256']))
        day_record=read(ledger/f'day-{day}.json');_check_sha(day_record)
        if day_record['registration_sha256']!=reg['sha256']:raise ValueError('PAPER_DAY_REGISTRATION')
    request_key=sha({'date':day,'number':number,'registration':reg['sha256'],'source':obs['source']['raw_sha256'],
        'caller':digest(__file__),'seed':c['seed'],'runs':c['runs'],'classification':'DIAGNOSTIC' if diagnostic else 'FORWARD'})
    folder=private_directory(Path(c['store'])/'races'/day/f'R{number:02}'/request_key)
    with private_lock(folder/'request.lock') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        if (folder/'complete.json').exists():return read(folder/'complete.json')
        race_id=f'KM-LOCAL-URW-{day.replace("-","")}-R{number:02}-'+('DIAGNOSTIC' if diagnostic else 'FORWARD-RESEARCH')+'-R1'
        save_json(folder/'source-observation.json',obs)
        npath=folder/'numerical.json'
        if not npath.exists():save_json(npath,numerical(obs,race_id))
        n=read(npath);_check_sha(n);pack=parsed_owner_feature_pack(n)
        compath=folder/'comparison.json'
        if not compath.exists():
            if diagnostic:
                predictions={a:predict_conditioned_owner(m,pack,historical_replay=True) for a,m in models.items()}
                comparison=seal({'classification':'POSTCUTOFF_DIAGNOSTIC_NOT_A_PRESTART_FREEZE','race_id':race_id,
                    'race_date':day,'scheduled_post_at':obs['race']['scheduled_post_at'],'prediction_cutoff':cutoff.isoformat(),
                    'created_at':now().isoformat(),'feature_pack':pack,'models':models,'predictions':predictions,
                    'protocol':reg['existing_owner_protocol_unchanged'],'production_authority':False,'forward_oos_credit':0})
                save_json(compath,comparison)
            else:freeze_owner_forward_comparison(pack,models['BASELINE'],models['CANDIDATE'],protocol=reg['existing_owner_protocol_unchanged'],output=compath)
        comparison=read(compath);_check_sha(comparison);arms={};audits={}
        for arm in ARMS:
            af=private_directory(folder/arm);pred=comparison['predictions'][arm];original=original_portfolio(pred)
            data=krs_input(n,pred,seed=c['seed'],runs=c['runs']);output,er=simulate(af,c,data,race_id,number,day)
            utility=build_krs_prediction_utility(original['semantic_request'],{'status':'EXECUTED','output':output})
            ref={'original_prediction_sha256':pred['sha256'],'original_comparison_sha256':comparison['sha256'],
                'immutable_original_mec_sha256':original['mec']['sha256'],'immutable_semantic_sha256':sha(original['semantic_request']),
                'krs_utility_sha256':utility['sha256'],'krs_snapshot_sha256':sha(utility['snapshot']),
                'krs_master_seed':c['seed'],'krs_input_sha256':sha(data),'krs_output_file_sha256':er['output_file_sha256']}
            ts=canonical_tickets(original['mec']['tickets']);inactive=[f['runner_id'] for f in obs['facts'] if f['status']!='ACTIVE_DECLARED']
            selected=select_portfolio(pred,ts,source_ref=ref,krs_utility=utility,excluded_runner_ids=inactive)
            off=select_portfolio(pred,ts,source_ref=ref,excluded_runner_ids=inactive)
            ranked=[h for h in pred['ranking'] if h not in inactive][:4]
            top4=canonical_tickets([{'bet_type':'EXACTA','selection':list(map(int,x)),'stake':100} for x in permutations(ranked,2)]+
                [{'bet_type':'TRIO','selection':list(map(int,x)),'stake':100} for x in combinations(ranked,3)])
            methods={'P0S1':{'selection':selected,'tickets':selected['selected_tickets']},
                'P0S1_NO_KRS':{'selection':off,'tickets':off['selected_tickets']},'TOP4_BOX_DIAGNOSTIC':{'tickets':top4}}
            for value in methods.values():value['tree']=tree(pred,value['tickets'])
            audits[arm]=seal({'race_id':race_id,'source_snapshot_sha256':obs['source']['raw_sha256'],
                'reference_static':pred,'master_seed':c['seed'],'started_at':er['started_at'],'completed_at':er['completed_at'],
                'snapshot':output['snapshot'],'semantic_request':original['semantic_request'],'mec':original['mec'],
                'krs_utility':utility,'krs_input_sha256':sha(data),'krs_output_file_sha256':er['output_file_sha256'],
                'ticket_tree':tree(pred,ts),'production_authority':False})
            arms[arm]={'prediction':pred,'original_mec':original,'engine_receipt':er,'krs_utility':utility,'methods':methods}
        forward=None
        if not diagnostic:
            # The registered writer, not this transport, owns reservation/day budgets.
            bundle=folder/'forward-input.json';save_json(bundle,{'frozen':comparison,'audits':audits,'observation':obs})
            forward=private_directory(folder/'registered-freeze')
            existing=forward/'research-selection-freeze.json'
            if existing.exists():
                old=read(existing);_check_sha(old)
                events=registered._ledger_events(reg,Path(reg['canonical_ledger_path']))
                matching=[e for e in events if e.get('artifact_sha256')==old['sha256']
                    and e.get('status')=='FROZEN_PENDING_INDEPENDENT_ANCHOR']
                if len(matching)!=1 or old['input_bundle_sha256']!=sha(read(bundle)):
                    raise ValueError('PAPER_ORPHAN_FORWARD_ARTIFACT_NOT_ADMITTED')
            else:
                registered.freeze(SimpleNamespace(registration=Path(c['registration']),ledger=Path(reg['canonical_ledger_path']),
                    ledger_checkpoint=Path(c['checkpoint']),expected_checkpoint_sha256=c['checkpoint_sha256'],input_bundle=bundle,output=forward))
            accepted=read(forward/'research-selection-freeze.json')
            for arm in ARMS:
                view=accepted['views'][arm]
                for method,key in (('P0S1','P0S1'),('P0S1_NO_KRS','P0S1_NO_KRS')):
                    s=view['cells'][key]['selection'] if method=='P0S1' else view[key]
                    arms[arm]['methods'][method]={'selection':s,'tickets':s['selected_tickets'],'tree':tree(arms[arm]['prediction'],s['selected_tickets'])}
            registered.checkpoint(SimpleNamespace(registration=Path(c['registration']),output=folder/'checkpoint-after.json'))
        artifact=seal({'classification':'POSTCUTOFF_DIAGNOSTIC_NOT_FORWARD' if diagnostic else 'REGISTERED_FORWARD_PAPER_PENDING_PRIVATE_SAVE',
            'race_id':race_id,'provider_race_id':obs['race']['provider_race_id'],'race_date':day,'race_no':number,
            'created_at':now().isoformat(),'prediction_cutoff':cutoff.isoformat(),'registration_sha256':reg['sha256'],
            'registered_head':reg['registered_head'],'caller_sha256':digest(__file__),'source':obs['source'],'race':obs['race'],
            'numerical':n,'comparison':comparison,'arms':arms,'production_authority':False,'signed_final_claim':False,
            'forward_oos_credit':0,'private_storage_required':True,'public_redistribution_authorized':False,'actual_purchase':False,
            'original_v2_ledger_mutated':not diagnostic,'current_active_verified':False,
            'source_latest_change_check':'NOT_PERFORMED_SAVED_ASOF_ONLY','formal_quality_credit':0})
        save_json(folder/'calculation.json',artifact)
        body=render(artifact);immutable(folder/'readback.txt',body.encode())
        archive=folder/'private-artifact.zip'
        files=[p for p in folder.rglob('*') if p.is_file() and p.name not in ('request.lock','private-artifact.zip')]
        manifest={str(p.relative_to(folder)):{'bytes':p.stat().st_size,'sha256':digest(p)} for p in files}
        with ZipFile(archive,'x',compression=ZIP_DEFLATED) as z:
            for p in files:z.write(p,str(p.relative_to(folder)))
            z.writestr('BYTE_MANIFEST.json',json.dumps(manifest,ensure_ascii=False,sort_keys=True))
        result=seal({'status':'PRIVATE_SAVE_REQUIRED','race_id':race_id,'race_date':day,'race_no':number,
            'folder':str(folder),'archive':str(archive),'archive_sha256':digest(archive),'artifact_sha256':artifact['sha256'],
            'answer_sha256':digest(folder/'readback.txt'),'classification':artifact['classification'],
            'completed_at':now().isoformat(),'chat_render_verified':False,'user_received':False})
        save_json(folder/'complete.json',result);return result

def render(artifact):
    a=artifact;n=a['numerical'];s=n['candidate_full_numerical_summary'];b=a['arms']['BASELINE'];c=a['arms']['CANDIDATE']
    names={str(r['runner_id']):r['name'] for r in n['runners']}
    lines=[f"浦和{a['race_no']}R｜{a['race_date']}｜{a['classification']}",
        f"Provider {a['provider_race_id']} / Race {a['race_id']}",
        f"計算保存時刻 {a['created_at']} / 参考Cutoff {a['prediction_cutoff']}",
        f"SOURCE原取得 {a['source']['fetched_at']}。現在の取消・除外・馬体重は未検証。Verified Activeではありません。",
        'FORMAL HOLD。期限後の新計算はDiagnosticであり、事前予測・正式FINAL・未知未来OOSに算入しません。' if a['classification'].startswith('POSTCUTOFF') else 'REGISTERED PAPER / 非Production。正式署名・購入認可ではありません。',
        f"全{len(names)}頭×29={s['required_count']}セル：実計算{s['calculated_count']}、規則中立{s['ruled_neutral_count']}、未解決{s['unresolved_count']}。",
        '全馬登録モデル評価（UNKNOWNは観測不足であり能力不足ではありません）',
        '|馬番・馬名|B順位|C順位|B Role|C Role|欠測|','|---|---:|---:|---|---|---|']
    for rid in sorted(names,key=int):
        pb=b['prediction'];pc=c['prediction']
        lines.append(f"|{rid} {names[rid]}|{pb['ranking'].index(rid)+1}|{pc['ranking'].index(rid)+1}|{','.join(pb['role_columns'][rid]) or '—'}|{','.join(pc['role_columns'][rid]) or '—'}|UNKNOWN {len(pb['missingness'][rid])}項目|")
    lines+=['研究6系列は独立会計。6案の合算を購入推奨としません。単位100円、1系列上限2,000円。',
            '|Owner / 方式|点数|仮想額|状態|','|---|---:|---:|---|']
    for arm in ARMS:
        for method in METHODS:
            m=a['arms'][arm]['methods'][method];count=len(m['tickets']);stake=sum(t['stake'] for t in m['tickets'])
            lines.append(f"|{arm}/{method}|{count}|{stake}円|{'NO-BET' if not count else '計算済・研究票'}|")
    for arm in ARMS:
        x=a['arms'][arm];pred=x['prediction'];er=x['engine_receipt'];u=x['krs_utility']
        lines.append(f"\n{arm}｜W/P2/P3")
        for role in ('W','P2','P3'):lines.append(role+' = '+','.join(h for h in pred['rankings_by_role'][role] if role in pred['role_columns'][h]))
        lines.append(f"KRS {er['run_count']}回 / seed {er['master_seed']} / 実完了 {er['completed_at']}")
        lines.append('SSR-W / SSR-P2 / SSR-P3（未較正のシミュレーション支持値。実勝率・EVではない）')
        for row in sorted(u['summary'],key=lambda r:int(r['horse_no'])):
            lines.append(f"{row['horse_no']}: {row['SSR-W']:.4f} / {row['SSR-P2']:.4f} / {row['SSR-P3']:.4f}")
        for method in METHODS:
            m=x['methods'][method];lines.append('\n'+arm+' / '+method+'｜全選択票・各Stake')
            lines.append(m['tree']['text'])
            if 'selection' in m:
                se=m['selection'];lines.append(f"Core/Protection={se['tier_spend_yen']} / 未使用{se['unused_budget_yen']}円 / NO-BET理由={se['no_bet_reason']}")
    lines+=['\n最終結論：登録済みモデル・既存選択Policyによる計算結果です。購入推奨・性能合格ではありません。',
        '全29指数・各Provenance・非選択票・完全KRSは同一の私有原本に保存。',
        '登録ID '+a['registration_sha256'],'原本Artifact SHA '+a['sha256'],'SOURCE Raw SHA '+a['source']['raw_sha256']]
    return '\n'.join(lines)+'\n'

def publish(config_path, complete_path, readback_zip, storage_receipt_path):
    c,reg,_=configuration(config_path);complete=read(complete_path);_check_sha(complete)
    folder=Path(complete['folder']);private_directory(folder)
    if digest(readback_zip)!=complete['archive_sha256'] or digest(complete['archive'])!=complete['archive_sha256']:
        raise ValueError('PAPER_EXTERNAL_READBACK_BYTE_MISMATCH')
    receipt=read(storage_receipt_path)
    if not receipt.get('storage_id') or not receipt.get('provider_created_at') or receipt.get('readback_sha256')!=digest(readback_zip):
        raise ValueError('PAPER_EXTERNAL_STORAGE_RECEIPT_MISSING')
    with ZipFile(readback_zip) as z:
        manifest=json.loads(z.read('BYTE_MANIFEST.json'))
        if set(z.namelist())!=set(manifest)|{'BYTE_MANIFEST.json'}:raise ValueError('PAPER_REMOTE_ARCHIVE_MEMBERS')
        for name,ref in manifest.items():
            raw=z.read(name)
            if len(raw)!=ref['bytes'] or hashlib.sha256(raw).hexdigest()!=ref['sha256']:raise ValueError('PAPER_REMOTE_ARCHIVE_BYTES')
        artifact=json.loads(z.read('calculation.json'));_check_sha(artifact)
        if artifact['sha256']!=complete['artifact_sha256'] or z.read('readback.txt')!=(folder/'readback.txt').read_bytes():
            raise ValueError('PAPER_REMOTE_CALCULATION_OR_ANSWER_MISMATCH')
        if not artifact['classification'].startswith('POSTCUTOFF'):
            if (datetime.fromisoformat(receipt['provider_created_at'])>=datetime.fromisoformat(artifact['prediction_cutoff'])
                    or now()>=datetime.fromisoformat(artifact['prediction_cutoff'])):
                raise ValueError('PAPER_EXTERNAL_SAVE_OR_READBACK_AFTER_CUTOFF')
            if 'checkpoint-after.json' not in manifest:raise ValueError('PAPER_UPDATED_CHECKPOINT_MISSING')
    checkpoint_sha=(manifest['checkpoint-after.json']['sha256']
                    if not artifact['classification'].startswith('POSTCUTOFF') else c['checkpoint_sha256'])
    pub=seal({**complete,'status':'VERIFIED_PRIVATE_RESEARCH_READBACK','storage':receipt,
        'registration_sha256':reg['sha256'],'private_storage_required':True,'public_redistribution_authorized':False,
        'checkpoint_file_sha256':checkpoint_sha,
        'checkpoint_scope':'INITIAL_SNAPSHOT_NOT_CURRENT_LIVE_LEDGER' if artifact['classification'].startswith('POSTCUTOFF') else 'UPDATED_CHECKPOINT_INCLUDED_IN_READBACK_ARCHIVE',
        'published_at':now().isoformat(),'formal_final_proven':False,'forward_oos_credit':0})
    dest=private_directory(Path(c['store'])/'publications'/complete['race_date']/f"R{complete['race_no']:02}")
    save_json(dest/(complete['artifact_sha256']+'.json'),pub)
    return pub

def read_delivery(config_path,intent):
    c,reg,_=configuration(config_path);root=Path(c['store'])/'publications'/intent['race_date']/f"R{intent['race_no']:02}"
    rows=[]
    for p in root.glob('*.json'):
        pub=read(p);_check_sha(pub)
        if pub['registration_sha256']!=reg['sha256'] or pub['race_no']!=intent['race_no'] or pub['race_date']!=intent['race_date']:
            raise ValueError('PAPER_CATALOG_RACE_OR_REGISTRATION_MIX')
        folder=Path(pub['folder']);private_directory(folder)
        if not folder.resolve().is_relative_to((Path(c['store'])/'races'/intent['race_date']/f"R{intent['race_no']:02}").resolve()):
            raise ValueError('PAPER_CATALOG_FOLDER_OUTSIDE_RACE_STORE')
        if digest(folder/'readback.txt')!=pub['answer_sha256']:raise ValueError('PAPER_CATALOG_ANSWER_SHA')
        artifact=read(folder/'calculation.json');_check_sha(artifact)
        if artifact['sha256']!=pub['artifact_sha256']:raise ValueError('PAPER_CATALOG_ARTIFACT_SHA')
        if artifact['classification'].startswith('POSTCUTOFF') and now()<datetime.fromisoformat(artifact['prediction_cutoff']):continue
        # Re-expand every independent portfolio before displaying any body.
        for arm in ARMS:
            for method in METHODS:
                m=artifact['arms'][arm]['methods'][method]
                if tree(artifact['arms'][arm]['prediction'],m['tickets'])!=m['tree']:raise ValueError('PAPER_CATALOG_TREE_CHANGED')
        rows.append(pub)
    if not rows:return None
    # A later diagnostic must not replace a valid pre-cutoff registered freeze.
    pub=max(rows,key=lambda r:(not r['classification'].startswith('POSTCUTOFF'),r['published_at']))
    body=(Path(pub['folder'])/'readback.txt').read_text()
    if pub['storage'].get('url'):body+='\n本人用完全原本：'+pub['storage']['url']+'\n'
    return {**pub,'body':body,'execution_id':pub['race_id'],
        'prediction_reexecution':False,'answer_required_parts':[body],
        'delivery':{'chat_render_verified':False,'user_acknowledgement_verified':False}}

def main():
    os.umask(0o077);p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',required=True)
    sub=p.add_subparsers(dest='action',required=True)
    for name in ('prepare','read'):
        q=sub.add_parser(name);q.add_argument('--query',required=True)
    q=sub.add_parser('publish');q.add_argument('--complete',required=True);q.add_argument('--readback',required=True);q.add_argument('--receipt',required=True)
    a=p.parse_args()
    if a.action=='publish':result=publish(a.config,a.complete,a.readback,a.receipt)
    else:
        from runtime.local_race_entry import resolve_chat_intent
        intent=resolve_chat_intent(a.query)
        result=prepare(a.config,intent) if a.action=='prepare' else read_delivery(a.config,intent)
    print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':main()
