"""Unadopted FNB context -> independent role/Pair/Third research prediction.

No Production Owner, source admission, signing, numerical consumer or capital
authority is granted. The v2.1 canon specifies mechanisms, not this algorithm.
All interval extrapolation, movement-cost and Pareto choices here are NEW
RESEARCH HYPOTHESES. Printed historical position sequences are retained as
such, never relabelled as measured acceleration, named corners or intentions.
"""
from __future__ import annotations

import copy
from datetime import datetime, timezone, timedelta
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import re
from statistics import median

MODEL_ID = "KM-FNB-CONTEXT-PARETO-STATIC-RESEARCH-v0.1-20261103"
VERSION = "0.1"
CONTEXT_PROFILE = "KM-FNB-TRAJECTORY-CONTEXT-HYPOTHESIS-v0.1-20261103"
OBSERVATION_PROFILE = "KM-FNB-OBSERVATION-ANTECEDENTS-RESEARCH-v0.1-20261103"
CLASSIFICATION = "PRIVATE_RESEARCH_UNADOPTED_NOT_REGISTERED_OOS"
CANON = "KM-LOCAL-FNB-v2.1-20260928-R1"
STAGES = ("Leader", "Pressing", "Tracking", "Mid-race Progression",
          "Absorption", "Final Conversion")


def sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def _time(value):
    try:
        out = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValueError("FNB_CANDIDATE_CLOCK_INVALID") from exc
    if out.tzinfo is None:
        raise ValueError("FNB_CANDIDATE_CLOCK_AWARE_REQUIRED")
    return out.astimezone(timezone.utc)


def _digest(doc):
    if not isinstance(doc, dict) or doc.get("sha256") != sha({k:v for k,v in doc.items() if k != "sha256"}):
        raise ValueError("FNB_CANDIDATE_ORIGINAL_SHA_MISMATCH")


def _value(x):
    return None if x is None else round(float(x), 12)


def _summary(values):
    return {"min":_value(min(values)), "max":_value(max(values)), "median":_value(median(values))}


def _observation_rows(packet):
    _digest(packet)
    if (packet.get("profile") != OBSERVATION_PROFILE or packet.get("venue_canon") != CANON
            or packet.get("classification") != CLASSIFICATION
            or packet.get("raw_to_normalized_tables_equal") is not True
            or not re.fullmatch(r"KM-LOCAL-FNB-\d{8}-R\d{2}(?:-[A-Za-z0-9_]+)*", str(packet.get("race_id")))):
        raise ValueError("FNB_CANDIDATE_QUALIFIED_OBSERVATION_PACKET_REQUIRED")
    race_day = datetime.strptime(packet["race_id"].split("-")[3], "%Y%m%d").date()
    freeze = _time(packet["source_freeze_at"])
    rows = packet.get("runners")
    if not isinstance(rows, list) or len(rows) < 2:
        raise ValueError("FNB_CANDIDATE_FULL_UNIVERSE_REQUIRED")
    ids = [str(x.get("runner_id")) for x in rows]
    if any(not x.isdigit() or int(x) < 1 for x in ids) or len(set(ids)) != len(ids):
        raise ValueError("FNB_CANDIDATE_UNIVERSE_INVALID")
    for runner in rows:
        for row in runner.get("historical_fnb_observations") or []:
            event_day=datetime.fromisoformat(row["event_date"]).date()
            fetched=_time(row.get("source_fetched_at"))
            if (row.get("source_raw_sha256") != packet["raw_card_sha256"]
                    or fetched > freeze or event_day >= race_day
                    or event_day > fetched.astimezone(timezone(timedelta(hours=9))).date()):
                raise ValueError("FNB_CANDIDATE_HISTORICAL_LINEAGE_OR_TIME_INVALID")
            n, finish, positions = row.get("field_size"), row.get("finish"), row.get("printed_position_sequence")
            if (type(n) is not int or n < 2 or type(finish) is not int or not 1 <= finish <= n
                    or not isinstance(positions, list)
                    or any(type(p) is not int or not 1 <= p <= n for p in positions)):
                raise ValueError("FNB_CANDIDATE_HISTORICAL_POSITIONS_INVALID")
            if row.get("same_distance") is not (row.get("distance_m") == packet["header"]["distance"]):
                raise ValueError("FNB_CANDIDATE_DISTANCE_FLAG_CONTRADICTION")
    return rows


