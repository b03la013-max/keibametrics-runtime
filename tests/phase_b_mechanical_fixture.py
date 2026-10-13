"""Independent test registration; never edits the real frozen Phase B protocol."""
import copy,json
import local_candidate_postresult as forward

def register(monkeypatch):
    protocol=copy.deepcopy(forward._forward_protocol())
    protocol['version']='MECHANICAL-TEST-CURRENT-CODE / NOT_REAL_PHASE_B_OOS'
    protocol['definition_sha256']=forward._definition_hashes()
    protocol['scope']='PYTEST_TEMP_LEDGER_ONLY / NO_REAL_OOS_CREDIT'
    monkeypatch.setattr(forward,'_forward_protocol',lambda:copy.deepcopy(protocol))
    return protocol
