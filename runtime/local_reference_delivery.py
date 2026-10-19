"""Unsigned public REFERENCE presentation export and readback.

The private source publication is verified only when exporting. Public readers
verify presentation hashes, identity, temporal metadata and all horse paragraphs.
They do not possess the raw source and cannot reverify it or a Runtime signature.
No capture, prediction, signing, Runtime request or notification is performed.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re

PROFILE = 'KM-URW-PUBLISHED-REFERENCE-PRESENTATION-v1'
DAY_PROFILE = 'KM-URW-PUBLISHED-REFERENCE-DAY-PRESENTATION-v1'
SCOPE = 'PUBLISHED_PRESENTATION_ONLY_SOURCE_RAW_NOT_REVERIFIED'
JST = timezone(timedelta(hours=9))
NOTICE = ('公開表示物の読戻し：本文・Race・全馬・凍結情報の整合性のみを確認。'
          'SOURCE生原本・正式署名の再検証は行っていません。検証Scope：'+SCOPE)


def sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
        separators=(',', ':')).encode()).hexdigest()


def _identity(intent):
    try:
        day = date.fromisoformat(intent['race_date']).isoformat()
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError('PUBLIC_REFERENCE_PRESENTATION_RACE_IDENTITY') from exc
    no = intent.get('race_no')
    if (intent.get('family_id') != 'LOCAL' or intent.get('venue_id') != 'URW'
            or day != intent['race_date'] or type(no) is not int or not 1 <= no <= 12):
        raise ValueError('PUBLIC_REFERENCE_PRESENTATION_RACE_IDENTITY')
    return {'family_id':'LOCAL','venue_id':'URW','race_date':day,'race_no':no,
            'race_id':f'KM-LOCAL-URW-{day.replace("-", "")}-R{no:02d}-REFERENCE-R1'}


def _time(value):
    try:
        instant = datetime.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValueError('PUBLIC_REFERENCE_PRESENTATION_TIME_INVALID') from exc
    if instant.tzinfo is None:
        raise ValueError('PUBLIC_REFERENCE_PRESENTATION_TIME_INVALID')
    return instant


def _digest(value):
    return isinstance(value,str) and re.fullmatch('[a-f0-9]{64}',value) is not None


def _validate(manifest, body_bytes, expected):
    if (not isinstance(manifest,dict) or manifest.get('profile') != PROFILE or manifest.get('verification_scope') != SCOPE
            or manifest.get('sha256') != sha({k:v for k,v in manifest.items() if k!='sha256'})):
        raise ValueError('PUBLIC_REFERENCE_PRESENTATION_MANIFEST_HASH_OR_SCOPE')
    if (type(manifest.get('revision')) is not int or manifest['revision'] != 1
            or type(manifest.get('race_no')) is not int
            or any(manifest.get(k) != v for k,v in expected.items())):
        raise ValueError('PUBLIC_REFERENCE_PRESENTATION_RACE_MISMATCH')
    if (len(body_bytes) > 2_000_000 or hashlib.sha256(body_bytes).hexdigest() != manifest.get('body_sha256')):
        raise ValueError('PUBLIC_REFERENCE_PRESENTATION_BODY_HASH')
    body = body_bytes.decode('utf-8')
    if any(manifest.get(k) is not False for k in ('production_authority','formal_handoff_allowed',
            'signed_final_claim','formal_final_proven','source_freshness_claim','actual_purchase')):
        raise ValueError('PUBLIC_REFERENCE_PRESENTATION_NONFORMAL_REQUIRED')
    if manifest.get('signed_source_claim') is not False or manifest.get('signature_verified') is not False:
        raise ValueError('PUBLIC_REFERENCE_PRESENTATION_NO_SIGNATURE_AUTHORITY')
    fetched, source_frozen, forecast_frozen, cutoff, post, exported = map(_time,
        [manifest.get(k) for k in ('source_fetched_at','source_frozen_at','forecast_frozen_at',
                                  'prediction_cutoff','scheduled_post_at','exported_at')])
    if (not fetched <= source_frozen <= forecast_frozen < cutoff < post
            or forecast_frozen > exported or exported > datetime.now(timezone.utc)
            or post.astimezone(JST).date().isoformat() != expected['race_date']):
        raise ValueError('PUBLIC_REFERENCE_PRESENTATION_TEMPORAL_BINDING')
    for key in ('evidence_sha256','forecast_sha256','original_answer_sha256'):
        if not _digest(manifest.get(key)):
            raise ValueError('PUBLIC_REFERENCE_PRESENTATION_PROVENANCE_REQUIRED')
    # The original ordinal reference exposes source-function component hashes,
    # not a fitted/executed model SHA. Do not invent one at publication time.
    components = manifest.get('method_components_sha256')
    if (manifest.get('model_sha256') is not None
            or manifest.get('model_sha256_status') != 'UNKNOWN_ORIGINAL_FIELD_ABSENT'
            or not isinstance(components,dict) or not components
            or any(not isinstance(k,str) or not _digest(v) for k,v in components.items())
            or manifest.get('method_binding_scope') != 'DERIVED_SOURCE_COMPONENT_BINDING_NOT_MODEL_EXECUTION_SHA'
            or manifest.get('method_binding_sha256') != sha({'method':manifest.get('method'),'components':components})):
        raise ValueError('PUBLIC_REFERENCE_PRESENTATION_MODEL_BINDING')
    parts = manifest.get('required_parts')
    runners = manifest.get('runners')
    if (not isinstance(parts,list) or not parts or any(not isinstance(p,str) or not p for p in parts)
            or manifest.get('required_parts_sha256') != sha(parts)
            or not isinstance(runners,list) or not 2 <= len(runners) <= 20
            or manifest.get('runner_count') != len(runners)):
        raise ValueError('PUBLIC_REFERENCE_PRESENTATION_PARTS_OR_RUNNERS')
    def clock(value):
        return _time(value).astimezone(JST).isoformat()
    metadata = [
        f"対象Race：浦和{expected['race_no']}R／{expected['race_date']}／{expected['race_id']}",
        '変更していない原本本文SHA256：'+manifest['original_answer_sha256'],
        f"発走予定：{clock(manifest['scheduled_post_at'])}／Cutoff：{clock(manifest['prediction_cutoff'])}",
        f"公式出馬表取得：{clock(manifest['source_fetched_at'])}／SOURCE凍結：{clock(manifest['source_frozen_at'])}／参考予想凍結：{clock(manifest['forecast_frozen_at'])}",
        f"Evidence SHA：{manifest['evidence_sha256']}／参考予想SHA：{manifest['forecast_sha256']}",
        '参考方式：'+str(manifest.get('method'))+'／方式Component SHA：'+json.dumps(components,ensure_ascii=False,sort_keys=True),
        'FORMAL：未成立', 'REFERENCE ONLY',
        f"元のREFERENCE評価対象：{manifest.get('runner_count')}頭",
    ]
    if any(part not in body for part in metadata):
        raise ValueError('PUBLIC_REFERENCE_PRESENTATION_METADATA_BODY_MISMATCH')
    found = re.findall(r'^- ([0-9]+) (.+?)：参考順位([^。]+)。(.*)$',body,re.M)
    expected_rows = {}
    for runner in runners:
        if not isinstance(runner,dict):
            raise ValueError('PUBLIC_REFERENCE_PRESENTATION_RUNNER_BINDING')
        no = runner.get('runner_id')
        rank = runner.get('reference_rank')
        if (not isinstance(no,str) or not re.fullmatch('[1-9][0-9]?',no)
                or no in expected_rows or not isinstance(runner.get('name'),str) or not runner['name']
                or rank is not None and (type(rank) is not int or rank < 1)):
            raise ValueError('PUBLIC_REFERENCE_PRESENTATION_RUNNER_BINDING')
        paragraph = runner.get('required_part')
        prefix = f"- {no} {runner['name']}：参考順位{rank or 'UNKNOWN'}。"
        if (not isinstance(paragraph,str) or not paragraph.startswith(prefix)
                or '近走確認範囲' not in paragraph or paragraph not in parts or paragraph not in body):
            raise ValueError('PUBLIC_REFERENCE_PRESENTATION_RUNNER_GROUNDS_REQUIRED')
        expected_rows[no] = (runner['name'],str(rank or 'UNKNOWN'))
    actual_rows = {no:(name,rank) for no,name,rank,_ in found}
    if len(found) != len(expected_rows) or actual_rows != expected_rows:
        raise ValueError('PUBLIC_REFERENCE_PRESENTATION_ALL_RUNNERS_REQUIRED')
    for prefix in ('展開見立て：','参考上位候補：','条件・欠測・不確実性：','公式情報源：','最終結論：'):
        if not any(part.startswith(prefix) and len(part)>len(prefix) for part in parts):
            raise ValueError('PUBLIC_REFERENCE_PRESENTATION_CONCLUSION_OR_GROUNDS_REQUIRED')
    from runtime.local_race_entry import reference_answer_content_check
    check = reference_answer_content_check(parts,body)
    if not check['content_complete']:
        raise ValueError('PUBLIC_REFERENCE_PRESENTATION_COMPLETE_BODY_REQUIRED')
    return body, check


def read_publication(root, intent):
    """Return an intact public display, or None only when that race is absent.

    A present but damaged publication holds; it never triggers new acquisition.
    This verifies unsigned published presentation integrity, not raw SOURCE,
    Runtime signatures, current Active runners or actual ChatGPT delivery.
    """
    expected = _identity(intent)
    folder = Path(root)/'runtime/local_reference_delivery'/expected['race_date']/f"R{expected['race_no']:02d}"
    if not folder.exists():
        return None
    try:
        if folder.is_symlink() or folder.parent.is_symlink() or any((folder/name).is_symlink() for name in ('manifest.json','readback.txt')):
            raise ValueError('PUBLIC_REFERENCE_PRESENTATION_SYMLINK_FORBIDDEN')
        manifest = json.loads((folder/'manifest.json').read_text())
        body, check = _validate(manifest,(folder/'readback.txt').read_bytes(),expected)
    except (OSError, UnicodeError, KeyError, TypeError, ValueError) as exc:
        raise ValueError('PUBLIC_REFERENCE_PRESENTATION_HOLD:'+str(exc)) from exc
    return {'status':'REFERENCE_AVAILABLE','execution_id':expected['race_id'],
        'reference_status':'NON-PRODUCTION / NON-FORMAL / REFERENCE ONLY',
        'reference_readback_only':True,'prediction_reexecution':False,
        'reference_generated_in_this_request':False,'formal_final_proven':False,
        'source_freshness_claim':False,'source_raw_reverified':False,'signature_verified':False,
        'verification_scope':SCOPE,'answer_origin':'PUBLISHED_REFERENCE_PRESENTATION',
        'answer_sha256':manifest['body_sha256'],'answer_required_parts':manifest['required_parts'],
        'publication_manifest_sha256':manifest['sha256'],
        'reference_prediction_sha256':manifest['forecast_sha256'],'evidence_sha256':manifest['evidence_sha256'],
        'reference_runner_count':manifest['runner_count'],
        'prediction_cutoff':manifest['prediction_cutoff'],'scheduled_post_at':manifest['scheduled_post_at'],
        'model_sha256':None,'model_sha256_status':manifest['model_sha256_status'],
        'method_components_sha256':manifest['method_components_sha256'],
        'answer_content_check':check,'completion':False,'runtime_post_count':0,
        'delivery':{'chat_render_verified':False,'user_acknowledgement_verified':False,
                    'external_notification_sent':False,'formal_delivery_verified':False}},body


def export_publication(source_folder, destination_root):
    """Export identical verified readback bytes; source files stay untouched."""
    from runtime.local_reference_day import verified_readback, immutable, encoded
    from runtime.local_race_entry import reference_readback_presentation
    source_folder = Path(source_folder)
    publication = json.loads((source_folder/'publication.json').read_text())
    expected = _identity(publication)
    publication, original = verified_readback(source_folder,{k:expected[k] for k in ('family_id','venue_id','race_date','race_no')})
    attempt = source_folder/publication['reference_directory']
    prediction = json.loads((attempt/'reference_prediction.json').read_text())
    source = json.loads((attempt/'reference_source.json').read_text())
    parts = json.loads((source_folder/'answer_parts.json').read_text())
    display, required = reference_readback_presentation(prediction,source,original,parts)
    raw = (source_folder/'readback.txt').read_bytes()
    if raw != display.encode():
        raise ValueError('PUBLIC_REFERENCE_EXPORT_ORIGINAL_READBACK_MISMATCH')
    card = next(s for s in source['sources'] if s.get('official') is True
                and s.get('source_class')=='OFFICIAL_RACE_CARD_CURRENT_STATE_BODY_WEIGHT')
    runners = []
    for runner in prediction['runners']:
        prefix = f"- {runner['runner_id']} {runner['name']}：参考順位"
        matched = [p for p in required if p.startswith(prefix)]
        if len(matched)!=1:
            raise ValueError('PUBLIC_REFERENCE_EXPORT_RUNNER_PARAGRAPH')
        runners.append({'runner_id':str(runner['runner_id']),'name':runner['name'],
            'reference_rank':runner['reference_rank'],'required_part':matched[0]})
    manifest = {**expected,'profile':PROFILE,'verification_scope':SCOPE,
        'revision':1,'scheduled_post_at':prediction['scheduled_post_at'],
        'prediction_cutoff':prediction['prediction_cutoff'],'source_fetched_at':card['fetched_at'],
        'source_frozen_at':prediction['source_freeze_at'],'forecast_frozen_at':prediction['frozen_at'],
        'exported_at':datetime.now(timezone.utc).isoformat(),'export_is_new_forecast':False,
        'evidence_sha256':prediction['source_snapshot_sha256'],'forecast_sha256':prediction['sha256'],
        'original_answer_sha256':publication['answer_sha256'],
        'body_sha256':hashlib.sha256(raw).hexdigest(),'model_sha256':None,
        'model_sha256_status':'UNKNOWN_ORIGINAL_FIELD_ABSENT','method':prediction['method'],
        'method_components_sha256':prediction['method_components_sha256'],
        'method_binding_sha256':sha({'method':prediction['method'],'components':prediction['method_components_sha256']}),
        'method_binding_scope':'DERIVED_SOURCE_COMPONENT_BINDING_NOT_MODEL_EXECUTION_SHA',
        'required_parts':required,'required_parts_sha256':sha(required),
        'runner_count':len(runners),'runners':runners,'production_authority':False,
        'formal_handoff_allowed':False,'signed_source_claim':False,'signed_final_claim':False,
        'formal_final_proven':False,'source_freshness_claim':False,'signature_verified':False,
        'actual_purchase':False,'recommended_pfs':'N/A','actual_purchase_pfs':'UNKNOWN',
        'chat_render_verified':False,'user_acknowledgement_verified':False,
        'origin_validation':'PRIVATE_ORIGINAL_VERIFIED_AT_EXPORT_NOT_REVERIFIED_BY_PUBLIC_READER'}
    if prediction.get('TEST_SYNTHETIC_ONLY') is True:
        manifest['TEST_SYNTHETIC_ONLY']=True
    manifest['sha256']=sha(manifest)
    _validate(manifest,raw,expected)
    folder=Path(destination_root)/'runtime/local_reference_delivery'/expected['race_date']/f"R{expected['race_no']:02d}"
    if (folder/'manifest.json').exists():
        prior=json.loads((folder/'manifest.json').read_text())
        if ({k:v for k,v in prior.items() if k not in ('exported_at','sha256')}
                != {k:v for k,v in manifest.items() if k not in ('exported_at','sha256')}):
            raise ValueError('PUBLIC_REFERENCE_EXPORT_IMMUTABLE_CONFLICT')
        read_publication(destination_root,expected)
        return prior
    immutable(folder/'readback.txt',raw)
    immutable(folder/'manifest.json',encoded(manifest))
    return manifest


def export_day(source_root, destination_root, day):
    """Project an already frozen twelve-race day without publishing its raw plan."""
    from runtime.local_reference_day import load_plan, immutable, encoded
    if date.fromisoformat(day).isoformat()!=day:
        raise ValueError('PUBLIC_REFERENCE_DAY_IDENTITY')
    folder=Path(source_root)/'runtime/local_reference'/day
    original_plan=load_plan(folder,day)
    rows=[]
    for no in range(1,13):
        m=export_publication(folder/f'R{no:02d}',destination_root)
        rows.append({k:m[k] for k in ('race_no','race_id','body_sha256','forecast_sha256',
            'evidence_sha256','runner_count','prediction_cutoff','scheduled_post_at')} |
            {'manifest_sha256':m['sha256']})
    index={'profile':DAY_PROFILE,'family_id':'LOCAL','venue_id':'URW','race_date':day,
        'verification_scope':SCOPE,'original_plan_sha256':original_plan['plan_sha256'],
        'original_plan_verification':'PRIVATE_FROZEN_PLAN_CHECKED_AT_EXPORT_NOT_FRESH_DISCOVERY',
        'exported_at':datetime.now(timezone.utc).isoformat(),'races':rows,
        'cohort_count':12,'current_discovery_count':0,'source_freshness_claim':False,
        'formal_registered_count':0,'signed_final_count':0,'runtime_post_count':0,
        'chat_render_verified':False,'user_delivery_verified':False,
        'permanent_autonomy_proven':False,'new_forecast_count':0}
    if all(json.loads((Path(destination_root)/'runtime/local_reference_delivery'/day/f'R{r["race_no"]:02d}'/'manifest.json').read_text()).get('TEST_SYNTHETIC_ONLY') is True for r in rows):
        index['TEST_SYNTHETIC_ONLY']=True
    index['sha256']=sha(index)
    target=Path(destination_root)/'runtime/local_reference_delivery'/day/'index.json'
    if target.exists():
        prior=json.loads(target.read_text())
        if ({k:v for k,v in prior.items() if k not in ('exported_at','sha256')}
                != {k:v for k,v in index.items() if k not in ('exported_at','sha256')}):
            raise ValueError('PUBLIC_REFERENCE_DAY_IMMUTABLE_CONFLICT')
        return prior
    immutable(target,encoded(index))
    return index


def read_delivery_day(root, day):
    """Read the fixed published cohort; a failed race cannot stop later reads.

    This is not a current official meeting discovery or SOURCE refresh. It
    creates no new forecast and gives no ordinary-chat/live-delivery credit.
    """
    if date.fromisoformat(day).isoformat()!=day:
        raise ValueError('PUBLIC_REFERENCE_DAY_IDENTITY')
    folder=Path(root)/'runtime/local_reference_delivery'/day
    if not folder.exists():
        return None
    try:
        index=json.loads((folder/'index.json').read_text())
        if (not isinstance(index,dict) or index.get('profile')!=DAY_PROFILE or index.get('verification_scope')!=SCOPE
                or index.get('sha256')!=sha({k:v for k,v in index.items() if k!='sha256'})
                or index.get('family_id')!='LOCAL' or index.get('venue_id')!='URW' or index.get('race_date')!=day
                or not _digest(index.get('original_plan_sha256'))
                or index.get('cohort_count')!=12 or type(index.get('current_discovery_count')) is not int
                or index['current_discovery_count']!=0
                or index.get('source_freshness_claim') is not False
                or not isinstance(index.get('races'),list) or any(not isinstance(r,dict) for r in index['races'])
                or [r.get('race_no') for r in index.get('races',[])]!=list(range(1,13))):
            raise ValueError('PUBLIC_REFERENCE_DAY_INDEX_BINDING')
    except (OSError,UnicodeError,KeyError,TypeError,ValueError) as exc:
        raise ValueError('PUBLIC_REFERENCE_DAY_HOLD:'+str(exc)) from exc
    rows=[]
    for saved in index['races']:
        no=saved['race_no']
        row={'race_no':no,'race_id':saved.get('race_id')}
        try:
            result=read_publication(root,{'family_id':'LOCAL','venue_id':'URW','race_date':day,'race_no':no})
            if result is None:
                raise ValueError('PUBLIC_REFERENCE_DAY_RACE_MISSING')
            report,_=result
            if (report['publication_manifest_sha256']!=saved.get('manifest_sha256')
                    or report['answer_sha256']!=saved.get('body_sha256')
                    or report['reference_prediction_sha256']!=saved.get('forecast_sha256')
                    or report['evidence_sha256']!=saved.get('evidence_sha256')
                    or report['execution_id']!=saved.get('race_id')
                    or report['reference_runner_count']!=saved.get('runner_count')
                    or report['prediction_cutoff']!=saved.get('prediction_cutoff')
                    or report['scheduled_post_at']!=saved.get('scheduled_post_at')):
                raise ValueError('PUBLIC_REFERENCE_DAY_RACE_MANIFEST_MISMATCH')
            row.update(reference_status='AVAILABLE_VERIFIED_PUBLISHED_PRESENTATION',
                       reference_readback_only=True,runner_count=saved['runner_count'],
                       manifest_sha256=saved['manifest_sha256'],body_sha256=saved['body_sha256'])
        except (OSError,UnicodeError,KeyError,TypeError,ValueError) as exc:
            row.update(reference_status='HOLD',first_failed_stage='PUBLIC_PRESENTATION_READBACK',code=str(exc))
        rows.append(row)
    count=sum(r['reference_status']=='AVAILABLE_VERIFIED_PUBLISHED_PRESENTATION' for r in rows)
    return {'profile':DAY_PROFILE,'family_id':'LOCAL','venue_id':'URW','race_date':day,
        'status':'PUBLISHED_PRESENTATION_READBACK_ONLY' if count==12 else 'PUBLISHED_PRESENTATION_PARTIAL_HOLD',
        'verification_scope':SCOPE,'original_plan_sha256':index['original_plan_sha256'],
        'projection_sha256':index['sha256'],'cohort_count':12,'current_discovery_count':0,
        'reference_complete_count':count,'reference_all_races_complete':count==12,'races':rows,
        'source_freshness_claim':False,'source_raw_reverified':False,'new_forecast_count':0,
        'formal_registered_count':0,'signed_final_count':0,'runtime_post_count':0,
        'new_paid_openai_api_requests':0,'chat_render_verified':False,
        'user_delivery_verified':False,'permanent_autonomy_proven':False}
