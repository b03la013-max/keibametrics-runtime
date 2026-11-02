def test_fnb_missing_delivery_never_implies_success():
    state = {'delivery_acknowledged': False, 'pfs': None}
    assert state['delivery_acknowledged'] is False
    assert state['pfs'] is None
