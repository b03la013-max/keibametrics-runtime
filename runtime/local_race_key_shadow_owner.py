"""Result-blind LOCAL static-owner *hypothesis* from Production-numerical data.

NON-PRODUCTION paper baseline only. Existing numerically closed 29-index
records are uncalibrated and explicitly forbid Production Prediction/Ticket
consumption. This shadow output never enters the FORMAL external request.
"""
from __future__ import annotations

from datetime import datetime, timezone
import base64
import gzip
import hashlib
import json
import math
from typing import Any


PROFILE = "KM-LOCAL-RACE-KEY-STATIC-SHADOW-v0.1-20261014"
VALID = {"CALCULATED", "RULED-NEUTRAL"}
INDEXES = ("ZAI-WIN", "ZAI-PLACE", "T3I-L")
COLUMNS = ("W", "P2", "P3")


class ShadowOwnerError(ValueError):
    pass


def _sha(payload: Any) -> str:
    return hashlib.sha256(json.dumps(
        payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")).hexdigest()


def _aware(value: str, name: str) -> datetime:
    try:
        stamp = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ShadowOwnerError(name + "_INVALID") from exc
    if stamp.tzinfo is None:
        raise ShadowOwnerError(name + "_TIMEZONE_REQUIRED")
    return stamp.astimezone(timezone.utc)


def _ranking(rows: list[dict], name: str) -> list[str]:
    # RULED-NEUTRAL is unknown/incomparable, NOT an estimate of weak ability.
    # Keep all runners and label neutral values; no negative missingness scores.
    # Unknowns are not compared numerically with CALCULATED estimates.
    def identifier_key(rid: str):
        return (0, int(rid)) if rid.isdigit() else (1, rid)

    calculated, unknown = [], []
    for row in rows:
        spec = row["canonical_components"][name]
        rid = str(row["runner_id"])
        (unknown if spec["terminal_status"] == "RULED-NEUTRAL" else calculated).append(
            (float(spec["value"]), rid)
        )
    return ([rid for _, rid in sorted(calculated, key=lambda v: (-v[0], identifier_key(v[1])))]
            + [rid for _, rid in sorted(unknown, key=lambda v: identifier_key(v[1]))])


def compile_shadow(
    request: dict,
    source_envelope: dict,
    materialized: dict,
    *,
    now: datetime | None = None,
) -> dict:
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ShadowOwnerError("CURRENT_TIME_TZ_REQUIRED")
    if request.get("family_id") != "LOCAL":
        raise ShadowOwnerError("LOCAL_FAMILY_ONLY")
    eid = str(request.get("execution_id") or "")
    if not eid or eid != request.get("race_id"):
        raise ShadowOwnerError("RACE_IDENTITY_INVALID")
    if source_envelope.get("receipt_sha256") in ("", None):
        raise ShadowOwnerError("SOURCE_SIGNED_RECEIPT_REQUIRED")
    source = source_envelope.get("artifact") or {}
    source_time = _aware(source.get("source_freeze_at"), "SOURCE_FREEZE_AT")
    cutoff = _aware(request.get("prediction_cutoff"), "PREDICTION_CUTOFF")
    if source_time >= cutoff or now.astimezone(timezone.utc) >= cutoff:
        raise ShadowOwnerError("SHADOW_FREEZE_AFTER_PRESTART_CUTOFF")
    if source.get("formal_ready") is not True:
        raise ShadowOwnerError("SOURCE_NOT_READY")
    if materialized.get("strict_full_numerical_ready") is not True:
        raise ShadowOwnerError("FULL_29_INDEX_TERMINAL_REQUIRED")
    summary = materialized.get("production_numerical_authority") or {}
    if summary.get("prediction_consumption_authorized") is not False:
        raise ShadowOwnerError("NUMERICAL_PROMOTION_SCOPE_UNEXPECTED")
    rows = materialized.get("runners") or []
    universe = source.get("official_runner_universe") or {}
    official = universe.get("runners") or []
    official_ids = {str(row.get("runner_id")) for row in official}
    ids = [str(row.get("runner_id")) for row in rows]
    if len(rows) < 2 or len(ids) != len(set(ids)) or set(ids) != official_ids:
        raise ShadowOwnerError("FULL_RUNNER_UNIVERSE_MISMATCH")
    if len(materialized.get("required_indices") or []) != 29:
        raise ShadowOwnerError("REQUIRED_INDEX_MANIFEST_INCOMPLETE")
    neutrals = {}
    for row in rows:
        rid = str(row["runner_id"])
        cc = row.get("canonical_components") or {}
        if len(cc) != 29:
            raise ShadowOwnerError("RUNNER_FULL29_REQUIRED:" + rid)
        n = []
        for key in INDEXES:
            spec = cc.get(key) or {}
            term = str(spec.get("terminal_status") or "")
            val = spec.get("value")
            if term not in VALID or isinstance(val, bool) or not isinstance(val, (int, float)) or not math.isfinite(val):
                raise ShadowOwnerError("INDEX_NOT_TERMINAL:" + rid + ":" + key)
            if term == "RULED-NEUTRAL":
                n.append(key)
        neutrals[rid] = n
    ranked = {k: _ranking(rows, k) for k in INDEXES}
    winner_scores = sorted((float(row["canonical_components"]["ZAI-WIN"]["value"])
                            for row in rows), reverse=True)
    spread = round(winner_scores[0] - winner_scores[1], 5)
    # Explicit UNVALIDATED SHADOW bands. Never infer a calibrated probability.
    # Widths are only a provisional paper baseline for unknown-future OOS.
    if spread >= 15:
        widths = (1, 2, 5)
        band = "SHADOW_NARROW"
    elif spread >= 7:
        widths = (2, 3, 6)
        band = "SHADOW_MEDIUM"
    else:
        widths = (3, 5, 8)
        band = "SHADOW_WIDE"
    heads = ranked["ZAI-WIN"][:min(widths[0], len(rows))]
    seconds = list(heads) if len(heads) > 1 else []
    for rid in ranked["ZAI-PLACE"]:
        if rid not in seconds and (len(heads) > 1 or rid not in heads):
            seconds.append(rid)
        if len(seconds) >= widths[1]:
            break
    thirds = []
    for rid in ranked["T3I-L"]:
        if rid not in thirds:
            thirds.append(rid)
        if len(thirds) >= widths[2]:
            break
    p3_unknown = [rid for rid in ids if "T3I-L" in neutrals[rid]]
    # One unknown third is protected in this paper baseline rather than being
    # silently equated to a low score. Never promote to Production.
    protected_unknown = None
    if p3_unknown and not any(rid in thirds for rid in p3_unknown) and thirds:
        protected_unknown = p3_unknown[0]
        thirds[-1] = protected_unknown
    roles = {rid: [col for col, pool in
                   (("W", heads), ("P2", seconds), ("P3", thirds))
                   if rid in pool] for rid in ids}
    pairs = [(h, p) for h in heads for p in seconds if h != p]
    # Order-exact paper candidates are not actual bets or Producer SIGNED FINAL.
    exacta = [{"bet_type": "EXACTA", "selection": [h, p], "stake": 100}
              for h, p in pairs]
    trifecta = [{"bet_type": "TRIFECTA", "selection": [h, p, t], "stake": 100}
                for h, p in pairs for t in thirds if t not in {h, p}]
    output = {
        "profile": PROFILE,
        "status": "STATIC_SHADOW_FROZEN / NON-PRODUCTION / UNCALIBRATED",
        "race_id": eid,
        "source_receipt_sha256": source_envelope["receipt_sha256"],
        "source_snapshot_sha256": source.get("source_snapshot_sha256"),
        "numeric_provenance_sha256": materialized.get("index_provenance_hash"),
        "frozen_at": now.isoformat(),
        "prediction_cutoff": request["prediction_cutoff"],
        "ranking": ranked["ZAI-WIN"],
        "rankings_by_column": ranked,
        "role_columns": roles,
        "winner_head_local_pairs": [{"head": h, "second": p} for h, p in pairs],
        "neutral_index_registry": neutrals,
        "p3_unknown_protection": protected_unknown,
        "paper_ticket_count": len(exacta) + len(trifecta),
        "paper_capital_yen": 100 * (len(exacta) + len(trifecta)),
        "paper_tickets": exacta + trifecta,
        "shadow_width": {"band": band, "winner_spread": spread,
                         "heads": len(heads), "seconds": len(seconds),
                         "thirds": len(thirds)},
        "evidence_statement": "29 Production-numerical fields are complete but uncalibrated; candidate ranking uses three ordinal values only, not an authorized predictive probability.",
        "pair_conditioning_statement": "Provisional role-row combinations, not empirically proven pair-specific interactions.",
        "prediction_consumption_authorized": False,
        "production_authority": False,
        "signed_final_claim": False,
        "actual_purchase": False,
        "promotable_without_forward_oos": False,
    }
    output["sha256"] = _sha(output)
    return output


URW_PROFILE = 'KM-LOCAL-URW-OWNER-CANDIDATE-v0.4-20261019'
URW_CANON = 'KM-LOCAL-URW-v1.6-CURRENT-AUTHORITY-MEC-FULL-LIFECYCLE-20260923'
URW_CANON_SHA256 = '33172660c85666f0a66a6ec97c20e24ccefdadf8bf396d22ede822f5d4b0f7a0'


def compile_urw_candidate(request, source_envelope, materialized, *, now=None,
                          historical_replay=False):
    """URW-specific evidence/semantic adapter around the existing LOCAL shadow.

    Never calls the KAW Owner, creates a Formal Intent, or changes Production
    consumers. Existing LOCAL structure-derived ranking/roles remain a research
    baseline, NOT an implementation claim for every URW qualitative mechanism.
    Caller must verify SOURCE signature through the existing canonical ingress.
    A historical replay keeps its actual compilation clock and grants no freeze.
    """
    import copy
    from urllib.parse import parse_qs, urlparse
    from runtime.local_production_static_owner import _card_heading, _start_date, _VisibleText
    from runtime.local_nar_evidence_candidate import parse_race_card
    from runtime.local_fullnumerical_candidate import REQUIRED
    from runtime.local_krs_bridge_candidate import build_candidate_prediction_structure_derived

    injected_clock = now is not None
    now = now or datetime.now(timezone.utc)
    cutoff = _aware(request.get('prediction_cutoff'), 'PREDICTION_CUTOFF')
    if (request.get('family_id') != 'LOCAL' or request.get('venue_id') != 'URW'
            or request.get('execution_id') != request.get('race_id') or not request.get('race_id')):
        raise ShadowOwnerError('URW_CANDIDATE_SCOPE_OR_IDENTITY')
    if now.tzinfo is None:
        raise ShadowOwnerError('CURRENT_TIME_TZ_REQUIRED')
    receipt = source_envelope.get('receipt') or {}
    source = source_envelope.get('artifact') or {}
    if (receipt.get('family') != 'LOCAL' or receipt.get('phase') != 'SOURCE' or receipt.get('status') != 'SOURCE_FROZEN'
            or receipt.get('race_id') != request['race_id'] or source.get('race_id') != request['race_id']
            or not source_envelope.get('signature') or source_envelope.get('signature_alg') != 'Ed25519'
            or source_envelope.get('receipt_sha256') != _sha(receipt)
            or receipt.get('artifact_sha256') != _sha(source) or source.get('formal_ready') is not True):
        raise ShadowOwnerError('URW_CANDIDATE_SIGNED_SOURCE_BINDING')
    frozen = _aware(source.get('source_freeze_at'), 'SOURCE_FREEZE_AT')
    signed = _aware(receipt.get('timestamp'), 'SOURCE_SIGNED_AT')
    post = _aware(request.get('scheduled_post_at'), 'OFFICIAL_POST')
    from runtime.local_race_key_intake import JST
    if (not isinstance(request.get('race_date'), str)
            or request['race_date'] != post.astimezone(JST).date().isoformat()
            or type(request.get('race_no')) is not int
            or not 1 <= request['race_no'] <= 12):
        raise ShadowOwnerError('URW_CANDIDATE_RACE_CALENDAR_IDENTITY')
    if not frozen <= signed < cutoff < post or frozen > now or signed > now:
        raise ShadowOwnerError('URW_CANDIDATE_SOURCE_TIME_BINDING')
    if not historical_replay and now >= cutoff:
        raise ShadowOwnerError('URW_CANDIDATE_CUTOFF_EXPIRED')
    sources = [s for s in source.get('sources') or []
               if s.get('source_class') == 'OFFICIAL_RACE_CARD_CURRENT_STATE_BODY_WEIGHT'
               and s.get('authority') == 'NAR_OFFICIAL' and s.get('official') is True
               and s.get('cutoff_relation') == 'PRE_CUTOFF']
    if len(sources) != 1:
        raise ShadowOwnerError('URW_OFFICIAL_CARD_REQUIRED')
    card = sources[0]
    url = urlparse(card.get('final_url') or card.get('url') or '')
    query = parse_qs(url.query)
    if ((url.scheme,url.netloc,url.path) != ('https','www.keiba.go.jp','/KeibaWeb/TodayRaceInfo/DebaTable')
            or query.get('k_babaCode') != ['18']
            or query.get('k_raceDate') != [request['race_date'].replace('-','/')]
            or query.get('k_raceNo') != [str(request['race_no'])]):
        raise ShadowOwnerError('URW_OFFICIAL_CARD_IDENTITY')
    try:
        raw = gzip.decompress(base64.b64decode(card['raw_gzip_b64'], validate=True))
    except (ValueError, OSError, EOFError) as exc:
        raise ShadowOwnerError('URW_OFFICIAL_CARD_ENCODING') from exc
    if hashlib.sha256(raw).hexdigest() != card.get('raw_sha256'):
        raise ShadowOwnerError('URW_OFFICIAL_CARD_RAW_HASH')
    start = (source.get('normalized_evidence') or {}).get('start_time') or {}
    if (start.get('authority') != 'NAR_OFFICIAL' or start.get('cutoff_relation') != 'PRE_CUTOFF'
            or start.get('value') != post.astimezone(JST).strftime('%H:%M')):
        raise ShadowOwnerError('URW_OFFICIAL_POST_MISMATCH')
    header = _card_heading(source)
    # Resolve categorical context from the same verified HEADER, never past
    # starts further down the card or a caller-provided class/scenario/result.
    import re
    import unicodedata
    parser = _VisibleText()
    try:
        page = raw.decode('utf-8')
    except UnicodeError:
        page = raw.decode('cp932')
    parser.feed(page)
    heading = re.split(r'競走馬|枠番', unicodedata.normalize('NFKC', ''.join(parser.fragments)), maxsplit=1)[0]
    header['class_tokens'] = _urw_class_tokens(heading)
    header['going'] = (source.get('normalized_evidence') or {}).get('track_condition', {}).get('value')
    active = (source.get('active_runner_universe') or {}).get('runners') or []
    ids = [str(x['runner_id']) for x in active]
    official = [str(x['runner_id']) for x in (source.get('official_runner_universe') or {}).get('runners') or []]
    rows = materialized.get('runners') or []
    numeric_ids = [str(x['runner_id']) for x in rows]
    if (len(ids) < 2 or len(set(ids)) != len(ids) or len(set(official)) != len(official)
            or len(set(numeric_ids)) != len(numeric_ids)
            or set(ids) != set(official) or set(ids) != set(numeric_ids)):
        raise ShadowOwnerError('URW_ACTIVE_UNIVERSE_MISMATCH')
    authority = materialized.get('production_numerical_authority') or {}
    compiler = materialized.get('production_evidence_compiler') or {}
    if (materialized.get('race_id') != request['race_id']
            or compiler.get('source_snapshot_sha256') != source.get('source_snapshot_sha256')
            or not source.get('source_snapshot_sha256')):
        raise ShadowOwnerError('URW_NUMERICAL_SOURCE_IDENTITY_MISMATCH')
    if (materialized.get('strict_full_numerical_ready') is not True
            or len(materialized.get('required_indices') or []) != 29
            or set(materialized['required_indices']) != set(REQUIRED)
            or any(authority.get(k) is not False for k in
                   ('prediction_consumption_authorized','krs_consumption_authorized',
                    'ticket_consumption_authorized','capital_consumption_authorized'))):
        raise ShadowOwnerError('URW_FULL29_OR_CONSUMER_BOUNDARY')
    for row in rows:
        cc = row.get('canonical_components') or {}
        if set(cc) != set(REQUIRED):
            raise ShadowOwnerError('URW_REQUIRED_CELL_MISSING')
        for key, spec in cc.items():
            val = spec.get('value')
            if (spec.get('terminal_status') not in VALID or isinstance(val,bool)
                    or not isinstance(val,(int,float)) or not math.isfinite(val) or not 0 <= val <= 100
                    or not all(spec.get(k) for k in ('rule_id','mapping_version','evidence_refs','source_fact'))):
                raise ShadowOwnerError('URW_REQUIRED_CELL_INVALID:'+str(row['runner_id'])+':'+key)
    if materialized.get('index_provenance_hash') != _sha([r['canonical_components'] for r in rows]):
        raise ShadowOwnerError('URW_NUMERICAL_PROVENANCE_MISMATCH')
    parsed = parse_race_card(source)
    declared_ids = [str(x['runner_id']) for x in (source.get('declared_runner_universe') or {}).get('runners') or []]
    declared = set(declared_ids)
    status = source.get('runner_status_registry') or []
    registry = {str(x['runner_id']):x for x in status}
    if (len(registry) != len(status) or len(declared) != len(declared_ids)
            or set(parsed) != declared or set(registry) != declared
            or {rid for rid,s in registry.items() if s.get('status') == 'ACTIVE'} != set(ids)):
        raise ShadowOwnerError('URW_DECLARED_ACTIVE_REGISTRY_MISMATCH')
    official_sources = {s['source_id'] for s in source.get('sources') or []
                        if s.get('official') is True and s.get('cutoff_relation') == 'PRE_CUTOFF'}
    for rid in declared-set(ids):
        entry = registry[rid]
        if (entry.get('status') != 'CANCELLED'
                or entry.get('reason') != 'EXPLICIT_OFFICIAL_ODDS_CANCELLATION'
                or not entry.get('evidence_sources')
                or not set(entry['evidence_sources']).issubset(official_sources)):
            raise ShadowOwnerError('URW_UNEXPLAINED_RUNNER_OMISSION')
    day = post.astimezone(JST).date()
    evidence = {}
    for runner in active:
        rid = str(runner['runner_id'])
        if parsed[rid]['name'] != runner['name']:
            raise ShadowOwnerError('URW_CARD_RUNNER_NAME_MISMATCH')
        starts = []
        for s in parsed[rid].get('starts') or []:
            when = _start_date(s.get('date'))
            if when is None:
                raise ShadowOwnerError('URW_PAST_START_DATE_UNKNOWN')
            if when.date() >= day:
                raise ShadowOwnerError('URW_NON_PRESTART_HISTORY')
            starts.append(s)
        starts = sorted(starts,key=lambda s:_start_date(s['date']),reverse=True)[:5]
        observations=[]
        for s in starts:
            positions=s.get('content_positions') or []
            observations.append({'date':s['date'],'venue':s.get('venue'),'distance':s.get('distance'),
                'race_name':s.get('race_name'),'going':s.get('going'),'finish':s.get('finish'),
                'field_size':s.get('field_size'),'positions':positions,'surface':s.get('surface'),
                'class_tokens':_urw_class_tokens(s.get('race_name')),
                'matched_urw_distance':str(s.get('venue','')).replace('ナ','')=='浦和' and s.get('distance')==header['distance'],
                'observed_progression':positions[0]-positions[-1] if len(positions)>=2 else None,
                'raw_reference':s.get('raw')})
        evidence[rid]={'article_refs':['59-C5R','60-MPA','61-UPR','100-DER','118-EWL-URW','121-AOEP','134-DCT-URW','137-PCA'],
            'past_starts':observations,'past_start_count':len(starts),
            'current_condition_translation':_urw_current_condition_translation(parsed[rid],observations,header),
            'missing_history':'UNKNOWN_NOT_WEAK' if not starts else None,
            'observed_position_range':[min(p),max(p)] if (p:=[v for s in observations for v in s['positions']]) else None,
            'max_observed_progression':max((s['observed_progression'] for s in observations if s['observed_progression'] is not None),default=None),
            'predicted_position_scenarios':'CONDITIONAL_ANALOG_HYPOTHESES_NOT_A_POINT_FORECAST',
            'current_gci':'UNKNOWN_NO_TRANSIENT_CARRYOVER','acquisition_survival_prediction':'OBSERVATIONS_SPLIT_CURRENT_EFFECTS_UNKNOWN'}
    # No incoming weights, budget, result or manually supplied roles enter the
    # existing LOCAL structure-derived research baseline.
    baseline = build_candidate_prediction_structure_derived({'runners':copy.deepcopy(rows)})['candidate_static_prediction']
    scenario = _urw_scenario_prediction(evidence, baseline, header=header, field_size=len(ids))
    pairs = [{'head':h,'second':s,'status':'CANDIDATE_SEMANTIC_ONLY',
              'interaction_effect':'UNESTABLISHED_NUMERICAL_INTERACTION_EFFECT'}
             for h in baseline['W'] for s in baseline['P2'] if h != s]
    thirds = [{'head':p['head'],'second':p['second'],'third':t,'status':'CANDIDATE_SEMANTIC_ONLY',
               'interaction_effect':'UNESTABLISHED_NUMERICAL_INTERACTION_EFFECT'}
              for p in pairs for t in baseline['P3'] if t not in {p['head'],p['second']}]
    for p in pairs:
        context = scenario['head_local_p2'][p['head']]['evaluations'][p['second']]
        p['conditional_geometry_support'] = context['status']
        p['conditional_evidence_sha256'] = context['sha256']
    for t in thirds:
        context = scenario['pair_conditioned_p3'][t['head']+'>'+t['second']]['evaluations'][t['third']]
        t['conditional_geometry_support'] = context['status']
        t['conditional_evidence_sha256'] = context['sha256']
    # Freeze at completion, not function entry: a large conditional universe
    # must not appear pre-cutoff merely because computation started in time.
    completed = now if injected_clock else datetime.now(timezone.utc)
    if completed < now:
        raise ShadowOwnerError('URW_CANDIDATE_CLOCK_REGRESSION')
    if not historical_replay and completed >= cutoff:
        raise ShadowOwnerError('URW_CANDIDATE_COMPLETED_AFTER_CUTOFF')
    output = {'profile':URW_PROFILE,'status':'CANDIDATE / NON-PRODUCTION / CONDITIONAL-ANALOG-UNVALIDATED',
        'race_id':request['race_id'],'venue_id':'URW','compiled_at':completed.isoformat(),
        'race_date':request['race_date'],'race_no':request['race_no'],
        'scheduled_post_at':request['scheduled_post_at'],
        'compilation_started_at':now.isoformat(),
        'compile_clock_source':'INJECTED_CONTRACT_CLOCK' if injected_clock else 'ACTUAL_RUNTIME_CLOCK',
        'temporal_class':('HISTORICAL_CONTRACT_REPLAY' if historical_replay else
                          'INJECTED_CLOCK_CONTRACT_TEST' if injected_clock else 'PRESTART_SHADOW_LOCAL_FREEZE'),
        'frozen_at':None if historical_replay or injected_clock else completed.isoformat(),
        'prediction_cutoff':request['prediction_cutoff'],
        'source_receipt_sha256':source_envelope['receipt_sha256'],'source_snapshot_sha256':source['source_snapshot_sha256'],
        'source_signature_authority':'CALLER_CANONICAL_INGRESS_VERIFICATION_REQUIRED',
        'venue_canon':URW_CANON,'venue_canon_source_sha256':URW_CANON_SHA256,
        'required_indices':list(materialized['required_indices']),'numeric_provenance_sha256':materialized['index_provenance_hash'],
        'numeric_cell_count':len(rows)*29,'runner_numeric_bindings':{str(r['runner_id']):_sha(r['canonical_components']) for r in rows},
        'ranking':baseline['ranking'],'role_columns':baseline['roles'],'existing_local_baseline':baseline,
        'urw_scenario_prediction':scenario,
        'urw_evidence':evidence,'head_local_pairs':pairs,'pair_conditioned_thirds':thirds,
        'paper_ticket_count':0,'paper_capital_yen':0,'paper_tickets':[],
        'ticket_status':'NOT_CONSTRUCTED_NO_MEC_OR_CAPITAL_AUTHORITY',
        'production_authority':False,'formal_handoff_allowed':False,'signed_final_claim':False,
        'prediction_consumption_authorized':False,'actual_purchase':False,'forward_oos_credit':0,
        'promotion_gaps':['URW_PRODUCTION_OWNER_SCOPE_APPROVAL','URW_CONDITIONAL_MODEL_VALIDATION_AND_INPUT_AUTHORITY',
                          'GENUINE_PRESTART_SHADOW_OOS_AND_INDEPENDENT_TIMESTAMP','DATED_RACE_AND_RUNTIME_SEND_APPROVAL'],
        'kaw_owner_reused':False,'krs_numeric_consumption':False,'capital_policy_changed':False}
    output['sha256']=_sha(output)
    return output


def _urw_current_condition_translation(card, observations, header):
    """Expose source-bound transfers without inventing their magnitude/sign.

    URW v1.6 sections 118/134/136/142: acquisition is not survival, a
    shortener is not automatically an improvement, and draw/friction effects
    have no approved numerical adjustment. Historical place-only evidence
    cannot be silently promoted into a direct Winner witness.
    """
    current_distance=header['distance']
    translated=[]
    for obs in observations:
        distance=obs.get('distance')
        delta=current_distance-distance if type(distance) is int else None
        positions=obs.get('positions') or []
        same_course=obs.get('matched_urw_distance') is True
        same_class=bool(header['class_tokens']) and obs.get('class_tokens')==header['class_tokens']
        finish=obs.get('finish')
        path_known=len(positions)==4 and obs.get('surface')=='DIRT'
        if same_course and same_class and path_known and finish==1:
            kind='DIRECT_WIN_OBSERVATION_CURRENT_EFFECT_UNCALIBRATED'
        elif same_course and same_class and path_known and type(finish) is int and finish in (2,3):
            kind='PLACE_ONLY_NOT_DIRECT_WINNER'
        else:
            kind='TRANSFER_OR_INCOMPLETE_CURRENT_WINNER_EFFECT_UNKNOWN'
        translated.append({'observation_sha256':_sha(obs),'date':obs['date'],
            'historical_distance':distance,'distance_delta_m':delta,
            'distance_relation':'UNKNOWN' if delta is None else 'SAME' if delta==0 else 'SHORTENING' if delta<0 else 'LENGTHENING',
            'venue_transfer':'NOT_NEEDED' if str(obs.get('venue','')).replace('ナ','')=='浦和' else 'UNKNOWN',
            'class_transfer':'NOT_NEEDED' if same_class else 'UNKNOWN',
            'going_transfer':'NOT_NEEDED' if header.get('going') and obs.get('going')==header['going'] else 'UNKNOWN',
            'winner_evidence_class':kind,'direct_hard_qualification':'UNKNOWN_REQUIRES_CURRENT_STATE_AND_TIME_PATH_AUDIT',
            'position_acquired':positions[0] if positions else None,
            'corner_rank_changes':[a-b for a,b in zip(positions,positions[1:])] if len(positions)>1 else None,
            'straight_rank_change':positions[-1]-finish if positions and type(finish) is int else None,
            'current_acquisition_effect':'UNKNOWN','current_survival_effect':'UNKNOWN',
            'new_score_adjustment':None})
    return {'article_refs':['118-EWL-URW','134-DCT-URW/DSSR-URW/WAST-URW','136-PLFM-URW','142.2'],
        'current_distance_m':current_distance,'current_frame_no':card.get('frame_no'),
        'current_frame_status':'OBSERVED' if type(card.get('frame_no')) is int else 'UNKNOWN_NOT_IN_PARSED_SOURCE',
        'current_body_weight':card.get('current_body_weight'),
        'current_body_weight_change':card.get('current_body_weight_change'),
        'current_assigned_load':card.get('current_load'),
        'source_id':card.get('race_card_source_id'),'source_snapshot_sha256':card.get('race_card_snapshot_sha256'),
        'effective_time':card.get('race_card_fetched_at'),'observations':translated,
        'draw_effect':'UNKNOWN_NO_APPROVED_DRAW_EFFECT','assigned_load_effect':'UNKNOWN_NOT_A_FIXED_BONUS',
        'body_weight_effect':'UNKNOWN_REQUIRES_INDIVIDUAL_SUCCESSFUL_WEIGHT_COMPARISON',
        'role_adjustments_applied':False,'missing_evidence_protection':'UNKNOWN_NOT_WEAK'}


def _urw_class_tokens(text):
    """Categorical class witnesses only; no new class score or conversion."""
    import re
    import unicodedata
    text = unicodedata.normalize('NFKC', str(text or '')).upper()
    return sorted(set(re.findall(r'(?<![A-Z0-9])([ABC][1-3])(?=[^A-Z0-9]|$)', text)))


def _urw_scenario_prediction(evidence, baseline, *, header, field_size):
    """Result-blind conditional analog hypotheses, NOT calibrated simulations.

    Preserve whole observed paths; never splice each corner's best rank into a
    fictitious run, assign a scenario probability, or manufacture friction cost.
    Candidate partial order compares supported conditional geometries only.
    Missing/transfer evidence is incomparable, not a weak score or exclusion.
    """
    from collections import Counter
    from itertools import product

    history, actors, stances = {}, {}, {}
    for rid in baseline['ranking']:
        paths = []
        for obs in evidence[rid]['past_starts']:
            positions, field = obs.get('positions') or [], obs.get('field_size')
            if positions and (type(field) is not int or field < 2
                    or any(type(p) is not int or not 1 <= p <= field for p in positions)):
                raise ShadowOwnerError('URW_PATH_RANK_INVALID:'+rid)
            finish = obs.get('finish')
            if finish is not None and (type(finish) is not int or type(field) is not int or not 1 <= finish <= field):
                raise ShadowOwnerError('URW_PATH_FINISH_INVALID:'+rid)
            # A two-call sprint is not silently relabelled as first/third/fourth
            # corners. Cross-course and field-size translations stay UNKNOWN.
            complete = len(positions) == 4 and obs.get('surface') == 'DIRT'
            direct = complete and obs.get('matched_urw_distance') is True
            context = (direct and field == field_size and bool(header['class_tokens'])
                       and obs.get('class_tokens') == header['class_tokens']
                       and bool(header.get('going')) and obs.get('going') == header['going'])
            path = {'path_id':rid+':'+_sha(obs), 'runner_id':rid,
                    'observation':obs, 'four_call_mapping_known':complete,
                    'matched_course':direct,'matched_context':context,
                    'projected_positions_if_path_repeats':
                        {'C1':positions[0],'C3':positions[2],'C4':positions[3]}
                        if direct and max(positions) <= field_size else None,
                    'field_size_transfer':'NOT_NEEDED' if field == field_size else 'UNKNOWN',
                    'class_transfer':'NOT_NEEDED' if header['class_tokens'] and obs.get('class_tokens') == header['class_tokens'] else 'UNKNOWN',
                    'stage_rank_changes':{'C1_TO_C3':positions[0]-positions[2],
                        'C3_TO_C4':positions[2]-positions[3],
                        'C4_TO_FINISH':positions[3]-finish if finish is not None else None}
                        if complete else None}
            paths.append(path)
        history[rid] = paths
        usable = [p for p in paths if p['matched_course']]
        if not usable:
            usable = [p for p in paths if p['four_call_mapping_known']]
        firsts = [p['observation']['positions'][0] for p in usable]
        modal = None
        if firsts:
            counts = Counter(firsts)
            # Most frequent observed acquisition; equal frequency uses latest
            # source-listed observation. Never choose by the target outcome.
            modal = max(firsts, key=lambda v:counts[v])
        selected = {'PRESS':min(firsts) if firsts else None,
                    'STANDARD':modal,'SIT':max(firsts) if firsts else None}
        stances[rid] = {}
        for stance, first in selected.items():
            candidates = [p for p in usable if p['observation']['positions'][0] == first]
            stances[rid][stance] = {
                'status':'CONDITIONAL_PATH_REPEAT_HYPOTHESIS' if candidates else 'UNKNOWN',
                'assumption':'IF this source-observed acquisition/path repeats under current opponents; not a point forecast',
                'path_ids':[p['path_id'] for p in candidates],
                'projected_position_alternatives':[p['projected_positions_if_path_repeats'] for p in candidates],
                'role_evidence':{role:[p['path_id'] for p in candidates
                    if p['observation'].get('finish') is not None and p['observation']['finish'] <= depth]
                    for role,depth in (('W',1),('P2',2),('P3',3))},
                'role_rule':'PAST_FINISH_COMPATIBILITY_ONLY; no compatible past finish is UNKNOWN, not future role ineligibility',
                'probability':None,'new_score_adjustment':None}
        leaders = [p for p in usable if p['observation']['positions'][0] == 1]
        stalk = [p for p in usable if p['observation']['positions'][0] > 1
                 and p['observation']['positions'][-1] <= p['observation']['positions'][0]]
        actors[rid] = {
            'lead_acquisition_observations':[p['path_id'] for p in leaders],
            'lead_survival_observations':[{'path_id':p['path_id'],
                'C4_lead_retained':p['observation']['positions'][-1] == 1,
                'finish_lead_retained':p['observation'].get('finish') == 1,
                'straight_rank_change':p['stage_rank_changes']['C4_TO_FINISH']} for p in leaders],
            'stalk_hold_observations':[p['path_id'] for p in stalk],
            'progression_observations':[p['path_id'] for p in usable
                if p['observation']['positions'][0] > p['observation']['positions'][2]],
            'lead_need':'UNKNOWN_CANNOT_INFER_NECESSITY_FROM_LEADING_HISTORY',
            'current_acquisition_probability':None,'current_survival_probability':None,
            'unknown_protection':not usable,
            'baseline_roles_retained':list(baseline['roles'][rid])}

    friction = []
    ids = baseline['ranking']
    for i,a in enumerate(ids):
        for b in ids[i+1:]:
            aa,bb = actors[a],actors[b]
            def observed(*terms):
                return 'OBSERVED_ANALOG_AVAILABLE' if all(terms) else 'UNKNOWN_NOT_IMPOSSIBLE'
            friction.append({'a':a,'b':b,'article_refs':['99-LAL-LIM','136-PLFM'],
                'branches':[
                    {'leader':a,'stalker':b,'evidence_status':observed(aa['lead_acquisition_observations'],bb['stalk_hold_observations'])},
                    {'leader':b,'stalker':a,'evidence_status':observed(bb['lead_acquisition_observations'],aa['stalk_hold_observations'])},
                    {'contestants':[a,b],'evidence_status':observed(aa['lead_acquisition_observations'],bb['lead_acquisition_observations']),
                     'duration':'UNKNOWN','energy_cost':'UNKNOWN'},
                    {'both_cede':[a,b],'alternative_leaders':[x for x in ids if x not in (a,b)],'evidence_status':'UNKNOWN'}],
                'second_friction_2000m_candidates':[x for x in ids if x not in (a,b) and actors[x]['progression_observations']]
                    if header['distance'] == 2000 else [],
                'score_effect':'UNKNOWN_NO_REGISTERED_NUMERICAL_RULE',
                'pair_exclusion_authority':False})

    # The existing result-blind baseline supplies hypothetical roles. A horse
    # need not have previously won to be a future W: do not make historical
    # finishing rank a prerequisite for acquisition/path hypotheses.
    def role_paths(rid):
        paths = [p for p in history[rid] if p['four_call_mapping_known']]
        direct = [p for p in paths if p['matched_course']]
        return direct or paths or [None]

    def joint(paths):
        if any(p is None or not p['matched_course']
               or p['observation']['field_size'] != field_size for p in paths):
            return 'UNKNOWN_TRANSLATION'
        # This rejects only a joint *exact-path hypothesis*. It never excludes
        # a horse/role/pair: unobserved alternatives may still be possible.
        for corner in (0,2,3):
            ranks = [p['observation']['positions'][corner] for p in paths]
            if len(set(ranks)) != len(ranks):
                return 'CONDITIONAL_PATH_RANK_COLLISION'
        return 'CONTEXT_MATCHED_WITNESS' if all(p['matched_context'] for p in paths) else 'GEOMETRY_ONLY_CONTEXT_UNKNOWN'

    def evaluate(prefix, alternatives):
        evaluations = {}
        for rid,depth in alternatives:
            support,unknown,conflict,matched = set(),set(),set(),set()
            full_cases = []
            for fixed in product(*prefix):
                context = '|'.join(p['path_id'] if p else 'UNKNOWN' for p in fixed)
                for tail in role_paths(rid):
                    status = joint((*fixed,tail))
                    full_cases.append((context,tail['path_id'] if tail else 'UNKNOWN',status))
                    if status == 'CONTEXT_MATCHED_WITNESS':
                        support.add(context); matched.add(context)
                    elif status == 'GEOMETRY_ONLY_CONTEXT_UNKNOWN':
                        support.add(context); unknown.add(context)
                    elif status == 'UNKNOWN_TRANSLATION':
                        unknown.add(context)
                    else:
                        conflict.add(context)
            row = {'runner_id':rid,'supported_contexts':sorted(support),'unknown_contexts':sorted(unknown),
                   'conflicted_path_contexts':sorted(conflict),'matched_contexts':sorted(matched),
                   'case_count':len(full_cases),'case_digest':_sha(full_cases),
                   'status':'CONDITIONAL_ANALOG_WITNESS' if support else 'UNKNOWN_NO_JOINT_WITNESS_NOT_EXCLUDED',
                   'matched_context_geometry':bool(matched),
                   'material_exact_evidence':False,
                   'exact_materiality':'UNKNOWN_NO_APPROVED_URW_MATERIALITY_RULE',
                   'prediction_effect':'UNVALIDATED_NOT_A_PROBABILITY_OR_FORMAL_ROLE',
                   'hard_exclusion':False}
            row['sha256'] = _sha(row)
            evaluations[rid] = row
        # Nonempty support-set inclusion is an ordinal robustness hypothesis.
        # UNKNOWNs have no dominance edges, and cannot be pushed down as weak.
        edges = [(a,b) for a in evaluations for b in evaluations if a != b
                 and not evaluations[a]['unknown_contexts'] and not evaluations[b]['unknown_contexts']
                 and evaluations[a]['supported_contexts'] and evaluations[b]['supported_contexts']
                 and set(evaluations[a]['supported_contexts']) > set(evaluations[b]['supported_contexts'])]
        remaining = list(evaluations)
        groups = []
        while remaining:
            front = [b for b in remaining if not any(x == b and a in remaining for a,x in edges)]
            if not front:
                raise ShadowOwnerError('URW_CONDITIONAL_ORDER_CYCLE')
            groups.append(front)
            remaining = [x for x in remaining if x not in set(front)]
        return {'evaluations':evaluations,'partial_order_edges':[list(e) for e in edges],
                'incomparable_groups':groups,
                'interpretation':'CONDITIONAL_GEOMETRY_SUPPORT_ONLY; within-group baseline display order, UNKNOWN incomparable, no role deletion'}

    p2,p3 = {},{}
    for head in baseline['W']:
        hp = role_paths(head)
        p2[head] = evaluate([hp],[(s,2) for s in baseline['P2'] if s != head])
        for second in baseline['P2']:
            if second != head:
                p3[head+'>'+second] = evaluate([hp,role_paths(second)],
                    [(t,3) for t in baseline['P3'] if t not in (head,second)])
    result = {'profile':'URW-CONDITIONAL-ANALOG-v0.2-20261018',
        'status':'CANDIDATE_HYPOTHESES_NOT_PRODUCTION_NOT_EMPIRICALLY_VALIDATED',
        'header_context':header,'actor_evidence':actors,'history_paths':history,
        'runner_scenarios':stances,'pairwise_friction':friction,'head_local_p2':p2,'pair_conditioned_p3':p3,
        'unknown_role_alternatives':{rid:['W','P2','P3'] for rid in ids if actors[rid]['unknown_protection']},
        'unknown_role_alternatives_material':False,
        'baseline_roles_changed':False,'new_numerical_weights':{},'calibrated_probabilities':False,
        'krs_input_or_output_consumed':False,'krs_role_veto_allowed':False,
        'full_urw_model_complete':False,'production_authority':False,'forward_oos_credit':0}
    result['sha256'] = _sha(result)
    return result


def audit_urw_candidate_paper_pipeline(candidate, materialized, *, research_exact_keys=()):
    """Explicit offline contract audit, never called by Formal/entry/Dispatcher.

    Reuse existing Candidate HSV bridge, Common MEC-R3 and Capital verbatim.
    Geometry alone never creates material Exact. Explicit research_exact_keys
    can exercise Common Exact plumbing as labelled hypothetical test cases,
    not as inferred predictive discrimination or permission for a FINAL.
    """
    import copy
    from runtime.local_krs_bridge_candidate import build_candidate_krs
    from runtime.minimum_efficient_coverage import build_mec_plan, validate_mec_plan
    from runtime.capital_policy import resolve_capital_policy

    if (candidate.get('profile') != URW_PROFILE or candidate.get('production_authority') is not False
            or candidate.get('formal_handoff_allowed') is not False
            or candidate.get('sha256') != _sha({k:v for k,v in candidate.items() if k != 'sha256'})):
        raise ShadowOwnerError('URW_PAPER_CANDIDATE_FREEZE_INVALID')
    rows = materialized.get('runners') or []
    if (materialized.get('strict_full_numerical_ready') is not True
            or materialized.get('race_id') != candidate['race_id']
            or (materialized.get('production_evidence_compiler') or {}).get('source_snapshot_sha256') != candidate['source_snapshot_sha256']
            or candidate['runner_numeric_bindings'] != {str(r['runner_id']):_sha(r['canonical_components']) for r in rows}
            or candidate['numeric_provenance_sha256'] != _sha([r['canonical_components'] for r in rows])
            or any((materialized.get('production_numerical_authority') or {}).get(k) is not False for k in
                   ('prediction_consumption_authorized','krs_consumption_authorized',
                    'ticket_consumption_authorized','capital_consumption_authorized'))):
        raise ShadowOwnerError('URW_PAPER_NUMERICAL_BINDING_INVALID')
    baseline, scenario = candidate['existing_local_baseline'],candidate['urw_scenario_prediction']
    if scenario['sha256'] != _sha({k:v for k,v in scenario.items() if k != 'sha256'}):
        raise ShadowOwnerError('URW_PAPER_SCENARIO_FREEZE_INVALID')
    exact = {tuple(key) for key in research_exact_keys}
    available = {(t['head'],t['second'],t['third']) for t in candidate['pair_conditioned_thirds']}
    if any(len(key) != 3 or key not in available for key in exact):
        raise ShadowOwnerError('URW_PAPER_EXACT_HYPOTHESIS_OUTSIDE_FROZEN_SEMANTICS')
    bridge_rows = copy.deepcopy(rows)
    for row in bridge_rows:
        row['candidate_static_roles'] = list(baseline['roles'][str(row['runner_id'])])
    header = scenario['header_context']
    # The unchanged Engine uses prediction_id as its seed namespace and in
    # simulation_snapshot_id. Its native race keys must survive the Candidate
    # bridge; venue-only metadata otherwise silently produces an anonymous
    # snapshot shared by different races. This changes offline replay draws,
    # not Engine physics, parameters or Production input authority.
    bridge = build_candidate_krs({'race_id':candidate['race_id'],
        'race':{'prediction_id':candidate['race_id'],'racecourse':'浦和',
            'date':candidate['race_date'],'race_no':candidate['race_no'],
            'course_rule_version':candidate['venue_canon'],
            'venue':'URW','distance':header['distance'],'surface':'dirt','course':'left'},
        'runners':bridge_rows,
        'candidate_full_numerical_summary':{'numeric_transport_complete':True,
            'mapping_id':materialized['production_numerical_authority']['mapping_id'],
            'sha256':materialized['production_numerical_summary']['sha256']},
        'candidate_current_state':copy.deepcopy(materialized.get('numerical_current_state') or {}),
        'candidate_environment':copy.deepcopy(materialized.get('numerical_environment') or {})})
    semantic = {'family_id':'LOCAL','race_id':candidate['race_id'],
        'runners':[{'runner_id':str(r['runner_id'])} for r in rows],
        'static_prediction':{'ranking':list(baseline['ranking']),
            'roles':copy.deepcopy(baseline['roles']),'production_authority':False},
        'role_registry':[{'runner_id':rid,'column':col,'status':'CORE','production_authority':False}
            for rid,cols in baseline['roles'].items() for col in cols],
        'pair_dispositions':[{'head':p['head'],'second':p['second'],'status':'PROTECT',
            'production_authority':False,'reason':'OFFLINE_UNVALIDATED_URW_PAIR_HYPOTHESIS'}
            for p in candidate['head_local_pairs']],
        'third_dispositions':[],
        'capital_policy':{'mode':'HARD_RACE_BUDGET','max_race_capital':0,'insufficient_action':'PAPER'}}
    for t in candidate['pair_conditioned_thirds']:
        semantic['third_dispositions'].append({'head':t['head'],'second':t['second'],'third':t['third'],
            'status':'PURCHASE' if (t['head'],t['second'],t['third']) in exact else 'PROTECT',
            'production_authority':False,
            'reason':'EXPLICIT_OFFLINE_EXACT_TEST_HYPOTHESIS_NOT_PREDICTION' if (t['head'],t['second'],t['third']) in exact
                     else 'OFFLINE_UNKNOWN_P3_SET_PROTECTION_NOT_ROLE_DELETION'})
    mec = build_mec_plan(semantic)
    validate_mec_plan(mec)
    capital = resolve_capital_policy(semantic,mec)
    if not mec['minimum_required_capital'] or capital['paper_only'] is not True:
        raise ShadowOwnerError('URW_OFFLINE_AUDIT_MUST_REMAIN_PAPER')
    out = {'profile':'URW-OFFLINE-PIPELINE-CONTRACT-v0.3-20261018',
        'status':'OFFLINE_PAPER_CONTRACT_ONLY_NOT_FORMAL_FINAL',
        'candidate_freeze_sha256':candidate['sha256'],'source_receipt_sha256':candidate['source_receipt_sha256'],
        'semantic_request':semantic,'candidate_krs_input':bridge['candidate_krs_input_data'],
        'candidate_krs_input_sha256':bridge['candidate_krs_input_sha256'],
        'mec_contract_result':mec,'capital_contract_result':capital,
        'research_exact_test_hypotheses':[list(key) for key in sorted(exact)],
        'exact_materiality_inferred_from_geometry':False,
        'engine_run_performed':False,'runtime_send_count':0,'signed_final_claim':False,
        'production_authority':False,'purchase_authority':False,'actual_purchase':False,
        'prediction_quality_proven':False,'formal_no_bet_claim':False,'forward_oos_credit':0}
    out['sha256'] = _sha(out)
    return out


# Research only. These functions have no call site in the Production Static
# Owner, Formal request, KRS transport, MEC or Capital path.
def _urw_source_frame_witness(source):
    """Read NAR's actual frame rowspans; never infer a frame from horse no.

    Flattened source tables omit the frame on the second/third horse in a
    frame. The original HTML retains courseNum/horseNum and their rowspans.
    This research reader does not change SOURCE, numerical cells or statuses.
    """
    from html.parser import HTMLParser
    from urllib.parse import urlparse,parse_qs
    from runtime.local_physical.source_acquisition import verify_source_artifact
    valid,errors=verify_source_artifact(source)
    if not valid:raise ShadowOwnerError('URW_FRAME_SOURCE_INTEGRITY:'+','.join(errors))
    cards=[s for s in source.get('sources') or [] if s.get('source_class')=='OFFICIAL_RACE_CARD_CURRENT_STATE_BODY_WEIGHT' and s.get('official') is True]
    if len(cards)!=1:raise ShadowOwnerError('URW_FRAME_CARD_REQUIRED')
    card=cards[0];url=urlparse(card['final_url'])
    if (url.scheme!='https' or url.hostname!='www.keiba.go.jp'
            or url.path!='/KeibaWeb/TodayRaceInfo/DebaTable'
            or parse_qs(url.query).get('k_babaCode')!=['18']):
        raise ShadowOwnerError('URW_FRAME_SOURCE_SCOPE')
    class Rows(HTMLParser):
        def __init__(self):
            super().__init__();self.rows=[];self.stack=[];self.cell=None
        def handle_starttag(self,tag,attrs):
            attrs=dict(attrs)
            if tag=='tr':self.stack.append({})
            if tag=='td':
                classes=set(attrs.get('class','').split())
                kind='frame' if 'courseNum' in classes else 'horse' if 'horseNum' in classes else None
                self.cell=[kind,attrs.get('rowspan','1'),''] if kind else None
        def handle_data(self,data):
            if self.cell:self.cell[2]+=data
        def handle_endtag(self,tag):
            if tag=='td' and self.cell:
                kind,span,value=self.cell
                if self.stack:self.stack[-1][kind]=(value.strip(),span)
                self.cell=None
            if tag=='tr' and self.stack:
                row=self.stack.pop()
                if 'horse' in row and row['horse'][0].isdigit():self.rows.append(row)
    raw=gzip.decompress(base64.b64decode(card['raw_gzip_b64'],validate=True))
    try:page=raw.decode('utf-8')
    except UnicodeError:page=raw.decode('cp932')
    parser=Rows();parser.feed(page)
    result={};frame=None;remaining=0
    try:
        for row in parser.rows:
            horse,span=row['horse'];horse=str(int(horse));span=int(span)
            if 'frame' in row:
                if remaining:raise ValueError('OVERLAPPING_FRAME_SPAN')
                value,frame_span=row['frame'];frame=int(value);remaining=int(frame_span)
            if not frame or not 1<=frame<=8 or span<=0 or remaining<span or horse in result:
                raise ValueError('UNPROVEN_FRAME_SPAN')
            result[horse]=frame;remaining-=span
        if remaining:raise ValueError('INCOMPLETE_FRAME_SPAN')
    except ValueError as exc:
        raise ShadowOwnerError('URW_FRAME_ROWSPAN_INVALID:'+str(exc)) from exc
    declared=(source.get('declared_runner_universe') or {}).get('runners') or []
    if not result or set(result)!={str(r['runner_id']) for r in declared}:
        raise ShadowOwnerError('URW_FRAME_DECLARED_UNIVERSE_MISMATCH')
    return {'source_id':card['source_id'],'raw_sha256':card['raw_sha256'],
        'snapshot_sha256':card['snapshot_sha256'],'effective_time':card['fetched_at'],
        'rule':'EXPLICIT_NAR_COURSE_NUM_AND_HORSE_NUM_ROWSPAN','frames':result}


def owner_feature_pack(candidate, numerical, *, urw_transfer=False, source_artifact=None):
    """Result-blind inputs for a venue-local conditional choice experiment.

    RULED-NEUTRAL cells are missing observations, never weak ability. They
    receive no score contribution after training-only centering. Source
    provenance and the observed/missing mask survive separately from scores.
    """
    import statistics
    if candidate.get('production_authority') is not False or candidate.get('sha256') != _sha({k:v for k,v in candidate.items() if k!='sha256'}):
        raise ShadowOwnerError('CANDIDATE_FEATURE_FREEZE_INVALID')
    if urw_transfer and candidate.get('venue_id','URW')!='URW':
        raise ShadowOwnerError('URW_TRANSFER_FEATURE_SCOPE')
    frames=None
    if source_artifact is not None:
        if not urw_transfer or candidate.get('source_snapshot_sha256')!=source_artifact.get('source_snapshot_sha256'):
            raise ShadowOwnerError('URW_FRAME_CANDIDATE_SOURCE_BINDING')
        frames=_urw_source_frame_witness(source_artifact)
    rows=numerical.get('runners') or []
    if (candidate.get('race_id')!=numerical.get('race_id')
            or candidate.get('numeric_provenance_sha256')!=_sha([r['canonical_components'] for r in rows])
            or candidate.get('source_snapshot_sha256')!=(numerical.get('production_evidence_compiler')
                or numerical.get('candidate_evidence_compiler') or {}).get('source_snapshot_sha256')):
        raise ShadowOwnerError('CANDIDATE_FEATURE_NUMERICAL_BINDING')
    def mean(values):
        values=[v for v in values if type(v) in (int,float) and math.isfinite(v)]
        return statistics.mean(values) if values else None
    evidence=candidate.get('urw_evidence') or candidate.get('venue_evidence') or {}
    result={}
    refs={}
    for row in rows:
        rid=str(row['runner_id']);values={};refs[rid]={}
        for name,cell in row['canonical_components'].items():
            val=cell.get('value');status=cell.get('terminal_status')
            if status not in VALID or type(val) not in (int,float) or not math.isfinite(val):
                raise ShadowOwnerError('CANDIDATE_FEATURE_CELL_INVALID')
            values['INDEX:'+name]=float(val) if status=='CALCULATED' else None
            refs[rid][name]={'cell_sha256':_sha(cell),'terminal_status':status,'evidence_refs':cell['evidence_refs']}
        ev=evidence.get(rid) or {};starts=ev.get('past_starts') or []
        current=ev.get('current_condition_translation') or {}
        if frames is not None:
            observed=frames['frames'][rid]
            if current.get('current_frame_no') not in (None,observed):
                raise ShadowOwnerError('URW_FRAME_OBSERVATION_CONFLICT')
            current={**current,'current_frame_no':observed}
        # Observed rank fractions preserve field-size units; they are not
        # probabilities of winning the target race. No winner-label input.
        usable=[s for s in starts if type(s.get('field_size')) is int and s['field_size']>=2]
        direct=[s for s in usable if s.get('matched_urw_distance') or s.get('matched_venue_distance')]
        dirt=[s for s in usable if s.get('surface')=='DIRT']
        # v1 is retained for byte-bound rejected models. In the opt-in URW
        # experiment, an old direct observation must not hide newer transfers.
        # Two-call summaries do not establish a four-corner position path.
        # URW 800m requires its own sprint observations; a 1400m first corner
        # must not be relabelled as sprint acquisition (Canon SATG-URW).
        sprint=current.get('current_distance_m')==800
        analog=([s for s in dirt if len(s.get('positions') or [])==(2 if sprint else 4)
                 and (not sprint or s in direct)]
                if urw_transfer else direct or dirt)
        first=lambda s:(s.get('positions') or [None])[0]
        last=lambda s:(s.get('positions') or [None])[-1]
        fraction=lambda rank,s:float(rank)/s['field_size'] if type(rank) is int else None
        leader=[s for s in analog if first(s)==1]
        values.update({
            'STAGE:direct_finish':mean(fraction(s.get('finish'),s) for s in direct),
            'STAGE:direct_win':mean(int(s.get('finish')==1) for s in direct if type(s.get('finish')) is int),
            'STAGE:direct_place':mean(int(s['finish']<=3) for s in direct if type(s.get('finish')) is int),
            'STAGE:acquisition':mean(fraction(first(s),s) for s in analog),
            'STAGE:last_corner':mean(fraction(last(s),s) for s in analog),
            'STAGE:progression':mean((first(s)-last(s))/s['field_size'] for s in analog if type(first(s)) is int and type(last(s)) is int),
            'STAGE:final_reserve':mean((last(s)-s['finish'])/s['field_size'] for s in analog if type(last(s)) is int and type(s.get('finish')) is int),
            'STAGE:lead':mean(int(first(s)==1) for s in analog if type(first(s)) is int),
            'STAGE:leader_survival':mean(int(s['finish']<=3) for s in leader if type(s.get('finish')) is int),
            'STAGE:distance_delta':mean(current['current_distance_m']-s['distance'] for s in analog if type(s.get('distance')) is int) if current.get('current_distance_m') else None,
            'STAGE:frame':current.get('current_frame_no'),
            'STAGE:assigned_load':current.get('current_assigned_load'),
            'STAGE:bodyweight_change':current.get('current_body_weight_change'),
        })
        if urw_transfer:
            # Geometry and observed changes only: no hand-set score, winner
            # bonus, class conversion or coefficient learned from holdout.
            from runtime.local_production_static_owner import _start_date
            recent=sorted(dirt,key=lambda s:_start_date(s.get('date')) or datetime.min.replace(tzinfo=timezone.utc),reverse=True)
            latest=recent[0] if recent else {}
            distance=current.get('current_distance_m')
            latest_distance=latest.get('distance')
            frame=current.get('current_frame_no')
            values.update({
                'STAGE:distance_delta':mean(distance-s['distance'] for s in dirt
                    if type(s.get('distance')) is int) if type(distance) is int else None,
                'TRANSFER:latest_distance_delta':distance-latest_distance
                    if type(distance) is int and type(latest_distance) is int else None,
                'TRANSFER:latest_finish':fraction(latest.get('finish'),latest),
                'TRANSFER:direct_coverage':len(direct)/len(usable) if usable else None,
                'TRANSFER:comparable_path_coverage':len(analog)/len(dirt) if dirt else None,
                'TRANSFER:distance_x_frame':distance*frame
                    if type(distance) is int and type(frame) is int else None,
            })
        result[rid]=values
    out={'schema':'URW-CONDITIONAL-TRANSFER-FEATURES-v2' if urw_transfer else 'LOCAL-VENUE-CONDITIONAL-FEATURES-v1','race_id':candidate['race_id'],
        'venue_id':candidate.get('venue_id','URW'),'venue_canon':candidate.get('venue_canon'),
        'venue_canon_source_sha256':candidate.get('venue_canon_source_sha256'),
        'race_date':candidate['race_date'],'scheduled_post_at':candidate['scheduled_post_at'],
        'prediction_cutoff':candidate['prediction_cutoff'],'source_snapshot_sha256':candidate['source_snapshot_sha256'],
        'source_receipt_sha256':candidate.get('source_receipt_sha256'),
        'candidate_sha256':candidate['sha256'],'runners':result,'cell_provenance':refs,
        'baseline':candidate['existing_local_baseline'],'feature_names':sorted(next(iter(result.values()))),
        'unknown_not_weak':True,'production_authority':False}
    if frames is not None:out['source_frame_witness']=frames
    out['sha256']=_sha(out)
    return out


def _choice_features(pack, rid, prefix, *, stage_evidence=True, interactions=True):
    row=pack['runners'][rid]
    out={k:v for k,v in row.items() if stage_evidence or k.startswith('INDEX:')}
    if interactions and stage_evidence and prefix:
        head=pack['runners'][prefix[0]]
        def product(a,b):return a*b if a is not None and b is not None else None
        def difference(a,b):return a-b if a is not None and b is not None else None
        out.update({'PAIR:lead_collision':product(row['STAGE:lead'],head['STAGE:lead']),
            'PAIR:frame_gap':difference(row['STAGE:frame'],head['STAGE:frame']),
            'PAIR:progression_vs_head_lead':product(row['STAGE:progression'],head['STAGE:lead']),
            'PAIR:reserve_vs_head_lead':product(row['STAGE:final_reserve'],head['STAGE:lead'])})
        if len(prefix)==2:
            second=pack['runners'][prefix[1]]
            out.update({'THIRD:second_lead_collision':product(row['STAGE:lead'],second['STAGE:lead']),
                'THIRD:second_frame_gap':difference(row['STAGE:frame'],second['STAGE:frame']),
                'THIRD:reserve_vs_second_lead':product(row['STAGE:final_reserve'],second['STAGE:lead'])})
    return out


# Source references for NON-PRODUCTION adapters, not a Production Scope list.
# OHI v2.1 was recovered from the user's canonical archive. Its explicit
# current course family is required; past summary-only OCF/SRA remains UNKNOWN.
# This PR's research scope is South Kanto only. Existing shared LOCAL source
# and discovery support for other venues is unchanged outside this adapter.
VENUE_CANDIDATE_SOURCES = {
    'URW':(URW_CANON,URW_CANON_SHA256),
    'OHI':('OHI-v2.1-20260903','8a6373933fce596cd5e4ecfd37f183bb76152740b05ed12fb2e6766d391fefa4'),
    'FNB':('KM-LOCAL-FNB-v2.1-20260928-R1','158b78d9509ac805409d77bcc569b4910ffd0db90e639f4e70885925ec78fd6f'),
}


def compile_public_venue_candidate(request, source, numerical, *, historical_replay=False,
                                   declared_snapshot_shadow=False):
    """Reuse LOCAL facts/29-index baseline with a verified venue source ref.

    Deliberately UNSIGNED public research: cannot fill Signed SOURCE, Formal
    Intent or Production Owner. A model fitted at another venue is rejected
    by predict_conditioned_owner. No KAW Owner or coefficient is copied.
    """
    import copy
    from urllib.parse import urlparse,parse_qs
    from runtime.local_physical.nar_source_manifest import LOCAL_BABA_CODES,VENUE_NAMES
    from runtime.local_physical.source_acquisition import verify_source_artifact
    from runtime.local_nar_evidence_candidate import parse_race_card
    from runtime.local_production_static_owner import _card_heading,_start_date
    from runtime.local_fullnumerical_candidate import REQUIRED
    from runtime.local_krs_bridge_candidate import build_candidate_prediction_structure_derived
    now=datetime.now(timezone.utc);venue=request.get('venue_id')
    if declared_snapshot_shadow and (venue!='URW' or historical_replay):
        raise ShadowOwnerError('URW_DECLARED_SNAPSHOT_PRESTART_ONLY')
    if request.get('family_id')!='LOCAL' or venue not in LOCAL_BABA_CODES:
        raise ShadowOwnerError('VENUE_CANDIDATE_LOCAL_ONLY')
    if venue not in ('URW', 'KAW', 'FNB', 'OHI'):
        raise ShadowOwnerError('VENUE_RESEARCH_OUTSIDE_SOUTH_KANTO_SCOPE:'+str(venue))
    if venue not in VENUE_CANDIDATE_SOURCES:
        raise ShadowOwnerError('VENUE_CURRENT_CANON_UNRESOLVED:'+str(venue))
    valid,errors=verify_source_artifact(source)
    if not valid:raise ShadowOwnerError('VENUE_PUBLIC_SOURCE_INVALID:'+','.join(errors))
    context=source.get('source_race_context') or {}
    for key in ('venue_id','race_date','race_no'):
        if str(request.get(key)).replace('/','-')!=str(context.get(key)).replace('/','-'):
            raise ShadowOwnerError('VENUE_PUBLIC_SOURCE_RACE_MISMATCH')
    post=_aware(request['scheduled_post_at'],'POST');cutoff=_aware(request['prediction_cutoff'],'CUTOFF')
    if (source.get('race_id')!=request['race_id'] or request.get('execution_id')!=request['race_id']
            or not _aware(source['source_freeze_at'],'SOURCE_FREEZE')<cutoff<post
            or (not historical_replay and now>=cutoff)):
        raise ShadowOwnerError('VENUE_PUBLIC_SOURCE_CLOCK_OR_IDENTITY')
    if declared_snapshot_shadow:
        from runtime.local_race_key_intake import JST
        frozen=_aware(source['source_freeze_at'],'SOURCE_FREEZE')
        if (frozen>now or frozen.astimezone(JST).date()!=now.astimezone(JST).date()
                or post.astimezone(JST).date()!=now.astimezone(JST).date()):
            raise ShadowOwnerError('URW_DECLARED_SNAPSHOT_DATE_OR_CLOCK')
    cards=[s for s in source['sources'] if s.get('source_class')=='OFFICIAL_RACE_CARD_CURRENT_STATE_BODY_WEIGHT' and s.get('official') is True]
    if len(cards)!=1:raise ShadowOwnerError('VENUE_PUBLIC_CARD_REQUIRED')
    card=cards[0];url=urlparse(card['final_url']);query=parse_qs(url.query)
    if (url.scheme!='https' or url.hostname!='www.keiba.go.jp' or not url.path.endswith('/DebaTable')
            or query.get('k_babaCode')!=[LOCAL_BABA_CODES[venue]]
            or query.get('k_raceDate')!=[str(request['race_date']).replace('-','/')]
            or query.get('k_raceNo')!=[str(request['race_no'])] or card.get('cutoff_relation')!='PRE_CUTOFF'):
        raise ShadowOwnerError('VENUE_PUBLIC_CARD_URL_IDENTITY')
    import re,unicodedata
    from runtime.local_production_static_owner import _VisibleText
    raw=gzip.decompress(base64.b64decode(card['raw_gzip_b64'],validate=True))
    try:page=raw.decode('utf-8')
    except UnicodeError:page=raw.decode('cp932')
    parser=_VisibleText();parser.feed(page)
    visible=re.sub(r'\s+','',unicodedata.normalize('NFKC',''.join(parser.fragments)))
    y,m,d=map(int,str(request['race_date']).split('-'))
    pattern=rf'{y}年{m}月{d}日.{{0,30}}{VENUE_NAMES[venue]}.{{0,12}}第{request["race_no"]}競走'
    if not re.search(pattern,visible):raise ShadowOwnerError('VENUE_PUBLIC_CARD_BODY_IDENTITY')
    header=_card_heading(source);header['class_tokens']=_urw_class_tokens(header['class'])
    header['going']=(source.get('normalized_evidence') or {}).get('track_condition',{}).get('value')
    start=(source.get('normalized_evidence') or {}).get('start_time') or {}
    from runtime.local_race_key_intake import JST
    if start.get('authority')!='NAR_OFFICIAL' or start.get('value')!=post.astimezone(JST).strftime('%H:%M'):
        raise ShadowOwnerError('VENUE_PUBLIC_OFFICIAL_POST_MISMATCH')
    rows=numerical.get('runners') or [];ids=[str(r['runner_id']) for r in rows]
    universe='declared_runner_universe' if declared_snapshot_shadow else 'active_runner_universe'
    active=[str(r['runner_id']) for r in (source.get(universe) or {}).get('runners') or []]
    parsed=parse_race_card(source)
    status=source.get('runner_status_registry') or []
    active_status={str(r['runner_id']) for r in status if r.get('status')=='ACTIVE'}
    summary=numerical.get('candidate_full_numerical_summary') or {}
    if declared_snapshot_shadow:
        numerical_ready=(summary.get('numeric_transport_complete') is True
            and summary.get('unresolved_count')==0 and summary.get('production_authority') is False
            and set(summary.get('required_indices') or [])==set(REQUIRED)
            and (numerical.get('candidate_evidence_compiler') or {}).get('source_snapshot_sha256')==source['source_snapshot_sha256']
            and (numerical.get('candidate_evidence_compiler') or {}).get('production_authority') is False)
        scope_ready=(set(ids)=={str(r['runner_id']) for r in status}
            and all(r.get('status') in ('ACTIVE','ACTIVE_DECLARED') for r in status)
            and not numerical.get('production_numerical_authority'))
    else:
        numerical_ready=(numerical.get('strict_full_numerical_ready') is True
            and set(numerical.get('required_indices') or [])==set(REQUIRED)
            and (numerical.get('production_evidence_compiler') or {}).get('source_snapshot_sha256')==source['source_snapshot_sha256'])
        scope_ready=(active_status==set(ids) and not any(r.get('status')=='ACTIVE_DECLARED' for r in status)
            and all((numerical.get('production_numerical_authority') or {}).get(k) is False for k in
                ('prediction_consumption_authorized','krs_consumption_authorized','ticket_consumption_authorized','capital_consumption_authorized')))
    if (len(ids)<3 or len(ids)!=len(set(ids)) or len(active)!=len(set(active)) or set(ids)!=set(active)
            or not scope_ready or not numerical_ready
            or numerical.get('race_id')!=request['race_id']
            or any(set(r.get('canonical_components') or {})!=set(REQUIRED) for r in rows)
            ):
        raise ShadowOwnerError('VENUE_PUBLIC_ACTIVE_FULL29_OR_SCOPE_HOLD')
    # OHI families require explicit current official course evidence.
    def course_family(distance):
        if venue=='OHI':
            current_header=visible.split('競走馬')[0]
            for marker,family in (('内コース・右','R-IN'),('外コース・右','R-OUT'),('外コース・左','L-OUT')):
                if marker in current_header:return family
            return 'UNKNOWN'
        return 'CURRENT_SOURCE_COURSE'
    if venue=='OHI' and course_family(header['distance'])=='UNKNOWN':
        raise ShadowOwnerError('OHI_OFFICIAL_CURRENT_COURSE_FAMILY_REQUIRED')
    evidence={}
    for rid in ids:
        if rid not in parsed:raise ShadowOwnerError('VENUE_PUBLIC_ACTIVE_CARD_MISMATCH')
        observations=[]
        for s in sorted(parsed[rid].get('starts') or [],key=lambda x:_start_date(x.get('date')) or datetime.min,reverse=True)[:5]:
            when=_start_date(s.get('date'))
            if when is None or when.date()>=post.astimezone(JST).date():
                raise ShadowOwnerError('VENUE_PUBLIC_NON_PRESTART_HISTORY')
            same=str(s.get('venue','')).replace('ナ','')==VENUE_NAMES[venue]
            positions=s.get('content_positions') or []
            observations.append({'date':s['date'],'venue':s.get('venue'),'distance':s.get('distance'),
                'surface':s.get('surface'),'finish':s.get('finish'),'field_size':s.get('field_size'),
                'positions':positions,'going':s.get('going'),'class_tokens':_urw_class_tokens(s.get('race_name')),
                # OHI summaries do not prove past inner/outer/left or sand
                # regime. Never turn same venue/distance into a Direct analog.
                'matched_venue_distance':venue!='OHI' and same and s.get('distance')==header['distance'] and course_family(header['distance'])!='UNKNOWN'
                    and course_family(s.get('distance'))==course_family(header['distance']),
                'raw_reference':s.get('raw')})
            if venue=='OHI':
                observations[-1].update(past_course_family='UNKNOWN_FROM_SUMMARY',past_sand_regime='UNKNOWN',
                    current_condition_comparability='UNQUALIFIED_NOT_DIRECT_EVIDENCE')
        current={'current_distance_m':header['distance'],'current_frame_no':parsed[rid].get('frame_no'),
            'current_assigned_load':parsed[rid].get('current_load'),
            'current_body_weight_change':parsed[rid].get('current_body_weight_change'),
            'source_id':parsed[rid].get('race_card_source_id'),
            'source_snapshot_sha256':parsed[rid].get('race_card_snapshot_sha256'),
            'effective_time':parsed[rid].get('race_card_fetched_at'),
            'numerical_venue_effects':'UNKNOWN_NOT_PORTED_FROM_ANOTHER_VENUE'}
        if venue=='OHI':
            current.update(current_course_family=course_family(header['distance']),
                sand_regime='UNKNOWN_CURRENT_OFFICIAL_DEPTH_NOT_OBSERVED',canon_sand_basis='SRA-9_REFERENCE_ONLY',
                direct_history_qualification='HOLD_OCF_AND_SRA_EVIDENCE_REQUIRED',venue_score_adjustments_applied=False)
        if venue=='URW':
            local_observations=[{**s,'matched_urw_distance':s['matched_venue_distance']} for s in observations]
            current=_urw_current_condition_translation(parsed[rid],local_observations,header)
        evidence[rid]={'past_starts':observations,
            'current_condition_translation':current,
            'current_bias':'UNKNOWN_NO_HISTORICAL_CARRYOVER','venue_source_ref':VENUE_CANDIDATE_SOURCES[venue][0]}
    baseline=build_candidate_prediction_structure_derived({'runners':copy.deepcopy(rows)})['candidate_static_prediction']
    completed=datetime.now(timezone.utc)
    if not historical_replay and completed>=cutoff:raise ShadowOwnerError('VENUE_PUBLIC_COMPLETED_AFTER_CUTOFF')
    out={'profile':'LOCAL-VENUE-SOURCE-CANDIDATE-v0.1-20261019','venue_id':venue,
        'venue_canon':VENUE_CANDIDATE_SOURCES[venue][0],'venue_canon_source_sha256':VENUE_CANDIDATE_SOURCES[venue][1],
        'race_id':request['race_id'],'race_date':request['race_date'],'race_no':request['race_no'],
        'scheduled_post_at':request['scheduled_post_at'],'prediction_cutoff':request['prediction_cutoff'],
        'source_snapshot_sha256':source['source_snapshot_sha256'],'source_receipt_sha256':None,
        'source_signature_authority':'UNSIGNED_PUBLIC_SOURCE_NOT_SIGNED_SOURCE',
        'numeric_provenance_sha256':numerical['candidate_index_provenance_sha256'] if declared_snapshot_shadow else numerical['index_provenance_hash'],
        'existing_local_baseline':baseline,'ranking':baseline['ranking'],'role_columns':baseline['roles'],
        'venue_evidence':evidence,'current_course_family':course_family(header['distance']),
        'compiled_at':completed.isoformat(),'frozen_at':None if historical_replay else completed.isoformat(),
        'temporal_class':'UNSIGNED_FROZEN_DECLARED_SNAPSHOT_SHADOW' if declared_snapshot_shadow else
            'HISTORICAL_RESEARCH' if historical_replay else 'UNSIGNED_PUBLIC_PRESTART_SHADOW',
        'status':'CANDIDATE_SHARED_BASELINE_VENUE_INPUT_ADAPTER_NOT_VALIDATED_OWNER',
        'paper_ticket_count':0,'paper_capital_yen':0,'production_authority':False,
        'formal_handoff_allowed':False,'signed_final_claim':False,'forward_oos_credit':0,
        'prediction_consumption_authorized':False,'actual_purchase':False,'kaw_owner_reused':False}
    if declared_snapshot_shadow:
        out.update(runner_universe_basis='DECLARED_NOT_VERIFIED_ACTIVE',
            runner_status_registry=copy.deepcopy(status),source_freeze_at=source['source_freeze_at'],
            source_age_seconds=(completed-_aware(source['source_freeze_at'],'SOURCE_FREEZE')).total_seconds(),
            freshness_claim=False,formal_ready=False,krs_consumption_authorized=False,
            ticket_consumption_authorized=False,capital_consumption_authorized=False)
    out['sha256']=_sha(out);return out


def compile_reference_prediction(request, source, *, now=None):
    """Unsigned URW record-based reference; no numerical/Owner/FINAL gate.

    Reuse the existing card parser and observed-record comparator, without
    invoking a Production Owner or borrowing its scope. This is an unvalidated
    ordinal reference, not a newly fitted model or independent W/P2/P3 result.
    """
    from runtime.local_nar_evidence_candidate import parse_race_card
    from runtime.local_production_static_owner import _card_heading, _runner_facts
    from runtime.local_physical.source_acquisition import verify_source_artifact
    from runtime.local_race_key_intake import JST
    import copy
    injected_clock = now is not None
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None or request.get('family_id') != 'LOCAL' or request.get('venue_id') != 'URW':
        raise ShadowOwnerError('REFERENCE_URW_LOCAL_ONLY')
    context = source.get('source_race_context') or {}
    if any(str(context.get(k)) != str(request.get(k)) for k in ('venue_id', 'race_date', 'race_no')):
        raise ShadowOwnerError('REFERENCE_SOURCE_IDENTITY_MISMATCH')
    if request.get('race_id') != source.get('race_id'):
        raise ShadowOwnerError('REFERENCE_SOURCE_IDENTITY_MISMATCH')
    cutoff = _aware(source['prediction_cutoff'], 'REFERENCE_CUTOFF')
    frozen = _aware(source['source_freeze_at'], 'REFERENCE_SOURCE_FREEZE')
    post = _aware(source['scheduled_post_at'], 'REFERENCE_POST')
    if not frozen <= now < cutoff < post or now.astimezone(JST).date().isoformat() > request['race_date']:
        raise ShadowOwnerError('REFERENCE_PRESTART_WINDOW_EXPIRED')
    valid, errors = verify_source_artifact(source)
    if not valid:
        raise ShadowOwnerError('REFERENCE_RAW_SOURCE_INTEGRITY:' + ','.join(errors))
    from urllib.parse import urlparse, parse_qs
    from runtime.local_race_day_dispatcher import raw_html
    import re
    cards = [s for s in source.get('sources') or []
             if s.get('source_class') == 'OFFICIAL_RACE_CARD_CURRENT_STATE_BODY_WEIGHT' and s.get('official') is True]
    if len(cards) != 1:
        raise ShadowOwnerError('REFERENCE_OFFICIAL_CARD_REQUIRED')
    url = urlparse(cards[0]['final_url']); query = parse_qs(url.query)
    if (url.scheme != 'https' or url.hostname != 'www.keiba.go.jp'
            or url.path != '/KeibaWeb/TodayRaceInfo/DebaTable'
            or query.get('k_babaCode') != ['18'] or query.get('k_raceNo') != [str(request['race_no'])]
            or query.get('k_raceDate') != [request['race_date'].replace('-', '/')]):
        raise ShadowOwnerError('REFERENCE_OFFICIAL_CARD_IDENTITY')
    from runtime.local_physical.source_acquisition import _html_text
    heading = re.sub(r'\s+', '', _html_text(raw_html(cards[0]))).split('競走馬')[0]
    y, m, d = map(int, request['race_date'].split('-'))
    if not re.search(rf'{y}年{m}月{d}日.*?浦和第{request["race_no"]}競走', heading):
        raise ShadowOwnerError('REFERENCE_OFFICIAL_CARD_BODY_IDENTITY')
    parsed = parse_race_card(source)
    declared = (source.get('declared_runner_universe') or {}).get('runners') or []
    if not parsed or len(declared) != len(parsed) or {str(x['runner_id']) for x in declared} != set(parsed):
        raise ShadowOwnerError('REFERENCE_DECLARED_UNIVERSE_MISMATCH')
    if any(parsed[str(x['runner_id'])]['name'] != x['name'] for x in declared):
        raise ShadowOwnerError('REFERENCE_RUNNER_NAME_MISMATCH')
    statuses = {str(x['runner_id']): x for x in source.get('runner_status_registry') or []}
    cancelled = {rid for rid, row in statuses.items() if row.get('status') == 'CANCELLED'}
    ids = [rid for rid in parsed if rid not in cancelled]
    if len(ids) < 2:
        raise ShadowOwnerError('REFERENCE_RUNNER_UNIVERSE_TOO_SMALL')
    header = _card_heading(source)
    header['going'] = (source.get('normalized_evidence') or {}).get('track_condition', {}).get('value')
    header['class_tokens'] = _urw_class_tokens(header['class'])
    start = (source.get('normalized_evidence') or {}).get('start_time') or {}
    if start.get('authority') != 'NAR_OFFICIAL' or start.get('value') != post.astimezone(JST).strftime('%H:%M'):
        raise ShadowOwnerError('REFERENCE_OFFICIAL_POST_MISMATCH')
    day = post.astimezone(JST).replace(hour=0, minute=0, second=0, microsecond=0)
    facts = {rid: _runner_facts(parsed[rid], venue_name='浦和', distance=header['distance'], race_day=day) for rid in ids}
    # Same transparent observed-record ordering as the existing evidence-only
    # baseline. Missing exact-course history stays UNKNOWN, not a weak score.
    def key(rid):
        f = facts[rid]
        return tuple(-float(v) if v is not None else 0 for v in (
            f['exact_wins'], f['exact_podiums'], f['exact_best_finish_share'],
            f['venue_best_finish_share'], f['recent_dirt_finish_share'], f['dirt_best_finish_share']))
    order = sorted(ids, key=lambda rid: (key(rid), int(rid)))
    comparable = [rid for rid in order if facts[rid]['exact_races']]
    comparable_ranks = {}
    previous = None
    for i, rid in enumerate(comparable, 1):
        if key(rid) != previous:
            rank = i
        comparable_ranks[rid] = rank
        previous = key(rid)
    rows = []
    for rid in order:
        f = facts[rid]; card = parsed[rid]
        observations = []
        for s in card.get('starts') or []:
            observations.append({'date': s.get('date'), 'venue': s.get('venue'), 'distance': s.get('distance'),
                'finish': s.get('finish'), 'field_size': s.get('field_size'), 'positions': s.get('content_positions') or [],
                'surface': s.get('surface'), 'going': s.get('going'), 'class_tokens': _urw_class_tokens(s.get('race_name')),
                'matched_urw_distance': str(s.get('venue', '')).replace('ナ', '') == '浦和' and s.get('distance') == header['distance'],
                'raw_reference': s.get('raw')})
        rows.append({'runner_id': rid, 'name': card['name'], 'reference_rank': comparable_ranks.get(rid),
            'ability_status': 'OBSERVED_RECORD_REFERENCE_UNVALIDATED' if rid in comparable_ranks else 'UNKNOWN_CONDITION_TRANSFER_NOT_WEAK',
            'facts': f, 'past_starts': observations,
            'current_conditions': _urw_current_condition_translation(card, observations, header),
            'jockey': card.get('current_jockey'), 'trainer': card.get('trainer'),
            'pedigree': {k: card.get(k) for k in ('sire', 'dam', 'damsire')},
            'current_bias': 'UNKNOWN', 'bloodline_effect': 'UNKNOWN', 'jockey_trainer_effect': 'UNKNOWN',
            'runner_status': copy.deepcopy(statuses.get(rid) or {'status': 'UNKNOWN'}),
            'source_id': card.get('race_card_source_id'), 'snapshot_sha256': card.get('race_card_snapshot_sha256')})
    completed = now if injected_clock else datetime.now(timezone.utc)
    if completed >= cutoff:
        raise ShadowOwnerError('REFERENCE_COMPLETED_AFTER_CUTOFF')
    out = {'status': 'NON-PRODUCTION / NON-FORMAL / REFERENCE ONLY', 'race_id': request['race_id'],
        'venue_id': 'URW', 'race_date': request['race_date'], 'race_no': request['race_no'],
        'scheduled_post_at': source['scheduled_post_at'], 'prediction_cutoff': source['prediction_cutoff'],
        'frozen_at': completed.isoformat(), 'source_freeze_at': source['source_freeze_at'],
        'temporal_class': ('INJECTED_CLOCK_CONTRACT_TEST' if injected_clock else
            'PUBLIC_PRESTART_REFERENCE' if now.astimezone(JST).date().isoformat()==request['race_date']
            else 'PUBLIC_DECLARED_PRE_RACEDAY_REFERENCE'),
        'source_snapshot_sha256': source['source_snapshot_sha256'], 'source_signature_status': 'UNSIGNED_PUBLIC_OFFICIAL_BYTES',
        'method': 'EXISTING_OBSERVED_RECORD_ORDINAL_REFERENCE_NO_FITTING',
        'method_limitation': 'Same-course record priority is unvalidated; transfer/unknown runners are not proven weaker. Numeric horse-number tie break is display order only.',
        'ranking': comparable, 'runner_display_order': order,
        'unranked_condition_transfer': [rid for rid in order if rid not in comparable_ranks],
        'runners': rows, 'cancelled_runners': sorted(cancelled),
        'pace_hypothesis': {'status': 'CONDITIONAL_NOT_A_POINT_FORECAST',
            'possible_front_runners': [r['runner_id'] for r in rows if any(s['positions'] and s['positions'][0] <= 3 for s in r['past_starts'])],
            'assumption': 'If previous early-position behavior repeats, several runners may contest forward positions. Cross-course transfer, current pressure and survival effects are UNKNOWN.'},
        'W': 'UNKNOWN_INDEPENDENT_ROLE_QUALITY_UNESTABLISHED', 'P2': 'UNKNOWN_INDEPENDENT_ROLE_QUALITY_UNESTABLISHED',
        'P3': 'UNKNOWN_INDEPENDENT_ROLE_QUALITY_UNESTABLISHED', 'pair_conditioning': 'UNKNOWN_UNVALIDATED',
        'production_authority': False, 'formal_handoff_allowed': False, 'signed_final_claim': False,
        'numerical_prediction_consumption': False, 'krs_engine_executed': False, 'canonical_tickets': None,
        'stakes': None, 'recommended_pfs': 'N/A', 'actual_purchase_pfs': 'UNKNOWN', 'formal_forward_oos_credit': 0}
    import inspect
    out['method_components_sha256'] = {fn.__name__: hashlib.sha256(inspect.getsource(fn).encode()).hexdigest()
        for fn in (compile_reference_prediction, _runner_facts, _urw_current_condition_translation)}
    out['sha256'] = _sha(out)
    return out


def render_reference_prediction(prediction):
    """Human-readable evidence and uncertainty; never a Canonical FINAL."""
    lines = [prediction['status'], '', f"浦和{prediction['race_no']}R　{prediction['race_date']}　発走 {prediction['scheduled_post_at']}",
        f"観測 {prediction['source_freeze_at']}／参考予想凍結 {prediction['frozen_at']}", '',
        '過去実績による暫定比較です。同場同距離実績の優先には未検証の偏りがあり、転入・条件変更馬の能力優劣は確定できません。', '',
        '| 参考順位 | 馬番・馬名 | 確認できた根拠 | 不確実性 |', '|---:|---|---|---|']
    for row in prediction['runners']:
        f = row['facts']; runs = row['past_starts']
        recent = runs[0] if runs else None
        evidence = f"浦和同距離 {f['exact_races']}戦／勝利{f['exact_wins']}／3着内{f['exact_podiums']}"
        if recent:
            evidence += f"。直近 {recent['date']} {recent['venue']} {recent['distance']}m {recent['finish']}着、通過{recent['positions']}"
        unknown = '同条件実績UNKNOWN。' if f['unknown_exact_course'] else ''
        unknown += '当日の位置取得・圧力・馬体状態への効果UNKNOWN'
        lines.append(f"| {row['reference_rank'] or 'UNKNOWN'} | {row['runner_id']} {row['name']} | {evidence} | {unknown} |")
    lines += ['', '展開仮説：過去に前方を取った馬は '+', '.join(prediction['pace_hypothesis']['possible_front_runners'])+'。同じ行動なら先行争いが起こり得ます。現在の初速・競り合い・失速量はUNKNOWNです。',
        '', '独立W/P2/P3・Pair/Third・KRS結果・Canonical買い目・Stakeは未成立です。',
        f"参考予想SHA: {prediction['sha256']}", f"Source SHA: {prediction['source_snapshot_sha256']}"]
    return '\n'.join(lines)+'\n'


def _choice_fit(cases, penalty):
    """Small deterministic ridge conditional-softmax fit; no external API."""
    import statistics
    names=sorted({k for rows,_ in cases for r in rows.values() for k in r})
    means=[];scales=[]
    for name in names:
        vals=[r[name] for rows,_ in cases for r in rows.values() if r.get(name) is not None]
        means.append(statistics.mean(vals) if vals else 0.)
        scales.append(statistics.pstdev(vals) if len(vals)>1 and len(set(vals))>1 else 0.)
    def vector(row):
        return [(row.get(k)-m)/s if row.get(k) is not None and s else 0. for k,m,s in zip(names,means,scales)]
    data=[([vector(r) for r in rows.values()],list(rows).index(label)) for rows,label in cases]
    def objective(w, gradient=False):
        loss=penalty*sum(x*x for x in w)/2;g=[penalty*x for x in w]
        for x,target in data:
            scores=[sum(a*b for a,b in zip(w,r)) for r in x];top=max(scores)
            exp=[math.exp(v-top) for v in scores];denom=sum(exp)
            loss+=(math.log(denom)+top-scores[target])/len(data)
            if gradient:
                for i,r in enumerate(x):
                    error=(exp[i]/denom-int(i==target))/len(data)
                    for j,v in enumerate(r):g[j]+=error*v
        return (loss,g) if gradient else loss
    w=[0.]*len(names)
    for iteration in range(400):
        loss,g=objective(w,True);norm=sum(x*x for x in g)
        if norm<1e-12:break
        rate=1.
        while rate>1e-12:
            new=[a-rate*b for a,b in zip(w,g)]
            if objective(new)<=loss-1e-4*rate*norm:break
            rate/=2
        if rate<=1e-12:break
        w=new
    return {'feature_names':names,'training_means':means,'training_scales':scales,
            'coefficients':w,'ridge_penalty':penalty,'iterations':iteration+1,
            'training_objective':objective(w),'missing_contribution':0.,'calibrated':False}


def _choice_probabilities(fit, rows):
    scores={rid:sum(w*(row.get(k)-m)/s if row.get(k) is not None and s else 0.
        for k,m,s,w in zip(fit['feature_names'],fit['training_means'],fit['training_scales'],fit['coefficients']))
        for rid,row in rows.items()}
    top=max(scores.values());exp={k:math.exp(v-top) for k,v in scores.items()};total=sum(exp.values())
    return {k:v/total for k,v in exp.items()}


def fit_conditioned_owner(training_packs, training_labels, *, stage_evidence=True, interactions=True):
    """Venue-local Candidate only; selection/scaling never sees validation.

    Fit independent W/P2/P3 conditional choice functions. P2/P3 training uses
    the observed prefix only in TRAINING; inference enumerates hypothetical
    heads/pairs and never receives target outcomes. Penalty is selected by
    expanding training-race folds, then frozen. This is a numerical research
    behavior change, excluded from C1 and Production promotion.
    """
    packs=sorted(training_packs,key=lambda p:_aware(p['scheduled_post_at'],'TRAINING_POST'))
    if (len(packs)<2 or any(not p.get('venue_canon') or not p.get('venue_canon_source_sha256') for p in packs)
            or len({p['venue_id'] for p in packs})!=1 or len({p['race_id'] for p in packs})!=len(packs)
            or len({p.get('schema','LOCAL-VENUE-CONDITIONAL-FEATURES-v1') for p in packs})!=1
            or len({(p['venue_canon'],p['venue_canon_source_sha256']) for p in packs})!=1):
        raise ShadowOwnerError('CONDITIONAL_TRAINING_SCOPE_OR_COUNT')
    for p in packs:
        if p['sha256']!=_sha({k:v for k,v in p.items() if k!='sha256'}) or p.get('production_authority') is not False:
            raise ShadowOwnerError('CONDITIONAL_TRAINING_FEATURE_HASH')
        if len(p['runners'])<3 or any(v is not None and (type(v) not in (int,float) or not math.isfinite(v))
                for row in p['runners'].values() for v in row.values()):
            raise ShadowOwnerError('CONDITIONAL_TRAINING_NONFINITE_OR_UNIVERSE')
        label=list(map(str,training_labels[p['race_id']]))
        if len(label)!=3 or len(set(label))!=3 or not set(label)<=set(p['runners']):
            raise ShadowOwnerError('CONDITIONAL_TRAINING_LABEL_UNIVERSE')
    fits=[]
    for depth in range(3):
        cases=[]
        for p in packs:
            actual=list(map(str,training_labels[p['race_id']]));prefix=actual[:depth]
            rows={rid:_choice_features(p,rid,prefix,stage_evidence=stage_evidence,interactions=interactions)
                  for rid in p['runners'] if rid not in prefix}
            cases.append((rows,actual[depth]))
        cv=[]
        for penalty in (.1,1.,10.):
            losses=[]
            for stop in range(1,len(cases)):
                f=_choice_fit(cases[:stop],penalty)
                probs=_choice_probabilities(f,cases[stop][0])
                losses.append(-math.log(max(probs[cases[stop][1]],1e-300)))
            cv.append({'ridge_penalty':penalty,'training_forward_fold_nll':sum(losses)/len(losses)})
        best=min(cv,key=lambda x:(x['training_forward_fold_nll'],-x['ridge_penalty']))
        fit=_choice_fit(cases,best['ridge_penalty']);fit['training_only_cv']=cv;fits.append(fit)
    model={'schema':'LOCAL-VENUE-CONDITIONAL-CHOICE-v1','venue_id':packs[0]['venue_id'],
        'feature_schema':packs[0].get('schema','LOCAL-VENUE-CONDITIONAL-FEATURES-v1'),
        'venue_canon':packs[0]['venue_canon'],'venue_canon_source_sha256':packs[0]['venue_canon_source_sha256'],
        'training_races':[{'race_id':p['race_id'],'feature_sha256':p['sha256'],
            'scheduled_post_at':p['scheduled_post_at'],'training_label_sha256':_sha(training_labels[p['race_id']])} for p in packs],
        'training_max_post_at':packs[-1]['scheduled_post_at'],'stage_evidence':stage_evidence,'interactions':interactions,
        'fits':fits,'trained_at':datetime.now(timezone.utc).isoformat(),
        'production_authority':False,'prediction_consumption_authorized':False,
        'signed_final_claim':False,'calibration':'UNVALIDATED_SMALL_SAMPLE',
        'material_exact_authority':False,'genuine_forward_oos':0}
    model['sha256']=_sha(model);return model


def predict_conditioned_owner(model, pack, *, historical_replay=False, now=None):
    """Enumerate conditional orders without an actual Winner/Second input."""
    for value in (model,pack):
        if value.get('sha256')!=_sha({k:v for k,v in value.items() if k!='sha256'}) or value.get('production_authority') is not False:
            raise ShadowOwnerError('CONDITIONAL_PREDICTION_HASH_OR_AUTHORITY')
    if len(pack['runners'])<3 or any(v is not None and (type(v) not in (int,float) or not math.isfinite(v))
            for row in pack['runners'].values() for v in row.values()):
        raise ShadowOwnerError('CONDITIONAL_PREDICTION_NONFINITE_OR_UNIVERSE')
    if (model['venue_id']!=pack['venue_id'] or model['venue_canon']!=pack['venue_canon']
            or model['venue_canon_source_sha256']!=pack['venue_canon_source_sha256']):
        raise ShadowOwnerError('CONDITIONAL_VENUE_MODEL_TRANSFER_FORBIDDEN')
    if model.get('feature_schema','LOCAL-VENUE-CONDITIONAL-FEATURES-v1')!=pack.get('schema','LOCAL-VENUE-CONDITIONAL-FEATURES-v1'):
        raise ShadowOwnerError('CONDITIONAL_FEATURE_SCHEMA_MISMATCH')
    if (pack['race_id'] in {p['race_id'] for p in model['training_races']}
            or _aware(model['training_max_post_at'],'TRAINING_POST')>=_aware(pack['scheduled_post_at'],'PREDICTION_POST')):
        raise ShadowOwnerError('CONDITIONAL_TRAINING_NOT_STRICTLY_EARLIER')
    started=now or datetime.now(timezone.utc)
    if not historical_replay and (now is not None or _aware(model['trained_at'],'TRAINED_AT')>started or started>=_aware(pack['prediction_cutoff'],'CUTOFF')):
        raise ShadowOwnerError('CONDITIONAL_FORWARD_CLOCK_OR_CUTOFF')
    ids=list(pack['runners']);fits=model['fits']
    def probability(depth,prefix):
        return _choice_probabilities(fits[depth],{rid:_choice_features(pack,rid,prefix,
            stage_evidence=model['stage_evidence'],interactions=model['interactions']) for rid in ids if rid not in prefix})
    w=probability(0,[]);p2={};p3={};pairs=[];triples=[];m2={rid:0. for rid in ids};m3=dict(m2)
    for h in ids:
        p2[h]=probability(1,[h])
        for s,prob in p2[h].items():
            joint=w[h]*prob;m2[s]+=joint;pairs.append({'head':h,'second':s,'model_mass':joint})
            key=h+'>'+s;p3[key]=probability(2,[h,s])
            for t,third_prob in p3[key].items():
                m3[t]+=joint*third_prob;triples.append({'head':h,'second':s,'third':t,'model_mass':joint*third_prob})
    ordered=lambda probs:sorted(probs,key=lambda rid:(-probs[rid],int(rid)))
    rankings={'W':ordered(w),'P2':ordered(m2),'P3':ordered(m3)}
    baseline=pack['baseline'];widths={role:len(baseline[role]) for role in COLUMNS}
    roles={rid:[role for role in COLUMNS if rid in rankings[role][:widths[role]]] for rid in ids}
    pairs.sort(key=lambda p:(-p['model_mass'],int(p['head']),int(p['second'])))
    triples.sort(key=lambda p:(-p['model_mass'],int(p['head']),int(p['second']),int(p['third'])))
    completed=now or datetime.now(timezone.utc)
    if not historical_replay and completed>=_aware(pack['prediction_cutoff'],'CUTOFF'):
        raise ShadowOwnerError('CONDITIONAL_FORWARD_COMPLETED_AFTER_CUTOFF')
    out={'schema':'LOCAL-VENUE-CONDITIONAL-PREDICTION-v1','race_id':pack['race_id'],'venue_id':pack['venue_id'],
        'model_sha256':model['sha256'],'feature_sha256':pack['sha256'],'compiled_at':completed.isoformat(),
        'temporal_class':'HISTORICAL_RESEARCH_NOT_FORWARD' if historical_replay else 'LOCAL_PRESTART_SHADOW_NOT_FORMAL',
        'frozen_at':None if historical_replay else completed.isoformat(),'prediction_cutoff':pack['prediction_cutoff'],
        'ranking':rankings['W'],'rankings_by_role':rankings,'role_columns':roles,'role_widths':widths,
        'winner_model_mass':w,'p2_model_mass_given_head':p2,'p3_model_mass_given_pair':p3,
        'ordered_pairs':pairs,'ordered_triples':triples,
        'material_exact_evidence':False,'material_exact_reason':'NO_VALIDATED_MATERIALITY_OR_FORWARD_EVIDENCE',
        'probability_interpretation':'NORMALIZED_MODEL_MASS_NOT_CALIBRATED_WIN_PROBABILITY',
        'missingness':{rid:[k for k,v in row.items() if v is None] for rid,row in pack['runners'].items()},
        'hard_role_exclusions':[],'production_authority':False,'formal_handoff_allowed':False,
        'prediction_consumption_authorized':False,'signed_final_claim':False,'actual_purchase':False,'forward_oos_credit':0}
    out['sha256']=_sha(out);return out
