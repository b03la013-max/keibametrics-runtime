"""南関東 sire x course claims from the Owner library (Drive 1JXr373S6nA5dPnG02nSV1zidhhk_uAwHutWy5Uv7DOI,
「この5つの血統だけ覚えれば回収率上がります【南関東競馬】」 YouTube transcript, read 2026-11-18).
Figures are the creator's own aggregation (period / filters not stated): evidence-only claims."""
import json
from pathlib import Path

ALL = ['URW', 'FNB', 'OHI', 'KAW']
doc = {
    'profile': 'KM-NANKAN-SIRE-COURSE-RULES-v1.0-20261118',
    'source': {'drive_file_id': '1JXr373S6nA5dPnG02nSV1zidhhk_uAwHutWy5Uv7DOI', 'url': 'https://www.youtube.com/watch?v=y9ueTRRP-w4',
               'kind': 'YouTube transcript; creator aggregation, period and filters not stated'},
    'lines': {'APインディ系': ['シニスターミニスター', 'パイロ']},
    'rules': [
        {'id': 'N1', 'sire': 'シニスターミニスター', 'venues': ALL, 'side': 'buy', 'claim': '南関4場すべて複勝率34%以上・全体37%（人気になりやすい）'},
        {'id': 'N2', 'sire': 'ダノンレジェンド', 'venues': ALL, 'd': [1400, 1600], 'side': 'buy', 'claim': '1200m約32%・1400m38%・1500-1600m40%超'},
        {'id': 'N3', 'sire': 'ホッコータルマエ', 'venues': ['FNB'], 'd': [1200, 1200], 'side': 'buy', 'claim': '船橋1200m複勝率41%超（砂が深くパワー型が届く）'},
        {'id': 'N4', 'sire': 'ホッコータルマエ', 'venues': ['OHI'], 'd': [1200, 1200], 'side': 'caution', 'claim': '大井1200m複勝率27%'},
        {'id': 'N5', 'sire': 'ホッコータルマエ', 'venues': ALL, 'd': [1800, 1800], 'side': 'buy', 'claim': 'ダート1800m複勝率40.6%'},
        {'id': 'N6', 'sire': 'コパノリッキー', 'venues': ['KAW'], 'd': [900, 900], 'side': 'buy', 'claim': '川崎900m複勝率40.7%'},
        {'id': 'N7', 'sire': 'コパノリッキー', 'venues': ['KAW'], 'd': [1400, 1400], 'side': 'buy', 'claim': '川崎1400m複勝率43.8%'},
        {'id': 'N8', 'sire': 'コパノリッキー', 'venues': ['OHI'], 'd': [1200, 1200], 'side': 'caution', 'claim': '大井1200m複勝率22%（直線が長く先行が差される）'},
        {'id': 'N9', 'sire_line': 'APインディ系', 'venues': ALL, 'going': ['重', '不良'], 'side': 'buy',
         'claim': 'パイロ不良で複勝率37.9%（平常30%）、シニスターミニスター重以下で40%超'},
    ]}
if __name__ == '__main__':
    Path(__file__).with_name('sire_course_rules.json').write_text(json.dumps(doc, ensure_ascii=False, indent=1) + '\n')