def build_context(packet, *, generated_at):
    """Extrapolate explicitly hypothetical context from actual old sequences.

    Same-distance observations are used when available; otherwise other FNB
    distances remain a disclosed historical prior. No permanent horse/race ID,
    intention, pressure response, sand-era or corner name is inferred.
    """
    rows = _observation_rows(packet)
    if _time(generated_at) < _time(packet["generated_at"]):
        raise ValueError("FNB_CANDIDATE_CONTEXT_BEFORE_INPUT_AVAILABLE")
    runners = []
    for runner in rows:
        all_rows = [r for r in runner.get("historical_fnb_observations") or []
                    if r.get("printed_position_sequence")]
        exact = [r for r in all_rows if r["same_distance"]]
        selected = exact or all_rows
        current = {"runner_id":str(runner["runner_id"]), "name":runner["name"],
                   "input_observations":len(selected), "exact_distance_used":bool(exact),
                   "selection":"SAME_DISTANCE_IF_PRESENT_ELSE_OTHER_FNB_DISTANCE_PRIOR",
                   "interpretation_status":"RESEARCH_INFERRED_NOT_EMPIRICAL_MEASUREMENT",
                   "unknown":["current_tactical_intention", "measured_acceleration", "named_corner3", "named_corner4",
                              "competition_absorption_causality", "current_sand_effect"]}
        if not selected:
            current.update(status="UNKNOWN", FPR=None, LCC=None, reachable_position_range=None,
                           stage_cost_topology=None, paths=[], metrics=None)
            runners.append(current)
            continue
        paths = []
        for r in selected:
            n, positions, finish = r["field_size"], r["printed_position_sequence"], r["finish"]
            seq = [Fraction(p-1, n-1) for p in positions]
            f = Fraction(finish-1, n-1)
            gain = sum((max(a-b, Fraction(0)) for a,b in zip(seq,seq[1:])), Fraction(0))
            loss = sum((max(b-a, Fraction(0)) for a,b in zip(seq,seq[1:])), Fraction(0))
            # These are trajectory displacements, not measured physiological costs.
            costs = {"Leader":seq[0], "Pressing":abs(seq[-1]-seq[0]),
                     "Tracking":max(seq[-1]-seq[0],Fraction(0)),
                     "Mid-race Progression":gain, "Absorption":loss,
                     "Final Conversion":max(f-seq[-1],Fraction(0))}
            world = ("LEAD_HOLD" if positions[0] == positions[-1] == 1
                     else "PROGRESSION" if gain > 0 else "TRACK_OR_HOLD")
            paths.append({"source_event_date":r["event_date"], "source_raw_sha256":r["source_raw_sha256"],
                          "source_fetched_at":r["source_fetched_at"], "printed_position_sequence":copy.deepcopy(positions),
                          "field_size":n, "finish":finish, "distance_m":r["distance_m"],
                          "first_share":_value(seq[0]), "last_share":_value(seq[-1]), "finish_share":_value(f),
                          "world_hypothesis":world, "stage_cost_hypotheses":{k:_value(v) for k,v in costs.items()}})
        first = [p["first_share"] for p in paths]
        last = [p["last_share"] for p in paths]
        finish = [p["finish_share"] for p in paths]
        med = lambda key:_value(median(p["stage_cost_hypotheses"][key] for p in paths))
        current.update(status="RESEARCH_INFERRED", paths=paths,
            FPR={"acquisition":_summary(first), "maintenance_loss":med("Tracking")},
            LCC={"position_acquisition":_summary(first),
                 "leadership_acquisition_observations":sum(p["printed_position_sequence"][0]==1 for p in paths),
                 "leadership_maintenance_observations":sum(p["world_hypothesis"]=="LEAD_HOLD" for p in paths),
                 "competition_absorption":None, "finish_conversion_loss":med("Final Conversion")},
            reachable_position_range={"first_reported_hypothesis":_summary(first),
                "last_reported_hypothesis":_summary(last), "finish_hypothesis":_summary(finish),
                "corner3":None, "corner4":None, "units":"NORMALIZED_POSITION_SHARE_0_FRONT_1_BACK"},
            stage_cost_topology={s:med(s) for s in STAGES},
            metrics={"finish":_value(median(finish)), "maintenance":med("Tracking"),
                     "final_loss":med("Final Conversion"), "movement":med("Pressing")})
        runners.append(current)
    # Interval overlap is a candidate congestion proxy, not official intentions
    # or the canon's qualitative FSD density label. No high-FSD auto-promotion.
    known = [r for r in runners if r["status"] != "UNKNOWN"]
    for r in known:
        a = r["FPR"]["acquisition"]
        opponents = []
        for other in known:
            if other is r:continue
            b = other["FPR"]["acquisition"]
            if max(a["min"],b["min"]) <= min(a["max"],b["max"]):
                opponents.append(other["runner_id"])
        r["FSD"]={"overlapping_historical_acquisition_intervals":opponents,
                   "current_density_label":None, "current_assertion":None, "restraint":None,
                   "status":"HISTORICAL_INTERVAL_CONGESTION_HYPOTHESIS_NOT_OBSERVED_FSD"}
    out = {"profile":CONTEXT_PROFILE,"model_id":MODEL_ID,"model_version":VERSION,
           "classification":CLASSIFICATION,"venue_canon":CANON,"race_id":packet["race_id"],
           "generated_at":generated_at,"input_observation_sha256":packet["sha256"],
           "source_freeze_at":packet["source_freeze_at"],"source_snapshot_sha256":packet["source_snapshot_sha256"],
           "raw_card_sha256":packet["raw_card_sha256"],"source_receipt_sha256":packet["source_receipt_sha256"],
           "header":copy.deepcopy(packet["header"]),"runners":runners,
           "formal_context_ready":False,"current_track_bias":None,"new_empirical_scores":False}
    out["sha256"]=sha(out)
    return out


