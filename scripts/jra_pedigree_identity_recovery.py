"""Offline, exact official navigation-ID recovery; quarantined, never Production intake.

Opaque JRA CNAME locators are NOT asserted to be permanent horse/ancestry IDs.
No fuzzy names, external requests, token decoding or rewritten historical bytes.
"""
import base64,gzip,hashlib,json,re,sys,subprocess,os
from pathlib import Path
from collections import Counter,defaultdict
from datetime import datetime,timezone
from urllib.parse import urlsplit,parse_qs
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'runtime/jra_source_runtime')]
from verify_source_envelope import verify,sha_obj
from source_acquisition import _decode
from jra_pedigree_harvest import parse_horse_pedigree
from jra_horse_history import _date,_course,_int
from bs4 import BeautifulSoup
REPO='b03la013-max/keibametrics-runtime'
PARENT_KEYS=('sire','dam','damsire')
RUN_KEYS=('date','venue','race_name','surface','distance_m','finish','field_size')


def digest_bytes(raw):return hashlib.sha256(raw).hexdigest()
def stamp(value):
    t=datetime.fromisoformat(str(value).replace('Z','+00:00'))
    if t.tzinfo is None:raise ValueError('RECOVERY_TIMEZONE_REQUIRED')
    return t


def locator(url,kind):
    p=urlsplit(url)
    if (p.scheme!='https' or p.hostname!='www.jra.go.jp' or p.netloc!='www.jra.go.jp'
            or p.fragment or p.path!='/JRADB/access'+kind+'.html'):
        raise ValueError('RECOVERY_NON_OFFICIAL_LOCATOR')
    query=parse_qs(p.query,strict_parsing=True)
    if set(query)!={'CNAME'} or len(query['CNAME'])!=1:raise ValueError('RECOVERY_LOCATOR_QUERY')
    token=query['CNAME'][0]
    pattern=r'pw01dud[0-9]{12}/[0-9A-Fa-f]{2}' if kind=='U' else r'pw01sde[0-9]{22}/[0-9A-Fa-f]{2}'
    if not re.fullmatch(pattern,token):raise ValueError('RECOVERY_UNRECOGNIZED_LOCATOR')
    return token


def official_link(href,kind):
    return locator('https://www.jra.go.jp'+href if href.startswith('/') else href,kind)


