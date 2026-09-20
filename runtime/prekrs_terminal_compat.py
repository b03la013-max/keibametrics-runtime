"""KeibaMetrics JRA PRE_KRS terminal compatibility adapter v0.1.

Authoritative semantic status is terminal_status.
Legacy quorumprobe PRE_KRS currently treats only status=CALCULATED as resolved.
For RULED-HOLD / NOT-APPLICABLE, this adapter emits status=CALCULATED solely
as a legacy transport compatibility token while preserving formal_value=None,
missing_flag=True, transport_value, rule_id and semantic terminal_status.

This MUST NOT be interpreted as a formal numerical calculation.
"""
ALLOWED = {"CALCULATED", "RULED-HOLD", "NOT-APPLICABLE"}

def adapt_item(item: dict, runner_id: str | int | None = None) -> dict:
    semantic = str(item.get("terminal_status") or item.get("status") or "").upper()
    if semantic not in ALLOWED:
        return {
            "runner_id": str(runner_id) if runner_id is not None else item.get("runner_id"),
            "name": item.get("index_name") or item.get("name"),
            "status": semantic or "UNRESOLVED",
            "terminal_status": semantic or "UNRESOLVED",
            "value": item.get("transport_value"),
            "formal_value": item.get("formal_value"),
            "missing_flag": item.get("missing_flag"),
            "rule_id": item.get("calculation_rule_id") or item.get("rule_id"),
            "mapping_version": item.get("mapping_version"),
            "compatibility_mode": "NONE",
        }

    legacy = "CALCULATED"
    return {
        "runner_id": str(runner_id) if runner_id is not None else item.get("runner_id"),
        "name": item.get("index_name") or item.get("name"),
        "status": legacy,
        "terminal_status": semantic,
        "value": item.get("transport_value"),
        "formal_value": item.get("formal_value"),
        "missing_flag": bool(item.get("missing_flag", False)),
        "rule_id": item.get("calculation_rule_id") or item.get("rule_id"),
        "mapping_version": item.get("mapping_version"),
        "compatibility_mode": "LEGACY-PREKRS-TERMINAL-v0.1",
        "compatibility_semantics": (
            "status=CALCULATED means legacy gate resolved only; "
            "terminal_status remains authoritative and no formal value is invented"
        ),
    }

def adapt_calculator_output(calc: dict) -> list[dict]:
    out = []
    for runner in calc.get("runners", []):
        rid = runner.get("runner_id")
        for item in runner.get("items", []):
            out.append(adapt_item(item, rid))
    return out
