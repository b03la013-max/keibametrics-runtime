"""Result-blind LOCAL static-owner *hypothesis* from Production-numerical data.

NON-PRODUCTION paper baseline only. Existing numerically closed 29-index
records are uncalibrated and explicitly forbid Production Prediction/Ticket
consumption. This shadow output never enters the FORMAL external request.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import copy
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


def compile_candidate_portfolio(materialized, source, *, prediction=None, budget=None,
                                market=None, market_signatures_verified=False, frozen_at=None):
    """Reuse the frozen candidate owner, existing MEC/selector/capital in PAPER.

    No result argument is accepted. A new ticket conversion is a new arm even
    when its earlier role prediction was genuinely frozen before the race.
    """
    from runtime.local_production_static_owner import role_graph
    from runtime.minimum_efficient_coverage import build_mec_plan
    from runtime.local_aki_columns import build,decision
    from runtime.local_mec_r5_shadow import build_arm
    from runtime.capital_policy import resolve_capital_policy
    q=copy.deepcopy(materialized)
    pred=copy.deepcopy(prediction or q.get('candidate_static_prediction') or {})
    if pred.get('production_authority') is not False:
        raise ShadowOwnerError('NON_PRODUCTION_PREDICTION_REQUIRED')
    ranking=[str(x) for x in pred['ranking']];roles=pred['roles']
    heads=[str(x) for x in pred['W']];seconds=[str(x) for x in pred['P2']];thirds=[str(x) for x in pred['P3']]
    registry,pairs,third_graph=role_graph(ranking,[str(r['runner_id']) for r in q['runners']],heads,seconds,thirds,roles)
    q.update(static_prediction=pred,role_registry=registry,pair_dispositions=pairs,third_dispositions=third_graph,
             source_snapshot_sha256=source['source_snapshot_sha256'],aki_column_candidate='HEAD_LOCAL_VNEXT_R1')
    mec=build_mec_plan(q)
    selected=build(q,source);d=decision(q,selected)
    # Existing column-selected role universe defines a field-relative R5
    # orientation boundary. It is not selected by realized payouts.
    selected_ids={x for c in selected['columns'].values() for x in c['selected']}
    position={x:i+1 for i,x in enumerate(ranking)}
    width=max((position[x] for x in selected_ids),default=0)
    f={'final_ticket':{'tickets':mec['tickets']},'final_prediction_package':pred}
    r5=build_arm(q,f,'SET_PAIR_EXACT_TOP'+str(width))
    if selected['status']=='NO_BET':
        r5['tickets']=[]
    variants={'CANDIDATE_MEC_R3':mec['tickets'],'HEAD_LOCAL_COLUMNS':d['paper_tickets'],'MEC_R5_AKI_VARIABLE':r5['tickets']}
    from runtime.family_conversion_diagnostics import measure_capital_conversion
    measurements={name:measure_capital_conversion(q,{"tickets":mec["tickets"]},pred,{},candidate_tickets=ts) for name,ts in variants.items()}
    capital={}
    key=lambda t:(t['bet_type'],tuple(sorted(t['selection'])) if t['bet_type']=='TRIO' else tuple(t['selection']))
    baseline={key(t):set(t.get('coverage_ids') or []) for t in mec['tickets']}
    units={u['id'] for u in mec['coverage_units']}
    for name,ts in variants.items():
        retained=set().union(*(baseline.get(key(t),set()) for t in ts)) if ts else set()
        coverage=len(retained & units)/len(units) if units else 1.0
        basis={'profile':mec['profile'],'sha256':_sha(ts),'material_coverage_ratio':coverage,'minimum_required_capital':sum(t['stake'] for t in ts)}
        cq={**q,'capital_policy':{'mode':'RECOMMENDATION_ONLY'} if budget is None else {'mode':'HARD_RACE_BUDGET','max_race_capital':budget}}
        cap=resolve_capital_policy(cq,basis)
        capital[name]={'material_coverage_ratio_against_full_graph':coverage,'missing_material_units':sorted(units-retained),'capital':cap,'tickets':[] if cap['no_bet'] else ts,'shadow_capital_only':True}
    out={'status':'NON_PRODUCTION_PAPER_CONVERSION_CANDIDATE','source_snapshot_sha256':source['source_snapshot_sha256'],
         'prediction_sha256':pred['sha256'],'role_graph_sha256':_sha({'roles':registry,'pairs':pairs,'thirds':third_graph}),
         'selection_sha256':selected['sha256'],'selection':selected,'conversion_audit':d.get('conversion_audit'),
         'capital_measurements':measurements,'mec':mec,'variable_r5_width':width,'variants':variants,'capital_variants':capital,
         'budget':budget,'budget_authority':'UNSPECIFIED' if budget is None else 'EXPLICIT_PAPER_SCENARIO',
         'prediction':pred,'production_authority':False,'actual_purchase':False,'forward_oos_authority':False}
    if market is not None:
        out['market_evidence'] = {name: bind_market_evidence(q, market,
            signatures_verified=market_signatures_verified, tickets=cap['tickets'],
            frozen_at=frozen_at or datetime.now(timezone.utc).isoformat(),
            selection_sha256=selected['sha256']) for name, cap in capital.items()}
    out['sha256']=_sha(out)
    return out


def compact_portfolio(portfolio):
    """Sign essential tickets/stakes and hashes; keep large audit worlds off transport."""
    if 'capital_variants' not in portfolio:return portfolio
    return {k:copy.deepcopy(portfolio[k]) for k in ['status','source_snapshot_sha256','prediction_sha256',
        'role_graph_sha256','selection_sha256','variable_r5_width','capital_variants','budget',
        'budget_authority','prediction','production_authority','actual_purchase','sha256',
        *(['market_evidence'] if 'market_evidence' in portfolio else [])]}


def settle_ticket_capital_portfolios(final_envelope, result_envelope, *, signatures_verified):
    """Separate PAPER settlements with exact FINAL->RESULT binding; no OOS mutation."""
    if signatures_verified is not True:
        raise ValueError('EXTERNAL_SIGNATURE_VERIFICATION_REQUIRED')
    final=final_envelope['artifact'];result=result_envelope['artifact']
    if result['frozen_refs']['final_receipt_sha256']!=final_envelope['receipt_sha256']:
        raise ValueError('RESULT_FINAL_LINEAGE_MISMATCH')
    paper=final['final_prediction_package'].get('candidate_ticket_capital_paper')
    if not paper:return None
    if paper.get('candidate_krs_binding')!='VERIFIED_EFFECTIVE_INPUTS_AND_REAL_EXECUTIONS':
        return {'status':'HOLD','reason':'CANDIDATE_KRS_NOT_BOUND_TO_THIS_FINAL','production_authority':False}
    from mec_r4_shadow import settle_ticket_list
    facts={'official_result':result['official_result']}
    top=result['automatic_post_result_review']['official_top3'];facts['official_result']={**facts['official_result'],'top3':top}
    rows={}
    for name,portfolio in paper['portfolios'].items():
        if 'capital_variants' not in portfolio:
            rows[name]={'status':'HOLD','reason':portfolio.get('reason')};continue
        rows[name]={variant:{'settlement':settle_ticket_list(arm['tickets'],facts),
                    'capital':arm['capital'],'material_coverage_ratio':arm['material_coverage_ratio_against_full_graph']}
                    for variant,arm in portfolio['capital_variants'].items()}
    return {'status':'PAPER_SETTLED','rows':rows,'final_ref':final_envelope['receipt_sha256'],
            'result_ref':result_envelope['receipt_sha256'],'source_snapshot_sha256':paper['source_snapshot_sha256'],
            'code_binding_sha256':paper['code_binding_sha256'],'production_authority':False,'actual_purchase_pfs':None,
            'forward_oos_admission':'PENDING_SEPARATE_PREREGISTRATION_AND_TEMPORAL_REVIEW'}


# LOCAL observation/price binding only. JRA external-state policy is not reused.
MARKET_PAGES = {'WIN_PLACE': 'OddsTanFuku', 'EXACTA': 'OddsUmLenTan',
                'TRIO': 'Odds3LenFuku', 'TRIFECTA': 'Odds3LenTan'}


def market_source_manifest(request):
    """Opt-in diagnostic sources for the unchanged external SOURCE acquirer."""
    from runtime.local_physical.nar_source_manifest import build_local_nar_manifest, _url
    m = build_local_nar_manifest({**request, 'include_odds': True,
                                  'include_same_day_results': False})
    for kind in ('EXACTA', 'TRIO', 'TRIFECTA'):
        m['sources'].append({'source_id': 'NAR-MARKET-' + kind,
            'source_class': 'OFFICIAL_MARKET_PRICE_PANEL_SHADOW',
            'authority': 'NAR_OFFICIAL', 'official': True, 'required': False,
            'url': _url(MARKET_PAGES[kind], m['nar_baba_code'], m['race_date'], m['race_no']),
            'max_bytes': 900000, 'extract': []})
    m['market_observation_only'] = True
    m['production_consumption_authorized'] = False
    return m


def bind_market_evidence(request, envelope, *, signatures_verified, tickets=(),
                         frozen_at, selection_sha256, previous=None, previous_signatures_verified=False):
    """Bind literal ticket prices; no selection, stake, probability or EV change.

    SOURCE freeze is the conservative availability upper bound: fetched_at is
    acquisition START, not publication/completion. Final odds are diagnostic
    only even if a caller supplies a later artificial cutoff.
    """
    import base64, gzip, re, unicodedata
    from urllib.parse import urlparse, parse_qs
    from runtime.local_physical.source_acquisition import _decode, _html_text, _html_tables
    from runtime.local_physical.nar_source_manifest import LOCAL_BABA_CODES, VENUE_NAMES
    if signatures_verified is not True:
        raise ShadowOwnerError('MARKET_SOURCE_SIGNATURE_VERIFICATION_REQUIRED')
    a = envelope['artifact']; rec = envelope['receipt']
    if _sha(a) != rec.get('artifact_sha256') or _sha(rec) != envelope.get('receipt_sha256'):
        raise ShadowOwnerError('MARKET_SOURCE_HASH_MISMATCH')
    identity = {'venue_id': request['venue_id'], 'race_date': str(request['race_date']).replace('/', '-'),
                'race_no': int(request['race_no'])}
    context = a.get('source_race_context') or {}
    if (rec.get('race_id') != request['race_id'] or a.get('race_id') != request['race_id']
            or {**context, 'race_date': str(context.get('race_date')).replace('/', '-')} != identity):
        raise ShadowOwnerError('MARKET_RACE_IDENTITY_MISMATCH')
    official = {str(x['runner_id']) for x in (a.get('official_runner_universe') or {}).get('runners', [])}
    expected = {str(x['runner_id']) for x in request['runners']}
    if not official or official != expected:
        raise ShadowOwnerError('MARKET_RUNNER_UNIVERSE_MISMATCH')
    official_post = (a.get('normalized_evidence') or {}).get('start_time') or {}
    requested_post = _aware(request['scheduled_post_at'], 'SCHEDULED_POST')
    from datetime import timedelta
    if (official_post.get('authority') != 'NAR_OFFICIAL' or
            official_post.get('value') != requested_post.astimezone(timezone(timedelta(hours=9))).strftime('%H:%M')):
        raise ShadowOwnerError('MARKET_OFFICIAL_POST_TIME_MISMATCH')
    freeze = _aware(frozen_at, 'MARKET_BINDING_FREEZE')
    cutoff = min(_aware(request['prediction_cutoff'], 'PREDICTION_CUTOFF'),
                 _aware(request['scheduled_post_at'], 'SCHEDULED_POST'))
    available = _aware(a['source_freeze_at'], 'SOURCE_AVAILABLE_AT')
    global_reasons = []
    if rec.get('phase') != 'SOURCE':
        raise ShadowOwnerError('MARKET_SOURCE_PHASE_REQUIRED')
    if rec.get('status') != 'SOURCE_FROZEN' or a.get('formal_ready') is False:
        global_reasons.append('SOURCE_NOT_FORMAL_READY')
    if available > freeze or freeze >= cutoff:
        global_reasons.append('NOT_AVAILABLE_BEFORE_TICKET_CUTOFF')
    panels = {}
    for kind, page in MARKET_PAGES.items():
        matches = [s for s in a['sources'] if urlparse(s.get('requested_url', '')).path.endswith('/' + page)]
        panel = {'status': 'MISSING', 'prices': {}, 'source_available_at': a['source_freeze_at'],
                 'official_updated_at': None, 'freshness': 'UNKNOWN', 'reasons': list(global_reasons)}
        if len(matches) != 1:
            panel['reasons'].append('SOURCE_MISSING_OR_AMBIGUOUS'); panels[kind] = panel; continue
        s = matches[0]
        panel.update(source_id=s['source_id'], raw_sha256=s.get('raw_sha256'),
                     snapshot_sha256=s.get('snapshot_sha256'), fetched_at=s.get('fetched_at'),
                     url=s.get('final_url'))
        if s.get('status') == 'FETCH_FAILED' or not 200 <= int(s.get('http_status') or 0) < 300:
            panel.update(status='FETCH_FAILED', source_error=s.get('error'))
            panel['reasons'].append('FETCH_FAILED:' + str(s.get('error') or s.get('http_status')))
            panels[kind] = panel; continue
        if s.get('official') is not True or s.get('authority') != 'NAR_OFFICIAL':
            raise ShadowOwnerError('MARKET_NOT_OFFICIAL')
        for url in (s['requested_url'], s['final_url']):
            u = urlparse(url); q = parse_qs(u.query)
            if (u.scheme != 'https' or u.hostname != 'www.keiba.go.jp' or
                    u.path != '/KeibaWeb/TodayRaceInfo/' + page or
                    q.get('k_babaCode') != [LOCAL_BABA_CODES[identity['venue_id']]] or
                    q.get('k_raceNo') != [str(identity['race_no'])] or
                    q.get('k_raceDate') != [identity['race_date'].replace('-', '/')]):
                raise ShadowOwnerError('MARKET_URL_IDENTITY_MISMATCH')
        raw = gzip.decompress(base64.b64decode(s['raw_gzip_b64']))
        if hashlib.sha256(raw).hexdigest() != s['raw_sha256']:
            raise ShadowOwnerError('MARKET_RAW_HASH_MISMATCH')
        if _sha({k:v for k,v in s.items() if k != 'snapshot_sha256'}) != s['snapshot_sha256']:
            raise ShadowOwnerError('MARKET_SNAPSHOT_HASH_MISMATCH')
        html = _decode(raw, s.get('content_type') or '')
        text = unicodedata.normalize('NFKC', _html_text(html))
        if '当該賭け式は発売されていません' in text:
            panel.update(status='NOT_ON_SALE',identity_status='URL_AND_SIGNED_CARD_CONTEXT_ONLY / ERROR_PAGE_NO_RACE_HEADER')
            panels[kind] = panel; continue
        date = identity['race_date'].split('-')
        header = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日.*?第\s*(\d+)競走', text)
        if (not header or [int(x) for x in header.groups()] != [*map(int,date),identity['race_no']]
                or VENUE_NAMES[identity['venue_id']] not in re.sub(r'\s+', '', header.group())):
            raise ShadowOwnerError('MARKET_HEADER_IDENTITY_MISMATCH')
        acquired = _aware(s['fetched_at'], 'MARKET_FETCHED_AT')
        if acquired > available or s.get('cutoff_relation') != 'PRE_CUTOFF':
            panel['reasons'].append('MARKET_TEMPORAL_MISMATCH')
        if '最終' in text:
            panel['reasons'].append('FINAL_ODDS_NOT_PRESTART_EVIDENCE')
        update = re.search(r'(\d{1,2}):(\d{2})\s*(?:現在|更新)', text)
        if update:
            from datetime import timedelta
            jst = timezone(timedelta(hours=9))
            stamp = datetime.fromisoformat(identity['race_date'] + 'T' + ':'.join(update.groups()) + ':00').replace(tzinfo=jst)
            panel['official_updated_at'] = stamp.isoformat()
            age = (acquired-stamp).total_seconds()
            max_age = request.get('market_max_age_seconds')
            if age < 0:
                panel['reasons'].append('UPDATE_AFTER_ACQUISITION')
            elif max_age is not None:
                if isinstance(max_age,bool) or not isinstance(max_age,(int,float)) or not math.isfinite(max_age) or max_age < 0:
                    raise ShadowOwnerError('MARKET_MAX_AGE_INVALID')
                panel['freshness'] = 'STALE' if age > max_age else 'CURRENT'
        if panel['freshness'] == 'UNKNOWN': panel['reasons'].append('UPDATE_FRESHNESS_UNKNOWN')
        if panel['freshness'] == 'STALE' or s.get('stale') is True: panel['reasons'].append('UPDATE_DELAY')
        # Only official combination/odds tables. WIN/PLACE is not converted to
        # exact prices; no payout/result table is parsed here.
        if kind != 'WIN_PLACE':
            n = 2 if kind == 'EXACTA' else 3
            for table in _html_tables(html):
                if not table or table[0][:2] != ['組合せ', 'オッズ']: continue
                for row in table[1:]:
                    cells = [unicodedata.normalize('NFKC', str(x)).strip() for x in row]
                    if len(cells) < 2 or not re.fullmatch(r'\d+(?:-\d+){' + str(n-1) + '}', cells[0]): continue
                    ids = cells[0].split('-')
                    if len(set(ids)) != n or not set(ids) <= official:
                        raise ShadowOwnerError('MARKET_COMBINATION_RUNNER_MISMATCH')
                    if kind == 'TRIO': ids = sorted(ids, key=int)
                    key = '-'.join(ids)
                    try: value = float(cells[1].replace(',', ''))
                    except ValueError: continue
                    if not math.isfinite(value) or value <= 0: continue
                    if key in panel['prices'] and panel['prices'][key] != value:
                        raise ShadowOwnerError('MARKET_PRICE_CONFLICT')
                    panel['prices'][key] = value
        if kind == 'WIN_PLACE':
            panel['status'] = 'CONTEXT_CAPTURED_NOT_COMBINATION_PRICE'
        else:
            panel['status'] = 'OBSERVED' if panel['prices'] else 'PRICE_MISSING'
        panels[kind] = panel
    coverage = []
    for t in tickets:
        ids = [str(x) for x in t['selection']]
        if t['bet_type'] == 'TRIO': ids = sorted(ids,key=int)
        key = '-'.join(ids); p = panels.get(t['bet_type']) or {}
        quoted = p.get('prices',{}).get(key)
        coverage.append({'bet_type':t['bet_type'],'selection':ids,'quoted_odds':quoted,
                         'usable':quoted is not None and not p.get('reasons') and p.get('status')=='OBSERVED'})
    sufficient = bool(coverage) and all(x['usable'] for x in coverage)
    out = {'status':'OBSERVATION_ONLY / NON_PRODUCTION', 'race_identity':identity,
        'race_id':request['race_id'], 'runner_ids':sorted(official,key=int),
        'binding_scope':'SELECTION_AND_TICKET_BINDING' if selection_sha256 else 'SOURCE_OBSERVATION_ONLY',
        'source_receipt_sha256':envelope['receipt_sha256'], 'source_snapshot_sha256':a['source_snapshot_sha256'],
        'frozen_at':frozen_at,'prediction_cutoff':request['prediction_cutoff'],'scheduled_post_at':request['scheduled_post_at'],
        'selection_sha256':selection_sha256,'prediction_source_snapshot_sha256':request.get('source_snapshot_sha256'),
        'ticket_sha256':_sha(list(tickets)),
        'panels':panels,'ticket_price_coverage':coverage,
        'market_payout_sufficiency':'SUFFICIENT_OBSERVED_PRICES' if sufficient else 'UNKNOWN',
        'economic_action':'PAPER_ONLY / EV_UNCALIBRATED' if sufficient else 'HOLD_PRICE_EVALUATION / PAPER_ONLY',
        'price_changes':None,'production_authority':False,'actual_purchase_pfs':None}
    if previous:
        if previous_signatures_verified is not True:
            raise ShadowOwnerError('MARKET_PREVIOUS_BINDING_INVALID_SIGNATURE')
        if (_sha({k:v for k,v in previous.items() if k!='sha256'}) != previous.get('sha256') or
                previous['race_identity'] != identity or previous['runner_ids'] != out['runner_ids'] or
                _aware(previous['frozen_at'],'PREVIOUS_FREEZE') >= available):
            raise ShadowOwnerError('MARKET_PREVIOUS_BINDING_INVALID')
        for kind, panel in panels.items():
            old_panel = previous['panels'][kind]
            if panel.get('prices') and old_panel.get('prices') and (
                    _aware(panel['fetched_at'], 'CURRENT_FETCH') <= _aware(old_panel['fetched_at'], 'PREVIOUS_FETCH')):
                raise ShadowOwnerError('MARKET_PREVIOUS_BINDING_INVALID_FETCH_ORDER')
        out['price_change_authority'] = 'OBSERVATION_DIFFERENCE_ONLY / NO_STABILITY_CLAIM'
        out['price_changes'] = {kind:{key: value-previous['panels'][kind]['prices'][key]
            for key,value in panel['prices'].items() if key in previous['panels'][kind]['prices']}
            for kind,panel in panels.items()}
        out['previous_binding_sha256'] = previous['sha256']
    out['sha256'] = _sha(out)
    return out
