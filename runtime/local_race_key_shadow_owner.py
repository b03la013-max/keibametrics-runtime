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


URW_PROFILE = 'KM-LOCAL-URW-OWNER-CANDIDATE-v0.1-20261018'
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
    from runtime.local_production_static_owner import _card_heading, _start_date
    from runtime.local_nar_evidence_candidate import parse_race_card
    from runtime.local_fullnumerical_candidate import REQUIRED
    from runtime.local_krs_bridge_candidate import build_candidate_prediction_structure_derived

    now = now or datetime.now(timezone.utc)
    cutoff = _aware(request.get('prediction_cutoff'), 'PREDICTION_CUTOFF')
    if (request.get('family_id') != 'LOCAL' or request.get('venue_id') != 'URW'
            or request.get('execution_id') != request.get('race_id') or not request.get('race_id')):
        raise ShadowOwnerError('URW_CANDIDATE_SCOPE_OR_IDENTITY')
    if now.tzinfo is None:
        raise ShadowOwnerError('CURRENT_TIME_TZ_REQUIRED')
    receipt = source_envelope.get('receipt') or {}
    source = source_envelope.get('artifact') or {}
    if (receipt.get('phase') != 'SOURCE' or receipt.get('status') != 'SOURCE_FROZEN'
            or receipt.get('race_id') != request['race_id'] or source.get('race_id') != request['race_id']
            or not source_envelope.get('signature') or source_envelope.get('signature_alg') != 'Ed25519'
            or source_envelope.get('receipt_sha256') != _sha(receipt)
            or receipt.get('artifact_sha256') != _sha(source) or source.get('formal_ready') is not True):
        raise ShadowOwnerError('URW_CANDIDATE_SIGNED_SOURCE_BINDING')
    frozen = _aware(source.get('source_freeze_at'), 'SOURCE_FREEZE_AT')
    signed = _aware(receipt.get('timestamp'), 'SOURCE_SIGNED_AT')
    post = _aware(request.get('scheduled_post_at'), 'OFFICIAL_POST')
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
    from runtime.local_race_key_intake import JST
    if (start.get('authority') != 'NAR_OFFICIAL' or start.get('cutoff_relation') != 'PRE_CUTOFF'
            or start.get('value') != post.astimezone(JST).strftime('%H:%M')):
        raise ShadowOwnerError('URW_OFFICIAL_POST_MISMATCH')
    header = _card_heading(source)
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
                'field_size':s.get('field_size'),'positions':positions,
                'matched_urw_distance':str(s.get('venue','')).replace('ナ','')=='浦和' and s.get('distance')==header['distance'],
                'observed_progression':positions[0]-positions[-1] if len(positions)>=2 else None,
                'raw_reference':s.get('raw')})
        evidence[rid]={'article_refs':['59-C5R','60-MPA','61-UPR','100-DER','121-AOEP','137-PCA'],
            'past_starts':observations,'past_start_count':len(starts),
            'missing_history':'UNKNOWN_NOT_WEAK' if not starts else None,
            'observed_position_range':[min(p),max(p)] if (p:=[v for s in observations for v in s['positions']]) else None,
            'max_observed_progression':max((s['observed_progression'] for s in observations if s['observed_progression'] is not None),default=None),
            'predicted_position_scenarios':'UNESTABLISHED_NOT_INFERRED_FROM_RESULT',
            'current_gci':'UNKNOWN_NO_TRANSIENT_CARRYOVER','acquisition_survival_prediction':'REQUIRES_APPROVED_URW_EVALUATOR'}
    # No incoming weights, budget, result or manually supplied roles enter the
    # existing LOCAL structure-derived research baseline.
    baseline = build_candidate_prediction_structure_derived({'runners':copy.deepcopy(rows)})['candidate_static_prediction']
    pairs = [{'head':h,'second':s,'status':'CANDIDATE_SEMANTIC_ONLY',
              'interaction_effect':'UNESTABLISHED_NO_URW_SCENARIO_EVALUATOR'}
             for h in baseline['W'] for s in baseline['P2'] if h != s]
    thirds = [{'head':p['head'],'second':p['second'],'third':t,'status':'CANDIDATE_SEMANTIC_ONLY',
               'interaction_effect':'UNESTABLISHED_NO_URW_SCENARIO_EVALUATOR'}
              for p in pairs for t in baseline['P3'] if t not in {p['head'],p['second']}]
    output = {'profile':URW_PROFILE,'status':'CANDIDATE / NON-PRODUCTION / FULL-URW-CANON-NOT-EXECUTED',
        'race_id':request['race_id'],'venue_id':'URW','compiled_at':now.isoformat(),
        'temporal_class':'HISTORICAL_CONTRACT_REPLAY' if historical_replay else 'PRESTART_SHADOW_LOCAL_FREEZE',
        'frozen_at':None if historical_replay else now.isoformat(),'prediction_cutoff':request['prediction_cutoff'],
        'source_receipt_sha256':source_envelope['receipt_sha256'],'source_snapshot_sha256':source['source_snapshot_sha256'],
        'source_signature_authority':'CALLER_CANONICAL_INGRESS_VERIFICATION_REQUIRED',
        'venue_canon':URW_CANON,'venue_canon_source_sha256':URW_CANON_SHA256,
        'required_indices':list(materialized['required_indices']),'numeric_provenance_sha256':materialized['index_provenance_hash'],
        'numeric_cell_count':len(rows)*29,'runner_numeric_bindings':{str(r['runner_id']):_sha(r['canonical_components']) for r in rows},
        'ranking':baseline['ranking'],'role_columns':baseline['roles'],'existing_local_baseline':baseline,
        'urw_evidence':evidence,'head_local_pairs':pairs,'pair_conditioned_thirds':thirds,
        'paper_ticket_count':0,'paper_capital_yen':0,'paper_tickets':[],
        'ticket_status':'NOT_CONSTRUCTED_NO_MEC_OR_CAPITAL_AUTHORITY',
        'production_authority':False,'formal_handoff_allowed':False,'signed_final_claim':False,
        'prediction_consumption_authorized':False,'actual_purchase':False,'forward_oos_credit':0,
        'promotion_gaps':['URW_PRODUCTION_OWNER_SCOPE_APPROVAL','URW_SCENARIO_ROLE_EVALUATOR_AND_INPUT_AUTHORITY',
                          'GENUINE_PRESTART_SHADOW_OOS_AND_INDEPENDENT_TIMESTAMP','DATED_RACE_AND_RUNTIME_SEND_APPROVAL'],
        'kaw_owner_reused':False,'krs_numeric_consumption':False,'capital_policy_changed':False}
    output['sha256']=_sha(output)
    return output