def profile(snapshot):
    if (snapshot.get('snapshot_sha256')!=sha_obj({k:v for k,v in snapshot.items() if k!='snapshot_sha256'})
            or snapshot.get('authority')!='JRA_OFFICIAL' or snapshot.get('official') is not True
            or snapshot.get('http_status')!=200 or snapshot.get('raw_encoding')!='gzip+base64'):
        raise ValueError('RECOVERY_SNAPSHOT_BINDING')
    token=locator(snapshot['requested_url'],'U')
    if locator(snapshot['final_url'],'U')!=token:raise ValueError('RECOVERY_REDIRECT_IDENTITY')
    raw=gzip.decompress(base64.b64decode(snapshot['raw_gzip_b64'],validate=True))
    if len(raw)>6_000_000 or len(raw)!=snapshot['byte_count'] or digest_bytes(raw)!=snapshot['raw_sha256']:
        raise ValueError('RECOVERY_RAW_SHA')
    decoded=_decode(raw,snapshot['content_type']);ped=parse_horse_pedigree(decoded)
    if not all(ped.get(k) for k in ('horse_name',*PARENT_KEYS)):raise ValueError('RECOVERY_INCOMPLETE_PEDIGREE')
    soup=BeautifulSoup(decoded,'html.parser');parents={}
    for label,key in (('父','sire'),('母','dam'),('母の父','damsire')):
        cells=[]
        for dt in soup.select('dt'):
            if dt.get_text(strip=True).strip('：:')==label:
                dd=dt.find_next_sibling('dd')
                if dd:
                    copy=BeautifulSoup(str(dd),'html.parser')
                    for extra in copy.select('.sanku'):extra.decompose()
                    for link in copy.select('a[href]'):
                        if link.get_text(' ',strip=True)==ped[key]:
                            try:cells.append(official_link(link['href'],'U'))
                            except ValueError:pass  # foreign/unlinked ancestor is UNKNOWN, not a guessed JRA ID
        if len(set(cells))>1:raise ValueError('RECOVERY_PARENT_LOCATOR_AMBIGUOUS')
        parents[key]=cells[0] if cells else None
    runs=[]
    for table in soup.select('table'):
        rows=table.select('tr')
        if not rows:continue
        headers=[x.get_text(' ',strip=True) for x in rows[0].find_all(['th','td'],recursive=False)]
        if not {'年月日','場','レース名','距離','頭数','着順'}.issubset(headers):continue
        for tr in rows[1:]:
            cells=tr.find_all(['th','td'],recursive=False)
            def cell(key):
                idx=headers.index(key)
                return cells[idx] if idx<len(cells) else None
            def text(key):
                c=cell(key);return c.get_text(' ',strip=True) if c else ''
            date=_date(text('年月日'))
            if not date:continue
            surface,distance=_course(text('距離'));links=[]
            c=cell('レース名')
            for link in c.select('a[href]') if c else []:
                try:links.append(official_link(link['href'],'S'))
                except ValueError:pass
            if len(set(links))!=1:continue
            runs.append({'date':date,'venue':text('場'),'race_name':text('レース名'),
                         'surface':surface,'distance_m':distance,'finish':_int(text('着順')),
                         'field_size':_int(text('頭数')),'official_result_navigation_token':links[0]})
        break
    return {'profile_token':token,'pedigree':ped,'parent_profile_tokens':parents,'runs':runs}


def signature(h):return tuple(h.get(k) for k in ('horse_name',*PARENT_KEYS))
def run_key(run):return tuple(run.get(k) for k in RUN_KEYS)


