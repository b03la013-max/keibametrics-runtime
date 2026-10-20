"""Explicit SOURCE-first LOCAL entry. No prediction authority is inferred."""
from __future__ import annotations
import argparse
import copy
from datetime import date, datetime, timezone
import os
import re
import json
from pathlib import Path
from runtime import formal_execution_orchestrator as o
from runtime.local_fullnumerical_production import materialize_production
from runtime.local_numerical_authority_gate import assess
from runtime.local_static_input_resolver import resolve as resolve_static_input, input_packet
from runtime.local_race_key_shadow_owner import compile_shadow, compile_urw_candidate, ShadowOwnerError
from runtime.local_production_static_owner import build_formal_static, bind_urw_numerical_context, StaticOwnerError


def resolve_chat_intent(query, *, now=None):
    """Resolve one explicit URW race to the existing two-path entry.

    This is a callable Work/CLI entry, not a claim that ChatGPT automatically
    invokes GitHub. Existing authorized FORMAL requests keep their own path.
    """
    import unicodedata
    from runtime.local_race_key_intake import JST
    text = unicodedata.normalize('NFKC', str(query))
    matches = re.findall(r'(?:浦和|URW)\s*(?:第)?\s*(\d{1,2})\s*(?:R|レース|競走)', text, re.I)
    all_numbers = re.findall(r'(\d{1,2})\s*(?:R|レース|競走)', text, re.I)
    if len(matches) != 1 or len(all_numbers) != 1 or not 1 <= int(matches[0]) <= 12:
        raise ValueError('CHAT_ONE_EXPLICIT_URW_RACE_REQUIRED')
    if any(name in text for name in ('川崎', '船橋', '大井', '盛岡', '金沢', '名古屋', 'JRA', 'ばんえい')):
        raise ValueError('CHAT_AMBIGUOUS_OR_OUT_OF_SCOPE_VENUE')
    dates = re.findall(r'\d{4}-\d{2}-\d{2}', text)
    dates += ['-'.join((y, m.zfill(2), d.zfill(2))) for y, m, d in re.findall(r'(\d{4})年(\d{1,2})月(\d{1,2})日', text)]
    if len(set(dates)) > 1:
        raise ValueError('CHAT_AMBIGUOUS_RACE_DATE')
    if not dates and any(word in text for word in ('明日', '昨日', 'あす', 'あした')):
        raise ValueError('CHAT_EXPLICIT_DATE_REQUIRED_FOR_OTHER_DAY')
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError('CHAT_NOW_TIMEZONE_REQUIRED')
    day = date.fromisoformat(dates[0]) if dates else now.astimezone(JST).date()
    return {'family_id': 'LOCAL', 'venue_id': 'URW', 'race_date': day.isoformat(),
            'race_no': int(matches[0]), 'prediction_mode': 'AUTO',
            'requested_formal': '正式' in text}


def _chat_final(intent):
    """Search every Formal revision of this race; never generate a FINAL."""
    from runtime.local_race_key_gate import readback_final
    day = date.fromisoformat(intent['race_date']).strftime('%Y%m%d')
    prefix = f"KM-LOCAL-URW-{day}-R{intent['race_no']:02d}-"
    reports = []
    for path in sorted((o.ROOT/'runtime/executions').glob(prefix+'*')):
        if not re.fullmatch(re.escape(prefix) + r'(?:LIVE|FORMAL)-R[1-9]\d*', path.name):
            continue
        if not (path/'FORMAL/LATEST.json').is_file():
            continue
        report = readback_final(path.name, repo_root=o.ROOT)
        if report.get('signed_final_pass'):
            # Check the official SOURCE identity as well as the receipt ID.
            try:
                saved = o.resolve_phase(path.name, 'SOURCE', root=o.ROOT/'runtime/executions')
                context = o._load_checkpoint_json(saved, 'source_receipt_envelope.json')['artifact']['source_race_context']
                if any(str(context.get(k)).replace('/', '-') != str(intent[k]) for k in ('venue_id', 'race_date', 'race_no')):
                    raise ValueError('CHAT_FINAL_OFFICIAL_RACE_MISMATCH')
            except (OSError, ValueError, KeyError, TypeError) as exc:
                report = {**report, 'signed_final_pass': False, 'status': 'HOLD_READBACK', 'reason': str(exc)}
        reports.append(report)
    valid = [r for r in reports if r.get('signed_final_pass') and r.get('render_available')]
    if len(valid) == 1 and all(r.get('status') != 'HOLD_READBACK' for r in reports):
        return valid[0], reports
    # Competing or damaged revisions are reconciled, not silently superseded.
    return None, reports


def chat_formal_status(intent):
    """Read existing authority/dated-plan gates, without Runtime POST or writes."""
    from runtime.family_authority_guard import resolve_current_authority
    from runtime import local_race_day_dispatcher as dispatcher
    now = datetime.now(timezone.utc)
    blockers = []
    observation = {'status': 'BLOCKED', 'checked_at': now.isoformat(), 'runtime_post_count': 0}
    def block(stage, code):
        blockers.append({'stage': stage, 'code': code})
    try:
        _, authority = resolve_current_authority(root=o.ROOT, now=now)
        observation['current_authority_manifest'] = authority['manifest_id']
        owner = json.loads((o.ROOT/'profiles/local_production_static_owner_20261014_v1.json').read_text())
        observation['owner_venues'] = owner.get('venues', [])
        if (owner.get('enabled') is not True or 'URW' not in owner.get('venues', [])
                or owner.get('family_authority_basis') != authority['manifest_id']):
            block('AUTHORIZATION', 'VENUE_OWNER_NOT_AUTHORIZED')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        block('AUTHORIZATION', 'CURRENT_AUTHORITY_OR_OWNER_UNRESOLVED:'+str(exc))
    try:
        numeric = assess()
        observation['numerical'] = numeric
        if numeric.get('status') != 'READY':
            block('NUMERICAL', 'PRODUCTION_NUMERICAL_AUTHORITY_NOT_READY')
        if any(numeric.get(k) is not True for k in ('prediction_consumption_authorized',
                'krs_consumption_authorized', 'ticket_consumption_authorized', 'capital_consumption_authorized')):
            block('AUTHORIZATION', 'URW_NUMERICAL_DOWNSTREAM_CONSUMPTION_NOT_AUTHORIZED')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        block('NUMERICAL', 'NUMERICAL_AUTHORITY_UNRESOLVED:'+str(exc))
    name = intent['race_date']+'-URW'
    plan_path = o.ROOT/'runtime/local_race_day_plan'/(name+'.json')
    approval_path = o.ROOT/'profiles/local_autonomous_approvals'/(name+'.json')
    observation.update(plan_path=str(plan_path), approval_path=str(approval_path))
    try:
        if not approval_path.is_file():
            raise ValueError('DATED_OWNER_APPROVAL_REQUIRED')
        if os.environ.get('KM_LOCAL_AUTONOMOUS_ENABLED') != 'true':
            raise ValueError('OWNER_ACTIVATION_AND_DATED_APPROVAL_REQUIRED')
        plan = json.loads(plan_path.read_text())
        approval = json.loads(approval_path.read_text())
        if (plan.get('venue_id'), plan.get('race_date')) != ('URW', intent['race_date']):
            raise ValueError('CHAT_DATED_PLAN_IDENTITY_MISMATCH')
        if dispatcher.sha({k:v for k,v in plan.items() if k != 'plan_sha256'}) != plan.get('plan_sha256'):
            raise ValueError('DAY_PLAN_SHA_MISMATCH')
        dispatcher.authorization(approval, plan, o.ROOT, now)
        races = [r for r in plan['races'] if r['fields']['race_no'] == intent['race_no']]
        if len(races) != 1 or intent['race_no'] not in approval['race_numbers']:
            raise ValueError('CHAT_RACE_NOT_IN_APPROVED_SUBSET')
        o.check_deadline(races[0]['fields'], phase='SOURCE')
        observation.update(plan_sha256=plan['plan_sha256'], execution_id=races[0]['execution_id'],
                           source_status='FRESH_SIGNED_SOURCE_REQUIRED_IN_EXISTING_WORKFLOW')
    except (OSError, ValueError, KeyError, TypeError, o.FormalOrchestrationError) as exc:
        block('ACTIVATION', str(exc))
    observation['blockers'] = blockers
    if not blockers:
        observation['status'] = 'AUTHORIZED_EXISTING_DISPATCH'
    observation['first_failed_stage'] = blockers[0]['stage'] if blockers else None
    observation['code'] = blockers[0]['code'] if blockers else None
    observation['last_verified_stage'] = 'CURRENT_AUTHORITY' if observation.get('current_authority_manifest') else 'NONE'
    observation['resume_from'] = 'EXISTING_DATED_AUTHORIZED_RACE_KEY_WORKFLOW'
    observation['required_action'] = ('Qualify the URW Owner and authorized consumers, then approve the exact dated race/plan/runtime/cost scope; '
        'the existing workflow must acquire and verify fresh Signed SOURCE. Reference supplies no Formal authority.') if blockers else 'Use the existing claim-before-dispatch worker for this race only.'
    return observation


