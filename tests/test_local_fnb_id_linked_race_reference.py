"""Negative boundaries for the real unsigned derived-document transport."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json

import pytest

from runtime import local_fnb_id_linked_race_reference as linked


def _parsed():
    facts={k:'printed-'+k for k in linked.IDENTITY_FIELDS if k!='馬名'}
    return {'race_identity':{'race_date':'2026-11-04','race_no':1,'venue_id':'FNB'},
        'runners':[{'runner_number':1,'horse_name':'実馬','prestart_reference_fields':facts}]}


def _bridge(parsed):
    row=parsed['runners'][0]
    return {'resolved':[{'current_event_key':['船橋','20261104',1,1],
        'current_identity_facts':{'馬名':row['horse_name'],**row['prestart_reference_fields']},
        'observed_official_horse_id':'NAR:123456','Active_verified':False,
        'Production_qualification_granted':False}]}


def test_exact_event_dob_and_parent_facts_required_not_name_only():
    parsed=_parsed();bridge=_bridge(parsed)
    assert linked._resolve_current(parsed,bridge)['1']['observed_official_horse_id']=='NAR:123456'
    for field in linked.IDENTITY_FIELDS:
        bad=deepcopy(bridge);bad['resolved'][0]['current_identity_facts'][field]='different'
        with pytest.raises(ValueError,match='EXACT_OFFICIAL_FACT_CONFLICT'):
            linked._resolve_current(parsed,bad)


def test_native_id_bridge_cannot_grant_current_active_or_production():
    parsed=_parsed();bridge=_bridge(parsed)
    for key in ('Active_verified','Production_qualification_granted'):
        bad=deepcopy(bridge);bad['resolved'][0][key]=True
        with pytest.raises(ValueError,match='AUTHORITY_PROMOTION_FORBIDDEN'):
            linked._resolve_current(parsed,bad)


def test_ambiguous_bridge_does_not_pick_first_and_other_race_is_not_authorized():
    parsed=_parsed();bridge=_bridge(parsed);bridge['resolved']*=2
    with pytest.raises(ValueError,match='AMBIGUOUS'):
        linked._resolve_current(parsed,bridge)
    parsed['race_identity']['race_no']=2
    with pytest.raises(ValueError,match='ONLY_AUTHORIZED'):
        linked._resolve_current(parsed,{'resolved':[]})


def test_child_original_bytes_are_not_arbitrary_claimed_hash_or_current_alias():
    original=linked._original(b'actual archived HTTP bytes')
    assert linked._decode(original)==b'actual archived HTTP bytes'
    original['sha256']=hashlib.sha256(b'current CSV bytes').hexdigest()
    with pytest.raises(ValueError,match='CHILD_ORIGINAL_SHA_INVALID'):
        linked._decode(original)
    with pytest.raises(ValueError,match='OFFICIAL_BRIDGE_PIN_INVALID'):
        linked._pinned_json(b'{"resolved":[]}',linked.BRIDGE_SHA,'OFFICIAL_BRIDGE')


def test_immutable_document_write_refuses_overwrite(tmp_path):
    path=tmp_path/'input.json';linked._write_new(path,b'one')
    with pytest.raises(FileExistsError):linked._write_new(path,b'two')
    assert path.read_bytes()==b'one'


def test_document_availability_cannot_rehash_source_qualification_or_backdate():
    doc={'profile':linked.PROFILE,'classification':linked.CLASSIFICATION,
        'input_kind':'REAL_UNSIGNED_DERIVED_JSON_DOCUMENT_NOT_PROVIDER_HTTP_RAW',
        'prepared_at':'2026-11-03T16:00:00+00:00',
        **{k:False for k in ('formal_source_admitted','active_universe_verified','source_signature_issued',
                            'new_numeric_policy','retroactive_R12_enrichment','actual_purchase')}}
    now=datetime(2026,11,3,17,tzinfo=timezone.utc)
    for change in ({'formal_source_admitted':True},{'source_signature_issued':True},
                   {'prepared_at':'2026-11-03T15:00:00+00:00'}):
        bad={**doc,**change};raw=linked._encode(bad)
        available={'document_sha256':linked._sha(raw),'document_bytes':len(raw),
            'document_kind':'DERIVED_DOCUMENT_NOT_PROVIDER_HTTP_RAW','formal_source_receipt':False,
            'available_at':'2026-11-03T16:01:00+00:00'}
        with pytest.raises(ValueError,match='CLASSIFICATION_OR_ACTUAL_AVAILABILITY_INVALID'):
            linked.materialize_document(raw,availability=available,now=now)


def test_private_original_store_blocks_git_worktree_and_symlinks(tmp_path):
    from runtime.local_fnb_research_runtime import ResearchHold
    worktree=tmp_path/'git';(worktree/'.git').mkdir(parents=True);(worktree/'.git'/'HEAD').write_text('ref: refs/heads/main')
    with pytest.raises(ResearchHold,match='PRIVATE_SOURCE_IN_GIT_WORKTREE_FORBIDDEN'):
        linked._write_new(worktree/'secret.json',b'private')
    safe=tmp_path/'safe';safe.mkdir();link=tmp_path/'link';link.symlink_to(safe,target_is_directory=True)
    with pytest.raises(ResearchHold,match='PRIVATE_STORE_SYMLINK_FORBIDDEN'):
        linked._write_new(link/'secret.json',b'private')
    target=tmp_path/'real';target.write_bytes(b'original');final=safe/'link.json';final.symlink_to(target)
    with pytest.raises(ResearchHold,match='PRIVATE_STORE_SYMLINK_FORBIDDEN'):
        linked._write_new(final,b'private')
    output=safe/'original.json';linked._write_new(output,b'private')
    assert output.stat().st_mode&0o777==0o600