def recover(root=ROOT,target_cutoff='2026-10-24T09:00:00+09:00'):
    root=Path(root);counts=Counter();observations=[];corpus_files={};targets=set()
    for path in sorted((root/'runtime/pedigree_corpus').glob('*.json')):
        raw=path.read_bytes();obj=json.loads(raw);rel=str(path.relative_to(root))
        valid=(obj.get('official') is True and obj.get('source')=='www.jra.go.jp'
               and obj.get('sha256')==digest_bytes(json.dumps({k:v for k,v in obj.items() if k!='sha256'},ensure_ascii=False,sort_keys=True).encode()))
        corpus_files[rel]={'file_sha256':digest_bytes(raw),'hash_valid':valid,'harvested_at':obj.get('harvested_at')}
        if not valid:counts['invalid_corpus_files']+=1;continue
        for i,h in enumerate(obj.get('horses',[])):
            observations.append((rel,i,h));targets.add(h.get('profile_token_sha256'))
            counts['horse_observations']+=1;counts['run_observations']+=len(h.get('runs',[]))
    index=defaultdict(list);proofs={};seen=set();source_files={}
    for path in sorted((root/'runtime/executions').glob('KM-JRA-*/SOURCE/runs/*/source_receipt_envelope.json')):
        counts['source_envelopes_seen']+=1
        try:
            checked=verify(path);env=json.loads(path.read_bytes());art=env['artifact']
            if (checked['github_repository']!=REPO or checked['family']!='JRA' or art.get('family_id')!='JRA'
                    or art['race_id']!=checked['race_id'] or art['source_snapshot_sha256']!=sha_obj({k:v for k,v in art.items() if k!='source_snapshot_sha256'})):
                raise ValueError('RECOVERY_SOURCE_IDENTITY')
            rel=str(path.relative_to(root));source_files[rel]=digest_bytes(path.read_bytes())
            counts['source_envelopes_crypto_verified']+=1
            for snap in art.get('sources',[]):
                if snap.get('source_class')!='OFFICIAL_JRA_HORSE_HISTORY':continue
                try:
                    token=locator(snap['requested_url'],'U')
                    if digest_bytes(token.encode()) not in targets:continue
                    sid=snap['snapshot_sha256']
                    if sid in seen:continue
                    record=profile(snap)
                    if stamp(snap['fetched_at'])>stamp(art['source_freeze_at']):raise ValueError('RECOVERY_SOURCE_TIME')
                    seen.add(sid)
                    proofs[sid]={'source_envelope':rel,'source_envelope_file_sha256':source_files[rel],
                                 'source_artifact_sha256':checked['artifact_sha256'],'receipt_sha256':checked['receipt_sha256'],
                                 'raw_sha256':snap['raw_sha256'],'snapshot_sha256':sid,
                                 'fetched_at':snap['fetched_at'],'source_freeze_at':art['source_freeze_at'],
                                 'github_run_id':checked['github_run_id'],'github_code_sha':checked['github_sha'],
                                 'crypto_verified':True,'oidc_reverified':False}
                    record['proof']=sid;index[digest_bytes(token.encode())].append(record)
                    counts['matched_raw_profiles']+=1
                except (ValueError,KeyError,TypeError,OSError) as exc:counts['raw_hold_'+type(exc).__name__+':'+str(exc)[:70]]+=1
        except Exception as exc:counts['envelope_hold_'+type(exc).__name__]+=1
    resolved=[];unresolved=Counter();names=defaultdict(set);identity_tokens=defaultdict(set)
    for rel,i,h in observations:
        names[h.get('horse_name')].add(signature(h));identity_tokens[signature(h)].add(h.get('profile_token_sha256'))
        matches=index.get(h.get('profile_token_sha256'),[])
        if not matches:unresolved['NO_EXACT_TOKEN_RAW_EVIDENCE']+=1;continue
        if {signature(m['pedigree']) for m in matches}!={signature(h)}:
            unresolved['CONFLICTING_PROFILE_PEDIGREE']+=1;continue
        parent_options={k:{m['parent_profile_tokens'][k] for m in matches if m['parent_profile_tokens'][k]} for k in PARENT_KEYS}
        if any(len(v)>1 for v in parent_options.values()):
            unresolved['CONFLICTING_PARENT_LOCATORS']+=1;continue
        parent_tokens={k:next(iter(v)) if v else None for k,v in parent_options.items()}
        parent_proofs={k:min((m for m in matches if m['parent_profile_tokens'][k]==token),
                            key=lambda m:stamp(proofs[m['proof']]['fetched_at']))['proof'] if token else None
                       for k,token in parent_tokens.items()}
        chosen=min(matches,key=lambda m:stamp(proofs[m['proof']]['fetched_at']))
        run_index=defaultdict(list)
        for m in matches:
            for run in m['runs']:run_index[run_key(run)].append((run['official_result_navigation_token'],m['proof']))
        bound=[]
        for j,run in enumerate(h.get('runs',[])):
            values=run_index.get(run_key(run),[])
            if len({token for token,_ in values})!=1:continue
            token,proof=min(values,key=lambda item:stamp(proofs[item[1]]['fetched_at']))
            available=max(stamp(corpus_files[rel]['harvested_at']),stamp(proofs[proof]['fetched_at']))
            if stamp(run['date']+'T00:00:00+09:00')>=stamp(target_cutoff):continue
            bound.append({'run_index':j,'official_result_navigation_token':token,'proof':proof,
                          'observed_at':proofs[proof]['fetched_at'],'chronology_before_target':available<stamp(target_cutoff)})
        proof=proofs[chosen['proof']]
        available=max(stamp(corpus_files[rel]['harvested_at']),stamp(proof['fetched_at']))
        resolved.append({'corpus_file':rel,'observation_index':i,'profile_token_sha256':h['profile_token_sha256'],
                         'official_profile_token':chosen['profile_token'],'parent_profile_tokens':parent_tokens,
                         'parent_profile_proofs':parent_proofs,
                         'permanent_horse_id':None,'permanent_sire_id':None,'permanent_damsire_id':None,
                         'identity_namespace':'JRA_OFFICIAL_NAVIGATION_CNAME_NOT_PERMANENT_REGISTRY_ID',
                         'proof':chosen['proof'],'original_observation_at':corpus_files[rel]['harvested_at'],
                         'identity_observed_at':proof['fetched_at'],'original_raw_bytes_equal':h.get('raw_sha256')==proof['raw_sha256'],
                         'earliest_content_available_at':available.isoformat(),'chronology_before_target':available<stamp(target_cutoff),
                         'run_bindings':bound,'research_training_eligible':False,'production_eligible':False})
    counts.update(profile_locator_resolved_observations=len(resolved),profile_locator_unresolved_observations=sum(unresolved.values()),
                  official_result_locator_resolved_runs=sum(len(r['run_bindings']) for r in resolved),
                  permanent_horse_ids_resolved=0,permanent_parent_ids_resolved=0,
                  same_name_multiple_pedigree_tuples=sum(len(v)>1 for v in names.values()),
                  same_pedigree_tuple_multiple_navigation_tokens=sum(len(v)>1 for v in identity_tokens.values()))
    counts['official_result_locator_unresolved_runs']=counts['run_observations']-counts['official_result_locator_resolved_runs']
    for key in PARENT_KEYS:
        counts[key+'_profile_locator_resolved_observations']=sum(bool(r['parent_profile_tokens'][key]) for r in resolved)
    out={'profile':'JRA-OFFICIAL-PEDIGREE-ID-RECOVERY-RESEARCH-v1','created_at':datetime.now(timezone.utc).isoformat(),
         'target_cutoff':target_cutoff,'production_effect':'NONE','counts':dict(counts),'unresolved':dict(unresolved),
         'corpus_files':corpus_files,'source_files':source_files,'raw_proofs':proofs,'resolved':resolved,
         'oidc_status':'NOT_REVERIFIED_LOCAL; stored PASS flags are not trusted as fresh OIDC proof',
         'research_training_eligible_observations':0,'production_eligible_observations':0,
         'temporal_scope':'Original observation, recovered identity/run evidence and target cutoff are separate; no historical backdate',
         'permanent_id_scope':'CNAME aliases are never merged or declared permanent IDs; no independent-offspring inflation',
         'oidc_path':'existing gh attestation verify, signer-workflow pinned before admission; Production requires separate Owner intake',
         'code_sha256':digest_bytes(Path(__file__).read_bytes())}
    out['sha256']=sha_obj(out);return out




