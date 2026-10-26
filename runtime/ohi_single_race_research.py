"""Explicit OHI private single-race computation. No Formal/Dispatcher mutation.

Reuse frozen LOCAL arithmetic, OHI conditional model, KRS Engine, Common MEC
and Family capital default. This profile is not registered OOS or an Owner.
"""
from __future__ import annotations
import argparse,copy,hashlib,json,os,re,subprocess,sys,time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urljoin
sys.path.insert(0,str(Path(__file__).resolve().parent))
from runtime.ohi_nankan_private_source import *
from runtime.local_nar_evidence_candidate import compile_parsed_candidate_evidence
from runtime.local_fullnumerical_candidate import materialize_candidate,REQUIRED
from runtime.local_fullnumerical_production import _assert_registry_equivalence
from runtime.local_krs_bridge_candidate import build_candidate_prediction_structure_derived,build_candidate_krs
from runtime.local_race_key_shadow_owner import owner_feature_pack,predict_conditioned_owner
from runtime.minimum_efficient_coverage import build_mec_plan,validate_mec_plan
from runtime.capital_policy import resolve_capital_policy,load_family_default_capital_policy
from runtime.jra_ticket_tree_renderer import render_ticket_tree

PROFILE='OHI-SINGLE-RACE-PRIVATE-RESEARCH-v1-20261026'
CLASS='OHI_SINGLE_RACE_PRESTART_NONPRODUCTION_NOT_REGISTERED_OOS'
MODEL='1706af57e008bd158214f70edc77b0f2eb59c220c828202f71ef770ad25b3a84'
ENGINE='9929df994aa7964173edef9af7e9a705628ce377babf22df3af4e280fc275421'
PARAM='d8c027ee5bcc8fd3d2c248e8059b341776be38910e833d7589f09ab817c161f5'

