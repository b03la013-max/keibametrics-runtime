"""Read-only verification of real rescue FINALs in an isolated Git snapshot."""
import base64, datetime as dt, hashlib, json, sys, urllib.request
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'runtime'))
from jra_delivery import verify_signed_final, canonical_bytes
from jra_production_postresult import _sha
from jra_ticket_tree_renderer import render_ticket_tree
from family_authority_guard import resolve_current_authority
snapshot=Path(sys.argv[1])
race_no=int(sys.argv[2]) if len(sys.argv)>2 else 6
venues=sys.argv[3:] or ['NGT','KYO','TKY']
_,authority=resolve_current_authority(ROOT)
contract=json.loads((ROOT/authority['common_family_components']['family_runtime_contracts_profile']).read_text())['families']['JRA']
with urllib.request.urlopen(contract['external_endpoint'].rstrip('/')+'/health',timeout=20) as response:health=json.load(response)
assert health['receipt_signer']['public_key_b64']=='UhjfD9zFt+e77/9JUB19R6/XFC3SG4pM5twHBqfUSzI='
key=Ed25519PublicKey.from_public_bytes(base64.b64decode(health['receipt_signer']['public_key_b64']))
rows=[]
for venue in venues:
    rid=f'KM-JRA-{venue}-20261017-R{race_no:02d}'
    f=json.loads((snapshot/'runtime/final_artifacts'/f'{rid}.json').read_text())
    verify_signed_final(f,health,contract)
    for field in ['pre_krs_receipt','krs_run_receipt','final_receipt']:
        e=f[field];assert e['receipt_sha256']==_sha(e['receipt'])
        key.verify(base64.b64decode(e['signature']),canonical_bytes(e['receipt']))
    tree=render_ticket_tree(f)
    receipt=json.loads((snapshot/'runtime/jra_delivery'/rid/'availability_receipt.json').read_text())
    assert receipt['sha256']==_sha({k:v for k,v in receipt.items() if k!='sha256'})
    assert receipt['final_sha256']==f['sha256']
    assert receipt['tree_sha256']==hashlib.sha256(tree['text'].encode()).hexdigest()
    assert receipt['availability_verified_before_post'] is True
    assert (snapshot/'runtime/jra_delivery'/rid/'canonical_tree.txt').read_text()==tree['text']
    row={'race_id':rid,'final_sha256':f['sha256'],'signed_at':f['final_receipt']['receipt']['timestamp'],'cutoff':f['prediction_cutoff'],'signature_and_payload_verified':True,'receipt_signatures_verified':3,'full20':f['final_prediction_package']['execution_stage_manifest']['FULL_NUMERICAL_CALCULATION_VERIFIED'],'krs':f['krs_run_receipt']['receipt'].get('actual_run_count'),'ticket_count':tree['ticket_count'],'investment':tree['total_investment'],'bvi':f['final_prediction_package']['execution_stage_manifest']['BVI_PRE_KRS_CONSUMPTION_VERIFIED'],'capital':f.get('capital_policy_decision'),'availability':receipt,'user_received':'NOT_VERIFIED','actual_purchase':'UNVERIFIED'}
    assert dt.datetime.fromisoformat(row['signed_at'].replace('Z','+00:00'))<dt.datetime.fromisoformat(row['cutoff'])
    rows.append(row)
    print(json.dumps(row,ensure_ascii=False))
    print(tree['text'])
out={'observed_at':dt.datetime.now(dt.timezone.utc).isoformat(),'snapshot':str(snapshot),'finals':rows}
(Path(__file__).parent/f'rescue_r{race_no:02d}_verified.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