def verify_recovery_bindings(recovery,root=ROOT):
    """Re-derive referenced identities from bytes, never from a rehashed sidecar.

    This validates content/Ed25519 consistency only. GitHub origin and provider
    timestamps still require the separate authenticated attestation verifier.
    """
    root=Path(root).resolve();cutoff=stamp(recovery['target_cutoff'])
    if recovery['sha256']!=sha_obj({k:v for k,v in recovery.items() if k!='sha256'}):
        raise ValueError('RECOVERY_REPORT_HASH')
    corpora={};raw_proofs={};sources={};seen_rows=set()
    def file_path(name,prefix):
        path=(root/name).resolve()
        if (not isinstance(name,str) or not str(name).startswith(prefix)
                or not path.is_relative_to((root/prefix).resolve()) or path.relative_to(root).as_posix()!=name):
            raise ValueError('RECOVERY_BINDING_PATH')
        return path
    def corpus(name):
        if name not in corpora:
            raw=file_path(name,'runtime/pedigree_corpus/').read_bytes();obj=json.loads(raw)
            expected=recovery['corpus_files'][name]
            if (digest_bytes(raw)!=expected['file_sha256'] or obj.get('official') is not True
                    or obj.get('source')!='www.jra.go.jp' or expected.get('harvested_at')!=obj.get('harvested_at')
                    or obj.get('sha256')!=digest_bytes(json.dumps({k:v for k,v in obj.items() if k!='sha256'},ensure_ascii=False,sort_keys=True).encode())):
                raise ValueError('RECOVERY_BINDING_CORPUS')
            stamp(obj['harvested_at']);corpora[name]=obj
        return corpora[name]
    def raw_proof(sid):
        if sid not in raw_proofs:
            proof=recovery['raw_proofs'][sid];name=proof['source_envelope']
            if name not in sources:
                path=file_path(name,'runtime/executions/');raw=path.read_bytes();env=json.loads(raw);art=env['artifact'];checked=verify(path)
                if (digest_bytes(raw)!=recovery['source_files'][name]
                        or checked['github_repository']!=REPO or checked['family']!='JRA'
                        or art.get('family_id')!='JRA' or art['race_id']!=checked['race_id']
                        or art['source_snapshot_sha256']!=sha_obj({k:v for k,v in art.items() if k!='source_snapshot_sha256'})):
                    raise ValueError('RECOVERY_BINDING_SOURCE')
                sources[name]=(digest_bytes(raw),checked,art['source_freeze_at'],
                               [s for s in art.get('sources',[]) if s.get('snapshot_sha256') in recovery['raw_proofs']])
            file_sha,checked,source_freeze,snaps=sources[name]
            snapshots=[s for s in snaps if s.get('snapshot_sha256')==sid]
            if len(snapshots)!=1 or snapshots[0].get('source_class')!='OFFICIAL_JRA_HORSE_HISTORY':
                raise ValueError('RECOVERY_BINDING_SNAPSHOT')
            snap=snapshots[0];parsed=profile(snap)
            expected={'source_envelope_file_sha256':file_sha,
                      'source_artifact_sha256':checked['artifact_sha256'],'receipt_sha256':checked['receipt_sha256'],
                      'raw_sha256':snap['raw_sha256'],'snapshot_sha256':sid,'fetched_at':snap['fetched_at'],
                      'source_freeze_at':source_freeze,'github_run_id':checked['github_run_id'],
                      'github_code_sha':checked['github_sha']}
            if any(proof.get(k)!=v for k,v in expected.items()) or stamp(snap['fetched_at'])>stamp(source_freeze):
                raise ValueError('RECOVERY_BINDING_RAW_PROOF')
            raw_proofs[sid]=(proof,parsed)
        return raw_proofs[sid]
    for row in recovery['resolved']:
        name=row['corpus_file'];index=row['observation_index'];key=(name,index)
        if type(index) is not int or index<0 or key in seen_rows:raise ValueError('RECOVERY_BINDING_DUPLICATE_OBSERVATION')
        seen_rows.add(key);obj=corpus(name)
        if index>=len(obj['horses']):raise ValueError('RECOVERY_BINDING_OBSERVATION_INDEX')
        horse=obj['horses'][index];proof,parsed=raw_proof(row['proof'])
        token=parsed['profile_token'];available=max(stamp(obj['harvested_at']),stamp(proof['fetched_at']))
        if (signature(parsed['pedigree'])!=signature(horse) or digest_bytes(token.encode())!=horse['profile_token_sha256']
                or row['profile_token_sha256']!=horse['profile_token_sha256'] or row['official_profile_token']!=token
                or row['identity_namespace']!='JRA_OFFICIAL_NAVIGATION_CNAME_NOT_PERMANENT_REGISTRY_ID'
                or any(row.get(k) is not None for k in ('permanent_horse_id','permanent_sire_id','permanent_damsire_id'))
                or row.get('research_training_eligible') is not False or row.get('production_eligible') is not False
                or row['original_observation_at']!=obj['harvested_at'] or row['identity_observed_at']!=proof['fetched_at']
                or row['original_raw_bytes_equal']!=(horse.get('raw_sha256')==proof['raw_sha256'])
                or stamp(row['earliest_content_available_at'])!=available
                or row['chronology_before_target']!=(available<cutoff)):
            raise ValueError('RECOVERY_BINDING_PROFILE')
        for parent in PARENT_KEYS:
            parent_token=row['parent_profile_tokens'][parent];sid=row['parent_profile_proofs'][parent]
            if (parent_token is None)!=(sid is None):raise ValueError('RECOVERY_BINDING_PARENT')
            if sid is not None:
                _,parent_raw=raw_proof(sid)
                if (parent_raw['profile_token']!=token or signature(parent_raw['pedigree'])!=signature(horse)
                        or parent_raw['parent_profile_tokens'][parent]!=parent_token):
                    raise ValueError('RECOVERY_BINDING_PARENT')
        seen_runs=set()
        for run in row['run_bindings']:
            index=run['run_index']
            if type(index) is not int or index<0 or index>=len(horse['runs']) or index in seen_runs:
                raise ValueError('RECOVERY_BINDING_RUN_INDEX')
            seen_runs.add(index);item=horse['runs'][index];run_proof,run_raw=raw_proof(run['proof'])
            tokens={r['official_result_navigation_token'] for r in run_raw['runs'] if run_key(r)==run_key(item)}
            available=max(stamp(obj['harvested_at']),stamp(run_proof['fetched_at']))
            if (run_raw['profile_token']!=token or signature(run_raw['pedigree'])!=signature(horse)
                    or tokens!={run['official_result_navigation_token']}
                    or run['observed_at']!=run_proof['fetched_at']
                    or stamp(item['date']+'T00:00:00+09:00')>=cutoff
                    or run['chronology_before_target']!=(available<cutoff)):
                raise ValueError('RECOVERY_BINDING_RUN')
    return True


