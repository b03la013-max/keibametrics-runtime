from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))

from jra_evidence_feature_normalizer_candidate import (
    bodyweight_vs_estimate,
    gate_dash_symbol,
    market_rank,
    newcomer_sire_place_rate,
    rate_band,
    stable_comment,
    trend_ratio,
    workout_final_1f,
    workout_partner_level,
    workout_short_comment,
)

def test_direct_symbols_are_deterministic():
    assert gate_dash_symbol("◎") == "VERY_STRONG"
    assert gate_dash_symbol("○") == "POSITIVE"

def test_rate_bands_are_deterministic():
    assert rate_band(0.31) == "VERY_STRONG"
    assert rate_band(0.15) == "POSITIVE"
    assert newcomer_sire_place_rate(0.35) == "VERY_STRONG"

def test_bodyweight_and_market_bands():
    assert bodyweight_vs_estimate(462, 470) == "POSITIVE"
    assert market_rank(1, 15) == "VERY_STRONG"
    assert market_rank(8, 15) == "NEUTRAL"
    assert trend_ratio(1.26) == "VERY_STRONG"

def test_workout_bands():
    assert workout_final_1f(11.7, "栗ＣＷ") == "VERY_STRONG"
    assert workout_final_1f(12.4, "栗坂") == "VERY_STRONG"
    assert workout_partner_level("古馬３勝") == "VERY_STRONG"
    assert workout_short_comment("仕上がり良好") == "STRONG"

def test_comment_bands():
    assert stable_comment("ダート向きの血統。期待できそう。") == "STRONG"
    assert stable_comment("まだ緩さを残します") == "CAUTION"