def utcnow():return datetime.now(timezone.utc)
def seal(d):return {**d,'sha256':sha(d)}
def load(p):return json.loads(Path(p).read_text())
def write(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    if p.exists():raise ValueError('IMMUTABLE_RESEARCH_OUTPUT_EXISTS:'+str(p))
    p.write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
def private_root(path):
    p=Path(path)
    if not p.is_absolute() or '..' in p.parts or any(x.is_symlink() for x in [p,*p.parents]):raise ValueError('OHI_PRIVATE_PATH_REQUIRED')
    code=Path(__file__).resolve().parents[1]
    if p.resolve().is_relative_to(code):raise ValueError('OHI_RAW_AND_OUTPUT_OUTSIDE_CODE_REQUIRED')
    return p
def check_source_time(o,stage,*,diagnostic=False):
    now=utcnow();cut=datetime.fromisoformat(o['race']['prediction_cutoff'])
    stamps=[datetime.fromisoformat(x['fetched_at']) for x in o['receipts']]
    if any(t.tzinfo is None or t>now for t in stamps):raise ValueError('OHI_SOURCE_TIME_UNKNOWN:'+stage)
    if not diagnostic and (now>=cut or any((now-t).total_seconds()>=600 for t in stamps)):
        raise ValueError('OHI_SOURCE_OR_CUTOFF_EXPIRED:'+stage)
    return dict(stage=stage,observed_at=now.isoformat(),classification='POSTCUTOFF_OR_OFFLINE_DIAGNOSTIC' if diagnostic else CLASS)

def capture(day,number,folder):
    folder=private_root(folder)
    if folder.exists():raise ValueError('OHI_CAPTURE_REVISION_ALREADY_EXISTS')
    folder.mkdir(parents=True,mode=0o700)
    client=Client();receipts=[]
    def get(name,url):
        meta,raw=client.get(url);(folder/(name+'.raw.html')).write_bytes(raw);write(folder/(name+'.receipt.json'),meta);receipts.append(meta);return raw,meta
    calendar,cm=get('calendar',ORIGIN+'/calendar/000000.do')
    links={urljoin(cm['url'],a.attrs.get('href','')) for a in DOM(decode(calendar)).root.all('a')}
    links=sorted(u for u in links if re.fullmatch(re.escape(ORIGIN)+'/program/'+day.replace('-','')+r'20[0-9]{4}\.do',u))
    if len(links)!=1:raise ValueError('OHI_CALENDAR_PROGRAM_NOT_UNIQUE')
    program,pm=get('program',links[0]);races=parse_program(program,pm['url'],day)
    race=next((r for r in races if r['race_no']==number),None)
    if race is None:raise ValueError('OHI_RACE_NOT_IN_OFFICIAL_PROGRAM')
    if utcnow()>=datetime.fromisoformat(race['prediction_cutoff']):raise ValueError('OHI_RESEARCH_PRESTART_CUTOFF_PASSED')
    try:card,cardmeta=get('card',race['observed_card_url'])
    except ObservedRedirect as e:
        if e.receipt.get('location')!=ORIGIN+'/uma_shosai/'+race['provider_race_id']+'.do':raise
        write(folder/'redirect.receipt.json',e.receipt);card,cardmeta=get('card',e.receipt['location'])
    dom=DOM(decode(card)).root
    changes_links={urljoin(cardmeta['url'],a.attrs.get('href','')) for a in dom.all('a') if '/henko_info/' in a.attrs.get('href','')}
    if changes_links!={ORIGIN+'/henko_info/00000000000000.do'}:raise ValueError('OHI_CHANGES_LINK_IDENTITY')
    changes,chgmeta=get('changes',next(iter(changes_links)))
    return observe(race,card,cardmeta,changes,chgmeta,receipts,program_races=races)

def observe(race,card,cardmeta,changes,chgmeta,receipts,*,program_races):
    for raw,meta in ((card,cardmeta),(changes,chgmeta)):
        if meta.get('http_status')!=200 or hashlib.sha256(raw).hexdigest()!=meta['raw_sha256']:raise ValueError('OHI_RAW_RECEIPT_MISMATCH')
        if (meta.get('source_policy') or {}).get('usage_scope')!='USER_PERSONAL_NONCOMMERCIAL_PRIVATE_ONLY_NOT_PUBLIC_REDISTRIBUTION':raise ValueError('OHI_PRIVATE_SOURCE_SCOPE_REQUIRED')
    ex=[];cardobs={};facts=parse_single_card(card,race,cardmeta['url'],excluded_rows=ex,card_observations=cardobs)
    ch=dated_changes(changes,chgmeta,race)
    if ex or any(f['status']!='ACTIVE_DECLARED' for f in facts):raise ValueError('OHI_CARD_CHANGE_CONTRADICTION_REQUIRES_EXPLICIT_ITEM_ADAPTER')
    for f in facts:
        for s in f['starts']:
            if datetime.strptime(s['date'],'%y.%m.%d').date()>datetime.fromisoformat(cardmeta['fetched_at']).date():raise ValueError('OHI_HISTORY_AFTER_CAPTURE')
    dom=DOM(decode(card)).root
    def walk(n):
        yield n
        for c in n.children:
            if isinstance(c,Node):yield from walk(c)
    menus=[x for x in walk(dom) if x.attrs.get('data-menu')=='odds']
    if len(menus)!=1:raise ValueError('OHI_MARKET_PUBLICATION_STATE_UNKNOWN')
    menu=menus[0]
    if 'is-disable' not in menu.attrs.get('class','').split() or menu.attrs.get('href'):
        raise ValueError('OHI_ENABLED_MARKET_OBSERVATION_REQUIRES_OHI_ODDS_ADAPTER')
    return seal(dict(profile=PROFILE,source_profile='OHI-NANKAN-PRIVATE-SINGLE-CARD-DATED-CHANGES-v1-20261026',race=race,program_races=program_races,facts=facts,source=cardmeta,changes=ch,receipts=receipts,card_observation=cardobs,market={'status':'MARKET_UNAVAILABLE_UI_DISABLED_NO_LINK','prices':None,'betting_membership':None,'observation':menu.attrs},runner_universe_basis='DATED_OFFICIAL_CARD_AND_EXPLICIT_DATED_NO_CHANGES_NOT_VERIFIED_ACTIVE',active_verified=False,formal_source_claim=False,signed_source_claim=False,production_authority=False,formal_forward_oos_credit=0))

def numerical(o,rid):
    equivalence=_assert_registry_equivalence()
    facts=copy.deepcopy(o['facts']);race={**o['race'],'venue':'OHI','class':o['race']['race_name']}
    for f in facts:f.update(race_card_source_id='NANKAN-CARD:'+race['provider_race_id'],race_card_snapshot_sha256=o['source']['raw_sha256'],race_card_fetched_at=o['source']['fetched_at'])
    req={'family_id':'LOCAL','venue_id':'OHI','race_id':rid,'race':race,'runners':[{'runner_id':f['runner_id'],'name':f['name']} for f in facts],'production_authority':False,'input_observation':{'raw_sha256':o['source']['raw_sha256'],'source_fetched_at':o['source']['fetched_at'],'source_url':o['source']['url']}}
    src={'source_snapshot_sha256':o['sha256'],'source_freeze_at':o['source']['fetched_at'],'normalized_evidence':{}}
    n=materialize_candidate(compile_parsed_candidate_evidence(src,req,{f['runner_id']:f for f in facts}))
    summary=n['candidate_full_numerical_summary']
    if not summary['numeric_transport_complete'] or summary['terminalized_count']!=len(facts)*29 or summary['unresolved_count']:raise ValueError('OHI_FULL29_INCOMPLETE')
    n['production_transform_equivalence']=equivalence
    return n

def verify_observation(o,source_dir):
    source_dir=private_root(source_dir)
    docs={};receipts=[]
    for name in ('calendar','program','card','changes'):
        raw=(source_dir/(name+'.raw.html')).read_bytes();meta=load(source_dir/(name+'.receipt.json'))
        if meta.get('http_status')!=200 or hashlib.sha256(raw).hexdigest()!=meta.get('raw_sha256'):raise ValueError('OHI_SAVED_SOURCE_RAW_MISMATCH:'+name)
        docs[name]=(raw,meta);receipts.append(meta)
    calendar,cm=docs['calendar'];program,pm=docs['program'];day=o['race']['race_date']
    observed={urljoin(cm['url'],a.attrs.get('href','')) for a in DOM(decode(calendar)).root.all('a')}
    if cm['url']!=ORIGIN+'/calendar/000000.do' or pm['url'] not in observed:raise ValueError('OHI_SAVED_PROGRAM_NOT_OBSERVED_IN_CALENDAR')
    races=parse_program(program,pm['url'],day);race=next((r for r in races if r['race_no']==o['race']['race_no']),None)
    if race!=o['race']:raise ValueError('OHI_SAVED_RACE_PROGRAM_MISMATCH')
    card,cardmeta=docs['card'];changes,chgmeta=docs['changes']
    rebuilt=observe(race,card,cardmeta,changes,chgmeta,receipts,program_races=races)
    if rebuilt!=o:raise ValueError('OHI_SAVED_OBSERVATION_FACTS_OR_RECEIPTS_MISMATCH')
    return True

def feature_pack(o,n,baseline,model,rid):
    evidence={}
    for f in o['facts']:
        starts=[dict(date=s['date'],venue=s['venue'],distance=s['distance'],surface=s['surface'],finish=s['finish'],field_size=s['field_size'],positions=s['content_positions'],going=s.get('going'),matched_venue_distance=False,past_course_family='UNKNOWN_FROM_SUMMARY',past_sand_regime='UNKNOWN') for s in f['starts']]
        evidence[f['runner_id']]={'past_starts':starts,'current_condition_translation':{'current_distance_m':o['race']['distance'],'current_frame_no':f['frame_no'],'current_assigned_load':f['current_load'],'current_body_weight_change':f['current_body_weight_change']}}
    candidate=seal(dict(production_authority=False,race_id=rid,venue_id='OHI',venue_canon=model['venue_canon'],venue_canon_source_sha256=model['venue_canon_source_sha256'],race_date=o['race']['race_date'],scheduled_post_at=o['race']['scheduled_post_at'],prediction_cutoff=o['race']['prediction_cutoff'],source_snapshot_sha256=o['sha256'],numeric_provenance_sha256=sha([r['canonical_components'] for r in n['runners']]),venue_evidence=evidence,existing_local_baseline=baseline))
    return owner_feature_pack(candidate,n)

def simulate(o,n,pred,rid,folder,engine,params):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True,mode=0o700)
    if hashlib.sha256(Path(engine).read_bytes()).hexdigest()!=ENGINE or hashlib.sha256(Path(params).read_bytes()).hexdigest()!=PARAM:raise ValueError('OHI_KRS_ASSET_HASH_MISMATCH')
    rows=copy.deepcopy(n['runners'])
    for row in rows:row['candidate_static_roles']=(pred.get('role_columns') or pred.get('roles'))[str(row['runner_id'])]
    family=o['race']['course_family']
    if family not in ('LEFT','INNER_RIGHT','OUTER_RIGHT'):raise ValueError('OHI_OBSERVED_COURSE_FAMILY_REQUIRED')
    race={'prediction_id':rid,'racecourse':'大井','date':o['race']['race_date'],'race_no':o['race']['race_no'],'distance':o['race']['distance'],'surface':'dirt','course':'left' if family=='LEFT' else 'right','course_rule_version':'OHI_FIXED_RESEARCH_NOT_FORMAL_OWNER'}
    inp=build_candidate_krs({**n,'race':race,'runners':rows,'seed':1,'run_count':5000})['candidate_krs_input_data'];write(folder/'input.json',inp)
    started=utcnow();t=time.monotonic()
    with (folder/'engine.log').open('x') as log:subprocess.run([sys.executable,str(engine),str(folder/'input.json'),'--output',str(folder/'output.json'),'--csv',str(folder/'summary.csv'),'--params',str(params),'--runs','5000','--seed','1','--short'],stdout=log,stderr=subprocess.STDOUT,timeout=300,check=True)
    out=load(folder/'output.json');s=out['snapshot']
    if s.get('prediction_id')!=rid or s.get('date')!=o['race']['race_date'] or s.get('race_no')!=o['race']['race_no'] or s.get('run_count')!=5000 or s.get('master_seed')!=1 or {str(x['horse_no']) for x in out['summary']}!={f['runner_id'] for f in o['facts']}:raise ValueError('OHI_KRS_OUTPUT_IDENTITY')
    receipt=seal(dict(started_at=started.isoformat(),completed_at=utcnow().isoformat(),wall_seconds=time.monotonic()-t,engine_sha256=ENGINE,parameter_map_sha256=PARAM,input_sha256=sha(inp),output_sha256=sha(out),runs=5000,seed=1,external_signed_receipt=False,actual_engine_executed=True,unknown_environment_defaults_not_observations=True))
    write(folder/'receipt.json',receipt);return out,receipt