def _dominates(a,b):
    return all(x <= y for x,y in zip(a,b)) and any(x < y for x,y in zip(a,b))


def _rank(vectors, ids):
    known = {rid:v for rid,v in vectors.items() if v is not None}
    missing = set(ids)-set(known)
    pending, layers = set(known), {}
    layer=0
    while pending:
        layer += 1
        front = {rid for rid in pending if not any(_dominates(known[o],known[rid]) for o in pending if o != rid)}
        if not front:raise ValueError("FNB_CANDIDATE_PARETO_NONFINITE_INPUT")
        layers.update({rid:layer for rid in front});pending-=front
    order=sorted(known,key=lambda rid:(layers[rid],known[rid],int(rid)))+sorted(missing,key=int)
    rows=[]
    for display,rid in enumerate(order,1):
        if rid in missing:
            row={"runner_id":rid,"rank":None,"rank_interval":{"min":1,"max":len(ids)},
                 "pareto_layer":None,"unknown":True,"comparison_vector":None}
        else:
            strictly_ahead=sum(layers[o]<layers[rid] for o in known)
            same_layer=sum(layers[o]==layers[rid] for o in known)
            row={"runner_id":rid,"rank":strictly_ahead+1,
                 "rank_interval":{"min":strictly_ahead+1,"max":strictly_ahead+same_layer+len(missing)},
                 "pareto_layer":layers[rid],"unknown":False,"comparison_vector":list(known[rid])}
        row["display_order_not_ability_rank"]=display;rows.append(row)
    return {"rows":rows,"display_order":order,"front":[rid for rid in order if layers.get(rid)==1],
            "unknown_protected":sorted(missing,key=int),"unknown_is_not_weak":True}


def _worlds(runner):
    return set(p["world_hypothesis"] for p in runner["paths"])