def _chat_reference(intent, *, output, run_id):
    """Check the current permitted card before returning a prestart reference."""
    from runtime import urw_nankan_reference_source as nankan
    from runtime.local_race_key_intake import JST
    import hashlib
    import tempfile
    if date.fromisoformat(intent['race_date']) < datetime.now(timezone.utc).astimezone(JST).date():
        return _chat_frozen_reference(intent, output=output, run_id=run_id)
    try:
        # Both raw evidence and the complete derived chat response are private.
        # An Actions/Git output must never acquire these private provider bytes.
        nankan.private_directory(output)
        root = Path(os.environ.get('KM_URW_PRIVATE_REFERENCE_ROOT',
            str(Path(tempfile.gettempdir())/f'km-urw-private-reference-{os.getuid()}')))
        private = nankan.private_directory(root/intent['race_date']/f"R{intent['race_no']:02d}")
        prior = {json.loads(p.read_text())['forecast_sha256']
                 for p in private.glob('**/publication.json')}
        manifest, evidence, prediction, content = nankan.capture_race(
            intent['race_date'], intent['race_no'], private, refresh=True)
        parts = content.rstrip('\n').split('\n\n')
        generated = manifest['forecast_sha256'] not in prior
        eid = (f"KM-LOCAL-URW-{intent['race_date'].replace('-', '')}-R{intent['race_no']:02d}"
               f"-NANKAN-REFERENCE-{manifest['forecast_sha256'][:12]}")
        return {'execution_id': eid, 'status': 'CURRENT_PRIVATE_REFERENCE_AVAILABLE',
            'answer_origin': 'CURRENT_OFFICIAL_NANKAN_PRIVATE_REFERENCE',
            'private_reference_root': str(root),
            'answer_sha256': hashlib.sha256(content.encode()).hexdigest(),
            'answer_required_parts': parts, 'reference_readback_only': not generated,
            'reference_generated_in_this_request': generated, 'prediction_reexecution': generated,
            'current_official_checked': True, 'source_freshness_claim': True,
            'current_official_checked_at': datetime.now(timezone.utc).isoformat(),
            'source_raw_reverified': True, 'active_verified': False,
            'source_frozen_at': evidence['source_frozen_at'],
            'forecast_frozen_at': manifest['frozen_at'],
            'source_sha256': evidence['sources'][3]['raw_sha256'],
            'reference_prediction_sha256': manifest['forecast_sha256'],
            'reference_runner_count': manifest['runner_count'],
            'formal_final_proven': False, 'production_authority': False,
            'signed_source_claim': False,
            'verification_scope': 'PRIVATE_NANKAN_RAW_CHECKED_UNSIGNED_REFERENCE_ONLY',
            'public_redistribution_authorized': False}, content
    except (OSError, ValueError, KeyError, TypeError) as exc:
        # A fresh-source failure may show an intact historical freeze, but
        # must never silently label that freeze as the current forecast.
        code = exc.receipt['code'] if isinstance(exc, nankan.NankanError) else str(exc)
        try:
            reference, content = _chat_frozen_reference(intent, output=output, run_id=run_id,
                                                       allow_generation=False)
        except (OSError, ValueError, KeyError, TypeError) as missing:
            raise exc from missing
        notice = ('当日公式再確認HOLD：'+code+'。以下は旧Freezeの履歴であり、'
                  '現在の出走集合を反映した新しい予測ではありません。')
        content = notice+'\n\n'+content
        return {**reference, 'current_official_checked': False,
            'current_official_hold': code, 'source_freshness_claim': False,
            'answer_sha256': hashlib.sha256(content.encode()).hexdigest(),
            'answer_required_parts': [notice]+reference.get('answer_required_parts', [])}, content


