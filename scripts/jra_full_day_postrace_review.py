"""Reproducible, analysis-only JRA day audit over immutable artifacts.

No network, signing, dispatch, prediction recomputation, or policy writes.
Official collection is a separate read-only command. Missing evidence stays missing.
"""
from __future__ import annotations
import argparse, base64, csv, hashlib, json, re, statistics, subprocess, sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from bs4 import BeautifulSoup
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'runtime'), str(ROOT/'runtime/jra_source_runtime')]
from jra_delivery import verify_signed_final, canonical_bytes
from jra_source_runtime.verify_source_envelope import verify as verify_source
from krs_prediction_utility import evaluate_against_result
from jra_production_krs_contract import production_krs_payload

BASE = 'HPI SSI CFI RFI BVI JTI CSI TRI BWI GCI PRI KGI VMI'.split()
DERIVED = 'DCR TPI ZAI_WIN ZAI_PLACE SRI F3S T3I'.split()
BET = {'単勝':'WIN','複勝':'PLACE','枠連':'BRACKET_QUINELLA','馬連':'QUINELLA',
       'ワイド':'WIDE','馬単':'EXACTA','3連複':'TRIO','3連単':'TRIFECTA'}
UNORDERED = {'QUINELLA','WIDE','TRIO','BRACKET_QUINELLA'}
VENUE = {'04':'NGT','05':'TKY','08':'KYO'}

def read(p, default=None):
    return json.loads(p.read_text()) if p.exists() else default

def sha(obj):
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()

def write(p, obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+'\n')

def dt(s):
    return datetime.fromisoformat(s.replace('Z','+00:00')) if s else None

def text(node):
    return node.get_text(' ',strip=True) if node else ''

def nums(s):
    return [int(x) for x in re.findall(r'\d+',s)]

def parse_official(html, expected_date, expected_venue, race_no):
    soup=BeautifulSoup(html,'html.parser')
    date=text(soup.select_one('.date_line .date'))
    if expected_date.replace('-','年',1).split('年')[0]+'年' not in date:
        raise ValueError('OFFICIAL_DATE_MISMATCH')
    date_digits=nums(date)
    if date_digits[:3]!=[int(x) for x in expected_date.split('-')]:
        raise ValueError('OFFICIAL_DATE_MISMATCH')
    label={'NGT':'新潟','TKY':'東京','KYO':'京都'}[expected_venue]
    if label not in date: raise ValueError('OFFICIAL_VENUE_MISMATCH')
    number=soup.select_one('.race_number img')
    if number is None or nums(number.get('alt',''))!=[race_no]:
        raise ValueError('OFFICIAL_RACE_NUMBER_MISMATCH')
    table=next((t for t in soup.select('table') if t.select_one('thead .place') and t.select_one('thead .num')),None)
    if table is None: raise ValueError('OFFICIAL_FINISH_TABLE_MISSING')
    runners=[]
    for row in table.select('tbody > tr'):
        n=text(row.select_one('td.num')); finish=text(row.select_one('td.place'))
        if not n.isdigit():continue
        runners.append({'horse_no':int(n),'finish':int(finish) if finish.isdigit() else None,
                        'finish_status':finish,'name':text(row.select_one('td.horse')),
                        'time':text(row.select_one('td.time')),'margin':text(row.select_one('td.margin')),
                        'passing_positions':nums(text(row.select_one('td.corner'))),
                        'final_3f':text(row.select_one('td.f_time')),
                        'win_popularity':int(text(row.select_one('td.pop'))) if text(row.select_one('td.pop')).isdigit() else None,
                        'bodyweight':text(row.select_one('td.h_weight'))})
    finished=[x for x in runners if x['finish'] is not None]
    if len(finished)<3: raise ValueError('OFFICIAL_RESULT_INCOMPLETE')
    payouts={}
    for li in soup.select('.refund_unit li'):
        name=text(li.select_one('dt')); bt=BET.get(name)
        if not bt:continue
        entries=[]
        for line in li.select('.line'):
            sel=nums(text(line.select_one('.num')))
            yen=nums(text(line.select_one('.yen')).replace(',',''))
            if not sel and not yen:continue  # e.g. no bracket quinella for 8-runner fields
            if not sel or len(yen)!=1: raise ValueError('OFFICIAL_PAYOUT_PARSE_AMBIGUOUS:'+name)
            entries.append({'selection':sel,'per_100_yen':yen[0]})
        payouts[bt]=entries
    if not all(payouts.get(x) for x in ('WIN','PLACE','QUINELLA','WIDE','EXACTA','TRIO','TRIFECTA')):
        raise ValueError('OFFICIAL_SEVEN_BET_TYPES_INCOMPLETE')
    tables=[]
    for t in soup.select('table'):
        if t is not table: tables.append([[text(c) for c in row.select('th,td')] for row in t.select('tr')])
    # Keep the notice verbatim as evidence. Automatic refund settlement is held
    # whenever withdrawn runners/exceptional refund text requires adjudication.
    exceptional=[x for x in runners if x['finish'] is None]
    body=text(soup)
    return {'race_date':expected_date,'venue':expected_venue,'race_no':race_no,'date_heading':date,
            'conditions':text(table.select_one('caption')),'scheduled_post':text(soup.select_one('.date_line .time')),
            'environment':text(soup.select_one('.date_line .baba')),'runners':runners,
            'finish_order':[x['horse_no'] for x in finished],
            'top3':[x['horse_no'] for x in sorted(finished,key=lambda x:x['finish'])[:3]],
            'top3_display_order_is_not_unique':len({x['finish'] for x in sorted(finished,key=lambda x:x['finish'])[:3]})!=3,
            'dead_heat':len({x['finish'] for x in finished})!=len(finished),
            'payouts':payouts,'lap_and_corner_tables':tables,'exceptional_runners':exceptional,
            'refund_notice':text(soup.select_one('.refund_area')),
            'special_refund_detected':bool(re.search('返還|特払いとな|競走取りやめ',text(soup.select_one('.refund_unit')))),
            'official_result_acquisition':'VERIFIED_IDENTITY_AND_COMPLETE_PAYOUTS',
            'signed_result_receipt_verification':'SEPARATE_CHECK_REQUIRED'}

def normalize_selection(bt,selection):
    v=tuple(int(x) for x in selection)
    return tuple(sorted(v)) if bt in UNORDERED else v

