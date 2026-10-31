"""Canonical read model of an existing SOURCE/OIDC-bound JRA NO-BET.

No SOURCE acquisition, numerical calculation, KRS, signing, mail or activation.
The existing Terminal and SOURCE verifiers retain ownership of their contracts.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess
from datetime import datetime,timezone

PROFILE='KM-JRA-NO-BET-PRESENTATION-v1'
DELIVERY_SCOPE='JRA_VERIFIED_NO_BET_COMPLETE_BODY'
TRUST_POLICY={'repository':'b03la013-max/keibametrics-runtime',
              'source_workflow':'km-jra-source-first-runner.yml',
              'terminal_workflow':'km-jra-formal-single-entry.yml',
              'source_ref':'refs/heads/main','deny_self_hosted_runners':True,
              'source_trust_class':'GITHUB_ACTIONS_EPHEMERAL_ED25519_PLUS_GITHUB_OIDC_ATTESTATION'}


def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,
                                    separators=(',',':'),allow_nan=False).encode()).hexdigest()


def file_sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def instant(value):
    stamp=datetime.fromisoformat(str(value).replace('Z','+00:00'))
    if stamp.tzinfo is None:raise ValueError('NO_BET_PRESENTATION_TIMEZONE_REQUIRED')
    return stamp


class GitHubNoBetTrust:
    """Use the existing GitHub/Sigstore verifier; never accept a verified flag.

    Owner activation separately pins TRUST_POLICY's digest. The verifier binds
    the actual input file bytes, repository, workflow, main ref and code commit.
    Only its successful JSON result supplies independent witnessed timestamps.
    """
    def __init__(self,*,bundle_paths=None):
        self.cache={}
        self.bundle_paths=dict(bundle_paths or {})

    def verify(self,path,*,kind,code_sha,not_before,not_after):
        if kind not in {'source','terminal'} or not re.fullmatch(r'[0-9a-f]{40}',str(code_sha)):
            raise ValueError('NO_BET_OIDC_CODE_OR_KIND_INVALID')
        path=Path(path);before=file_sha(path)
        workflow=TRUST_POLICY[kind+'_workflow']
        key=(before,kind,code_sha,str(not_before),str(not_after))
        if key in self.cache:return self.cache[key]
        command=['gh','attestation','verify',str(path),'--repo',TRUST_POLICY['repository'],
                 '--signer-workflow',TRUST_POLICY['repository']+'/.github/workflows/'+workflow,
                 '--source-ref',TRUST_POLICY['source_ref'],'--source-digest',code_sha,
                 '--deny-self-hosted-runners','--format','json']
        if kind in self.bundle_paths:
            command+=['--bundle',str(Path(self.bundle_paths[kind]))]
        result=subprocess.run(command,capture_output=True,text=True,timeout=25,check=False)
        if result.returncode!=0:raise ValueError('NO_BET_INDEPENDENT_OIDC_NOT_VERIFIED:'+kind)
        values=json.loads(result.stdout)
        if not isinstance(values,list) or not values:raise ValueError('NO_BET_OIDC_RESULT_REQUIRED')
        qualified=[]
        for value in values:
            verified=value.get('verificationResult') or {}
            statement=verified.get('statement') or {}
            certificate=(verified.get('signature') or {}).get('certificate') or {}
            workflow_uri='https://github.com/'+TRUST_POLICY['repository']+'/.github/workflows/'+workflow+'@'+TRUST_POLICY['source_ref']
            if (certificate.get('issuer')!='https://token.actions.githubusercontent.com'
                    or certificate.get('subjectAlternativeName')!=workflow_uri
                    or certificate.get('sourceRepositoryDigest')!=code_sha
                    or certificate.get('sourceRepositoryRef')!=TRUST_POLICY['source_ref']
                    or certificate.get('runnerEnvironment')!='github-hosted'
                    or not any((subject.get('digest') or {}).get('sha256')==before
                               for subject in statement.get('subject') or [])):
                continue
            times=[]
            for stamp in verified.get('verifiedTimestamps') or []:
                value=stamp.get('timestamp') or stamp.get('time')
                if value:times.append(instant(value))
            eligible=[t for t in times if instant(not_before)<=t<=instant(not_after)]
            if eligible:qualified.append((min(eligible),digest(statement)))
        if not qualified or file_sha(path)!=before:
            raise ValueError('NO_BET_OIDC_BYTES_OR_PRE_CUTOFF_WITNESS_INVALID:'+kind)
        witnessed,statement_sha=min(qualified)
        proof={'artifact_file_sha256':before,'repository':TRUST_POLICY['repository'],
               'workflow':workflow,'source_ref':TRUST_POLICY['source_ref'],'source_digest':code_sha,
               'verified_timestamps':[witnessed.astimezone(timezone.utc).isoformat()],
               'verification_statement_sha256':statement_sha}
        self.cache[key]=proof
        return proof


def _basis(terminal_path,intent_path,source_envelope_path,*,root,producer_sha,trust):
    if not isinstance(trust,GitHubNoBetTrust):raise ValueError('NO_BET_INDEPENDENT_TRUST_VERIFIER_REQUIRED')
    from jra_source_runtime.verify_source_envelope import verify
    from jra_execution_maturity_bridge import source_checkpoint_manifest
    from jra_production_no_bet_terminal import verify_no_bet_terminal
    from jra_aki_no_bet_terminal import PROFILE as AKI_PROFILE,verify_aki_no_bet_terminal
    terminal_path,intent_path,source_envelope_path=map(Path,(terminal_path,intent_path,source_envelope_path))
    originals={path:path.read_bytes() for path in (terminal_path,intent_path,source_envelope_path)}
    terminal=json.loads(originals[terminal_path]);intent=json.loads(originals[intent_path])
    envelope=json.loads(originals[source_envelope_path]);receipt=envelope.get('receipt') or {}
    if (not re.fullmatch(r'KM-JRA-[A-Z]{3}-[0-9]{8}-R[0-9]{2}',str(terminal.get('race_id')))
            or not re.fullmatch(re.escape(str(terminal.get('race_id')))+r'-[A-Za-z0-9._-]{1,100}',
                                str(terminal.get('source_execution_id')))):
        raise ValueError('NO_BET_PRESENTATION_SAFE_RACE_EXECUTION_ID_REQUIRED')
    if terminal.get('profile')==AKI_PROFILE:
        decision=verify_aki_no_bet_terminal(terminal,race_id=intent.get('race_id'),require_live=True,root=root)
    else:decision=verify_no_bet_terminal(terminal,race_id=intent.get('race_id'),require_live=True)
    source=verify(source_envelope_path)
    checkpoint=source_checkpoint_manifest(envelope,terminal.get('source_execution_id'))
    clocks={'prediction_cutoff':terminal.get('prediction_cutoff') or checkpoint['prediction_cutoff'],
            'scheduled_post_at':terminal.get('scheduled_post_at') or intent.get('scheduled_post_at'),
            'source_freeze_at':terminal.get('source_freeze_at') or checkpoint['source_freeze_at']}
    report=terminal.get('failure_report') or {}
    authority=report.get('current_authority_manifest') or intent.get('current_authority_manifest')
    if not re.fullmatch(r'KM-FAMILY-CURRENT-AUTHORITY-[0-9]{8}-R[0-9]+',str(authority)):
        raise ValueError('NO_BET_PRESENTATION_AUTHORITY_REQUIRED')
    owner=json.loads((Path(root)/'profiles'/(authority.replace('-','_')+'.json')).read_text())
    if (owner.get('manifest_id')!=authority or intent.get('family_id')!='JRA'
            or source.get('family')!='JRA' or source.get('status')!='PASS' or receipt.get('phase')!='SOURCE'
            or receipt.get('errors') or envelope.get('github_repository')!=TRUST_POLICY['repository']
            or source.get('race_id')!=terminal.get('race_id')
            or (report and checkpoint!=report.get('source_checkpoint_manifest'))
            or (not report and terminal.get('source_checkpoint_manifest_sha256')!=checkpoint['sha256'])
            or terminal.get('signed_source_receipt_sha256')!=source.get('receipt_sha256')
            or terminal.get('source_snapshot_sha256')!=checkpoint['source_snapshot_sha256']
            or instant(intent['prediction_cutoff'])!=instant(clocks['prediction_cutoff'])
            or instant(intent['scheduled_post_at'])!=instant(clocks['scheduled_post_at'])
            or instant(checkpoint['prediction_cutoff'])!=instant(clocks['prediction_cutoff'])
            or instant(checkpoint['source_freeze_at'])!=instant(clocks['source_freeze_at'])
            or not instant(checkpoint['source_freeze_at'])<=instant(receipt['timestamp'])
                <=instant(terminal['created_at'])<=instant(clocks['prediction_cutoff'])<instant(clocks['scheduled_post_at'])):
        raise ValueError('NO_BET_PRESENTATION_SOURCE_OWNER_IDENTITY_OR_TIME_MISMATCH')
    official=(envelope.get('artifact') or {}).get('jra_official_runner_universe') or {}
    declared=official.get('runners') or []
    names={str(r.get('runner_id') or r.get('horse_no')):r.get('name') for r in declared}
    if (official.get('universe_type')!='ACTIVE' or not declared or len(names)!=len(declared)
            or set(names)!=set(terminal['index_universe'])):
        raise ValueError('NO_BET_PRESENTATION_ACTIVE_RUNNER_UNIVERSE_MISMATCH')
    proofs={'source':trust.verify(source_envelope_path,kind='source',code_sha=envelope.get('github_sha'),
                 not_before=receipt['timestamp'],not_after=terminal['created_at']),
            'terminal':trust.verify(terminal_path,kind='terminal',code_sha=producer_sha,
                 not_before=terminal['created_at'],not_after=clocks['prediction_cutoff'])}
    if any(path.read_bytes()!=raw for path,raw in originals.items()):
        raise ValueError('NO_BET_PRESENTATION_INPUT_BYTES_CHANGED_DURING_VERIFICATION')
    return terminal,intent,decision,authority,proofs,names,clocks


def _render(detail):
    lines=[detail['race_id'],'正式状態 NO_BET（Signed FINALとは別の正規Terminal）',
           'NO-BET種別：'+detail['subtype'],
           'Full20適格計算：'+str(detail['full20_eligible'])+'／正常AKI見送り数値判断：'+str(detail['normal_aki_no_bet']),
           '正式フル予測完走：False（Terminalの配送成立とは別）',
           '発走：'+detail['scheduled_post_at'],'Prediction Cutoff：'+detail['prediction_cutoff'],
           'SOURCE Freeze：'+detail['source_freeze_at'],
           'Terminal作成：'+detail['created_at'],'Authority：'+detail['authority'],
           '正式NO-BET理由：'+str(detail['decision_reason']),
           '買い目\n└─ NO-BET：0点・0円\nPFS：N/A（投資0円）',
           'PRE_KRS／KRS／Signed FINAL：未実行・未成立。未成立Role・券面を追加しない。',
           '本人閲覧・ACK：UNKNOWN','全馬20指数・原本Evidence：']
    for row in detail['runners']:
        lines.append('\n馬番 '+row['runner_id']+' '+str(row.get('name') or '馬名未収録'))
        for name,cell in row['indices'].items():
            lines.append(name+'：'+json.dumps(cell,ensure_ascii=False,sort_keys=True))
    lines+=['SOURCE SHA：'+detail['source_sha256'],'SOURCE Receipt：'+detail['source_receipt_sha256'],
            'NO-BET Terminal SHA：'+detail['terminal_sha256'],
            'Terminal原本：'+detail['terminal_ref'],
            'SOURCE/OIDC独立検証：'+json.dumps(detail['trust'],ensure_ascii=False,sort_keys=True),
            '事後読戻しと発走前Deliveryは別検収。実購入の証明ではない。']
    return '\n'.join(lines)+'\n'


def build_no_bet_presentation(terminal_path,*,intent_path,source_envelope_path,root,producer_sha,trust=None):
    trust=trust if trust is not None else GitHubNoBetTrust()
    terminal,intent,decision,authority,proofs,names,clocks=_basis(terminal_path,intent_path,source_envelope_path,
                                        root=root,producer_sha=producer_sha,trust=trust)
    rows=terminal['index_universe']
    # Values/Evidence come only from the attested Terminal ledger. Names come
    # from the bound signed SOURCE active universe, never auxiliary prepared rows.
    from jra_aki_no_bet_terminal import PROFILE as AKI_PROFILE
    from jra_production_no_bet_terminal import PROFILE as EVIDENCE_PROFILE
    subtype=('AKI_NO_BET' if terminal['profile']==AKI_PROFILE else 'EVIDENCE_NO_BET'
             if terminal['profile']==EVIDENCE_PROFILE else 'STATIC_OWNER_UNAUTHORIZED_NO_BET')
    full20=terminal.get('production_full20_ready') is True and all(
        cell.get('terminal_status')=='CALCULATED' for row in rows.values() for cell in row.values())
    detail={'race_id':terminal['race_id'],'status':'NO_BET','authority':authority,
            'subtype':subtype,'full20_eligible':full20,'normal_aki_no_bet':subtype=='AKI_NO_BET' and full20,
            'formal_full_prediction_completed':False,
            'source_freeze_at':clocks['source_freeze_at'],
            'created_at':terminal['created_at'],'prediction_cutoff':clocks['prediction_cutoff'],
            'scheduled_post_at':clocks['scheduled_post_at'],'decision_reason':terminal['decision_reason'],
            'clock_origins':{key:'TERMINAL' if terminal.get(key) else
                'SIGNED_SOURCE_CHECKPOINT' if key!='scheduled_post_at' else 'FORMAL_INTENT'
                for key in clocks},
            'ticket_count':0,'total_investment':0,'tickets':[],'pfs':None,'pfs_status':'N/A_ZERO_INVESTMENT',
            'signed_final_verified':False,'terminal_sha256':terminal['sha256'],
            'source_sha256':terminal['source_snapshot_sha256'],
            'source_receipt_sha256':terminal['signed_source_receipt_sha256'],
            'terminal_ref':'runtime/jra_no_bet_terminals/'+terminal['source_execution_id']+'.json',
            'runners':[{'runner_id':str(rid),'name':names.get(str(rid)),'indices':rows[rid]}
                       for rid in sorted(rows,key=lambda rid:int(rid))],
            'verification':decision,'trust':proofs,'trust_policy_sha256':digest(TRUST_POLICY)}
    from execution_store import require_public_storage
    require_public_storage(detail)
    text=_render(detail)
    manifest={'profile':PROFILE,'race_id':detail['race_id'],'terminal_sha256':terminal['sha256'],
              'subtype':subtype,'full20_eligible':full20,'normal_aki_no_bet':detail['normal_aki_no_bet'],
              'formal_full_prediction_completed':False,
              'source_sha256':detail['source_sha256'],'intent_sha256':digest(intent),
              'terminal_file_sha256':file_sha(terminal_path),'source_envelope_file_sha256':file_sha(source_envelope_path),
              'producer_sha':producer_sha,'trust_policy_sha256':digest(TRUST_POLICY),
              'detail_sha256':digest(detail),'text_sha256':hashlib.sha256(text.encode()).hexdigest(),
              'new_signature_issued':False,'user_delivery_verified':False}
    manifest['sha256']=digest(manifest)
    return {'manifest':manifest,'detail':detail,'text':text}


def save_no_bet_presentation(directory,bundle):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    files={'no_bet_presentation.json':json.dumps(bundle['manifest'],ensure_ascii=False,sort_keys=True,indent=2)+'\n',
           'no_bet_presentation_detail.json':json.dumps(bundle['detail'],ensure_ascii=False,sort_keys=True,indent=2)+'\n',
           'no_bet_presentation.md':bundle['text']}
    # Never replace an existing projection or make a new timestamp on retry.
    for name,value in files.items():
        path=directory/name
        if path.exists() and path.read_bytes()!=value.encode():raise ValueError('NO_BET_PRESENTATION_IMMUTABLE_CONFLICT')
    for name,value in files.items():
        path=directory/name
        if not path.exists():path.write_text(value)
    return bundle


def read_no_bet_presentation(directory,terminal_path,*,intent_path,source_envelope_path,root,producer_sha,trust=None):
    directory=Path(directory)
    saved={'manifest':json.loads((directory/'no_bet_presentation.json').read_text()),
           'detail':json.loads((directory/'no_bet_presentation_detail.json').read_text()),
           'text':(directory/'no_bet_presentation.md').read_text()}
    expected=build_no_bet_presentation(terminal_path,intent_path=intent_path,
                source_envelope_path=source_envelope_path,root=root,producer_sha=producer_sha,trust=trust)
    if saved!=expected:raise ValueError('NO_BET_PRESENTATION_CANONICAL_PROJECTION_MISMATCH')
    return saved