def selection(o,pred,rid):
    roles=pred.get('role_columns') or pred['roles'];ranking=pred['ranking'];ids=[f['runner_id'] for f in o['facts']]
    heads=[r for r in ids if 'W' in roles[r]];seconds=[r for r in ids if 'P2' in roles[r]];thirds=[r for r in ids if 'P3' in roles[r]]
    # Common MEC's existing PROTECT hypotheses. No new material-Exact rule,
    # score threshold, KRS rescue, probability/EV or budget-driven truncation.
    pairs=[dict(head=h,second=s,status='PROTECT',reason='FIXED_UNVALIDATED_ROLE_PAIR_HYPOTHESIS') for h in heads for s in seconds if h!=s]
    third=[dict(head=p['head'],second=p['second'],third=t,status='PROTECT',reason='FIXED_UNVALIDATED_ROLE_THIRD_HYPOTHESIS') for p in pairs for t in thirds if t not in (p['head'],p['second'])]
    req={'family_id':'LOCAL','race_id':rid,'runners':[{'runner_id':i} for i in ids],'static_prediction':{'ranking':ranking,'roles':roles},'role_registry':[{'runner_id':i,'column':c,'status':'CORE'} for i,cs in roles.items() for c in cs],'pair_dispositions':pairs,'third_dispositions':third,'capital_policy':load_family_default_capital_policy()}
    mec=build_mec_plan(req);valid=validate_mec_plan(mec)
    if valid.get('mec_verified') is not True:raise ValueError('OHI_MEC_INVALID:'+str(valid))
    capital=resolve_capital_policy(req,mec);tickets=[] if capital['no_bet'] else mec['tickets']
    tree=render_ticket_tree({'static_prediction':{'ranking':ranking},'final_ticket':{'tickets':tickets,'total_investment':sum(t['stake'] for t in tickets)}})
    if len(tree['reflattened_tickets'])!=len(tickets) or tree['total_investment']!=sum(t['stake'] for t in tickets):raise ValueError('OHI_TREE_STAKE_MISMATCH')
    return dict(semantic_request=req,mec=mec,mec_validation=valid,capital=capital,tickets=tickets,tree=tree,research_paper_only=True,actual_investment_reserved=0,selection_semantics='EXPLICIT_RESEARCH_ROLE_HYPOTHESIS_PROJECTION_NOT_PAST_FROZEN_TICKETS',krs_selection_effect='OBSERVED_FOR_AUDIT_NOT_A_NEW_PURCHASE_POLICY',conditional_exact_materiality='UNVALIDATED_NO_NEW_TRIFECTA_AUTHORITY')