def settle_tickets(tickets, official):
    rows=[];seen=set()
    for ticket in tickets:
        bt=ticket['bet_type'];sel=normalize_selection(bt,ticket['selection']);stake=ticket['stake']
        if bt not in BET.values():raise ValueError('UNSUPPORTED_BET_TYPE:'+bt)
        if not isinstance(stake,int) or isinstance(stake,bool) or stake<=0 or stake%100:
            raise ValueError('INVALID_STAKE')
        if len(sel)!=len(set(sel)):raise ValueError('DUPLICATE_RUNNER_IN_TICKET')
        key=(bt,sel)
        if key in seen:raise ValueError('DUPLICATE_CANONICAL_TICKET')
        seen.add(key)
        if any(x['finish_status'] in ('取消','除外') for x in official['exceptional_runners']) or official['special_refund_detected']:
            raise ValueError('REFUND_ADJUDICATION_REQUIRED')
        matches=[p for p in official['payouts'].get(bt,[]) if normalize_selection(bt,p['selection'])==sel]
        if len(matches)>1:raise ValueError('AMBIGUOUS_DUPLICATE_PAYOUT')
        ret=(matches[0]['per_100_yen']*stake//100) if matches else 0
        rows.append({**ticket,'investment':stake,'return':ret,'profit_loss':ret-stake,
                     'hit':bool(matches),'payout_match':matches[0] if matches else None})
    inv=sum(x['investment'] for x in rows);ret=sum(x['return'] for x in rows)
    return {'investment':inv,'return':ret,'profit_loss':ret-inv,'pfs':ret/inv*100 if inv else None,
            'hit':any(x['hit'] for x in rows),'hit_but_loss':bool(ret>0 and ret<inv),'tickets':rows}

def aggregate(rows):
    inv=sum(x['investment'] for x in rows);ret=sum(x['return'] for x in rows)
    return {'race_count':len(rows),'investment':inv,'return':ret,'profit_loss':ret-inv,
            'weighted_pfs':ret/inv*100 if inv else None}

def robust(rows):
    exposed=[x for x in rows if x['investment']>0]
    by_return=sorted(exposed,key=lambda x:(-x['return'],x['post'],x['race_id']))
    exclusions={}
    for n in (1,2,3):
        removed=by_return[:n];removedids={x['race_id'] for x in removed}
        exclusions[str(n)]={'definition':'Exclude entire races (both investment and return); ties: post then race_id',
                            'excluded_race_ids':[x['race_id'] for x in removed],
                            **aggregate([x for x in exposed if x['race_id'] not in removedids])}
    cum=peak=drawdown=streak=maxstreak=0;timeline=[]
    for x in sorted(exposed,key=lambda x:(x['post'],x['race_id'])):
        cum+=x['return']-x['investment'];peak=max(peak,cum);drawdown=max(drawdown,peak-cum)
        streak=streak+1 if x['return']==0 else 0;maxstreak=max(maxstreak,streak)
        timeline.append({'race_id':x['race_id'],'post':x['post'],'cumulative_profit_loss':cum,'drawdown':peak-cum})
    total=aggregate(rows);total_return=total['return']
    return {**total,'median_exposed_race_pfs':statistics.median([x['return']/x['investment']*100 for x in exposed]) if exposed else None,
            'largest_return_share':by_return[0]['return']/total_return if total_return else None,
            'largest_investment_share':max((x['investment'] for x in exposed),default=0)/total['investment'] if total['investment'] else None,
            'max_drawdown_yen':drawdown,'max_zero_return_streak':maxstreak,'largest_returns_excluded':exclusions,
            'chronology_definition':'Official scheduled post; ties race_id; recommendation exposure, not account cash balance',
            'timeline':timeline}

def verify_envelope(env,public_key):
    rec=env['receipt']
    if env.get('receipt_sha256')!=sha(rec):raise ValueError('RECEIPT_HASH_MISMATCH')
    if env.get('signature_alg')!='Ed25519':raise ValueError('SIGNATURE_ALGORITHM_MISMATCH')
    Ed25519PublicKey.from_public_bytes(base64.b64decode(public_key,validate=True)).verify(
        base64.b64decode(env['signature'],validate=True),canonical_bytes(rec))
    return {'status':'SIGNATURE_VERIFIED','receipt_sha256':sha(rec),'receipt':rec}

def metric(values):
    known=[x for x in values if isinstance(x,bool)]
    return {'numerator':sum(known),'denominator':len(known),'rate':sum(known)/len(known) if known else None}

def prediction(final,official,market_observation=None):
    actual=[str(x) for x in official['top3']];w,p2,p3=actual
    ranking=[str(x) for x in final['static_prediction']['ranking']]
    roles=final['static_prediction'].get('roles',{})
    columns={role:[str(h) for h,v in roles.items() if role in v] for role in ['W','P2','P3']}
    pairs={(str(x['head']),str(x['second'])) for x in final.get('pair_dispositions',[]) if x.get('status') in ('PURCHASE','PROTECT','PRESERVE')}
    thirds={(str(x['head']),str(x['second']),str(x['third'])) for x in final.get('third_dispositions',[]) if x.get('status') in ('PURCHASE','PROTECT','PRESERVE')}
    candidates=set().union(*map(set,columns.values()))
    market={str(x['horse_no']):x['win_popularity'] for x in official['runners']}
    frozen_market={str(x['horse_no']):x.get('popularity_rank') for x in (market_observation or {}).get('runners',[])}
    ranks=[ranking.index(h)+1 if h in ranking else None for h in actual]
    exact=tuple(actual) in thirds
    result={'ranking':ranking,'columns':columns,'winner_rank':ranks[0],'p2_rank':ranks[1],'p3_rank':ranks[2],
            'W':w in columns['W'],'P2':p2 in columns['P2'],'P3':p3 in columns['P3'],
            'ordered_pair':(w,p2) in pairs,'pair_conditioned_third':exact,'ordered_exact':exact,
            'top3_set_in_role_union':set(actual)<=candidates,
            'top3_set_in_static_top3':set(actual)==set(ranking[:3]),
            'top3_mean_rank':statistics.mean(ranks) if all(x is not None for x in ranks) else None,
            'candidate_width':len(candidates),'capture_efficiency':len(set(actual)&candidates)/len(candidates) if candidates else None,
            'winner_market_popularity':market.get(w),
            'market_relative_winner_rank_gain':frozen_market[w]-ranks[0] if frozen_market.get(w) is not None and ranks[0] is not None else None,
            'closing_market_relative_winner_rank_gain':market[w]-ranks[0] if market.get(w) is not None and ranks[0] is not None else None,
            'market_basis':{'source':'Signed SOURCE official market observation','captured_at':(market_observation or {}).get('captured_at'),
                            'frozen_market_winner_rank':frozen_market.get(w),'closing_popularity_diagnostic':market.get(w)},
            'alternative_winner':'NOT SEPARATELY EMITTED',
            'head_local_p2':[s for h,s in sorted(pairs) if h==w],
            'correct_pair_thirds':[t for h,s,t in sorted(thirds) if (h,s)==(w,p2)],
            'pair_count':len(pairs),'third_count':len(thirds)}
    if official.get('top3_display_order_is_not_unique'):
        for key in ['P2','P3','ordered_pair','pair_conditioned_third','ordered_exact','p2_rank','p3_rank']:
            result[key]=None
        result['ordered_metric_status']='PENDING DEAD-HEAT ADJUDICATION; displayed top3 is an unordered set after winner'
        result['official_payable_orders']=[p['selection'] for p in official['payouts']['TRIFECTA']]
    return result

def failure_record(label,owner='JRA Family',repair='PREDICTIVE HYPOTHESIS',strength='OBSERVED',materiality='MATERIAL',temporal='PRE-RACE VERIFIED'):
    return {'classification':label,'materiality':materiality,'evidence_strength':strength,'owner':owner,
            'repair_type':repair,'temporal_eligibility':temporal}

def analyze(day):
    compact=day.replace('-','');evidence=ROOT/'evidence'/('jra_day_review_'+compact)
    out=ROOT/'runtime/daily_reviews'/('JRA-'+day);out.mkdir(parents=True,exist_ok=True)
    status=read(ROOT/'runtime/jra_race_day_status'/f'{day}.json');schedule=read(ROOT/'runtime/jra_race_day_plan'/f'{day}.schedule.json')
    collection=read(evidence/'official/collection.json',{})
    health=read(evidence/'runtime_health.json',{})
    current=read(evidence/'current_authority.json',{})
    workflow_runs=[]
    for path in [evidence/'github_2.json',*sorted(evidence.glob('workflow_runs_page*.json'))]:workflow_runs+=read(path,{}).get('workflow_runs',[])
    runmap={str(x['id']):x for x in workflow_runs}
    result_checkpoints={}
    for p in (evidence/'result_checkpoints').glob('*/result_receipt_envelope.json'):
        obj=read(p);result_checkpoints[obj.get('receipt',{}).get('race_id')]=p
    official={};official_meta={};parse_errors=[]
    for rec in collection.get('races',[]):
        key=rec['race_key'];venue=VENUE.get(key[:2]);rn=int(key[-2:]);rid=f'KM-JRA-{venue}-{compact}-R{rn:02}'
        try:
            p=ROOT/rec['path']
            if hashlib.sha256(p.read_bytes()).hexdigest()!=rec['decoded_utf8_sha256']:raise ValueError('COLLECTION_HASH_MISMATCH')
            obj=parse_official(p.read_text(),day,venue,rn);obj['provenance']=rec
            official[rid]=obj;official_meta[rid]=rec
            write(evidence/'official'/f'{rid}.json',obj)
        except Exception as exc:parse_errors.append({'race_id':rid,'error':str(exc)})
    rows=[];cell_rows=[];ticket_rows=[];input_refs={};missing=[];numerical_rank_rows=[];other_lanes=[]
    def ref(p):
        if p.exists():
            rel=str(p.relative_to(ROOT));input_refs[rel]=hashlib.sha256(p.read_bytes()).hexdigest();return rel
        return None
    for p in [ROOT/'runtime/jra_race_day_status'/f'{day}.json',ROOT/'runtime/jra_race_day_plan'/f'{day}.schedule.json']:
        ref(p)
    for s in sorted(status['races'],key=lambda x:(x['post'],x['race_id'])):
        rid=s['race_id'];eid=rid+'-LIVE-R1';venue=rid.split('-')[2]
        paths={
            'intent':ROOT/'runtime/jra_formal_intents'/f'{eid}.json',
            'request':ROOT/'runtime/requests'/f'{eid}-FORMAL.json',
            'final':ROOT/'runtime/final_artifacts'/f'{rid}.json',
            'result':ROOT/'runtime/results'/f'{rid}.json',
            'review':ROOT/'runtime/reviews_auto'/f'{rid}-AUTO.json',
            'learning':ROOT/'runtime/learning_states'/f'{rid}.json',
            'gap':ROOT/'runtime/exact_gaps'/f'{eid}.json',
            'paper_or_no_bet':ROOT/'runtime/jra_no_bet_terminals'/f'{eid}.json',
            'publication':ROOT/'runtime/jra_delivery'/rid/'publication.json',
            'availability':ROOT/'runtime/jra_delivery'/rid/'availability_receipt.json',
            'candidate_pre_result':ROOT/'runtime/jra_static_owner_forward_oos'/rid/'pre_result.json',
            'candidate_result':ROOT/'runtime/source_candidate_results'/f'{rid}.json',
            'mec_shadow':ROOT/'runtime/mec_shadow_artifacts'/f'{rid}.json',
            'mec_shadow_result':ROOT/'runtime/mec_shadow_results'/f'{rid}.json',
            'krs_measurement':ROOT/'runtime/krs_oos_measurements'/f'{rid}.json'}
        sources=sorted((ROOT/'runtime/executions'/eid/'SOURCE/runs').glob('*/source_receipt_envelope.json'))
        if sources:paths['source']=sources[-1]
        objects={k:read(p,{}) for k,p in paths.items()};refs={k:ref(p) for k,p in paths.items()}
        gap=objects['gap'];req=objects['request'] or gap.get('prepared_numerical_request',{});final=objects['final'];result=objects['result'];o=official.get(rid)
        request_ref=refs['request'] or refs['gap']
        request_prefix='' if objects['request'] else 'prepared_numerical_request.'
        source=objects.get('source',{});sp=final.get('static_prediction') or req.get('static_prediction') or {}
        pkg=final.get('final_prediction_package',{})
        status_small={k:v for k,v in s.items() if k!='aki_selection_failure'}
        if 'aki_selection_failure' in s:status_small['aki_selection_failure']={k:v for k,v in s['aki_selection_failure'].items() if k!='selection_ledger'}
        row={'race_id':rid,'venue':venue,'race_no':s['race_no'],'post':s['post'],'observed_status':status_small,
             'artifact_refs':refs,'official_result':o,'authority':{'review_time':current.get('path'),
             'race_time_manifest':req.get('current_authority_manifest','UNKNOWN'),
             'source_git_sha':source.get('github_sha','UNKNOWN'),'source_run_id':source.get('github_run_id','UNKNOWN'),
             'static_owner':sp.get('authority','UNKNOWN'),'numerical_mapping':req.get('base_index_mapping_authority','UNKNOWN'),
             'static_activation':req.get('static_owner_activation_binding','UNKNOWN'),
             'policy_fingerprint':(req.get('bvi_static_consumption_proof') or {}).get('policy_fingerprint','UNKNOWN'),
             'source_checkpoint':req.get('source_checkpoint_manifest','UNKNOWN'),
             'krs_engine':(final.get('krs_run_receipt') or {}).get('receipt',{}),
             'mec_policy':(final.get('minimum_efficient_coverage') or {}).get('profile','UNKNOWN'),
             'capital_policy':final.get('capital_policy_decision','UNKNOWN')},
             'temporal':{'scheduled_post':s['post'],'prediction_cutoff':req.get('prediction_cutoff') or objects['intent'].get('prediction_cutoff'),
                         'intent_deadline':s.get('retry_deadline') or 'UNKNOWN: no immutable race-time resolver deadline recorded',
                         'standard_dispatch_window_open':schedule[rid]['dispatch_window_open'],
                         'standard_dispatch_window_close':schedule[rid]['dispatch_window_close'],
                         'source_deadline':req.get('prediction_cutoff') or objects['intent'].get('prediction_cutoff'),
                         'final_deadline':req.get('prediction_cutoff') or objects['intent'].get('prediction_cutoff'),
                         'external_dispatch_deadline':req.get('external_dispatch_deadline_at') or objects['intent'].get('external_dispatch_deadline_at'),
                         'source_freeze':(source.get('artifact') or {}).get('source_freeze_at'),
                         'static_freeze':final.get('static_freeze_timestamp') or req.get('static_freeze_timestamp'),
                         'final_freeze':final.get('final_freeze_timestamp')},
             'verification':{},'execution':{},'prediction':None,'aki':None,'krs':None,'bvi':None,
             'settlement':None,'first_material_failure':None,'secondary_failures':[],
             'dominant_pfs_loss_owner':'UNDETERMINED','actual_purchase_status':'NOT VERIFIED'}
        v=row['verification'];ex=row['execution']
        if req:
            v['temporal_evidence']={key:(dt(value)<=dt(row['temporal']['prediction_cutoff'])) if value and row['temporal']['prediction_cutoff'] else None
                 for key,value in [('source_before_cutoff',row['temporal']['source_freeze']),('static_before_cutoff',row['temporal']['static_freeze']),('final_before_cutoff',row['temporal']['final_freeze'])]}
        if source:
            try:v['source']=verify_source(paths['source'])
            except Exception as exc:v['source']={'valid':False,'error':str(exc)}
            att=paths['source'].parent/'source_attestation.json';ref(att)
            v['source_oidc']={'saved_assertion':read(att,{}),'independent_sigstore_verification':'NOT VERIFIED: bundle not persisted'}
            v['source_request_binding']={'snapshot_sha_matches':req.get('source_snapshot_sha256')==(source.get('artifact') or {}).get('source_snapshot_sha256') if req.get('source_snapshot_sha256') else None,
                'checkpoint_receipt_matches':(req.get('source_checkpoint_manifest') or gap.get('source_checkpoint_manifest') or {}).get('receipt_sha256')==source.get('receipt_sha256')}
            if o:
                su=(source.get('artifact') or {}).get('official_runner_universe',{}).get('runners',[])
                frozen_numbers={int(x.get('horse_no') or x.get('runner_id')) for x in su}
                official_numbers={x['horse_no'] for x in o['runners']}
                v['runner_universe']={'frozen_runner_count':len(frozen_numbers),'official_runner_count':len(official_numbers),
                    'same_numbers':frozen_numbers==official_numbers,'only_frozen':sorted(frozen_numbers-official_numbers),
                    'only_result':sorted(official_numbers-frozen_numbers)}
        else:v['source']={'valid':False,'status':'NOT EXECUTED'}
        final_valid=False
        if final:
            try:
                verify_signed_final(final,health['health'],health['contract']);final_valid=True
                v['final']={'signature_and_payload':'PASS','immutable_hash':'PASS'}
            except Exception as exc:v['final']={'signature_and_payload':'FAIL','error':type(exc).__name__+':'+str(exc)}
            for phase,key in [('PRE_KRS','pre_krs_receipt'),('KRS_RUN','krs_run_receipt')]:
                try:v[phase]=verify_envelope(final[key],health['health']['receipt_signer']['public_key_b64'])
                except Exception as exc:v[phase]={'status':'FAIL','error':str(exc)}
        ex['Intent']=bool(objects['intent']);ex['SOURCE']=bool(source and (source.get('receipt') or {}).get('status')=='PASS')
        ex['Signed_SOURCE']=bool(v['source'].get('valid'))
        calc=pkg.get('actual_numerical_calculation',{})
        actual_cells=[r.get('canonical_components',{}) for r in req.get('runners',[])]
        frozen_full=bool(actual_cells and all(all(isinstance(c.get(i,{}).get('value'),(int,float)) for i in BASE+DERIVED) for c in actual_cells))
        ex['Full20']=bool(calc and calc.get('calculated_count')==calc.get('required_count') and calc.get('required_count',0)>0) or bool(gap.get('verified_full_index_count') and gap.get('verified_full_index_count')==gap.get('required_index_count')) or frozen_full
        ex['Static']=bool(sp.get('ranking') and sp.get('production_authority'))
        ex['AKI']=bool(pkg.get('official_aki_package') or objects['paper_or_no_bet'].get('aki_selection_failure') or gap.get('aki_selection_failure'))
        ex['PRE_KRS']=v.get('PRE_KRS',{}).get('status')=='SIGNATURE_VERIFIED'
        ex['KRS']=v.get('KRS_RUN',{}).get('status')=='SIGNATURE_VERIFIED'
        ex['MEC']=bool(final.get('minimum_efficient_coverage'));ex['Capital']=bool(final.get('capital_policy_decision'))
        ex['Signed_FINAL']=final_valid
        ex['Signed_FINAL_before_post']=bool(final_valid and dt(final['final_receipt']['receipt']['timestamp'])<dt(s['post']))
        ex['Published_before_post']=bool(objects['availability'].get('availability_verified_before_post') and objects['availability'].get('final_sha256')==final.get('sha256'))
        ex['Delivery']=bool(objects['availability'].get('user_delivery_verified') and objects['availability'].get('user_received_at') and dt(objects['availability']['user_received_at'])<dt(s['post']))
        ex['Settlement']=bool(result.get('settlement'));ex['Learning']=bool(objects['learning'])
        row['formal_grade']='SIGNED FINAL / '+('PAPER' if final.get('final_ticket',{}).get('no_bet') else 'RECOMMENDATION') if final_valid else ('NO SIGNED FINAL')
        row['temporal_eligibility']='PRE-RACE VERIFIED' if ex['Signed_FINAL_before_post'] else 'NOT EXECUTED' if not final else 'UNKNOWN'
        for run_id in [str(s.get('formal_run_id','')),str(s.get('workflow_run_id','')),str(source.get('github_run_id',''))]:
            if run_id in runmap:row.setdefault('workflow_results',[]).append(runmap[run_id])
        if objects['publication'].get('run_url'):
            formal_id=objects['publication']['run_url'].rstrip('/').split('/')[-1]
            if formal_id in runmap:row.setdefault('workflow_results',[]).append(runmap[formal_id])
        # Result receipt is not embedded in the settlement record. Locate actual
        # immutable envelopes separately; never upgrade a state string to proof.
        result_envs=list((ROOT/'runtime/executions'/eid/'RESULT').glob('runs/*/result_receipt_envelope.json'))
        if rid in result_checkpoints:result_envs.append(result_checkpoints[rid])
        v['result_receipt']={'status':'NOT VERIFIED','reason':'No persisted raw signed RESULT envelope','paths':[ref(p) for p in result_envs]}
        for rp in result_envs:
            try:
                env=read(rp);verification=verify_envelope(env,health['health']['receipt_signer']['public_key_b64'])
                original=read(rp.parent/'result_request.json',{})
                if env['receipt']['artifact_sha256']!=sha(original):raise ValueError('SIGNED_RESULT_PAYLOAD_MISMATCH')
                if original.get('race_id')!=rid:raise ValueError('RESULT_RACE_ID_MISMATCH')
                if original.get('frozen_prediction_ref',{}).get('final_receipt_sha256')!=final.get('final_receipt_sha256'):raise ValueError('RESULT_FINAL_RECEIPT_BINDING_MISMATCH')
                ref(rp);ref(rp.parent/'result_request.json');ref(rp.parent/'provenance.json')
                v['result_receipt']={**verification,'payload_binding':'PASS','path':str(rp.relative_to(ROOT)),
                    'same_as_saved_result_request':sha(original)==sha(result) if result else None}
            except Exception as exc:v['result_receipt']={'status':'FAIL','error':str(exc)}
        learning=objects['learning']
        v['learning']={'recorded':bool(learning),'hash_verified':bool(learning and learning.get('sha256')==sha({k:v for k,v in learning.items() if k!='sha256'})),
                       'next_race_consumption':'NOT VERIFIED','signed_result_dependency':v['result_receipt']['status']}
        numerical=[]
        indexed=req.get('index_provenance_ledger',{}).get('runners',{})
        hsv={str(x['horse_no']):x for x in req.get('krs_input_data',{}).get('horses',[])}
        canonical={str(x['runner_id']):x.get('canonical_components',{}) for x in req.get('runners',[])}
        for horse,spec in indexed.items():
            vals={idx:(spec.get('base_indices',{}).get(idx) or {}).get('value') for idx in BASE}
            vals['DCR']=(spec.get('dcr') or {}).get('score')
            vals.update({idx:(hsv.get(horse,{}).get('static') or {}).get(idx.lower()) for idx in DERIVED if idx!='DCR'})
            vals.update({idx:canonical.get(horse,{}).get(idx,{}).get('value',value) for idx,value in vals.items()})
            for idx,value in vals.items():
                cell=canonical.get(horse,{}).get(idx) or (spec.get('base_indices',{}).get(idx) or {})
                refs0=cell.get('evidence_refs') or ([req.get('index_provenance_hash')] if idx in DERIVED else [])
                cell_rows.append({'race_id':rid,'runner_id':horse,'index':idx,'value':value if value is not None else 'UNKNOWN',
                                  'rule':cell.get('rule_id') or ('JRA-DCR-SCORE-v1' if idx=='DCR' else req.get('index_provenance_ledger',{}).get('formula_registry','UNKNOWN')),
                                  'evidence':json.dumps(refs0,ensure_ascii=False),'source_file':request_ref,
                                  'source_field':request_prefix+f'runners[runner_id={horse}].canonical_components.{idx}',
                                  'numerical_status':'FROZEN VALUE PRESENT' if value is not None else 'UNKNOWN',
                                  'production_authority':json.dumps(req.get('base_index_mapping_authority',{}),ensure_ascii=False)})
            numerical.append({'runner_id':horse,'values':vals})
        row['numerical']={'runner_count':len(indexed),'required_cells':len(indexed)*20,
                          'persisted_value_count':sum(v is not None for x in numerical for v in x['values'].values()),
                          'actual_completion_evidence':calc or {k:gap.get(k) for k in ['verified_full_index_count','required_index_count','numerical_count_basis']},
                          'value_recomputation':'NONE: only persisted ledger and frozen KRS input read'}
        if o and numerical and final_valid:
            for idx in BASE+DERIVED:
                vals={x['runner_id']:x['values'][idx] for x in numerical if isinstance(x['values'][idx],(int,float))}
                ranking=sorted(vals,key=lambda h:(-vals[h],int(h)))
                actual=[str(x) for x in o['top3']]
                numerical_rank_rows.append({'race_id':rid,'index':idx,'runner_count':len(ranking),
                                           'winner_value':vals.get(actual[0]),'winner_rank':ranking.index(actual[0])+1 if actual[0] in ranking else None,
                                           'top3_ranks':[ranking.index(h)+1 if h in ranking else None for h in actual],
                                           'rank_definition':'Descending persisted value; ties horse_no. Diagnostic, not causal contribution.'})
        if final_valid and o and ex['Signed_FINAL_before_post']:
            row['prediction']=prediction(final,o,(source.get('artifact') or {}).get('jra_official_market_observation'))
            try:
                row['settlement']=settle_tickets(final['final_ticket']['tickets'],o)
                if row['settlement']['investment']!=final['final_ticket']['total_investment']:raise ValueError('FROZEN_TOTAL_INVESTMENT_MISMATCH')
                row['settlement']['lane']='PRODUCTION_FROZEN_RECOMMENDATION'
                old=result.get('settlement',{})
                row['settlement']['existing_reconciliation']={'existing_investment':old.get('total_investment'),'existing_return':old.get('total_payout'),
                    'investment_delta':row['settlement']['investment']-old['total_investment'] if 'total_investment' in old else None,
                    'return_delta':row['settlement']['return']-old['total_payout'] if 'total_payout' in old else None}
                for t in row['settlement']['tickets']:ticket_rows.append({'race_id':rid,'venue':venue,'post':s['post'],'lane':'PRODUCTION_FROZEN_RECOMMENDATION',**t})
            except Exception as exc:row['settlement']={'status':'BLOCKED','error':str(exc)}
            pred=row['prediction']
            row['aki']={'axes':(sp.get('aki_jra_v21') or {}).get('axes',{}),'profile':(sp.get('aki_jra_v21') or {}).get('profile'),
                        'axis_failure_risk':(sp.get('aki_jra_v21') or {}).get('axis_failure_risk'),
                        'selection':pkg.get('aki_column_selection',{}),'captures':{x:pred[x] for x in ['W','P2','P3','ordered_pair','ordered_exact']},
                        'overcompression':'NOT CAUSALLY IDENTIFIED: selected-column miss is not proof that upstream held the correct role',
                        'overexpansion':'HYPOTHESIS ONLY; no materiality deletion counterfactual has been frozen'}
            utility=final.get('krs_prediction_utility',{})
            if utility:
                semantic_eligible=not o.get('top3_display_order_is_not_unique')
                ev=evaluate_against_result(utility,o['top3'],static_ranking=sp.get('ranking'),static_roles=sp.get('roles',{})) if semantic_eligible else {'status':'PENDING_DEAD_HEAT_ORDER_ADJUDICATION','unique_rescue_role_count':None,'unique_harm_role_count':None}
                row['krs']={'execution_receipt':final['krs_run_receipt']['receipt'],'output_persisted':bool(utility.get('summary')),
                            'semantic_evaluation_eligible':semantic_eligible,
                            'raw_output_sha_verified':'NOT VERIFIED: full raw structured engine response not persisted',
                            'utility':ev,'production_effect':utility.get('production_effect'),'unique_rescue_to_production_ticket':0,
                            'actual_production_harm':False,'notice':'Frozen KRS proposals are Shadow; role-zone harm is potential non-confirmation, not a Production deletion.'}
                correct={role:int(h) for role,h in zip(['W','P2','P3'],o['top3'])}
                proposals=(utility.get('actionable_role_proposals') or []) if semantic_eligible else []
                unique=[];false=[]
                for proposal in proposals:
                    role=proposal['proposal'].removeprefix('ADD_').removesuffix('_SHADOW');horse=int(proposal['horse_no'])
                    if role in correct and horse==correct[role] and str(horse) not in pred['columns'].get(role,[]):unique.append(proposal)
                    else:false.append(proposal)
                row['krs']['unique_actionable_role_rescues']=unique
                row['krs']['false_positive_actionable_role_proposals']=false
                row['krs']['actionable_role_rescue_density']=len(unique)/len(proposals) if proposals else None
                row['krs']['legacy_summary_role_binding_mismatch']=sum(set(x.get('static_roles',[]))!=set(sp.get('roles',{}).get(str(x['horse_no']),[])) for x in utility.get('summary',[]))
            bvi=pkg.get('bvi_consumption_ledger') or req.get('bvi_consumption_ledger') or {}
            row['bvi']={k:v for k,v in bvi.items() if k not in ('runners','ledger','runner_ledger')}
            if not pred['W']:row['first_material_failure']=failure_record('WINNER DISCOVERY FAILURE')
            elif pred['P2'] is False:row['first_material_failure']=failure_record('P2 DISCOVERY FAILURE')
            elif not pred['ordered_pair']:row['first_material_failure']=failure_record('HEAD-LOCAL P2 FAILURE')
            elif not pred['P3']:row['first_material_failure']=failure_record('P3 DISCOVERY FAILURE')
            elif not pred['ordered_exact']:row['first_material_failure']=failure_record('PAIR-CONDITIONED THIRD FAILURE')
            elif row['settlement'].get('hit_but_loss'):row['first_material_failure']=failure_record('CAPITAL ALLOCATION FAILURE',repair='CAPITAL HYPOTHESIS',strength='INFERRED')
            else:row['first_material_failure']=failure_record('NO MATERIAL FAILURE',repair='NO CHANGE',materiality='NON-MATERIAL')
            if row['settlement'].get('profit_loss',0)<0:
                row['dominant_pfs_loss_owner']={'classification':'UNDETERMINED','first_observed_miss':row['first_material_failure']['classification'],
                    'evidence_strength':'INFERRED','observed_loss_yen':-row['settlement']['profit_loss'],
                    'causal_loss_allocation':'UNDETERMINED: no frozen controlled counterfactual; this is first observed miss, not proven dominant causal attribution'}
            if not ex['Delivery']:row['secondary_failures'].append(failure_record('DELIVERY FAILURE','Runtime','PROCESS',strength='UNKNOWN',materiality='UNKNOWN',temporal='UNKNOWN'))
            tickets=final['final_ticket']['tickets'];actual=o['top3']
            triohit=any(t['bet_type']=='TRIO' and set(t['selection'])==set(actual) for t in tickets)
            exacthit=any(t['bet_type']=='TRIFECTA' and list(t['selection'])==actual for t in tickets)
            row['semantic_conversion']={'result_structure':actual,'prediction_role':'EXISTED' if all(pred[x] for x in ['W','P2','P3']) else 'EXCLUDED',
                'ordered_pair':'EXISTED' if pred['ordered_pair'] else 'EXCLUDED',
                'pair_conditioned_third':'EXISTED' if pred['ordered_exact'] else 'EXCLUDED',
                'canonical_exact_ticket':'SELECTED' if exacthit else 'EXCLUDED',
                'unordered_trio_ticket':'SELECTED' if triohit else 'EXCLUDED',
                'purchased':'NOT VERIFIED','material_coverage_ratio':final.get('minimum_efficient_coverage',{}).get('material_coverage_ratio'),
                'notice':'A selected unordered TRIO does not establish correct ordered Winner/P2/P3.'}
            krsp=next((evidence/'krs_checkpoints').glob(f'*/{rid}/krs_response.json'),None)
            if krsp and row['krs']:
                try:
                    raw=read(krsp);rr=raw['run_receipt']['receipt'];ref(krsp);ref(krsp.parent.parent/'provenance.json')
                    verify_envelope(raw['run_receipt'],health['health']['receipt_signer']['public_key_b64'])
                    if raw['run_receipt']!=final['krs_run_receipt']:raise ValueError('KRS_RECEIPT_NOT_FINAL_BOUND')
                    if hashlib.sha256(raw['output_canonical_json'].encode()).hexdigest()!=rr['output_sha256']:raise ValueError('KRS_OUTPUT_SHA_MISMATCH')
                    if json.loads(raw['output_canonical_json'])!=raw['output']:raise ValueError('KRS_STRUCTURED_CANONICAL_MISMATCH')
                    payload=production_krs_payload(req)
                    input_candidates={'payload':sha(payload),'input_data':sha(payload['input_data'])}
                    row['krs']['raw_output_sha_verified']='PASS'
                    row['krs']['raw_output_ref']=str(krsp.relative_to(ROOT))
                    row['krs']['input_hash_comparison']={'receipt_input_sha256':rr['input_sha256'],'candidates':input_candidates,
                        'match':[k for k,vv in input_candidates.items() if vv==rr['input_sha256']]}
                except Exception as exc:row['krs']['raw_output_sha_verified']='FAIL: '+str(exc)
        else:
            err=s.get('execution_error') or gap.get('auto_handoff_error') or s.get('first_failure','')
            if s['state']=='FORMAL_FAILED':label='EXECUTION / RECEIPT FAILURE';owner='Runtime';repair='CORRECTNESS'
            elif 'PAIR' in err:label='AKI PAIR INFEASIBILITY';owner='JRA Family';repair='NO CHANGE'
            elif s['state']=='AKI_NO_BET':label='NO MATERIAL FAILURE';owner='JRA Family';repair='NO CHANGE'
            elif s['state']=='MISSED_WINDOW':label='RACE INTENT / DISPATCH FAILURE';owner='Runtime';repair='CORRECTNESS'
            elif 'RESOLVER' in s['state']:label='SOURCE / RESOLVER FAILURE';owner='External Source';repair='CORRECTNESS'
            else:label='UNDETERMINED';owner='Measurement';repair='PROCESS'
            row['first_material_failure']=failure_record(label,owner,repair,materiality='NON-MATERIAL' if label=='NO MATERIAL FAILURE' else 'MATERIAL')
            row['execution_failure_detail']={'first_failed_stage':s.get('first_failed_stage') or gap.get('first_blocked_stage') or s.get('first_blocked_stage'),
                                             'error':err,'gap_ref':refs['gap'],
                                             'gap_summary':{k:gap.get(k) for k in ['first_blocked_stage','formal_execution_failure','verified_full_index_count','required_index_count','numerical_count_basis']},
                                             'prediction_accuracy':'NOT EVALUATED: no verified pre-race Signed FINAL'}
        if not row['bvi']:
            bvi=req.get('bvi_consumption_ledger') or gap.get('prepared_numerical_request',{}).get('bvi_consumption_ledger') or {}
            if bvi:row['bvi']={k:v for k,v in bvi.items() if k not in ('runners','ledger','runner_ledger')}
        if req.get('runners'):
            counts=Counter()
            for runner in req['runners']:
                cell=runner.get('canonical_components',{}).get('BVI',{})
                if not isinstance(cell.get('value'),(int,float)):counts['UNKNOWN']+=1
                elif not cell.get('components'):counts['DCR_ONLY']+=1
                elif cell.get('adjustments'):counts['MEASURED_PLUS_DCR']+=1
                else:counts['MEASURED']+=1
            row['bvi_frozen_input_inventory']={'counts':dict(counts),'basis':request_ref,'phase':'Frozen numerical BVI input; downstream consumption proven only where existing ledger binds Static/FINAL'}
        # Analyze only existing frozen alternative ticket sets. They never enter
        # Production denominators or manufacture a FINAL for failed races.
        alternatives=[]
        candidate_dir=ROOT/'runtime/source_candidate_oos'/rid
        cp=candidate_dir/'candidate_final.json';pre=candidate_dir/'pre_result.json'
        if cp.exists() and pre.exists() and o:
            cf=read(cp);pr=read(pre);ref(cp);ref(pre)
            if dt(pr['frozen_at'])<dt(s['post']):
                lane='CANDIDATE_PAPER_REFERENCE' if cf.get('capital',{}).get('paper_only') or cf.get('capital',{}).get('no_bet') else 'CANDIDATE_FROZEN_RECOMMENDATION'
                alternatives.append((lane,cf.get('mec',{}).get('tickets',[]),str(cp.relative_to(ROOT))))
        shadow=objects['mec_shadow']
        if shadow and o and dt(shadow.get('generated_at'))<dt(s['post']):
            for arm,obj in shadow.get('arms',{}).items():
                alternatives.append(('MEC_SHADOW:'+arm,obj.get('tickets',[]),refs['mec_shadow']))
        row['alternative_lanes']=[]
        for lane,tickets,path in alternatives:
            try:
                settled=settle_tickets(tickets,o)
                rec={'race_id':rid,'post':s['post'],'venue':venue,'lane':lane,'source_ref':path,**settled}
                other_lanes.append(rec);row['alternative_lanes'].append({k:v for k,v in rec.items() if k!='tickets'})
            except Exception as exc:row['alternative_lanes'].append({'lane':lane,'status':'BLOCKED','error':str(exc)})
        if o and o.get('top3_display_order_is_not_unique'):
            row['result_status']='OFFICIAL DEAD HEAT; existing canonical RESULT is PENDING MANUAL ADJUDICATION; local payout settlement is analysis only'
        if result and o:
            previous=result.get('official_result',{})
            diffs=[]
            if previous.get('top3')!=o['top3']:diffs.append({'field':'top3','old':previous.get('top3'),'official':o['top3']})
            for bt,p in previous.get('payouts',{}).items():
                if isinstance(p,dict) and p not in o['payouts'].get(bt,[]):diffs.append({'field':bt,'old':p,'official':o['payouts'].get(bt)})
            v['official_reconciliation']={'status':'MATCH' if not diffs else 'MISMATCH','differences':diffs}
        missing.append({'race_id':rid,'missing_artifacts':[k for k,v0 in refs.items() if v0 is None],
                        'unverified':['ACTUAL_PURCHASE','USER_DELIVERY','INDEPENDENT_SOURCE_OIDC']+(['SIGNED_RESULT_ENVELOPE'] if v['result_receipt']['status']!='SIGNATURE_VERIFIED' else [])})
        rows.append(row)
        write(out/'races'/f'{rid}.json',row)
    settlement_rows=[{'race_id':r['race_id'],'post':r['post'],'venue':r['venue'],**{k:r['settlement'][k] for k in ['investment','return','profit_loss','pfs','hit','hit_but_loss']}}
                     for r in rows if r['settlement'] and 'investment' in r['settlement']]
    pervenue={v:aggregate([r for r in settlement_rows if r['venue']==v]) for v in VENUE.values()}
    def ticket_group(field):
        groups=defaultdict(list)
        for t in ticket_rows:groups[t.get(field,'UNKNOWN')].append(t)
        return {k:{'ticket_count':len(v),'investment':sum(t['investment'] for t in v),'return':sum(t['return'] for t in v),
                   'profit_loss':sum(t['profit_loss'] for t in v),'pfs':sum(t['return'] for t in v)/sum(t['investment'] for t in v)*100 if sum(t['investment'] for t in v) else None,
                   'hit_ticket_count':sum(t['hit'] for t in v),'hit_but_loss_race_count':sum(0<sum(t['return'] for t in v if t['race_id']==rid)<sum(t['investment'] for t in v if t['race_id']==rid) for rid in {t['race_id'] for t in v})} for k,v in groups.items()}
    predrows=[r['prediction'] for r in rows if r['prediction']]
    prediction_lanes={lane:[r['prediction'] for r in rows if r['prediction'] and (r['formal_grade'].endswith('PAPER') if lane=='PAPER' else not r['formal_grade'].endswith('PAPER'))] for lane in ['PRODUCTION','PAPER']}
    summary={'profile':'KM-JRA-FULL-DAY-AUDIT-v1','race_date':day,'generated_at':datetime.now(timezone.utc).isoformat(),
             'git_snapshot':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
             'population':len(rows),'status_snapshot_at':status['generated_at'],'official_results_count':len(official),
             'official_parse_errors':parse_errors,'status_counts':dict(Counter(r['observed_status']['state'] for r in rows)),
             'execution':{stage:{'numerator':sum(r['execution'].get(stage,False) for r in rows),'denominator':len(rows)} for stage in rows[0]['execution']},
             'prediction':{key:metric([p[key] for p in predrows]) for key in ['W','P2','P3','ordered_pair','ordered_exact','top3_set_in_role_union','top3_set_in_static_top3']},
             'prediction_by_lane':{lane:{key:metric([p[key] for p in lane_rows]) for key in ['W','P2','P3','ordered_pair','ordered_exact','top3_set_in_role_union','top3_set_in_static_top3']} for lane,lane_rows in prediction_lanes.items()},
             'winner_mean_rank':statistics.mean(p['winner_rank'] for p in predrows) if predrows else None,
             'market_relative_mean_winner_rank_gain':statistics.mean(p['market_relative_winner_rank_gain'] for p in predrows if p['market_relative_winner_rank_gain'] is not None) if predrows else None,
             'production_frozen_recommendation':robust([r for r in settlement_rows if r['investment']>0]),
             'paper_final_zero_exposure':aggregate([r for r in settlement_rows if r['investment']==0]),'per_venue':pervenue,
             'per_bet_type':ticket_group('bet_type'),'per_mec_tier':ticket_group('mec_tier'),
             'paper_final_count':sum(bool(r['settlement'] is not None and r['settlement'].get('investment')==0) for r in rows),
             'policy_no_bet_count':sum(r['observed_status']['state']=='AKI_NO_BET' for r in rows),
             'pair_infeasibility_count':sum(r['first_material_failure']['classification']=='AKI PAIR INFEASIBILITY' for r in rows),
             'first_material_failures':dict(Counter(r['first_material_failure']['classification'] for r in rows)),
             'source_signature_verified':sum(r['verification'].get('source',{}).get('valid',False) for r in rows),
             'result_receipt_verified':sum(r['verification']['result_receipt']['status']=='SIGNATURE_VERIFIED' for r in rows),
             'learning_hash_verified':sum(r['verification']['learning']['hash_verified'] for r in rows),
             'actual_purchase_pfs':'NOT VERIFIED','causal_pfs_loss_attribution':'UNDETERMINED',
             'limitations':['Single dependent meeting-day, no prospective policy comparison.','Market baseline is the saved pre-cutoff SOURCE observation; closing popularity is a separate diagnostic.',
                            'Raw RESULT envelopes recovered from Actions where available; independent SOURCE Sigstore bundle verification incomplete.',
                            'No Actual Purchase evidence or user receipt ACK verified.'],
             'analysis_only':True,'production_change_authorized':False}
    write(out/'audit_ledger.json',{'summary':summary,'races':rows})
    write(out/'summary.json',summary);write(out/'missing_artifacts.json',missing)
    write(out/'numerical_discrimination.json',numerical_rank_rows)
    write(out/'ticket_settlement.json',ticket_rows)
    write(out/'alternative_lane_settlements.json',other_lanes)
    write(out/'alternative_lane_summary.json',{lane:robust([r for r in other_lanes if r['lane']==lane]) for lane in sorted({r['lane'] for r in other_lanes})})
    write(out/'input_manifest.json',{'git_snapshot':summary['git_snapshot'],'inputs':input_refs,'method':'SHA256 exact file bytes','official_collection':collection})
    write(ROOT/'runtime/pfs_grand_review'/f'JRA-{day}.json',{'summary':summary['production_frozen_recommendation'],'race_settlements':settlement_rows,
        'per_venue':pervenue,'per_bet_type':summary['per_bet_type'],'per_tier':summary['per_mec_tier'],
        'lane':'PRODUCTION_FROZEN_RECOMMENDATION','actual_purchase':'NOT VERIFIED','audit_path':str(out.relative_to(ROOT))})
    if cell_rows:
        with (out/'full20_cells.csv').open('w',newline='') as fh:
            w=csv.DictWriter(fh,fieldnames=list(cell_rows[0]));w.writeheader();w.writerows(cell_rows)
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    return summary,rows

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--date',default='2026-10-17');a=p.parse_args();analyze(a.date)
