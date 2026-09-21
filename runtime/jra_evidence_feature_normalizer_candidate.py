from __future__ import annotations

import re


class EvidenceNormalizationError(ValueError):
    pass


def _band(value, bands):
    value = float(value)
    for threshold, category in bands:
        if value >= threshold:
            return category
    return bands[-1][1]


def mark_symbol(symbol):
    table = {
        "◎": "VERY_STRONG",
        "○": "STRONG",
        "▲": "POSITIVE",
        "△": "NEUTRAL",
        "・": "MIXED",
        "×": "WEAK",
    }
    if symbol not in table:
        raise EvidenceNormalizationError(f"UNKNOWN_MARK:{symbol}")
    return table[symbol]


def gate_dash_symbol(symbol):
    table = {
        "◎": "VERY_STRONG",
        "○": "POSITIVE",
        "△": "NEUTRAL",
        "×": "WEAK",
    }
    if symbol not in table:
        raise EvidenceNormalizationError(f"UNKNOWN_GATE_DASH:{symbol}")
    return table[symbol]


def pedigree_fit_symbol(symbol):
    table = {"◎": "VERY_STRONG", "○": "POSITIVE", "△": "NEUTRAL", "×": "WEAK"}
    if symbol not in table:
        raise EvidenceNormalizationError(f"UNKNOWN_PEDIGREE_FIT:{symbol}")
    return table[symbol]


def rate_band(rate):
    # Generic current jockey/trainer strike-rate support; candidate-only.
    return _band(float(rate), [
        (0.30, "VERY_STRONG"),
        (0.20, "STRONG"),
        (0.14, "POSITIVE"),
        (0.08, "NEUTRAL"),
        (0.04, "MIXED"),
        (0.00, "WEAK"),
    ])


def newcomer_sire_place_rate(rate):
    return _band(float(rate), [
        (0.30, "VERY_STRONG"),
        (0.22, "STRONG"),
        (0.15, "POSITIVE"),
        (0.10, "NEUTRAL"),
        (0.05, "MIXED"),
        (0.00, "WEAK"),
    ])


def bodyweight_vs_estimate(actual_kg, estimate_kg):
    delta = abs(float(actual_kg) - float(estimate_kg))
    if delta <= 4:
        return "STRONG"
    if delta <= 10:
        return "POSITIVE"
    if delta <= 18:
        return "NEUTRAL"
    if delta <= 28:
        return "CAUTION"
    return "WEAK"


def bodyweight_suitability(actual_kg, sex="F", distance_m=1400, surface="DIRT"):
    # Broad physical-readiness band only; never interpreted as ability.
    kg = float(actual_kg)
    if surface == "DIRT" and 1300 <= int(distance_m) <= 1600:
        if 450 <= kg <= 510:
            return "POSITIVE"
        if 425 <= kg < 450 or 510 < kg <= 530:
            return "NEUTRAL"
        if 400 <= kg < 425 or 530 < kg <= 545:
            return "MIXED"
        return "CAUTION"
    return "NEUTRAL"


def market_rank(rank, field_size):
    rank = int(rank)
    field_size = int(field_size)
    q = rank / max(field_size, 1)
    if rank == 1:
        return "VERY_STRONG"
    if q <= 0.20:
        return "STRONG"
    if q <= 0.40:
        return "POSITIVE"
    if q <= 0.67:
        return "NEUTRAL"
    if q <= 0.85:
        return "MIXED"
    return "WEAK"


def trend_ratio(ratio):
    # Ratio >1 = support strengthened versus prior observation.
    ratio = float(ratio)
    if ratio >= 1.25:
        return "VERY_STRONG"
    if ratio >= 1.10:
        return "STRONG"
    if ratio >= 0.97:
        return "POSITIVE"
    if ratio >= 0.85:
        return "NEUTRAL"
    if ratio >= 0.72:
        return "CAUTION"
    return "WEAK"


def workout_final_1f(seconds, course):
    s = float(seconds)
    course = str(course).upper()
    if "CW" in course or "栗ＣＷ" in course:
        if s <= 11.7:
            return "VERY_STRONG"
        if s <= 12.0:
            return "STRONG"
        if s <= 12.4:
            return "POSITIVE"
        if s <= 12.8:
            return "NEUTRAL"
        return "CAUTION"
    if "坂" in course or "HILL" in course:
        if s <= 12.4:
            return "VERY_STRONG"
        if s <= 12.7:
            return "STRONG"
        if s <= 13.0:
            return "POSITIVE"
        if s <= 13.5:
            return "NEUTRAL"
        return "CAUTION"
    return "NEUTRAL"


def workout_partner_level(text):
    t = str(text)
    if "オープン" in t or "重賞" in t or "古馬３勝" in t or "古馬3勝" in t:
        return "VERY_STRONG"
    if "古馬２勝" in t or "古馬2勝" in t:
        return "STRONG"
    if "古馬１勝" in t or "古馬1勝" in t or "二歳１勝" in t or "2歳1勝" in t:
        return "POSITIVE"
    if "未勝利" in t or "新馬" in t:
        return "NEUTRAL"
    return "MIXED"


def workout_short_comment(text):
    t = str(text)
    strong = ["絶好", "抜群", "好調教", "仕上がり良好", "動き軽快", "キビキビ", "上等"]
    positive = ["良化", "順調", "時計以上", "動き良", "水準", "仕上る"]
    caution = ["平凡", "力感乏しく", "素軽さ欠く", "一走様子", "慣れが必要"]
    if any(x in t for x in strong):
        return "STRONG"
    if any(x in t for x in positive):
        return "POSITIVE"
    if any(x in t for x in caution):
        return "CAUTION"
    return "NEUTRAL"


def stable_comment(text):
    t = str(text)
    strong = ["楽しみ", "期待できそう", "いいデビュー戦", "素材的にはいい", "センスの良さ"]
    positive = ["順調", "動きも悪くない", "条件も合いそう", "仕上がりは良好", "初戦から"]
    caution = ["使いながら", "まだ緩さ", "芯が入り切って", "自分からという感じではない", "あとは実戦"]
    if any(x in t for x in strong):
        return "STRONG"
    if any(x in t for x in positive):
        return "POSITIVE"
    if any(x in t for x in caution):
        return "CAUTION"
    return "NEUTRAL"


def explicit_speed_comment(text):
    t = str(text)
    if "いいスピード" in t or "スピードも十分" in t or "ゲートも結構速い" in t:
        return "STRONG"
    if "ゲートは速い" in t or "出脚良さそう" in t:
        return "POSITIVE"
    return "NEUTRAL"
