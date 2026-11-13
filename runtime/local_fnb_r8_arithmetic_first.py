"""R8 Decimal witness: derived numeric outputs built from frozen features."""
from decimal import Decimal
from runtime.local_fnb_r7_arithmetic_witness import d, clamp

D = Decimal


def avg(values):
    xs = list(values)
    if not xs:
        raise ValueError("R8_EMPTY_AVERAGE")
    return sum(xs, D(0)) / D(len(xs))


def feat(row, key):
    record = row["evidence_features"][key]
    return d(record["score"])


def val(row, key):
    return d(row["canonical_components"][key]["value"])


def initial(row, front_pressure):
    parts = ("position_acquisition", "position_maintenance",
             "third_corner_progression", "leadership_stalk_acceptance",
             "kickback_traffic_tolerance", "going_adaptation",
             "course_geometry", "going_fit")
    evi = avg(feat(row, k) for k in parts)
    result = {
        "EVI/CEV": evi,
        "CCI": feat(row, "cci_specificity"),
        "TRI": feat(row, "tri_vertical_comparison"),
        "DRS": feat(row, "class_change_pressure"),
        "URP": avg((D(100)-val(row,"DRS"), front_pressure)),
        "HCS": avg(feat(row,k) for k in
                   ("class_level","opponent_strength","recent_finish")),
    }
    return {k:clamp(v) for k,v in result.items()}


def price(rows):
    ordered = sorted(rows, key=lambda r: (
        -avg(val(r,k) for k in ("TPI-L","SRI-L","HPI-L","CFIg-L","RFIg-L")),
        int(r["runner_id"])))
    ranks={str(r["runner_id"]):i+1 for i,r in enumerate(ordered)}
    n=len(rows)
    result={}
    for row in rows:
        rid=str(row["runner_id"])
        popularity=(row.get("raw_candidate_evidence") or {}).get("popularity")
        if popularity is None:
            result[rid]={"PRI":D(52),"OPI-V":D(52)}
        else:
            a=D(ranks[rid]-1)/D(max(1,n-1))
            m=D(int(popularity)-1)/D(max(1,n-1))
            result[rid]={
                "PRI":clamp(D(100)*(D(1)-abs(a-m))),
                "OPI-V":clamp(D(50)+D(50)*(m-a))}
    return result
