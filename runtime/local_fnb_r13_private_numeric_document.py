"""FNB R13: lossless private all-horse 29-index evidence document.

This formats already executed numeric cells with their original states and
evidence references. No ranks, W/P2/P3, predicted probabilities, B/C tickets,
or capital decisions are inferred from the index grid. It is NOT a FORMAL
complete recommendation, NO-BET ticket or recipient-acknowledged Delivery.
"""
from __future__ import annotations

def _safe(value):
    return str(value).replace("\r"," ").replace("\n"," ").replace("|","／")

def render_full_numeric(materialized, *, classification, race_id, source_description='既存公式SOURCE'):
    indices=materialized.get("required_indices")
    rows=materialized.get("runners")
    if not isinstance(indices,list) or len(indices)!=29 or len(set(indices))!=29:
        raise ValueError("FNB_PRIVATE_NUMERIC_DOCUMENT_REQUIRES_29_INDICES")
    if not isinstance(rows,list) or not rows:
        raise ValueError("FNB_PRIVATE_NUMERIC_DOCUMENT_RUNNERS_NOT_OBSERVED")
    ids=[str(x.get("runner_id")) for x in rows]
    if len(ids)!=len(set(ids)):
        raise ValueError("FNB_PRIVATE_NUMERIC_DOCUMENT_DUPLICATE_RUNNERS")
    lines=[
        "# ケイバメトリクス船橋｜全馬29指数・独立私有数値原本",
        "",
        "**分類**："+classification,
        "**対象Race**："+_safe(race_id),
        "**注意**：以下は"+source_description+"から得た指数計算セルの原本であり、"
        "正式な予測順位・KRS・券面・実購入・配送完了を示しません。",
        "UNKNOWNはWEAKではありません。規定中立は弱い馬という意味ではありません。",
        "",
        "## 全馬29指数と欠測根拠",
    ]
    terminal_counts={"CALCULATED":0,"RULED-NEUTRAL":0}
    for row in rows:
        rid=str(row["runner_id"])
        name=_safe(row.get("horse_name") or row.get("name") or "馬名未記録")
        lines+=["", "### "+rid+"番 "+name, "",
                "| 指数 | 実数値 | 原本状態 | Rule ID | 根拠件数 |",
                "|---|---:|---|---|---:|"]
        cells=row.get("canonical_components") or {}
        if set(cells)!=set(indices):
            raise ValueError("FNB_PRIVATE_DOCUMENT_29_INDEX_CELLS_INCOMPLETE:"+rid)
        for idx in indices:
            cell=cells[idx]
            state=cell.get("terminal_status")
            if state not in terminal_counts:
                raise ValueError("FNB_PRIVATE_DOCUMENT_NOT_CALCULATED_OR_RULED_NEUTRAL:"+idx)
            terminal_counts[state]+=1
            val=cell.get("value")
            if type(val) not in (int,float):
                raise ValueError("FNB_PRIVATE_DOCUMENT_INDEX_NOT_NUMERIC:"+idx)
            rule=_safe(cell.get("rule_id") or "UNKNOWN")
            refs=cell.get("evidence_refs") or []
            if not isinstance(refs,list):
                raise ValueError("FNB_PRIVATE_DOCUMENT_EVIDENCE_REFS_INVALID:"+idx)
            lines.append(f"| {_safe(idx)} | {float(val):.6f} | {state} | {rule} | {len(refs)} |")
        missing=row.get("numerical_missing_components") or []
        lines+=["",f"証拠欠測：{len(missing)}構成要素。",
                ("欠測名："+", ".join(_safe(k) for k in missing) if missing else "欠測名：なし。")]
    lines+=["","## 本原本の実行状態","",
        f"- 対象馬数：{len(rows)}",
        f"- 必須指数セル：{len(rows)*29}",
        f"- CALCULATED：{terminal_counts['CALCULATED']}",
        f"- RULED-NEUTRAL：{terminal_counts['RULED-NEUTRAL']}",
        "- 2 Ownerの順位・W/P2/P3：**この数値専用実行では未計算**",
        "- KRS・発走展開・未較正SSR/LSR：**この数値専用実行では未計算**",
        "- B/C各3方式・Stake・券面ツリー：**未計算**（計算済み0票NO-BETではない）",
        "- 推薦投資・払戻・PFS：**未算定／NULL**",
        "- Signed FINAL／本人Delivery ACK：**未成立**",
        "- 登録Forward OOS増分：**0**",
        ""]
    return {"body":"\n".join(lines),"runners":len(rows),
            "full_numeric_cells":sum(terminal_counts.values()),
            "terminal_counts":terminal_counts,
            "private_full_document_only":True,
            "complete_prediction_or_six_bet_portfolios":False,
            "recipient_ack_verified":False}