def run(o,output,model_path,engine,params,*,source_dir,diagnostic=False):
    output=private_root(output)
    if output.exists():raise ValueError('OHI_REUSE_EXISTING_ORIGINAL_REQUIRES_READER_NOT_RECOMPUTE')
    output.mkdir(parents=True,mode=0o700);events=[check_source_time(o,'START',diagnostic=diagnostic)];rid='OHI-'+o['race']['provider_race_id']+'-PRIVATE-R1'
    if o.get('sha256')!=sha({k:v for k,v in o.items() if k!='sha256'}) or o.get('production_authority') is not False or o.get('active_verified') is not False or o.get('profile')!=PROFILE:raise ValueError('OHI_SOURCE_FREEZE_HASH_OR_SCOPE')
    verify_observation(o,source_dir)
    root=Path(__file__).resolve().parents[1]
    dependencies=['runtime/ohi_nankan_private_source.py','runtime/ohi_single_race_research.py','runtime/urw_nankan_reference_source.py','runtime/urw_reference_source_policy.py','runtime/local_fullnumerical_production.py','runtime/local_nar_evidence_candidate.py','runtime/local_fullnumerical_candidate.py','runtime/local_krs_bridge_candidate.py','runtime/local_race_key_shadow_owner.py','runtime/minimum_efficient_coverage.py','runtime/capital_policy.py','mapping/local_evidence_feature_rule_registry_v0.1_candidate_20260923.json','mapping/local_full_numerical_mapping_v0.1_candidate_20260923.json','profiles/ohi_single_race_nonproduction_20261026.json','profiles/family_user_capital_default_20261003_R1.json']
    profile=load(root/dependencies[-2])
    if (profile.get('profile')!=PROFILE or profile.get('formal_admission') is not False or profile.get('source_max_age_seconds')!=600 or profile.get('fixed_ohi_candidate_model')!=MODEL or profile.get('engine_sha256')!=ENGINE or profile.get('parameters_sha256')!=PARAM or profile.get('krs_runs_per_owner')!=5000 or profile.get('krs_seed')!=1 or profile.get('runtime_post_allowed') is not False or profile.get('real_purchase') is not False):raise ValueError('OHI_RESEARCH_PROFILE_BINDING')
    manifest=seal(dict(profile=PROFILE,source_sha256=o['sha256'],model_sha256=MODEL,engine_sha256=ENGINE,parameters_sha256=PARAM,dependency_sha256={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in dependencies},formal_authority=False,production_effect='NONE'))
    write(output/'execution-manifest.json',manifest)
    write(output/'observation.json',o);model=load(model_path)
    if model['sha256']!=MODEL or sha({k:v for k,v in model.items() if k!='sha256'})!=MODEL or model['venue_id']!='OHI':raise ValueError('OHI_FIXED_MODEL_REQUIRED')
    n=numerical(o,rid);write(output/'numerical.json',n)
    baseline=build_candidate_prediction_structure_derived(n)['candidate_static_prediction'];write(output/'baseline.json',baseline)
    pack=feature_pack(o,n,baseline,model,rid);write(output/'features.json',pack)
    pred=predict_conditioned_owner(model,pack,historical_replay=diagnostic);write(output/'candidate.json',pred)
    events.append(check_source_time(o,'PRE_KRS',diagnostic=diagnostic))
    owners={'BASELINE':baseline,'OHI_FIXED_CANDIDATE':pred}
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures={name:pool.submit(simulate,o,n,p,rid,output/name,engine,params) for name,p in owners.items()}
        krs={name:f.result() for name,f in futures.items()}
    portfolios={name:selection(o,p,rid) for name,p in owners.items()}
    for name,v in portfolios.items():write(output/name/'portfolio.json',v)
    events.append(check_source_time(o,'FREEZE',diagnostic=diagnostic))
    result=seal(dict(profile=PROFILE,classification='POSTCUTOFF_OR_OFFLINE_DIAGNOSTIC' if diagnostic else CLASS,race=o['race'],source_sha256=o['sha256'],source_fetched_at=o['source']['fetched_at'],freeze_at=utcnow().isoformat(),execution_manifest_sha256=manifest['sha256'],numerical_summary=n['candidate_full_numerical_summary'],all_runners=o['facts'],numerical_cells={r['runner_id']:r['canonical_components'] for r in n['runners']},owners=owners,krs={name:{'output':x[0],'receipt':x[1]} for name,x in krs.items()},portfolios=portfolios,stage_clocks=events,registered_oos_credit=0,formal_source=False,signed_final=False,production_authority=False,actual_purchase=False,price_status=o['market'],changes_status=o['changes']['status']))
    write(output/'prediction-original.json',result)
    body=render(result);(output/'answer.md').write_text(body)
    write(output/'readback-manifest.json',seal({'prediction_sha256':result['sha256'],'answer_sha256':hashlib.sha256(body.encode()).hexdigest(),'files':{str(p.relative_to(output)):hashlib.sha256(p.read_bytes()).hexdigest() for p in output.rglob('*') if p.is_file()},'screen_ack':False,'private_remote_readback':False}))
    return result

