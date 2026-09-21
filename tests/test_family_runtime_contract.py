import sys
sys.path.insert(0,"runtime")
from family_runtime_contract import load_contracts, resolve_family_runtime, FamilyRuntimeError

c=load_contracts()
assert resolve_family_runtime({"family_id":"JRA"},c)["executable"] is True

for fam in ["LOCAL","BAN"]:
    try:
        resolve_family_runtime({"family_id":fam},c)
        raise AssertionError("missing attestation must fail")
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
