"""LOCAL canonical terminal compatibility utilities.

This module preserves the distinction between a formal canonical value and a
transport-only numerical proxy needed by legacy/KRS interfaces.  It MUST NOT be
used to claim that RULED-HOLD or NOT-APPLICABLE indices were numerically
calculated.
"""
ALLOWED={"CALCULATED","RULED-NEUTRAL","RULED-HOLD","NOT-APPLICABLE"}

def canonical_terminal(*, name, terminal_status, rule_id, evidence_refs, source_fact,
                       mapping_version, value=None, transport_value=None):
    st=str(terminal_status).upper()
    if st not in ALLOWED:
        raise ValueError(f"BAD_TERMINAL_STATUS:{name}:{st}")
    tv = value if st=="CALCULATED" else transport_value
    if isinstance(tv,bool) or not isinstance(tv,(int,float)) or not 0 <= float(tv) <= 100:
        raise ValueError(f"TRANSPORT_VALUE_REQUIRED:{name}:{tv}")
    formal = float(tv) if st in {"CALCULATED","RULED-NEUTRAL"} else None
    return {
        "value":float(tv),
        "formal_value":formal,
        "transport_value":float(tv),
        "terminal_status":st,
        "missing_flag":st in {"RULED-HOLD","NOT-APPLICABLE"},
        "rule_id":str(rule_id),
        "mapping_version":str(mapping_version),
        "evidence_refs":[str(x) for x in evidence_refs],
        "source_fact":str(source_fact),
        "transport_semantics":(
            "FORMAL_CANONICAL" if formal is not None
            else "TRANSPORT_ONLY_NOT_FORMAL_NUMERIC"
        ),
    }