def predict(context, *, frozen_at, context_enabled=True, upstream_krs_input=None):
    """Generate unadopted role semantics; ablation is the same model, not B/C.

    No fixed role widths or ticket selection is introduced. Research semantic
    fronts are Pareto layers over declared ordinal costs, not probabilities.
    A PRE_KRS draft only rebinds static roles/semantic context; the upstream HSV
    and numerical static arrays are preserved exactly. It does not claim those
    physical arrays consume context or that a qualified KRS execution occurred.
    """
    _digest(context)
    if (context.get("profile") != CONTEXT_PROFILE or context.get("model_id") != MODEL_ID
            or context.get("classification") != CLASSIFICATION):
        raise ValueError("FNB_CANDIDATE_CONTEXT_IDENTITY_MISMATCH")
    if _time(frozen_at) < _time(context["generated_at"]):
        raise ValueError("FNB_CANDIDATE_PREDICTION_BEFORE_CONTEXT")
    rows=context["runners"];ids=[r["runner_id"] for r in rows];byid={r["runner_id"]:r for r in rows}
    if (len(ids)<2 or len(ids)!=len(set(ids))
            or any(not isinstance(rid,str) or not rid.isdigit() or int(rid)<1 for rid in ids)):
        raise ValueError("FNB_CANDIDATE_CONTEXT_UNIVERSE_INVALID")
    for row in rows:
        if row.get("status")=="UNKNOWN":
            if row.get("metrics") is not None or row.get("paths"):
                raise ValueError("FNB_CANDIDATE_UNKNOWN_WITH_SYNTHETIC_METRIC")
            continue
        values=list((row.get("metrics") or {}).values())+list((row.get("stage_cost_topology") or {}).values())
        if (row.get("status")!="RESEARCH_INFERRED" or not values or
                any(type(v) not in (int,float) or not math.isfinite(v) or v<0 for v in values)):
            raise ValueError("FNB_CANDIDATE_CONTEXT_NONFINITE_OR_INVALID")
    def vec(rid,column):
        r=byid[rid];m=r["metrics"]
        if m is None:return None
        if not context_enabled:return (m["finish"],)
        collision=len(r["FSD"]["overlapping_historical_acquisition_intervals"])
        lcc=r["LCC"];cost=r["stage_cost_topology"];ranges=r["reachable_position_range"]
        held=lcc["leadership_maintenance_observations"]/r["input_observations"]
        acquired=lcc["leadership_acquisition_observations"]/r["input_observations"]
        spread=ranges["finish_hypothesis"]["max"]-ranges["finish_hypothesis"]["min"]
        if column=="W":
            return (m["finish"],r["FPR"]["maintenance_loss"],cost["Final Conversion"],
                    collision,-held,cost["Absorption"],spread)
        if column=="P2":
            return (m["finish"],cost["Tracking"],cost["Pressing"],cost["Leader"],
                    ranges["last_reported_hypothesis"]["max"],-acquired)
        return (m["finish"],lcc["finish_conversion_loss"],cost["Mid-race Progression"],
                cost["Absorption"],spread)
    columns={c:_rank({rid:vec(rid,c) for rid in ids},ids) for c in ("W","P2","P3")}
    conditional_p2,thirds,pairs,third_dispositions=[],[],[],[]
    for h in columns["W"]["front"]:
        candidates=[r for r in ids if r!=h]
        vectors={}
        for rid in candidates:
            v=vec(rid,"P2")
            if v is not None and context_enabled:
                # A head-specific collision dimension, not a head-independent P2 pool.
                overlap=rid in byid[h]["FSD"]["overlapping_historical_acquisition_intervals"]
                v=(*v,int(overlap))
            vectors[rid]=v
        ranked=_rank(vectors,candidates)
        conditional_p2.append({"head":h,"ranking":ranked,
            "P2_reachability_review":{"unconditional_front":columns["P2"]["front"],
                "head_conditioned_front":ranked["front"],
                "review_candidates":sorted(set(ranked["front"])-set(columns["P2"]["front"]),key=int),
                "automatic_production_promotion":False}})
        for p2 in ranked["front"]:
            pairs.append({"head":h,"second":p2,"status":"UNADOPTED_RESEARCH_SEMANTIC_ONLY",
                          "reason":"HEAD_CONDITIONED_PARETO_FRONT_NOT_TICKET_SELECTION"})
            eligible=[rid for rid in ids if rid not in {h,p2}]
            vectors={}
            for rid in eligible:
                v=vec(rid,"P3")
                if v is not None and context_enabled:
                    duplicate=bool(_worlds(byid[rid]) & (_worlds(byid[h]) | _worlds(byid[p2])))
                    v=(*v,int(duplicate))
                vectors[rid]=v
            ranked3=_rank(vectors,eligible)
            thirds.append({"head":h,"second":p2,"ranking":ranked3,
                           "conditioning":"PAIR_SPECIFIC_WORLD_OVERLAP_DIMENSION" if context_enabled else "CONTEXT_ABLATION"})
            for p3 in ranked3["front"]:
                third_dispositions.append({"head":h,"second":p2,"third":p3,
                    "status":"UNADOPTED_RESEARCH_SEMANTIC_ONLY","reason":"PAIR_CONDITIONED_PARETO_FRONT_NOT_TICKET_SELECTION"})
    roles={rid:[c for c in ("W","P2","P3") if rid in columns[c]["front"]]
           +(["W_UNKNOWN_POSSIBLE","P2_UNKNOWN_POSSIBLE","P3_UNKNOWN_PROTECTED"]
             if byid[rid]["metrics"] is None else []) for rid in ids}
    unknown_ids=columns["W"]["unknown_protected"]
    unresolved=[]
    for h in unknown_ids:
        unresolved.append({"head":h,"second_candidates":[r for r in ids if r!=h],
            "third_candidates_rule":"ALL_ACTIVE_EXCLUDING_THIS_HEAD_AND_CHOSEN_SECOND",
            "status":"UNKNOWN_HEAD_PATH_NOT_EVALUATED_NOT_REJECTED_NOT_PURCHASED"})
    for h in columns["W"]["front"]:
        for second in unknown_ids:
            unresolved.append({"head":h,"second":second,"third_candidates":[r for r in ids if r not in {h,second}],
                "status":"UNKNOWN_SECOND_PATH_NOT_EVALUATED_NOT_REJECTED_NOT_PURCHASED"})
    for pair in pairs:
        for third in unknown_ids:
            if third not in {pair["head"],pair["second"]}:
                unresolved.append({"head":pair["head"],"second":pair["second"],"third":third,
                    "status":"UNKNOWN_THIRD_PATH_NOT_EVALUATED_NOT_REJECTED_NOT_PURCHASED"})
    out={"model_id":MODEL_ID,"model_version":VERSION,"model_code_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         "classification":CLASSIFICATION,"trial_arm":"CONTEXT" if context_enabled else "CONTEXT_REMOVED_ABLATION_SAME_MODEL",
         "independent_BC_pair":False,"race_id":context["race_id"],"freeze_at":frozen_at,
         "source_freeze_at":context["source_freeze_at"],"source_snapshot_sha256":context["source_snapshot_sha256"],
         "input_context_sha256":context["sha256"],"active_runners":ids,"column_rankings":columns,"roles":roles,
         "head_local_P2":conditional_p2,"pair_conditioned_Third":thirds,
         "unresolved_semantic_paths":unresolved,
         "pair_dispositions":pairs,"third_dispositions":third_dispositions,
         "runner_world_stage_basis":{rid:{"paths":byid[rid]["paths"],"unknown":byid[rid]["unknown"]} for rid in ids},
         "dependency_trace":{
             "FPR.maintenance_loss":["W"],
             "FPR.acquisition.interval":["FSD.overlap","Head-localP2.collision"],
             "FSD.historical_interval_overlap_count":["W"],
             "LCC.leadership_maintenance_observations/input_observations":["W"],
             "LCC.leadership_acquisition_observations/input_observations":["P2"],
             "LCC.finish_conversion_loss":["P3"],
             "Reachable.finish_interval_width":["W","P3"],
             "Reachable.last_reported.max":["P2"],
             "Stage.Leader":["P2"],"Stage.Pressing":["P2"],"Stage.Tracking":["P2"],
             "Stage.Mid-race Progression":["P3"],"Stage.Absorption":["W","P3"],
             "Stage.Final Conversion":["W"],
             "World.path_hypothesis":["Pair-conditionedThird.world_overlap"],
             "P2_Reachability_Rescue":["per-head review record; no automatic Production promotion"]},
         "unconsumed_unknown_fields":["current_tactical_intention","measured_acceleration",
             "named_corner3","named_corner4","current_FSD_density_label","current_track_bias",
             "competition_absorption_causality","current_sand_effect"],
         "confidence":"UNVALIDATED_NOT_CALIBRATED_NO_PROBABILITY_OR_EV",
         "production_adopted":False,"formal_owner_scope_granted":False,"registered_oos_increment":0,
         "ticket_generation_executed":False,"KRS_executed":False,"PRE_KRS_input":None}
    if upstream_krs_input is not None:
        q=copy.deepcopy(upstream_krs_input)
        race=q.get("race") or {}
        match=re.fullmatch(r"KM-LOCAL-FNB-(\d{8})-R(\d{2})(?:-[A-Za-z0-9_]+)*",context["race_id"])
        expected_day=datetime.strptime(match.group(1),"%Y%m%d").date().isoformat()
        observed_day=race.get("race_date",race.get("date"))
        if (race.get("race_id") is not None and race["race_id"]!=context["race_id"]
                or observed_day is not None and str(observed_day).replace("/","-")!=expected_day
                or race.get("race_no") is not None and race["race_no"]!=int(match.group(2))
                or not race.get("race_id") and (observed_day is None or race.get("race_no") is None)
                or race.get("venue",race.get("racecourse")) not in {"FNB","船橋"}
                or race.get("distance_m",race.get("distance"))!=context["header"]["distance"]
                or str(race.get("surface")).lower() not in {"dirt","ダート"}):
            raise ValueError("FNB_CANDIDATE_UPSTREAM_KRS_RACE_IDENTITY_MISMATCH")
        horses=q.get("horses")
        if (not isinstance(horses,list) or {str(h.get("horse_no")) for h in horses}!=set(ids)
                or len(horses)!=len(ids) or any(not isinstance(h.get("hsv"),dict) or not isinstance(h.get("static"),dict) for h in horses)):
            raise ValueError("FNB_CANDIDATE_UPSTREAM_KRS_UNIVERSE_OR_ARRAY_MISMATCH")
        for horse in horses:horse["static_roles"]=copy.deepcopy(roles[str(horse["horse_no"])])
        q["fnb_context_candidate_semantics"]={"model_id":MODEL_ID,"context_sha256":context["sha256"],
            "trial_arm":out["trial_arm"],"columns":columns,"pairs":pairs,"thirds":third_dispositions}
        q["keibametrics_input_authority"]={"input_mode":"UNADOPTED_RESEARCH_DRAFT_NOT_EXECUTABLE_AUTHORITY",
            "production_authority":False,"model_adoption_verified":False,
            "HSV_and_static_numeric_arrays_unchanged":True,
            "context_consumed_by_role_semantics":context_enabled,
            "context_consumed_by_KRS_physical_arrays":False}
        out["PRE_KRS_input"]=q;out["PRE_KRS_sha256"]=sha(q)
    out["sha256"]=sha(out)
    return out