def render(result):
    r=result['race'];n=result['numerical_summary'];b=result['owners']['BASELINE'];c=result['owners']['OHI_FIXED_CANDIDATE']
    out=[f"大井 {r['race_date']} {r['race_no']}R　{r['race_name']}",f"分類：{result['classification']}",f"発走 {r['scheduled_post_at']}／LOCAL研究Cutoff {r['prediction_cutoff']}（公式発売締切ではありません）",f"SOURCE {result['source_fetched_at']}／Freeze {result['freeze_at']}",f"Source SHA {result['source_sha256']}／原本SHA {result['sha256']}",f"全{len(result['all_runners'])}頭×29＝{n['required_count']}セル。実計算{n['calculated_count']}・規定中立{n['ruled_neutral_count']}・未解決{n['unresolved_count']}。full_numerical_complete={n['full_numerical_complete']}。",f"変更情報：{result['changes_status']}。価格：{result['price_status']['status']}。集合は公式Card＋日付付き変更の観測、Verified Activeではありません。","非Productionの独立PAPER比較です。正式FINAL、較正済み勝率、実購入指示ではありません。固定CandidateはOHI v2.1研究basisで、現行正式v2.3 Ownerへ昇格していません。","","|馬番・馬名|Baseline順位／Role|固定OHI Candidate順位／Role|中立セル（UNKNOWN）|","|---|---|---|---|"]
    for f in result['all_runners']:
        i=f['runner_id'];cells=result['numerical_cells'][i];missing=[k for k,v in cells.items() if v['terminal_status']=='RULED-NEUTRAL']
        out.append(f"|{i} {f['name']}|{b['ranking'].index(i)+1}／{'・'.join(b['roles'][i]) or '採用なし'}|{c['ranking'].index(i)+1}／{'・'.join(c['role_columns'][i]) or '採用なし'}|{len(missing)}：{', '.join(missing)}|")
    out+=['','欠測理由（原本）：']
    for f in result['all_runners']:out.append(f"{f['runner_id']} {f['name']}：履歴{len(f['starts'])}走、"+'／'.join(f['missingness']))
    for name,pred in result['owners'].items():
        roles=pred.get('role_columns') or pred['roles'];port=result['portfolios'][name];krs=result['krs'][name]
        out+=['',f'【{name}】']
        for col in ('W','P2','P3'):out.append(col+'：'+', '.join(i for i in pred['ranking'] if col in roles[i]))
        out+=[f"KRS実行：{krs['receipt']['runs']}回・seed{krs['receipt']['seed']}。未較正のシミュレーション出現率です。",'|馬番|SSR-W|SSR-P2|SSR-P3|','|---:|---:|---:|---:|']
        for x in sorted(krs['output']['summary'],key=lambda x:int(x['horse_no'])):out.append(f"|{x['horse_no']}|{x['SSR-W']*100:.2f}%|{x['SSR-P2']*100:.2f}%|{x['SSR-P3']*100:.2f}%|")
        lead=sorted(krs['output']['summary'],key=lambda x:(-x.get('LSR',0),int(x['horse_no'])))[:3]
        out+=['展開監査：LSR上位は '+', '.join(str(x['horse_no'])+'番 '+f"{x.get('LSR',0)*100:.2f}%" for x in lead)+'。観測した実展開や較正済み逃げ確率ではありません。','選択済み券面（全票、各100円）：','```text',port['tree']['text'],'```',f"点数 {len(port['tickets'])}／試算額 {sum(t['stake'] for t in port['tickets']):,}円／既存系列別上限 {port['capital']['capital_limit']:,}円／未使用 {port['capital']['unused_budget']:,}円。",'三連単：未実証の条件付きExactへ購入権限を付けないため0票。KRSは監査出力であり、新しい救済・購入Policyとして適用していません。']
    out+=['','結論：2案を合算しません。既存モデルの予測・MEC試算が成立した私有研究原本です。Candidateの優位・EV・将来成績は未証明です。馬体重・当日馬場は未観測で、後から更新が出た場合は新Revisionで再照合が必要です。', '','全馬29指数（N＝規定中立、C＝実計算。Provenanceはprediction-original.json内の各セル）：']
    for f in result['all_runners']:
        out+=['',f"{f['runner_id']} {f['name']}"]
        out.append('／'.join(f"{key} {v['value']:.3f} [{'N' if v['terminal_status']=='RULED-NEUTRAL' else 'C'}]" for key,v in result['numerical_cells'][f['runner_id']].items()))
    return '\n\n'.join(out)+'\n'

