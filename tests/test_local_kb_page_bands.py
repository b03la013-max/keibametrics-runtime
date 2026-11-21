from runtime.capture.keibabook_local_ingest import page_bands, _band


def test_page_bands_any_venue():
    race = {'pages': {
        '調教': {'tables': [{'cls': 'default cyokyo', 'rows': [
            ['枠番', '馬番', '馬名', '短評', ''], ['1', '1', 'A', '動き軽快', '↗'], ['(前回) ...'],
            ['2', '2', 'B', 'デキ落ちなし', '→'], ['3', '3', 'C', '反応鈍', '↘']]}]},
        '厩舎の話': {'tables': [{'cls': 'default danwa', 'rows': [
            ['枠番', '馬番', '馬 名厩舎の話'], ['1', '1', 'A'], ['◎【某師】状態は良く楽しみ。'],
            ['2', '2', 'B'], ['△【某師】今ひと息。']]}]}}}
    b = page_bands(race)
    assert b[1] == {'tri': 'VERY_STRONG', 'cci': 'VERY_STRONG'}
    assert b[2] == {'tri': 'NEUTRAL', 'cci': 'CAUTION'} and b[3] == {'tri': 'CAUTION'}
    assert _band('仕上がり良好') == 'STRONG' and _band('') == 'NEUTRAL'
    assert page_bands({'pages': {}}) == {}