def compare_context_ablation(context, *, frozen_at, upstream_krs_input=None):
    full=predict(context,frozen_at=frozen_at,upstream_krs_input=upstream_krs_input)
    control=predict(context,frozen_at=frozen_at,context_enabled=False,upstream_krs_input=upstream_krs_input)
    def projection(rank):
        return {"front":rank["front"],"display_order":rank["display_order"],
                "rows":[{k:r[k] for k in ("runner_id","rank","rank_interval","pareto_layer","unknown")}
                        for r in rank["rows"]]}
    def p2_projection(pred):
        return [{"head":x["head"],"ranking":projection(x["ranking"])} for x in pred["head_local_P2"]]
    def p3_projection(pred):
        return [{"head":x["head"],"second":x["second"],"ranking":projection(x["ranking"])}
                for x in pred["pair_conditioned_Third"]]
    out={"model_id":MODEL_ID,"classification":CLASSIFICATION,"race_id":context["race_id"],
         "comparison":"SAME_MODEL_CONTEXT_ABLATION_NOT_INDEPENDENT_BC_NOT_OOS",
         "context_prediction":full,"ablation_prediction":control,
         "rank_changed_columns":[c for c in ("W","P2","P3") if projection(full["column_rankings"][c])!=projection(control["column_rankings"][c])],
         "roles_changed":full["roles"]!=control["roles"],
         "head_local_P2_changed":p2_projection(full)!=p2_projection(control),
         "pair_conditioned_Third_changed":p3_projection(full)!=p3_projection(control),
         "PRE_KRS_draft_bytes_changed":full.get("PRE_KRS_sha256")!=control.get("PRE_KRS_sha256"),
         "PRE_KRS_physical_numeric_arrays_changed":False,
         "PRE_KRS_role_semantics_changed":upstream_krs_input is not None and (
             full["roles"]!=control["roles"] or p2_projection(full)!=p2_projection(control)
             or p3_projection(full)!=p3_projection(control)),
         "new_qualified_LIVE_SOURCE":0,"new_OOS":0}
    out["sha256"]=sha(out)
    return out


