import sys
sys.path.insert(0,"runtime")
from family_runtime_contract import load_contracts, resolve_family_runtime, FamilyRuntimeError

c=load_contracts()
jra=resolve_family_runtime({"family_id":"JRA"},c)
assert jra["executable"] is True

local=resolve_family_runtime({"family_id":"LOCAL"},c)
assert local["executable"] is True
assert local["source"]=="CANONICAL_VERIFIED_LOCAL_CONTRACT"
assert local["external_endpoint"]=="https://witnessstrictimage-production.up.railway.app"

try:
    resolve_family_runtime({"family_id":"BAN"},c)
    raise AssertionError("BAN missing attestation must fail")
except FamilyRuntimeError as e:
    assert "ATTESTATION_MISSING" in str(e)

ban={
 "family_id":"BAN",
 "family_runtime_attestation":{
   "family":"BAN",
   "adapter_sha256":"a"*64,
   "engine_sha256":"b"*64,
   "parameter_map_sha256_or_fingerprint":"94a47a3715f67f465d28a918c9cead17b6559f09f199b56f8cba38e8e906a871",
   "external_endpoint":"https://example.invalid",
   "signed_receipt_authority":"TEST",
   "runtime_version":"v2.4"
 }
}
assert resolve_family_runtime(ban,c)["executable"] is True
print("FAMILY_RUNTIME_CONTRACT_ACCEPTANCE_PASS")
