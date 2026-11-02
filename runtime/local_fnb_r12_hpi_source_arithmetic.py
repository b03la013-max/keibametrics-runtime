"""R12 independent HPI source-fact->component score audit, 6/63 components.

Reconstructs recorded HPI-L past-run recency, finish, margin, last corner,
class-score inputs and repeatability WITHOUT calling the candidate feature
compiler.  It uses already parsed raw candidate starts; parsing NAR HTML or
class-level text from untouched official bytes is NOT independently done.
Do not label six components as all 63 independently rederived.
"""
from __future__ import annotations

from decimal import Decimal
import math
from statistics import pstdev

COMPONENTS=("recent_finish","finish_margin","passing_position_content",
            "class_level","opponent_strength","repeatability")
WEIGHTS=[Decimal("0.30"),Decimal("0.25"),Decimal("0.20"),
         Decimal("0.15"),Decimal("0.10")]
PROFILE="KM-FNB-R12-INDEPENDENT-HPI-SIX-COMPONENT-ARITHMETIC-v1"


def d(value):
    return Decimal(str(value))


def clamp(value):
    return min(Decimal(100),max(Decimal(0),value))


def finish(position,field):
    if (type(position) is not int or type(field) is not int or field<=1):
        return None
    return clamp(Decimal(100)*d(field-position)/d(field-1))


def recent_weighted(values):
    slots=[(d(v),WEIGHTS[i]) for i,v in enumerate(values[:5]) if v is not None]
    if not slots:
        return None
    return sum(v*w for v,w in slots)/sum(w for _,w in slots)


def reconstruct_one(raw):
    starts=raw.get("starts") or []
    if not isinstance(starts,list):
        raise ValueError("HPI_HISTORY_STARTS_NOT_LIST")
    recent=[finish(r.get("finish"),r.get("field_size")) for r in starts]
    margins=[]
    last_corner=[]
    class_vals=[]
    opponent=[]
    for run in starts:
        margin=run.get("margin")
        margins.append(None if margin is None else
                       Decimal(100)*(-d(margin)/Decimal(2)).exp())
        positions=run.get("content_positions") or []
        last_corner.append(finish(positions[-1],run.get("field_size"))
                           if positions else None)
        class_score=run.get("class_score")
        class_vals.append(None if class_score is None else d(class_score))
        field=run.get("field_size")
        field=(field if field is not None else raw.get("race_field_size"))
        if field is None:
            field=12
        opponent.append(clamp(Decimal("0.75")*
            d(class_score if class_score is not None else 52)+
            Decimal("0.25")*clamp(Decimal(50)+
            (d(field)-Decimal(8))*Decimal(4))))
    valid=[float(v) for v in recent if v is not None]
    spread=(clamp(Decimal(100)-Decimal("1.6")*d(pstdev(valid)))
            if len(valid)>=2 else None)
    return {
        "recent_finish":recent_weighted(recent),
        "finish_margin":recent_weighted(margins),
        "passing_position_content":recent_weighted(last_corner),
        "class_level":recent_weighted(class_vals),
        "opponent_strength":recent_weighted(opponent),
        "repeatability":spread}


def verify_hpi_six(materialized):
    runners=materialized.get("runners") or []
    errors=[]
    cells=0
    observed=0
    neutral=0
    for horse in runners:
        rid=str(horse.get("runner_id"))
        try:
            expected=reconstruct_one(horse["raw_candidate_evidence"])
            records=horse["evidence_features"]
            for component in COMPONENTS:
                item=records[component]
                v=expected[component]
                missing=v is None
                want=Decimal(52) if missing else clamp(v)
                actual=item.get("score")
                if (type(actual) not in (int,float)
                        or d(actual).is_nan()
                        or d(actual).is_infinite()
                        or abs(d(actual)-want)>Decimal("0.000025")
                        or item.get("missing") is not missing):
                    raise ValueError("FEATURE_SCORE_OR_MISSING_DIFFERS:"+component)
                cells+=1
                if missing:neutral+=1
                else:observed+=1
        except (ValueError,KeyError,TypeError,ArithmeticError) as exc:
            errors.append("HORSE_"+rid+":"+str(exc))
    required=len(runners)*len(COMPONENTS)
    if cells!=required:
        errors.append("SIX_COMPONENT_GRID_NOT_FULL")
    return {
        "profile":PROFILE,
        "status":"HPI_SIX_PARSED_START_ARITHMETIC_VERIFIED" if not errors
                 else "HPI_COMPONENT_ARITHMETIC_HOLD",
        "runners":len(runners),"expected_cells":required,"checked_cells":cells,
        "observed_component_cells":observed,"neutral_component_cells":neutral,
        "independently_scored_component_types":list(COMPONENTS),
        "six_of_63_not_all_63_independent":True,
        "source_html_to_start_parser_independent":False,
        "class_name_to_class_score_independent":False,
        "source_license_or_live_signed":False,
        "actual_2026_11_02_prediction":False,
        "errors":errors[:40]}