def _chat_frozen_reference(intent, *, output, run_id, allow_generation=True):
    """Find the original prestart reference before considering a new capture."""
    day = date.fromisoformat(intent['race_date']).strftime('%Y%m%d')
    base = o.ROOT/'research/urw_owner'
    published = o.ROOT/'runtime/local_reference'/intent['race_date']/f"R{intent['race_no']:02d}"
    if (published/'publication.json').exists():
        from runtime.local_reference_day import verified_readback
        expected={k:intent[k] for k in ('family_id','venue_id','race_date','race_no')}
        publication,content=verified_readback(published,expected)
        reference=published/publication['reference_directory']
        original=json.loads((reference/'reference_intent.json').read_text())
        report=run_reference(original,output=reference,run_id=run_id)
        prediction=json.loads((reference/'reference_prediction.json').read_text())
        source=json.loads((reference/'reference_source.json').read_text())
        parts=json.loads((published/'answer_parts.json').read_text())
        content,parts=reference_readback_presentation(prediction,source,content,parts)
        import hashlib
        return {**report,'answer_sha256':hashlib.sha256(content.encode()).hexdigest(),
            'original_answer_sha256':publication['answer_sha256'],
            'answer_required_parts':parts,
            'answer_origin':'VERIFIED_FROZEN_REFERENCE_PUBLICATION'},content
    paths = [output/'reference', o.ROOT/'runtime/local_reference'/intent['race_date']/f"R{intent['race_no']:02d}"/'reference',
             base/(day+'_reference')/f"R{intent['race_no']:02d}",
             base/(day+'_prediction_availability')/'reference_repair'/f"R{intent['race_no']:02d}",
             base/(day+'_prediction_availability')/f"chat_R{intent['race_no']:02d}"]
    # An explicit old reference output remains readable with --query too.
    if (output/'reference_prediction.json').is_file():
        paths.insert(0, output)
    selected = next((p for p in paths if (p/'reference_prediction.json').exists()
                     or (p/'reference_intent.json').exists()), None)
    if selected is None:
        # A public display is distinct from raw SOURCE verification. Only use
        # it when no canonical/local raw cache exists; corruption never falls
        # through from an existing canonical publication into this path.
        if not published.exists():
            from runtime.local_reference_delivery import read_publication, NOTICE
            public = read_publication(o.ROOT,intent)
            if public is not None:
                import hashlib
                report, content = public
                content = NOTICE+'\n\n'+content
                return {**report,'answer_sha256':hashlib.sha256(content.encode()).hexdigest(),
                    'answer_required_parts':[NOTICE]+report['answer_required_parts']},content
        if not allow_generation:
            raise ValueError('CURRENT_REFERENCE_UNAVAILABLE_AND_NO_FROZEN_HISTORY')
        # A genuinely new chat request uses the same durable race publication
        # as the day worker, rather than leaving an unindexed research cache.
        # The race lock also serializes a simultaneous day-worker request.
        from runtime.local_reference_day import one_race
        generated = False
        def generate(request, *, output, run_id):
            nonlocal generated
            result = run_reference(request, output=output, run_id=run_id)
            generated = result.get('reference_readback_only') is not True
            return result
        one_race(published, intent['race_date'], intent['race_no'], generate=generate)
        report, content = _chat_frozen_reference(intent, output=output, run_id=run_id)
        report['reference_generated_in_this_request'] = generated
        return report, content
    ref_intent = {k:intent[k] for k in ('family_id', 'venue_id', 'race_date', 'race_no')}
    ref_intent['prediction_mode'] = 'REFERENCE'
    report = run_reference(ref_intent, output=selected, run_id=run_id)
    # Keep the frozen JSON and its original rendering immutable. Presentation
    # can be completed from that same verified SOURCE without a new forecast.
    prediction = json.loads((selected/'reference_prediction.json').read_text())
    source = json.loads((selected/'reference_source.json').read_text())
    content, parts = reference_answer(prediction, source)
    import hashlib
    original_answer_sha256=hashlib.sha256(content.encode()).hexdigest()
    content,parts=reference_readback_presentation(prediction,source,content,parts)
    report = {**report, 'answer_sha256': hashlib.sha256(content.encode()).hexdigest(),
              'original_answer_sha256':original_answer_sha256,
              'answer_required_parts': parts, 'answer_origin': 'VERIFIED_FROZEN_REFERENCE_AND_ITS_SOURCE'}
    return report, content


def reference_answer(prediction, source):
    """Complete an unsigned presentation using only the original frozen bytes.

    The legacy reference_prediction.md remains a verified immutable cache file.
    No call here captures evidence, fits a model, changes a rank or issues FINAL.
    """
    from html import unescape
    from runtime.local_race_day_dispatcher import raw_html
    from runtime.local_physical.source_acquisition import _html_text, verify_source_artifact
    from runtime.local_race_key_shadow_owner import _sha
    from runtime.local_race_key_intake import JST
    context = source.get('source_race_context') or {}
    if (any(str(prediction.get(k)) != str(context.get(k)) for k in ('venue_id', 'race_date', 'race_no'))
            or prediction.get('race_id') != source.get('race_id')
            or any(prediction.get(k) != source.get(k) for k in ('source_freeze_at', 'prediction_cutoff', 'scheduled_post_at'))
            or prediction.get('source_snapshot_sha256') != source.get('source_snapshot_sha256')
            or prediction.get('sha256') != _sha({k:v for k,v in prediction.items() if k != 'sha256'})
            or not verify_source_artifact(source)[0]):
        raise ValueError('REFERENCE_ANSWER_SOURCE_BINDING_HOLD')
    if (prediction.get('venue_id') != 'URW'
            or any(prediction.get(k) is not False for k in ('production_authority', 'formal_handoff_allowed', 'signed_final_claim'))):
        raise ValueError('REFERENCE_ANSWER_FORMAL_AUTHORITY_FORBIDDEN')
    def clock(value):
        instant = datetime.fromisoformat(value)
        if instant.tzinfo is None:
            raise ValueError('REFERENCE_ANSWER_TIMEZONE_REQUIRED')
        return instant.astimezone(JST).isoformat()
    if not (datetime.fromisoformat(source['source_freeze_at']) <= datetime.fromisoformat(prediction['frozen_at'])
            < datetime.fromisoformat(prediction['prediction_cutoff']) < datetime.fromisoformat(prediction['scheduled_post_at'])):
        raise ValueError('REFERENCE_ANSWER_TEMPORAL_HOLD')
    cards = [s for s in source['sources'] if s.get('official') is True
             and s.get('source_class') == 'OFFICIAL_RACE_CARD_CURRENT_STATE_BODY_WEIGHT']
    if len(cards) != 1:
        raise ValueError('REFERENCE_ANSWER_OFFICIAL_CARD_REQUIRED')
    card = cards[0]
    if not (datetime.fromisoformat(card['fetched_at']) <= datetime.fromisoformat(source['source_freeze_at'])
            <= datetime.fromisoformat(prediction['frozen_at']) <= datetime.now(timezone.utc)):
        raise ValueError('REFERENCE_ANSWER_SOURCE_TIME_HOLD')
    # NAR's race heading is before the runner table; never use a historical
    # race name embedded in a runner's past starts.
    head = raw_html(card).split('競走馬')[0]
    titles = re.findall(r'<h3\b[^>]*>(.*?)</h3>', head, re.S | re.I)
    title = re.sub(r'\s+', ' ', unescape(_html_text(titles[0]))).strip() if titles else 'UNKNOWN'
    cancelled = set(prediction.get('cancelled_runners') or [])
    rows = prediction['runners']
    expected = {str(r['runner_id']): r['name'] for r in source['declared_runner_universe']['runners']
                if str(r['runner_id']) not in cancelled}
    if (len(rows) != len(expected) or {str(r['runner_id']):r['name'] for r in rows} != expected):
        raise ValueError('REFERENCE_ANSWER_ALL_RUNNERS_REQUIRED')
    parts = [prediction['status'], f"浦和{prediction['race_no']}R｜{prediction['race_date']}｜競走名：{title}",
        f"発走予定：{clock(prediction['scheduled_post_at'])}／Cutoff：{clock(prediction['prediction_cutoff'])}",
        f"公式出馬表取得：{clock(card['fetched_at'])}／SOURCE凍結：{clock(prediction['source_freeze_at'])}／参考予想凍結：{clock(prediction['frozen_at'])}",
        'FORMAL：未成立。正式29指数・独立W/P2/P3・KRS・MEC・Capital・Signed FINAL・正式買い目は本REFERENCEから成立しません。',
        '全馬の参考評価（既存の記録比較順位を保持。同場同距離は出馬表の近走確認範囲の集計で、通算の「場」「距」成績ではありません）']
    for row in sorted(rows, key=lambda r:int(r['runner_id'])):
        f = row['facts']; runs = row['past_starts']; recent = runs[0] if runs else None
        evidence = f"近走確認範囲の浦和同距離{f['exact_races']}戦・{f['exact_wins']}勝・3着内{f['exact_podiums']}回"
        if recent:
            evidence += f"。直近{recent['date']} {recent['venue']} {recent['distance']}m {recent['finish']}着・通過{recent['positions']}"
        else:
            evidence += '。近走の具体的成績UNKNOWN'
        conditions = row.get('current_conditions') or {}
        distance = conditions.get('current_distance_m')
        change = (f"。距離変更：{recent['distance']}→{distance}m" if recent and distance else '。距離変更UNKNOWN')
        unknown = '同条件未確認を能力不足とは扱いません。' if row['reference_rank'] is None else ''
        parts.append(f"- {row['runner_id']} {row['name']}：参考順位{row['reference_rank'] or 'UNKNOWN'}。{evidence}{change}。{unknown}当日の位置取得・圧力・状態・条件変更の効果UNKNOWN。")
    if cancelled:
        names = {str(r['runner_id']):r['name'] for r in source['declared_runner_universe']['runners']}
        parts.append('取消・除外（元のSOURCE時点）：'+ '、'.join(f'{r} {names[r]}' for r in sorted(cancelled, key=int)))
    leaders = prediction.get('pace_hypothesis', {}).get('possible_front_runners') or []
    names = {str(r['runner_id']):r['name'] for r in rows}
    front = '、'.join(f'{r} {names[r]}' for r in leaders if r in names) or 'UNKNOWN'
    parts.append('展開見立て：過去に前方を取った馬は'+front+'。同じ行動を取る場合の先行競合という条件付き仮説です。今回の逃げ・初速・競り合い・失速量はUNKNOWN。')
    ranked = [r for r in rows if r['reference_rank'] is not None]
    top_rank = sorted({r['reference_rank'] for r in ranked})[:3]
    top = '、'.join(f"{r['runner_id']} {r['name']}（{r['reference_rank']}位）" for r in ranked if r['reference_rank'] in top_rank) or 'UNKNOWN'
    parts += ['参考上位候補：'+top+'。未検証の同条件記録比較であり、UNKNOWN馬より強いとの証明ではありません。',
        '条件・欠測・不確実性：元の宣言出走馬の比較であり、現在のVerified Active・取消変更・馬体状態は未確認。血統・騎手の数値効果と実勝率はUNKNOWN。',
        '公式情報源：'+card['final_url'],
        f"Evidence SHA：{prediction['source_snapshot_sha256']}／参考予想SHA：{prediction['sha256']}",
        '参考方式：'+prediction['method']+'／方式Component SHA：'+json.dumps(prediction.get('method_components_sha256',{}),ensure_ascii=False,sort_keys=True),
        '最終結論：上記を元の凍結時点の非正式参考評価として読戻しました。FORMAL HOLDを維持し、正式予測・購入認可・現在の予測への更新とは扱いません。']
    return '\n\n'.join(parts)+'\n', parts


