"""R8 independent Decimal witness for downstream *diagnostic* indices.

Only arithmetic is audited; no W/P2/P3 prediction, probability, policy or
capital authority is granted. Dependencies come from frozen recorded cells.
"""
from decimal import Decimal
from runtime.local_fnb_r7_arithmetic_witness import clamp
from runtime.local_fnb_r8_arithmetic_first import D, avg, feat, val


def roles(row, price_rows, front_pressure, n):
    pri=price_rows["PRI"]
    opi=price_rows["OPI-V"]
    uncertainty=D(100)-val(row,"DCR")
    divergence=D(100)-pri
    narrowness=D(100)-feat(row,"running_style_repro")
    waki=avg((uncertainty,val(row,"URP"),front_pressure,
              divergence,narrowness))
    competition=clamp(D(100)*D(n-1)/D(12))
    p2=avg((uncertainty,competition,divergence,val(row,"URP")))
    p3=avg((uncertainty,clamp(competition+D(10)),
            divergence,val(row,"URP")))
    friction=D(100)-feat(row,"position_maintenance")
    asi=D(100)-avg((waki,uncertainty,friction))
    t3=avg((opi,feat(row,"same_distance"),
            feat(row,"third_corner_progression"),
            feat(row,"position_maintenance"),
            val(row,"TRI"),val(row,"DRS"),
            feat(row,"good_weight_range")))
    zw=avg(val(row,k) for k in (
        "TPI-L","SRI-L","EVI/CEV","CFIg-L","NCI","DCR"))
    zp=avg(val(row,k) for k in (
        "TPI-L","SRI-L","EVI/CEV","CFIg-L","RFIg-L","DCR"))
    spread=max(zw,zp,t3)-min(zw,zp,t3)
    rsi=avg((clamp(spread*D("2.5")),divergence,uncertainty))
    wci=avg((zw,val(row,"SRI-L"),asi,D(100)-waki))
    return {k:clamp(v) for k,v in {
        "W-AKI":waki,"P2-AKI":p2,"P3-AKI":p3,
        "ASI":asi,"T3I-L":t3,"ZAI-WIN":zw,"ZAI-PLACE":zp,
        "RSI":rsi,"WCI":wci}.items()}