def reverify_oidc(recovery,root=ROOT,*,runner=subprocess.run):
    """Use the existing GitHub attestation path; a refusal stops all further calls."""
    root=Path(root)
    if recovery['sha256']!=sha_obj({k:v for k,v in recovery.items() if k!='sha256'}):
        raise ValueError('RECOVERY_REPORT_HASH')
    verify_recovery_bindings(recovery,root)
    needed={r['corpus_file'] for r in recovery['resolved']}
    for r in recovery['resolved']:
        for sid in {r['proof'],*(x['proof'] for x in r['run_bindings']),
                    *(p for p in r.get('parent_profile_proofs',{}).values() if p)}:
            needed.add(recovery['raw_proofs'][sid]['source_envelope'])
    verified={};stopped=False
    for name in sorted(needed):
        expected=(recovery['corpus_files'].get(name) or {}).get('file_sha256') or recovery['source_files'].get(name)
        path=root/name
        if not expected or digest_bytes(path.read_bytes())!=expected:raise ValueError('RECOVERY_ATTESTED_FILE_CHANGED')
        workflows=(['km-jra-pedigree-verified-backfill.yml','km-jra-pedigree-corpus-harvest.yml']
                   if name in recovery['corpus_files'] else ['km-jra-source-first-runner.yml'])
        source_digests={p['github_code_sha'] for p in recovery['raw_proofs'].values()
                        if p['source_envelope']==name} if name not in recovery['corpus_files'] else set()
        if source_digests and (len(source_digests)!=1 or not re.fullmatch(r'[0-9a-f]{40}',next(iter(source_digests)))):
            raise ValueError('RECOVERY_SOURCE_CODE_BINDING')
        outcomes=[];qualified=False
        for workflow in workflows:
            try:
                command=['gh','attestation','verify',str(path),'--repo',REPO,'--signer-workflow',
                         REPO+'/.github/workflows/'+workflow,'--source-ref','refs/heads/main',
                         '--deny-self-hosted-runners','--format','json']
                if source_digests:command+=['--source-digest',next(iter(source_digests))]
                proc=runner(command,capture_output=True,text=True,timeout=25)
                message=(proc.stderr or '')
                if proc.returncode:
                    refusal=bool(re.search(r'HTTP (?:401|403|429)|rate limit|permission denied|not authorized|authentication required',message,re.I))
                    unavailable=bool(re.search(r'HTTP 5[0-9]{2}|unknown flag|unknown command|gh auth login',message,re.I))
                    outcomes.append({'signer_workflow':workflow,'verified':False,
                                     'status':'REFUSED_STOPPED_NO_RETRY' if refusal else 'VERIFIER_UNAVAILABLE_STOPPED' if unavailable else 'ATTESTATION_OR_SIGNER_NOT_VERIFIED',
                                     'detail':message[-400:]})
                    if refusal or unavailable:stopped=True;break
                    continue
                data=json.loads(proc.stdout);times=[]
                for item in data:
                    for observed in (item.get('verificationResult') or {}).get('verifiedTimestamps') or []:
                        value=observed.get('timestamp') or observed.get('time')
                        if value:times.append(value)
                qualified=bool(times) and min(map(stamp,times))<stamp(recovery['target_cutoff'])
                outcomes.append({'signer_workflow':workflow,'verified':True,'verified_timestamps':times,
                                 'before_target_cutoff':qualified,'verification_output_sha256':digest_bytes(proc.stdout.encode())})
                break
            except (OSError,subprocess.SubprocessError,ValueError) as exc:
                outcomes.append({'verified':False,'status':'VERIFIER_ERROR','detail':type(exc).__name__});stopped=True;break
        verified[name]={'file_sha256':expected,'qualified':qualified,'checks':outcomes}
        if stopped:break
    qualified=[];runs=0
    for row in recovery['resolved']:
        corpus_ok=verified.get(row['corpus_file'],{}).get('qualified',False)
        proof=recovery['raw_proofs'][row['proof']]
        if corpus_ok and row['chronology_before_target'] and verified.get(proof['source_envelope'],{}).get('qualified',False):
            qualified.append({'corpus_file':row['corpus_file'],'observation_index':row['observation_index'],
                              'official_profile_token':row['official_profile_token'],'permanent_horse_id':None,
                              'identity_namespace':row['identity_namespace'],'production_eligible':False})
        for run in row['run_bindings']:
            source=recovery['raw_proofs'][run['proof']]['source_envelope']
            runs+=bool(corpus_ok and run['chronology_before_target'] and verified.get(source,{}).get('qualified',False))
    out={'profile':'JRA-PEDIGREE-RECOVERY-OIDC-RESEARCH-QUALIFICATION-v1',
         'recovery_sha256':recovery['sha256'],'observed_at':datetime.now(timezone.utc).isoformat(),
         'target_cutoff':recovery['target_cutoff'],'file_verifications':verified,'stopped_on_refusal':stopped,
         'qualified_profile_locator_observations':len(qualified),'qualified_result_locator_runs':runs,
         'qualified':qualified,'permanent_registry_ids_resolved':0,'research_training_eligible':False,
         'production_eligible':False,'production_effect':'NONE',
         'scope':'Attested official navigation identity lookup only; not permanent registry IDs, model fit or Production admission'}
    out['sha256']=sha_obj(out);return out


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--out',default='research/jra_pedigree/identity_recovery.json');p.add_argument('--target-cutoff',default='2026-10-24T09:00:00+09:00');p.add_argument('--verify-oidc',action='store_true');a=p.parse_args()
    result=recover(target_cutoff=a.target_cutoff);path=ROOT/a.out;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n')
    print(json.dumps({'counts':result['counts'],'unresolved':result['unresolved'],'oidc':result['oidc_status']},ensure_ascii=False))

    if a.verify_oidc:
        qualification=reverify_oidc(result)
        path.with_name('identity_recovery_oidc.json').write_text(json.dumps(qualification,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n')
        print(json.dumps({k:qualification[k] for k in ('qualified_profile_locator_observations','qualified_result_locator_runs','stopped_on_refusal')},ensure_ascii=False))