def reference_readback_presentation(prediction, source, original_body, original_parts):
    """Bind display metadata to the same frozen card, retaining the whole original.

    In a new-horse race no past-start distance appears in the original prose.
    Supply the current course explicitly so a client need not fill that gap
    from a previous race. This derivative never rewrites the frozen answer.
    """
    from html import unescape
    import hashlib
    import unicodedata
    from runtime.local_race_day_dispatcher import raw_html
    from runtime.local_physical.source_acquisition import _html_text
    _,required=reference_answer(prediction,source)  # original identity/hash/time guards
    if (not reference_answer_content_check(required,original_body)['content_complete']
            or not reference_answer_content_check(original_parts,original_body)['content_complete']):
        raise ValueError('REFERENCE_ORIGINAL_COMPLETE_BODY_REQUIRED')
    card=next(s for s in source['sources']
        if s.get('official') is True and s.get('source_class')=='OFFICIAL_RACE_CARD_CURRENT_STATE_BODY_WEIGHT')
    header=re.sub(r'\s+','',unicodedata.normalize('NFKC',unescape(
        _html_text(raw_html(card).split('競走馬')[0]))))
    day=date.fromisoformat(prediction['race_date'])
    courses=re.findall(r'(ダート|芝)([0-9,]+)m\((左|右)\)',header)
    if (f'{day.year}年{day.month}月{day.day}日' not in header
            or f"浦和第{prediction['race_no']}競走" not in header or len(courses)!=1):
        raise ValueError('REFERENCE_RACE_COURSE_HEADER_HOLD')
    surface,distance,direction=courses[0];distance=int(distance.replace(',',''))
    if any(r.get('current_conditions',{}).get('current_distance_m')!=distance for r in prediction['runners']):
        raise ValueError('REFERENCE_RACE_COURSE_SOURCE_MISMATCH')
    context=[
        '表示用Race照合：同じ凍結SOURCEから抽出。新規取得・再予測なし。原本にない情報を別Raceから補わないでください。',
        f"対象Race：浦和{prediction['race_no']}R／{prediction['race_date']}／{prediction['race_id']}",
        f'コース：浦和{surface}{distance}m（{direction}）',
        f"元のREFERENCE評価対象：{len(prediction['runners'])}頭（現在のVerified Active確定ではありません）",
        '変更していない原本本文SHA256：'+hashlib.sha256(original_body.encode()).hexdigest(),
        '以下に元の本文全体を保持します。元の取得・凍結時刻・順位・UNKNOWN・根拠・結論を変更しません。']
    return '\n\n'.join(context)+'\n\n'+original_body,context+original_parts


def reference_answer_content_check(parts, body):
    """Check actual returned/observed text; a status or byte count is no proof."""
    def normalized(text):
        import unicodedata
        return re.sub(r'\s+', '', unicodedata.normalize('NFKC', text))
    text = normalized(body)
    missing = [part for part in parts if normalized(part) not in text]
    return {'content_complete': bool(parts) and not missing, 'missing_parts': missing,
            'scope': 'SUPPLIED_BODY_ONLY_NOT_CHATGPT_RENDER_OR_USER_RECEIPT'}