def readback(output):
    output=Path(output);m=load(output/'readback-manifest.json');r=load(output/'prediction-original.json')
    if m['sha256']!=sha({k:v for k,v in m.items() if k!='sha256'}) or r['sha256']!=sha({k:v for k,v in r.items() if k!='sha256'}) or m['prediction_sha256']!=r['sha256']:raise ValueError('OHI_ORIGINAL_HASH_MISMATCH')
    for relative,digest in m['files'].items():
        if '..' in Path(relative).parts or Path(relative).is_absolute() or hashlib.sha256((output/relative).read_bytes()).hexdigest()!=digest:raise ValueError('OHI_READBACK_FILE_MISMATCH')
    body=(output/'answer.md').read_text()
    if hashlib.sha256(body.encode()).hexdigest()!=m['answer_sha256'] or body!=render(r):raise ValueError('OHI_READBACK_BODY_MISMATCH')
    return r,body

def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--source-dir');g.add_argument('--query');g.add_argument('--readback');p.add_argument('--output');p.add_argument('--model');p.add_argument('--engine');p.add_argument('--params');p.add_argument('--diagnostic',action='store_true');a=p.parse_args()
    if a.readback:
        result,body=readback(a.readback);print(body);return
    if not all((a.output,a.model,a.engine,a.params)):p.error('calculation requires output/model/engine/params')
    source_dir=a.source_dir
    if a.query:
        if a.diagnostic:p.error('query capture is prestart only; saved source diagnostic is separate')
        from runtime.local_race_entry import resolve_chat_intent
        intent=resolve_chat_intent(a.query)
        if intent['venue_id']!='OHI':raise ValueError('OHI_RESEARCH_QUERY_OTHER_VENUE')
        if Path(a.output).exists():
            result,body=readback(a.output)
            if any(result['race'][k]!=intent[k] for k in ('venue_id','race_date','race_no')):raise ValueError('OHI_READER_OTHER_RACE')
            print(json.dumps({'readback_at':utcnow().isoformat(),'original_freeze':result['freeze_at'],'current_source_rechecked':False,'original_generation_classification_preserved':True,'current_freshness_not_asserted':True,'prediction_or_krs_reexecuted':False}),file=sys.stderr)
            print(body);return
        source_dir=str(Path(a.output).with_name(Path(a.output).name+'.source'))
        observation=capture(intent['race_date'],intent['race_no'],source_dir);write(Path(source_dir)/'observation.json',observation)
    result=run(load(Path(source_dir)/'observation.json'),a.output,a.model,a.engine,a.params,source_dir=source_dir,diagnostic=a.diagnostic)
    print(json.dumps({'classification':result['classification'],'sha256':result['sha256'],'race':result['race'],'numerical_summary':result['numerical_summary']},ensure_ascii=False))
if __name__=='__main__':main()
