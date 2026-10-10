"""Render a JRA FINAL ticket set in the 中央競馬版 買い目表記規格 (標準ツリーフォーマット).

Pure presentation: never adds, drops or re-weights a ticket. Every rendered
block is checked to expand back to exactly the FINAL ticket set, so the tree
can never show a combination that was not frozen (規格 第14項 7–9, 14).
"""
from __future__ import annotations

from collections import OrderedDict
import itertools
import json
import sys

BET_LABEL = {"WIN": "単勝", "PLACE": "複勝", "WIDE": "ワイド", "QUINELLA": "馬連",
             "EXACTA": "馬単", "TRIO": "三連複", "TRIFECTA": "三連単"}
ORDER = ("WIN", "PLACE", "WIDE", "QUINELLA", "EXACTA", "TRIO", "TRIFECTA")


class TicketTreeError(ValueError):
    pass


def _branch(items, indent=""):
    items = list(items)
    return [f"{indent}{'└─' if i == len(items) - 1 else '├─'} {x}" for i, x in enumerate(items)]


def _sorter(ranking):
    pos = {int(h): i for i, h in enumerate(ranking or [])}
    return lambda h: (pos.get(int(h), 10 ** 6), int(h))


def _uniq(seq, key):
    return sorted(dict.fromkeys(seq), key=key)


def _ordered_blocks(combos, key):
    """Split ordered combos into rectangular formations (1着 x 2着 [x 3着])."""
    blocks, remaining = [], set(combos)
    width = len(next(iter(combos))) if combos else 0
    # Whole set as one formation (頭入替) when it expands exactly.
    cols = [_uniq([c[i] for c in combos], key) for i in range(width)]
    if {p for p in itertools.product(*cols) if len(set(p)) == width} == set(combos):
        return [cols]
    by_head = OrderedDict()
    for c in sorted(combos, key=lambda c: tuple(key(x) for x in c)):
        by_head.setdefault(c[0], []).append(c)
    # Merge heads that share an identical continuation set (頭入替).
    groups = OrderedDict()
    for head, cs in by_head.items():
        tails = frozenset(c[1:] for c in cs)
        groups.setdefault(tails, []).append(head)
    for tails, heads in groups.items():
        cols = [list(heads)] + [_uniq([t[i] for t in tails], key) for i in range(width - 1)]
        expanded = {p for p in itertools.product(*cols) if len(set(p)) == width}
        target = {c for c in remaining if c[0] in heads}
        if expanded == target:
            blocks.append(cols)
            remaining -= target
            continue
        # Not rectangular: one block per (head[, second]).
        for head in heads:
            hs = sorted((c for c in remaining if c[0] == head), key=lambda c: tuple(key(x) for x in c))
            if width == 2:
                blocks.append([[head], _uniq([c[1] for c in hs], key)])
            else:
                for s in _uniq([c[1] for c in hs], key):
                    blocks.append([[head], [s], _uniq([c[2] for c in hs if c[1] == s], key)])
            remaining -= set(hs)
    if remaining:
        raise TicketTreeError("TREE_DID_NOT_COVER_TICKETS")
    return blocks


def _unordered_blocks(combos, key):
    blocks = []
    for c in sorted(combos, key=lambda c: sorted(key(x) for x in c)):
        blocks.append([[x] for x in sorted(c, key=key)])
    return blocks


def _expand(bet, cols):
    if bet in ("EXACTA", "TRIFECTA"):
        return {p for p in itertools.product(*cols) if len(set(p)) == len(cols)}
    return {tuple(sorted(p)) for p in itertools.product(*cols) if len(set(p)) == len(cols)}


def render_ticket_tree(final_artifact: dict) -> dict:
    ft = final_artifact.get("final_ticket") or {}
    tickets = ft.get("tickets") or []
    ranking = (final_artifact.get("static_prediction") or {}).get("ranking") or []
    key = _sorter(ranking)
    decision = (final_artifact.get("capital_policy_decision") or {}).get("decision")
    fpp = final_artifact.get("final_prediction_package") or {}
    lines = ["買い目"]
    counts = OrderedDict()
    stake_total = 0
    if ft.get("no_bet") or not tickets:
        lines += _branch(["見送り"])
    by_bet = OrderedDict((b, []) for b in ORDER)
    for t in tickets:
        b = str(t.get("bet_type") or "").upper()
        if b not in by_bet:
            raise TicketTreeError(f"UNKNOWN_BET_TYPE:{b}")
        sel = tuple(int(x) for x in t["selection"])
        by_bet[b].append((sel, int(t.get("stake") or 0)))
        stake_total += int(t.get("stake") or 0)
    for bet, rows in by_bet.items():
        if not rows:
            continue
        combos = {s for s, _ in rows}
        if len(combos) != len(rows):
            raise TicketTreeError(f"DUPLICATE_TICKET:{bet}")
        stakes = sorted({st for _, st in rows})
        label = BET_LABEL[bet]
        if bet in ("WIN", "PLACE"):
            lines.append(label)
            lines += _branch(_uniq([s[0] for s in combos], key))
        else:
            blocks = (_ordered_blocks(combos, key) if bet in ("EXACTA", "TRIFECTA")
                      else _unordered_blocks(combos, key))
            covered = set()
            for i, cols in enumerate(blocks):
                covered |= _expand(bet, cols)
                tag = ("頭入替" if len(blocks) == 1 and len(cols[0]) > 1
                       and bet in ("EXACTA", "TRIFECTA")
                       else "本線" if i == 0 else "押さえ")
                lines.append(f"{label}（{tag}）")
                heads = (["1着", "2着", "3着"] if bet in ("EXACTA", "TRIFECTA")
                         else ["1列目", "2列目", "3列目"])
                for name, col in zip(heads, cols):
                    lines.append(name)
                    lines += _branch(col)
            want = combos if bet in ("EXACTA", "TRIFECTA") else {tuple(sorted(c)) for c in combos}
            if covered != want:
                raise TicketTreeError(f"TREE_EXPANSION_MISMATCH:{bet}")
        counts[label] = (len(rows), stakes)
    if counts:
        lines.append("点数")
        lines += _branch([f"{k}　{n}点" for k, (n, _) in counts.items()]
                         + [f"合計　{sum(n for n, _ in counts.values())}点"])
        all_stakes = sorted({s for _, ss in counts.values() for s in ss})
        lines.append("1点当たり")
        lines += _branch([f"{s}円" for s in all_stakes])
        lines.append("投資額")
        lines += _branch([f"{stake_total:,}円"])
    lines.append("購入判定")
    lines += _branch(["見送り" if ft.get("no_bet") else
                      "ペーパー" if decision == "PAPER" else
                      "推奨（資金上限判定なし）" if decision == "EXECUTE_RECOMMENDATION_PORTFOLIO" else
                      "実購入"])
    lines.append("確率状態")
    lines += _branch(["未較正"])
    lines.append("EV")
    lines += _branch(["算出不可"])
    if str(fpp.get("validation_status") or "").upper() == "UNVALIDATED":
        lines.append("検証状態")
        lines += _branch(["未検証（オーナー承認・前向きOOS 0件）"])
    return {"text": "\n".join(lines), "ticket_count": len(tickets), "total_investment": stake_total}


if __name__ == "__main__":
    art = json.load(open(sys.argv[1], encoding="utf-8"))
    print(render_ticket_tree(art)["text"])