def run_chat(intent, *, output, run_id):
    """FINAL first, authorized existing dispatch second, independent reference third."""
    if (intent.get('family_id') != 'LOCAL' or intent.get('venue_id') != 'URW'
            or type(intent.get('race_no')) is not int or not 1 <= intent['race_no'] <= 12):
        raise ValueError('CHAT_ONE_EXPLICIT_URW_RACE_REQUIRED')
    date.fromisoformat(intent['race_date'])
    if any(k in intent for k in ('execution_id', 'race_id')):
        raise ValueError('CHAT_IDENTITY_MUST_BE_RESOLVED_FROM_VENUE_DATE_RACE')
    if any(k in intent for k in ('static_prediction', 'signature', 'source_receipt_envelope', 'final_prediction_package')):
        raise ValueError('CHAT_CANNOT_SUPPLY_FORMAL_AUTHORITY_OR_PREDICTION')
    output.mkdir(parents=True, exist_ok=True, mode=0o700)
    final, search = _chat_final(intent)
    report = {'status': 'BOTH_UNAVAILABLE', 'race': {k:intent[k] for k in ('venue_id','race_date','race_no')},
              'observed_at': datetime.now(timezone.utc).isoformat(), 'final_search': search,
              'completion': False, 'formal_final_proven': False,
              'delivery': {'message_generated': False, 'external_notification_sent': False,
                           'user_acknowledgement_verified': False, 'formal_delivery_verified': False}}
    if final is None:
        formal = chat_formal_status(intent)
        if any(r.get('status') == 'HOLD_READBACK' for r in search) or len([r for r in search if r.get('signed_final_pass')]) > 1:
            formal.update(status='BLOCKED', first_failed_stage='FINAL', code='EXISTING_FINAL_RECONCILIATION_REQUIRED')
        report['formal'] = formal
        if formal['status'] == 'AUTHORIZED_EXISTING_DISPATCH':
            # Reuse the exact existing publisher/claim/worker. Do not create a
            # chat orchestrator or let one request dispatch other approved races.
            from runtime import local_race_day_dispatcher as dispatcher
            try:
                plan_path = Path(formal['plan_path'])
                plan = json.loads(plan_path.read_text())
                _, step = dispatcher.prepare_worker(o.ROOT, plan, plan_path,
                    plan_path.with_suffix('.state.json'), Path(formal['approval_path']),
                    only_execution_id=formal['execution_id'])
                state = step()
                cell = state['races'].get(formal['execution_id'], {})
                report['formal_dispatch'] = cell
                final, _ = _chat_final(intent)
                if cell.get('status') == 'DISPATCH_ACKNOWLEDGED_MONITOR_CHECKPOINTS':
                    formal['status'] = 'DISPATCH_OBSERVED_FINAL_NOT_YET_VERIFIED'
                elif cell.get('status') == 'WAIT_DISPATCH_WINDOW':
                    formal.update(status='WAITING_APPROVED_DISPATCH_WINDOW', code=cell['status'])
                else:
                    from runtime.formal_failure_diagnostics import failure_stage_for
                    code = cell.get('error') or cell.get('status') or 'EXISTING_DISPATCH_STATUS_MISSING'
                    formal.update(status='BLOCKED', first_failed_stage=failure_stage_for(code), code=code)
            except (OSError, ValueError, KeyError, TypeError, RuntimeError) as exc:
                formal.update(status='BLOCKED', first_failed_stage='RUNTIME', code=str(exc))
    if final is not None:
        report.update(status='FORMAL_VERIFIED', formal_final_proven=True, final=final,
                      execution_id=final['execution_id'], prediction_reexecution=False)
        message = ('FORMAL VERIFIED\n\n'+final['execution_id']+'\n\n'
            +'FINAL SHA: '+final['final_receipt_sha256']+'\n成立: '+final['freeze_time']
            +'\n署名: '+final['signature']+'\n点数: '+str(final.get('rendered_ticket_count','UNKNOWN'))
            +'\n総投資額: '+str(final['rendered_investment'])+'円\n\n'
            +'全馬・役割の正本:\n```json\n'+json.dumps(final['canonical_prediction']['prediction_package'],ensure_ascii=False,indent=2)
            +'\n```\n\n'+final['canonical_tree']+'\n\n通知・ユーザー受領は未確認です。\n')
    else:
        formal = report['formal']
        try:
            reference, content = _chat_reference(intent, output=output, run_id=run_id)
            report.update(status='FORMAL_BLOCKED_REFERENCE_AVAILABLE' if formal['status']=='BLOCKED'
                          else 'FORMAL_PENDING_REFERENCE_AVAILABLE', reference=reference,
                          execution_id=reference['execution_id'],
                          prediction_reexecution=reference.get('prediction_reexecution', False),
                          reference_generation_executed=reference.get('reference_generated_in_this_request',
                              reference.get('reference_readback_only') is not True))
            message = (f"FORMAL {formal['status']}：{formal.get('first_failed_stage') or 'FINAL'}／{formal.get('code') or formal['status']}\n\n"
                +f"チャット読戻し: {datetime.now(timezone.utc).isoformat()}。下記の観測・凍結時刻を維持し、現在のActive確定とは扱いません。\n\n"+content)
            report['answer_content_check'] = reference_answer_content_check(reference.get('answer_required_parts') or [], message)
            report['delivery']['chat_render_verified'] = False
        except (OSError, ValueError, KeyError, TypeError, RuntimeError) as exc:
            from runtime.formal_failure_diagnostics import failure_stage_for
            from runtime.urw_reference_source_policy import source_policy_failure
            cause = str(exc.__cause__ or exc)
            report['reference'] = {'status':'UNAVAILABLE', 'first_failed_stage':failure_stage_for(exc), 'code':str(exc),
                'root_cause':cause, 'last_verified_stage':'UNKNOWN', 'resume_from':'EXACT_ORIGINAL_REFERENCE_OR_PRE_CUTOFF_OFFICIAL_CARD',
                'required_action':'Restore the matching original files when damaged; without a saved reference, acquire complete official evidence before cutoff. Never backdate or regenerate an expired race.'}
            policy = source_policy_failure(exc)
            if policy:
                report['reference'].update(policy, root_cause=policy['code'],
                    required_action='Use an eligible original frozen reference or an officially permitted pre-cutoff source. Do not bypass robots or regenerate after cutoff.')
                evidence = policy['source_policy']
                detail = (f"DATA_SOURCE_POLICY／{policy['code']}／{evidence['reason']}\n"
                    +f"対象URL：{evidence.get('target_url', 'UNKNOWN')}\nrobots：{evidence['robots_url']}\n"
                    +f"robots SHA：{evidence.get('robots_sha256', 'UNKNOWN')}\n"
                    +'取得元ポリシーでREFERENCE取得を停止しました。保存済み原本又は許可された公式事前SOURCEが必要です。')
            else:
                detail = f"{str(exc)}／{cause}\n公式出馬表・全出走馬・事前凍結Artifactの不足又は整合性を確認してください。"
            report['reference']['unverified_information'] = ['対象Raceの全出走馬集合', '各馬の評価・根拠', 'REFERENCEの完成本文']
            missing = (policy['source_policy'].get('target_url', '公式出馬表URL未確認') if policy
                       else '公式出馬表・全出走馬集合・評価根拠・整合する事前凍結本文')
            message = (f"BOTH UNAVAILABLE\n\nFORMAL：{formal.get('first_failed_stage')}／{formal.get('code')}\n"
                       +f"REFERENCE：{detail}\n取得対象Raceの全出走馬と各馬評価は未確認です。期限後の新規予測は行いません。\n\n"
                       +f"最終結論：正式予測は未成立。参考全馬評価も未完成。取得不能・未確認：{missing}。\n")
    report['delivery']['message_generated'] = True
    report['final_search_scope'] = 'MATERIALIZED_CANONICAL_EXECUTION_STORE_NOT_A_REMOTE_ARTIFACT_SEARCH'
    report['message'] = message
    # Keep legacy reference files immutable when their directory was requested.
    (output/'chat_response.md').write_text(message, encoding='utf-8')
    o._write(output/'chat_entry_report.json', report)
    return report


