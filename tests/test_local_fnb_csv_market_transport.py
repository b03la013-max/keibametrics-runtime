"""Original printed cells only; synthetic signed fixtures, no real SOURCE."""
from copy import deepcopy
import base64,csv,gzip,hashlib,io,json,zipfile

import pytest
from runtime import local_fnb_csv_source_admission as admission
from runtime import local_fnb_csv_signed_capture as signed
from runtime import local_fnb_csv_current_universe as current
from tests.test_local_fnb_csv_signed_capture import fixture,prepare,NOW,REPO
from tests.test_local_fnb_csv_preliminary_numeric import sample,NOW as PRE_NOW
from runtime.local_fnb_csv_preliminary_numeric import materialize_preliminary


def rewrite_zip(raw, table, callback):
    output=io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(raw)) as old,zipfile.ZipFile(output,'w') as new:
        for member in old.namelist():
            data=old.read(member)
            if member.endswith('_'+table+'.csv'):
                reader=csv.DictReader(io.StringIO(data.decode('utf-8-sig'),newline=''))
                names=reader.fieldnames;rows=list(reader)
                callback(rows)
                text=io.StringIO(newline='');writer=csv.DictWriter(text,fieldnames=names)
                writer.writeheader();writer.writerows(rows);data=text.getvalue().encode('utf-8-sig')
            new.writestr(member,data)
    return output.getvalue()


def market_fixture(tmp_path, card_ranks=('', ''), odds_ranks=('2','1'), prices=('2.5','4.1')):
    f=fixture(tmp_path);root,binding,request,envelope,trust,resign=f
    for snap in envelope['artifact']['sources']:
        raw=gzip.decompress(base64.b64decode(snap['raw_gzip_b64']))
        is_card=snap['requested_url']==current.DAILY_URL
        def modify(rows):
            for no,row in enumerate(rows):
                row['人気']=(card_ranks if is_card else odds_ranks)[no]
                if not is_card:row['オッズ']=prices[no]
        raw=rewrite_zip(raw,'horselist' if is_card else 'odds',modify)
        snap.update(raw_gzip_b64=base64.b64encode(gzip.compress(raw)).decode(),
            raw_sha256=hashlib.sha256(raw).hexdigest(),byte_count=len(raw))
    resign()
    return f


def test_signed_prestart_odds_and_printed_popularity_reach_existing_market_formula_with_raw_lineage(tmp_path):
    out=prepare(market_fixture(tmp_path))
    consumed=admission.consume_with_approved_profile(out['assessment'],out['request'],
        binding=out['consumer_binding'],source_receipt=out['source_receipt'],repo_root=REPO,now=NOW)
    runners=consumed['numerical']['runners']
    assert [r['raw_candidate_evidence']['popularity'] for r in runners]==[2,1]
    assert [r['raw_candidate_evidence']['odds'] for r in runners]==[2.5,4.1]
    for row in runners:
        evidence=row['raw_candidate_evidence']['market_provenance']['popularity']
        assert evidence['table']=='odds' and evidence['csv_column']==10
        assert evidence['rank_inferred_from_odds'] is False
        assert row['canonical_components']['PRI']['terminal_status']=='CALCULATED'
        assert evidence['zip_raw_sha256'] in row['canonical_components']['PRI']['evidence_refs']
        assert row['evidence_features']['late_odds_changes_coverage']['raw_metric'] is True


def test_price_order_never_creates_missing_printed_rank(tmp_path):
    out=prepare(market_fixture(tmp_path,odds_ranks=('', '')))
    numeric=admission.compile_research_numeric(out['assessment'],out['request'])
    assert [r['raw_candidate_evidence']['popularity'] for r in numeric['runners']]==[None,None]
    assert all(r['canonical_components']['PRI']['terminal_status']=='RULED-NEUTRAL' for r in numeric['runners'])


def test_conflicting_printed_ranks_remain_unknown_without_whole_source_failure(tmp_path):
    out=prepare(market_fixture(tmp_path,card_ranks=('1','2')))
    rows=out['assessment']['source_candidate']['parsed_runner_evidence']
    assert all(r['popularity'] is None for r in rows.values())
    assert all(r['market_provenance']['popularity']['reason']=='CONFLICTING_PRINTED_RANKS_NOT_REORDERED' for r in rows.values())
    assert all(len(r['market_provenance']['popularity']['printed_observations'])==2 for r in rows.values())


def test_rehashed_market_values_cannot_override_printed_originals(tmp_path):
    out=prepare(market_fixture(tmp_path));assessment=deepcopy(out['assessment'])
    source=assessment['source_candidate'];source['parsed_runner_evidence']['1']['odds']=999.0
    source['sha256']=admission.sha({k:v for k,v in source.items() if k!='sha256'})
    assessment['sha256']=admission.sha({k:v for k,v in assessment.items() if k!='sha256'})
    with pytest.raises(ValueError,match='PRINTED_MARKET_RAW_REPLAY_MISMATCH'):
        admission.compile_research_numeric(assessment,out['request'])


@pytest.mark.parametrize('value',['','0','0.0','NaN','Infinity','-1'])
def test_invalid_or_absent_printed_values_are_unknown(value):
    row={'outcome_fields_separated':{'人気':value},'field_provenance':{}}
    out=admission.printed_csv_market(row,listed_count=12,capture={'captured_at':NOW.isoformat()},
        quote={'raw_quote':value,'raw_popularity':value})
    assert out['odds'] is None and out['popularity'] is None


def test_preliminary_producer_consumes_actual_printed_popularity_without_new_rank():
    raw,capture,race=sample()
    raw=rewrite_zip(raw,'horselist',lambda rows:[r.update(人気=str(2-no)) for no,r in enumerate(rows)])
    capture['raw_sha256']=hashlib.sha256(raw).hexdigest()
    out=materialize_preliminary(raw,capture=capture,race=race,now=PRE_NOW)
    assert [r['raw_candidate_evidence']['popularity'] for r in out['numerical']['runners']]==[2,1]
    assert all(r['canonical_components']['PRI']['terminal_status']=='CALCULATED' for r in out['numerical']['runners'])
