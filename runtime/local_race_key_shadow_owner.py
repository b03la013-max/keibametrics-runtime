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


URW_PROFILE = 'KM-LOCAL-URW-OWNER-CANDIDATE-v0.3-20261018'
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
        evidence[rid]={'article_refs':['59-C5R','60-MPA','61-UPR','100-DER','121-AOEP','137-PCA'],
            'past_starts':observations,'past_start_count':len(starts),
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