def specification():
    return {"model_id":MODEL_ID,"model_version":VERSION,"classification":CLASSIFICATION,
        "canon":CANON,"inherited_mechanisms":["FPR/FSD/LCC decomposition","range preservation","six separate stages",
            "Head-local P2","Pair-conditioned Third","P2 review is not automatic promotion","UNKNOWN is not weak"],
        "new_unadopted_hypotheses":["same-distance-if-present sample selection; other FNB distance fallback explicitly prior",
            "historical normalized position envelope as a possible future-position prior, not measured current range",
            "trajectory displacement as six separate cost proxies, not physiological measurement",
            "historical acquisition-interval overlap as congestion proxy, never current FSD density or intention",
            "Pareto layers over role-specific vectors; nondominated fronts are semantic proposals, not purchase instructions",
            "head-specific overlap dimension for P2; head/second World-overlap dimension for Third"],
        "raw_to_hypothesis_formulas":{
            "position_share":"(printed_position-1)/(historical_field_size-1); no named corner relabelling",
            "finish_share":"(historical_finish-1)/(historical_field_size-1); historical result strictly pre-Freeze",
            "FPR_acquisition":"min/max/median first printed position shares; a prior hypothesis, not today's measured acceleration",
            "FPR_maintenance":"median max(last_share-first_share,0)",
            "LCC_acquisition_count":"count(first printed position ==1); denominator selected observed rows",
            "LCC_maintenance_count":"count(first printed position == last printed position ==1); denominator selected observed rows",
            "FSD_interval_relation":"two historical acquisition intervals overlap inclusively; unknown intention and current density remain NULL",
            "Stage_Leader":"first printed position share",
            "Stage_Pressing":"abs(last printed share-first printed share)",
            "Stage_Tracking":"max(last printed share-first printed share,0)",
            "Stage_Progression":"sum(max(previous_share-next_share,0)) over adjacent printed positions",
            "Stage_Absorption":"sum(max(next_share-previous_share,0)); backward movement proxy, not causal contest resistance",
            "Stage_Final_Conversion":"max(finish_share-last_printed_share,0)",
            "Reachable_envelopes":"separate min/max/median over historical first, last, finish; hypotheses only; corner3/corner4=NULL",
            "World":"first=last=1 -> LEAD_HOLD; else any forward movement -> PROGRESSION; else TRACK_OR_HOLD; no actual tactical-intention claim",
            "Pareto":"a dominates b iff all role dimensions a<=b and at least one a<b; remove nondominated fronts iteratively",
            "P2_head_collision":"append indicator(target interval overlaps head interval) to candidate P2 vector",
            "Third_pair_world":"append indicator(target World set intersects head-or-second World set) to candidate P3 vector"},
        "role_vectors":{"W":["median normalized historical finish (lower better)","FPR median position loss",
                "Stage final loss","historical interval overlap count","negative observed lead-held fraction",
                "Stage absorption displacement","hypothetical finish interval width"],
            "P2":["median finish","Stage Tracking loss","Stage Pressing displacement","Stage Leader displacement",
                "hypothetical last reported interval upper endpoint","negative observed lead-acquisition fraction"],
            "P3":["median finish","LCC finish-conversion loss","Stage progression displacement",
                "Stage absorption displacement","hypothetical finish interval width"]},
        "parameters":{"weights":None,"fixed_role_widths":None,"fixed_probability_mapping":None,
            "pareto_selection":"nondominated first front; all layers retained; ties and missing rank intervals retained"},
        "missing":"unknown metrics stay null and rank interval1..N; unresolved W/P2/P3 and Head/Pair/Third paths retained explicitly, no synthetic score or forced ticket",
        "PRE_KRS":"existing HSV/static numeric arrays unchanged; candidate Role/Pair/Third/World draft bound by SHA; no claim of physical KRS context consumption",
        "scope":"research only; no ADOPTED qualification, Production policy, source signature, OOS or ticket authority",
        "empirical_validation":{"actual_prior_positions_may_be_consumed":True,"future_predictive_utility_validated":False},
        "required_before_adoption":["source access and admission","independent signature verification","permanent identity audit",
            "fresh current context beyond historical proxies","exact model/consumer adoption before cutoff",
            "frozen prospective role/pair/third evaluation","separate KRS physical mapping review if desired"],
        "falsification":["increment disappears under context ablation on future held-out races",
            "conditional Pair/Third fails incremental role/coverage control","proxy congestion has opposite out-of-day effect",
            "wrong corner assumptions or distance fallback inflate measured coverage","unknown protection wrongly treated as weak"],
        "rollback":"stop calling this isolated module; preserve originals; no change to current KAW Owner/Registry/Gateway/Signer"}
