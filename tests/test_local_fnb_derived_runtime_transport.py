"""Derived input transport only; no Engine, SOURCE or adoption is issued."""
import pytest
from runtime import local_fnb_csv_research_runtime as runtime
from runtime import local_fnb_id_linked_race_reference as document


def test_derived_document_entry_keeps_explicit_path_pin_and_reference_mode(tmp_path,monkeypatch):
    path=tmp_path/'input.json';raw=b'{"SYNTHETIC_DERIVED_NOT_SOURCE":true}\n';path.write_bytes(raw)
    pin=runtime.common.digest(raw)
    verified={'numerical':{'actual':'replayed'},'parsed':{'actual':'replayed'},
        'raw':b'SYNTHETIC_ZIP','request':{'race_id':'SYNTHETIC'}}
    monkeypatch.setattr(document,'load_document',lambda *args,**kwargs:verified)
    calls=[]
    monkeypatch.setattr(runtime,'_execute',lambda *args,**kwargs:calls.append((args,kwargs)) or {'reference':True})
    out=runtime.run_derived_document(path,pin,private_root=tmp_path/'private',engine='UNUSED',params='UNUSED')
    assert out=={'reference':True}
    assert calls[0][1]['derived_document_sha256']==pin
    assert calls[0][1]['derived_document_path']==path
    assert 'admission' not in calls[0][1] and 'owner_decision' not in calls[0][1]


def test_derived_document_cannot_be_used_as_qualified_source_or_unpinned_input(tmp_path):
    with pytest.raises(ValueError,match='NOT_QUALIFIED_SOURCE_AND_PIN_REQUIRED'):
        runtime._execute_locked({}, {}, b'', {}, private_root=tmp_path,engine='UNUSED',params='UNUSED',
            admission={},derived_document_path=tmp_path/'not-read',derived_document_sha256='a'*64)


def test_derived_packet_and_numeric_cannot_be_substituted_for_verified_document(tmp_path,monkeypatch):
    path=tmp_path/'input.json';raw=b'{"SYNTHETIC_ONLY":true}';path.write_bytes(raw);pin=runtime.common.digest(raw)
    monkeypatch.setattr(document,'load_document',lambda *args,**kwargs:{'document_sha256':pin,
        'numerical':{'from':'original'},'parsed':{},'raw':b'ORIGINAL','request':{}})
    with pytest.raises(ValueError,match='REPLAY_INPUT_MISMATCH'):
        runtime._execute_locked({'changed':True},{},b'ORIGINAL',{},private_root=tmp_path,
            engine='UNUSED',params='UNUSED',derived_document_path=path,derived_document_sha256=pin)