def _reference_availability_report(intent, *, output, run_id, prediction, eid):
    from runtime.family_authority_guard import resolve_current_authority
    authority = {'status': 'UNKNOWN'}
    try:
        _, canon = resolve_current_authority()
        authority = {'manifest_id': canon['manifest_id'], 'status': 'RESOLVED_FOR_FORMAL_DIAGNOSIS_ONLY'}
    except (ValueError, OSError, KeyError) as exc:
        authority['error'] = str(exc)
    try:
        policy = json.loads((o.ROOT/'profiles/local_production_static_owner_20261014_v1.json').read_text())
        formal_stop = ('VENUE_OWNER_NOT_AUTHORIZED' if policy.get('enabled') is not True or 'URW' not in policy.get('venues', [])
                       else 'FORMAL_REQUIRES_SEPARATE_AUTHORIZED_SINGLE_ENTRY')
    except (ValueError, OSError, TypeError, AttributeError):
        formal_stop = 'FORMAL_OWNER_POLICY_UNRESOLVED'
    report = {'status': 'REFERENCE_AVAILABLE', 'reference_status': prediction['status'],
        'execution_id': eid, 'run_id': run_id, 'reference_prediction_sha256': prediction['sha256'],
        'reference_message_path': str(output/'reference_prediction.md'), 'reference_available': True,
        'completion': False, 'formal_final_proven': False, 'formal_registration': False,
        'formal_availability': {'status': 'HOLD', 'first_failed_stage': 'AUTHORIZATION', 'code': formal_stop,
            'last_verified_stage': 'NONE', 'independent_reference_available': True,
            'resume_from': 'DATED_AUTHORIZED_FORMAL_SINGLE_ENTRY',
            'required_action': 'Owner quality/scope, exact dated activation and approved Runtime submission; reference evidence grants none of these.'},
        'current_authority_observation': authority, 'runtime_post_count': 0, 'new_paid_api_requests': 0,
        'signed_source_count': 0, 'signed_final_count': 0,
        'delivery': {'message_generated': True, 'external_notification_sent': False,
                     'user_acknowledgement_verified': False, 'formal_delivery_verified': False}}
    return report


def run_reference(intent, *, output, run_id):
    """Use the existing unsigned official capture/parser, no Runtime writes."""
    from scripts.urw_candidate_krs_replay import capture_public_urw_sources
    from runtime.local_physical.nar_runner_universe import enrich_source_artifact
    from runtime.local_physical.source_acquisition import sha_obj
    from runtime.local_race_key_shadow_owner import compile_reference_prediction, render_reference_prediction
    if (intent.get('family_id', 'LOCAL') != 'LOCAL' or intent.get('venue_id') != 'URW'
            or type(intent.get('race_no')) is not int or not 1 <= intent['race_no'] <= 12):
        raise ValueError('REFERENCE_URW_IDENTITY_REQUIRED')
    if any(key in intent for key in ('static_prediction', 'signature', 'source_receipt_envelope', 'final_prediction_package')):
        raise ValueError('REFERENCE_FORMAL_INPUT_MIXING_FORBIDDEN')
    day = date.fromisoformat(intent['race_date'])
    eid = f"KM-LOCAL-URW-{day:%Y%m%d}-R{intent['race_no']:02d}-REFERENCE-R1"
    if any(intent.get(k) not in (None, eid) for k in ('execution_id', 'race_id')):
        raise ValueError('REFERENCE_EXECUTION_ID_MISMATCH')
    if (output/'entry_report.json').exists() or (output/'reference_prediction.json').exists():
        # A repeated pull reads the exact original reference, including after
        # cutoff. It cannot refresh its clock, call SOURCE or create a FINAL.
        from runtime.local_race_key_shadow_owner import _sha
        from runtime.local_physical.source_acquisition import verify_source_artifact
        try:
            prior_path = output/'entry_report.json'
            prior = json.loads(prior_path.read_text()) if prior_path.exists() else None
            prediction = json.loads((output/'reference_prediction.json').read_text())
            source = json.loads((output/'reference_source.json').read_text())
            original = json.loads((output/'reference_intent.json').read_text())
            rendered = render_reference_prediction(prediction)
            message_path = output/'reference_prediction.md'
            if ((prior is not None and (prior.get('status') != 'REFERENCE_AVAILABLE' or prior.get('execution_id') != eid))
                    or prediction.get('race_id') != eid or source.get('race_id') != eid
                    or any(original.get(k) != intent.get(k) for k in ('venue_id', 'race_date', 'race_no'))
                    or prediction.get('sha256') != _sha({k:v for k,v in prediction.items() if k!='sha256'})
                    or (prior is not None and prior.get('reference_prediction_sha256') != prediction['sha256'])
                    or prediction['source_snapshot_sha256'] != source['source_snapshot_sha256']
                    or prediction.get('source_freeze_at') != source.get('source_freeze_at')
                    or prediction.get('prediction_cutoff') != source.get('prediction_cutoff')
                    or prediction.get('scheduled_post_at') != source.get('scheduled_post_at')
                    or any(prediction.get(k) is not False for k in ('production_authority','formal_handoff_allowed','signed_final_claim'))
                    or not verify_source_artifact(source)[0]
                    or not (datetime.fromisoformat(source['source_freeze_at'])
                            <= datetime.fromisoformat(prediction['frozen_at']) <= datetime.now(timezone.utc))
                    or datetime.fromisoformat(prediction['frozen_at']) >= datetime.fromisoformat(prediction['prediction_cutoff'])
                    or (message_path.exists() and message_path.read_text() != rendered)
                    or (prior is not None and not message_path.exists())):
                raise ValueError('REFERENCE_CACHE_INTEGRITY_HOLD')
            # A crash after the forecast freeze but before its presentation
            # receipt is recoverable from those exact bytes, even after cutoff.
            # Existing conflicting prose or receipts remain a hard HOLD.
            if prior is None:
                reference_answer(prediction, source)
                if not message_path.exists():
                    with message_path.open('x', encoding='utf-8') as message:
                        message.write(rendered)
                prior = _reference_availability_report(intent, output=output, run_id=run_id,
                    prediction=prediction, eid=eid)
                with prior_path.open('x', encoding='utf-8') as receipt:
                    json.dump(prior, receipt, ensure_ascii=False, sort_keys=True, indent=2)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise ValueError('REFERENCE_OUTPUT_ALREADY_EXISTS_NO_REEXECUTION') from exc
        return {**prior, 'reference_message_path': str(output/'reference_prediction.md'),
                'reference_readback_only': True, 'prediction_reexecution': False,
                'source_freshness_claim': False, 'readback_at': datetime.now(timezone.utc).isoformat()}
    request = {**intent, 'family_id': 'LOCAL', 'race_id': eid, 'execution_id': eid}
    output.mkdir(parents=True, exist_ok=True)
    o._write(output/'reference_intent.json', request)
    source, errors = capture_public_urw_sources(request, output=output/'public_capture', reference_only=True)
    source = enrich_source_artifact(source)
    source['source_snapshot_sha256'] = sha_obj({k: v for k, v in source.items() if k != 'source_snapshot_sha256'})
    o._write(output/'reference_source.json', source)
    if errors:
        raise ValueError('REFERENCE_OFFICIAL_SOURCE_HOLD:' + ','.join(errors))
    prediction = compile_reference_prediction(request, source)
    o._write(output/'reference_prediction.json', prediction)
    message = output/'reference_prediction.md'
    message.write_text(render_reference_prediction(prediction), encoding='utf-8')
    report = _reference_availability_report(intent, output=output, run_id=run_id, prediction=prediction, eid=eid)
    o._write(output/'entry_report.json', report)
    return report


def run(intent, *, output, run_id, github_sha=None, checkpoint_publisher=None):
    mode = intent.get('prediction_mode', 'FORMAL-PRODUCTION')
    if mode == 'AUTO':
        if checkpoint_publisher is not None:
            raise ValueError('CHAT_USES_EXISTING_AUTHORIZED_DISPATCH_PUBLISHER')
        return run_chat(intent, output=output, run_id=run_id)
    if mode == 'REFERENCE':
        if checkpoint_publisher is not None:
            raise ValueError('REFERENCE_CANNOT_PUBLISH_FORMAL_CHECKPOINTS')
        return run_reference(intent, output=output, run_id=run_id)
    if mode != 'FORMAL-PRODUCTION':
        raise ValueError('RACE_ENTRY_PREDICTION_MODE_INVALID')
    request = copy.deepcopy(intent)
    if request.get('family_id', 'LOCAL') != 'LOCAL':
        raise ValueError('RACE_ENTRY_FAMILY_NOT_LOCAL')
    request['family_id'] = 'LOCAL'
    if not request.get('execution_id') and not request.get('race_id'):
        venue = str(request.get('venue_id') or '').upper()
        day = date.fromisoformat(str(request.get('race_date') or '').replace('/', '-'))
        number = request.get('race_no')
        if not re.fullmatch(r'[A-Z]{3}', venue) or isinstance(number, bool) or not isinstance(number, int) or not 1 <= number <= 99:
            raise ValueError('RACE_ENTRY_IDENTITY_INVALID')
        request['venue_id'] = venue
        request['race_date'] = day.isoformat()
        request['race_id'] = request['execution_id'] = f'KM-LOCAL-{venue}-{day:%Y%m%d}-R{number:02d}-LIVE-R1'
    request['execution_id'] = o.derive_execution_id(request)
    if request.get('race_id') not in (None, request['execution_id']):
        raise ValueError('RACE_ENTRY_IDENTITY_MISMATCH')
    request['race_id'] = request['execution_id']
    authority_context = o.validate_request_context(request)
    if isinstance(authority_context, dict):
        if not request.get("current_authority_manifest"):
            request["current_authority_manifest"] = authority_context["current_authority_manifest"]
    # Readback is not a new prediction and must remain possible after cutoff.
    # Never enter SOURCE/Owner generation when a FINAL checkpoint exists. The
    # existing orchestrator checks immutable manifests and semantic/source basis.
    final_checkpoint = o.resolve_phase(request['execution_id'], 'FORMAL')
    if final_checkpoint and 'final_receipt_envelope.json' in ((final_checkpoint.get('manifest') or {}).get('files') or {}):
        canonical_path = o.ROOT/'runtime/formal_intents'/f"{request['execution_id']}.json"
        canonical = o._load(canonical_path) if canonical_path.is_file() else {}
        readback = {**canonical, **request, 'execution_phase': 'FORMAL'}
        readback.pop('analysis_only', None)
        # A changed request must fail closed, never fall through to generation.
        report = o.orchestrate(readback, run_id=run_id, github_sha=github_sha,
                               runtime_out=output/'formal', tmp_root=output/'tmp')
        report.update(execution_id=request['execution_id'], prediction_reexecution=False,
                      readback_only=True)
        from runtime.local_race_key_gate import readback_final
        # Existing FINAL readback never enters SOURCE/Prediction or a /verify
        # POST. A missing first presentation may use the canonical health GET.
        report['delivery']=readback_final(request['execution_id'],'readback')
        o._write(output/'entry_report.json', report)
        return report
    # Existing verified pre-cutoff SOURCE remains usable; reacquisition after
    # cutoff is forbidden. A late entry never creates a historical prediction.
    saved = o.resolve_phase(request['execution_id'], 'SOURCE')
    if saved is None:
        o.check_deadline(request, phase='SOURCE')
    request.update(execution_phase='SOURCE', analysis_only=True)
    o._write(output/'race_intent.json', request)
    source_report = o.orchestrate(request, run_id=run_id, github_sha=github_sha,
                                  runtime_out=output/'source', tmp_root=output/'tmp')
    saved = o.resolve_phase(request['execution_id'], 'SOURCE')
    if source_report.get('status') != 'SOURCE_PASS' or saved is None:
        failure = source_report.get('failure') or {}
        code = (source_report.get('first_failed_code') or source_report.get('code')
                or failure.get('code') or 'SOURCE_CHECKPOINT_MISSING_AFTER_RUN')
        report = {'status': 'HOLD', 'first_failed_phase': 'SOURCE',
                  'first_failed_code': code, 'code': code,
                  'completion': False, 'formal_final_proven': False,
                  'prediction_reexecution': False, 'no_bet_decision': False,
                  'execution_id': request['execution_id'], 'source': source_report}
        o._write(output/'entry_report.json', report)
        return report
    o.validate_source_checkpoint(saved['run_dir'], request)
    # Publish verified SOURCE before numerical/Static/FORMAL work can crash.
    # The existing strict Git persistence protects other races and immutable
    # records. A failed publish stops this worker before further execution.
    if checkpoint_publisher is not None:
        checkpoint_publisher([f"runtime/executions/{request['execution_id']}/SOURCE"])
    source = o._load_checkpoint_json(saved, 'source_receipt_envelope.json')
    numeric_request = copy.deepcopy(request)
    numeric_request['runners'] = source['artifact']['official_runner_universe']['runners']
    numeric_request = bind_urw_numerical_context(numeric_request, source['artifact'])
    authority = assess()
    if authority['status'] != 'READY':
        raise ValueError('PRODUCTION_NUMERICAL_AUTHORITY_NOT_READY')
    numerical = materialize_production(source['artifact'], numeric_request, authority['required_indices'])
    o._write(output/'numerical_materialization.json', numerical)
    report = {'status': 'HOLD', 'first_failed_phase': 'STATIC_FREEZE',
              'code': 'STATIC_PREDICTION_FREEZE_REQUIRED', 'completion': False,
              'execution_id': request['execution_id'], 'source': source_report,
              'source_receipt_sha256': source['receipt_sha256'],
              'numerical_diagnostic_only': True, 'prediction_reexecution': False,
              'formal_final_proven': False, 'no_bet_decision': False}
    if numerical.get('strict_full_numerical_ready') is not True:
        report.update(first_failed_phase='NUMERICAL', code='FULL_NUMERICAL_CLOSURE_REQUIRED')
        o._write(output/'entry_report.json', report)
        return report
    # Look up the exact canonical race ourselves; C2 is not a prerequisite
    # for the existing chat-owned frozen-input path.
    discovery_request = copy.deepcopy(request)
    for key in ('family_id', 'execution_id', 'race_id', 'current_authority_manifest'):
        discovery_request.setdefault(key, request.get(key))
    formal, resolution = resolve_static_input(discovery_request, source)
    report['owner_resolution'] = resolution
    generation_allowed = True
    try:
        o.check_deadline(request, phase='FORMAL')
    except o.FormalOrchestrationError as exc:
        generation_allowed = False
        report.update(code=str(exc), prestart_deadline_expired=True)
    o._write(output/'static_owner_input.json', input_packet(request, source, resolution,
                                                          generation_allowed=generation_allowed and intent.get('analysis_only') is not True))
    # Owner-authorized evidence-only Static. An earlier canonical manually
    # frozen intent always wins; no automatic shadow or uncalibrated 29-index
    # values are consumed to compute the Production ranking.
    if formal is None and generation_allowed and intent.get('analysis_only') is not True:
        policy_path = o.ROOT/'profiles/local_production_static_owner_20261014_v1.json'
        try:
            policy = json.loads(policy_path.read_text(encoding='utf-8'))
            generated, owner_ledger = build_formal_static(
                request, source, numerical, policy=policy)
            # Freeze the exact authorized intent before external Formal. Its
            # persistence is not evidence that a Signed FINAL already exists.
            o._write(output/'generated_formal_intent.json', generated)
            o._write(output/'production_static_owner.json', owner_ledger)
            o._write(o.ROOT/'runtime/formal_intents'/f"{request['execution_id']}.json", generated)
            formal = generated
            resolution = {
                'status': 'OWNER_GENERATED_FROZEN_INPUT',
                'input_mode': 'AUTO_PRODUCTION_EVIDENCE_ONLY',
                'owner_profile': owner_ledger['profile'],
                'source_receipt_sha256': source['receipt_sha256'],
                'static_generation_executed': True,
                'numerical_prediction_consumption': False,
                'empirical_oos_validated': False,
            }
            report['owner_resolution'] = resolution
        except (StaticOwnerError, ValueError, KeyError, OSError) as exc:
            report['production_static_owner'] = {
                'status': 'HOLD', 'reason': str(exc), 'signed_final_claim': False}

    # A deterministic, explicitly NON-PRODUCTION candidate can be frozen for
    # forward OOS while the authoritative chat-owned Static is absent. It may
    # never fill formal, final_prediction_package, or any Production ticket.
    if formal is None and generation_allowed and intent.get('analysis_only') is not True:
        try:
            compiler = compile_urw_candidate if request.get('venue_id') == 'URW' else compile_shadow
            shadow = compiler(request, source, numerical)
            o._write(output/'shadow_prediction.json', shadow)
            report['shadow_owner'] = {
                'status': 'FROZEN_NON_PRODUCTION',
                'profile': shadow['profile'],
                'sha256': shadow['sha256'],
                'paper_ticket_count': shadow['paper_ticket_count'],
                'production_prediction_changed': False,
                'formal_final_proven': False,
            }
        except (ShadowOwnerError, KeyError, ValueError) as exc:
            report['shadow_owner'] = {
                'status': 'HOLD',
                'reason': str(exc),
                'formal_final_proven': False,
                'production_prediction_changed': False,
            }
    if formal is not None and intent.get('analysis_only') is True:
        report.update(code='ANALYSIS_ONLY_SOURCE_COMPLETE', first_failed_phase=None)
    if formal is not None and generation_allowed and intent.get('analysis_only') is not True:
        canonical = o.ROOT/'runtime/formal_intents'/f"{request['execution_id']}.json"
        if checkpoint_publisher is not None and canonical.is_file():
            checkpoint_publisher([str(canonical.relative_to(o.ROOT))])
        formal.pop('execution_phase', None)
        formal.pop('analysis_only', None)
        report = o.orchestrate(formal, run_id=run_id, github_sha=github_sha,
                              runtime_out=output/'formal', tmp_root=output/'tmp')
        report['owner_resolution'] = resolution
    o._write(output/'entry_report.json', report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument('--request')
    inputs.add_argument('--query', help='Explicit URW race text: verified FINAL, authorized existing dispatch, or independent REFERENCE')
    parser.add_argument('--display', action='store_true', help='Print the returned chat message instead of the JSON report')
    parser.add_argument('--output', required=True)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--github-sha')
    parser.add_argument('--persist-checkpoints', action='store_true',
                        help='Use existing strict main-branch Git persistence before further stages')
    args = parser.parse_args()
    output = Path(args.output).resolve()
    preserve_existing_reference = False
    try:
        publisher = None
        if args.persist_checkpoints:
            if os.environ.get('GITHUB_ACTIONS') != 'true' or os.environ.get('GITHUB_REF') != 'refs/heads/main':
                raise ValueError('CHECKPOINT_PUBLISH_REQUIRES_EXISTING_MAIN_ACTIONS_ENTRY')
            from runtime.local_race_day_dispatcher import publish_state
            publisher = lambda paths: publish_state(o.ROOT, paths)
        intent = resolve_chat_intent(args.query) if args.query is not None else json.loads(Path(args.request).read_text())
        report = run(intent, output=output,
                     run_id=args.run_id, github_sha=args.github_sha, checkpoint_publisher=publisher)
    except (o.FormalOrchestrationError, ValueError, KeyError, OSError, RuntimeError) as exc:
        from runtime.formal_failure_diagnostics import failure_stage_for, resume_hint_for
        preserve_existing_reference = str(exc) == 'REFERENCE_OUTPUT_ALREADY_EXISTS_NO_REEXECUTION'
        report = {'status': 'HOLD', 'completion': False, 'code': str(exc), 'formal_final_proven': False,
                  'first_failed_stage': failure_stage_for(exc), 'root_cause': str(exc),
                  'last_verified_stage': 'UNKNOWN', 'resume_from': resume_hint_for(exc),
                  'required_action': resume_hint_for(exc)}
        if not preserve_existing_reference:
            o._write(output/'entry_report.json', report)
    if report.get('status') in {'HOLD', 'BLOCKED'}:
        report.setdefault('first_failure_observed_at', datetime.now(timezone.utc).isoformat())
        if not preserve_existing_reference:
            o._write(output/'entry_report.json', report)
    completion = report.get('completion')
    if isinstance(completion, dict) and completion.get('complete') is True:
        from runtime.local_race_key_gate import terminal_state
        try:
            report['delivery'] = terminal_state(report['execution_id'], 'success')
        except Exception as exc:
            # FINAL truth survives a delivery/verification transport failure.
            report['delivery'] = {'status': 'DELIVERY_HOLD', 'reason': str(exc),
                                  'prestart_delivery_pass': False}
        o._write(output/'entry_report.json', report)
    print(report['message'] if args.display and 'message' in report else json.dumps(report, ensure_ascii=False, default=str))
    return 0 if report.get('status') in {'REFERENCE_AVAILABLE', 'FORMAL_VERIFIED',
        'FORMAL_BLOCKED_REFERENCE_AVAILABLE', 'FORMAL_PENDING_REFERENCE_AVAILABLE'} else o.completion_exit_code(report)


if __name__ == '__main__':
    raise SystemExit(main())
