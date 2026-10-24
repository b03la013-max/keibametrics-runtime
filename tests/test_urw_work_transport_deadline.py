"""Synthetic host/clock contract tests; these are not LIVE delivery evidence."""
import json
from pathlib import Path
import shutil
import subprocess

import pytest


def work_scenario(*, fail=None, late=False, start_late=False, diagnostic=False, storage=True, published=False):
    node=shutil.which('node')
    if not node:pytest.skip('Node is required for the Work transport contract')
    source=Path('scripts/urw_work_transport.js').read_text()
    config={'fail':fail,'late':late,'start_late':start_late,'diagnostic':diagnostic,'storage':storage,'published':published}
    script='const transport='+source+';\n'+r'''
const scenario=SCENARIO, RealDate=Date;
const cutoff=RealDate.parse('2030-01-01T03:01:00+00:00');
let current=scenario.start_late?cutoff:cutoff-60000;
global.Date=class extends RealDate {
  constructor(...args){super(...(args.length?args:[current]));}
  static now(){return current;}
};
const commands=[], calls=[], patches=[];
const body='SYNTHETIC ALL_HORSES ALL_SIX_PORTFOLIOS STAKES_AND_UNUSED_FUNDS';
const complete={status:'PRIVATE_SAVE_REQUIRED',folder:'/private/synthetic-original',
  archive:'/private/synthetic-original/private-artifact.zip',archive_sha256:'synthetic-archive-sha',
  artifact_sha256:'synthetic-artifact-sha',race_id:'SYNTHETIC-R02',
  classification:scenario.diagnostic?'POSTCUTOFF_DIAGNOSTIC_NOT_FORWARD':'SINGLE_RACE_PRESTART_NONPRODUCTION_NOT_REGISTERED_OOS'};
const local={body,artifact_sha256:complete.artifact_sha256,classification:complete.classification,
  prediction_cutoff:new RealDate(cutoff).toISOString(),
  calculation_created_at:new RealDate(cutoff-70000).toISOString(),
  source_fetched_at:new RealDate(cutoff-120000).toISOString()};
let reads=0;
const error=stage=>{
  if(scenario.fail==='provider-code'&&stage==='upload')throw new Error('WORK_SYNTHETIC_SECRET_NOT_REAL');
  if(scenario.fail===stage)throw new Error('SYNTHETIC_SECRET_NOT_REAL');
};
const tools={
  exec_command:async args=>{
    commands.push(args.cmd);
    if(args.cmd.includes('_prepared_paper_answer'))return {exit_code:0,output:JSON.stringify(local)};
    if(args.cmd.includes('curl --fail')){error('download');return {exit_code:0,output:JSON.stringify({bytes:7,sha256:complete.archive_sha256})};}
    if(args.cmd.includes(' publish --complete')){
      error('publish');
      if(scenario.fail==='native-cutoff')return {exit_code:2,output:'ValueError: PAPER_EXTERNAL_SAVE_OR_READBACK_AFTER_CUTOFF'};
      return {exit_code:0,output:'{}'};
    }
    if(args.cmd.includes('runtime.local_race_entry')){
      if(scenario.late)current=cutoff+1000;
      return {exit_code:0,output:''};
    }
    if(args.cmd.startsWith('cat '))return {exit_code:0,output:JSON.stringify({status:'FORMAL_HOLD_SINGLE_RACE_READBACK_VERIFIED',message:body})};
    if(args.cmd.includes(' read --query')){
      reads++;
      return {exit_code:0,output:JSON.stringify(reads===1&&!scenario.published?null:{...local,race_id:complete.race_id})};
    }
    throw new Error('UNEXPECTED_SYNTHETIC_COMMAND');
  },
  apply_patch:async patch=>{patches.push(patch);return {};}
};
if(scenario.storage){
  tools.mcp__codex_apps__google_drive_upload_file=async()=>{calls.push('upload');error('upload');return {success:scenario.fail!=='upload-with-id',id:'SYNTHETIC_FILE_NOT_A_REAL_SAVE'};};
  tools.mcp__codex_apps__google_drive_get_file_metadata=async()=>{calls.push('metadata');error('metadata');return {id:scenario.fail==='metadata-id'?'SYNTHETIC_OTHER_FILE':'SYNTHETIC_FILE_NOT_A_REAL_SAVE',shared:scenario.fail==='metadata-sharing-unknown'?undefined:false,size:7,url:'https://example.invalid/synthetic',created_time:new RealDate(current).toISOString(),modified_time:new RealDate(current).toISOString()};};
  tools.mcp__codex_apps__google_drive_fetch=async()=>{calls.push('fetch');error('fetch');return {file_uri:{download_url:'https://example.invalid/synthetic-download'}};};
}
(async()=>{
  try{
    const result=await transport(tools,{repo:'synthetic-repo',python:'/verified/python',config:'synthetic-config',
      privateDirectory:'/private/synthetic',query:'2030-01-01 浦和2R',requestId:'synthetic-request',
      driveFolder:'SYNTHETIC_FOLDER_NOT_A_REAL_DRIVE',executionMode:'SINGLE_RACE_NONPRODUCTION',completed:complete});
    console.log(JSON.stringify({result,commands,calls,patches,body}));
  }catch(e){console.log(JSON.stringify({error:e.message,commands,calls,patches,body}));}
})();
'''.replace('SCENARIO',json.dumps(config))
    return json.loads(subprocess.run([node,'-e',script],check=True,text=True,capture_output=True).stdout)


@pytest.mark.parametrize('stage',['upload','metadata','fetch','download','publish'])
def test_external_failure_keeps_verified_body_and_specific_failed_stage(stage):
    result=work_scenario(fail=stage)
    assert 'error' not in result
    value=result['result']
    assert value['status']=='CALCULATED_PRIVATE_SAVE_PENDING' and value['body']==result['body']
    assert value['storage_hold']['stage']==stage.upper()
    assert value['completion'] is False and value['external_storage_roundtrip_verified'] is (stage=='publish')
    assert value['native_publication_verified'] is False
    assert value['chat_render_verified'] is False and value['user_acknowledgement_verified'] is False
    assert value['formal_quality_credit']==0 and value['timing']['prestart_delivery_ready'] is False
    assert 'SYNTHETIC_SECRET_NOT_REAL' not in json.dumps(value)
    assert not any(' prepare --query' in command for command in result['commands'])
    if stage!='upload':assert value['storage_attempt']['storage_id']=='SYNTHETIC_FILE_NOT_A_REAL_SAVE'
    else:assert value['storage_writes'] is None  # Provider may have created a file before failing.


def test_storage_roundtrip_and_body_ready_deadline_are_separate():
    result=work_scenario(late=True);value=result['result']
    assert value['status']=='CALCULATION_SAVED_DELIVERY_WINDOW_MISSED'
    assert value['body']==result['body'] and value['external_storage_roundtrip_verified'] is True
    assert value['completion'] is False and value['timing']['body_return_before_cutoff'] is False
    assert value['timing']['prestart_delivery_ready'] is False
    assert value['chat_render_verified'] is False and value['user_acknowledgement_verified'] is False
    assert value['timing']['scope']=='BODY_RETURN_READY_NOT_SCREEN_OR_USER_ACK'


def test_native_cutoff_refusal_keeps_body_without_hiding_the_deadline_cause():
    result=work_scenario(fail='native-cutoff');value=result['result']
    assert value['status']=='CALCULATED_PRIVATE_SAVE_PENDING' and value['body']==result['body']
    assert value['storage_hold']['stage']=='PUBLISH'
    assert value['storage_hold']['code']=='PRIVATE_STORAGE_PATH_INCOMPLETE'
    assert value['storage_hold']['native_deadline_code']=='PAPER_EXTERNAL_SAVE_OR_READBACK_AFTER_CUTOFF'
    assert value['external_storage_roundtrip_verified'] is True and value['completion'] is False
    assert value['native_publication_verified'] is False


def test_provider_error_cannot_masquerade_as_an_internal_code():
    result=work_scenario(fail='provider-code');value=result['result']
    assert value['storage_hold']['error_code']=='EXTERNAL_TOOL_ERROR'
    assert 'WORK_SYNTHETIC_SECRET_NOT_REAL' not in json.dumps(value)


def test_unconfirmed_upload_preserves_returned_id_without_asserting_creation():
    result=work_scenario(fail='upload-with-id');value=result['result']
    assert value['storage_hold']['error_code']=='WORK_TRANSPORT_PRIVATE_UPLOAD_NOT_CONFIRMED'
    assert value['storage_attempt']['storage_id']=='SYNTHETIC_FILE_NOT_A_REAL_SAVE'
    assert value['storage_writes'] is None and value['external_storage_roundtrip_verified'] is False


def test_metadata_for_another_file_cannot_supply_this_uploads_timestamp():
    result=work_scenario(fail='metadata-id');value=result['result']
    assert value['storage_hold']['stage']=='METADATA'
    assert value['storage_hold']['error_code']=='WORK_TRANSPORT_STORAGE_FILE_ID_MISMATCH'
    assert value['storage_attempt']['storage_id']=='SYNTHETIC_FILE_NOT_A_REAL_SAVE'
    assert value['external_storage_roundtrip_verified'] is False and value['completion'] is False
    assert result['calls']==['upload','metadata']


def test_unknown_sharing_is_not_a_confirmed_private_save():
    result=work_scenario(fail='metadata-sharing-unknown');value=result['result']
    assert value['status']=='CALCULATED_PRIVATE_SAVE_PENDING'
    assert value['storage_hold']['error_code']=='WORK_TRANSPORT_PRIVATE_SHARING_NOT_VERIFIED'
    assert value['external_storage_roundtrip_verified'] is False
    assert result['calls']==['upload','metadata']


def test_private_readback_attempt_uses_an_exclusive_distinct_path():
    result=work_scenario()
    command=next(command for command in result['commands'] if 'curl --fail' in command)
    assert 'set -e\nset -C\n' in command
    assert '/readback-synthetic-artifact-sha-' in command
    assert "/readback-synthetic-artifact-sha.zip'" not in command


def test_elapsed_prestart_window_does_not_start_new_forward_storage():
    result=work_scenario(start_late=True);value=result['result']
    assert value['status']=='CALCULATED_PRIVATE_SAVE_PENDING' and value['body']==result['body']
    assert value['storage_hold']['code']=='PRESTART_EXTERNAL_SAVE_WINDOW_ELAPSED'
    assert not result['calls'] and value['storage_writes']==0
    assert value['timing']['body_return_before_cutoff'] is False


def test_diagnostic_private_storage_remains_possible_after_cutoff():
    result=work_scenario(start_late=True,diagnostic=True);value=result['result']
    assert value['status']=='CALCULATION_PRIVATE_SAVE_READBACK_AND_INDEX_CONNECTED'
    assert value['body']==result['body'] and value['external_storage_roundtrip_verified'] is True
    assert result['calls']==['upload','metadata','fetch']
    assert value['timing']['prestart_delivery_ready'] is False and value['formal_quality_credit']==0


def test_actual_stage_clock_and_success_scope_are_retained_without_screen_claim():
    result=work_scenario();value=result['result']
    assert value['status']=='CALCULATION_PRIVATE_SAVE_READBACK_AND_INDEX_CONNECTED'
    assert value['timing']['body_return_before_cutoff'] is True
    assert value['timing']['prestart_delivery_ready'] is True
    assert value['timing']['source_fetched_at']=='2030-01-01T02:59:00.000Z'
    stages=[event['stage'] for event in value['timing']['stages']]
    assert stages[0]=='REQUEST_RECEIVED' and stages[-1]=='BODY_RETURN_READY'
    assert 'UPLOAD_COMPLETED' in stages and 'NATIVE_PUBLICATION_COMPLETED' in stages
    assert value['chat_render_verified'] is False and value['user_acknowledgement_verified'] is False


def test_missing_storage_still_retains_body_and_timing():
    result=work_scenario(storage=False);value=result['result']
    assert value['status']=='CALCULATED_PRIVATE_SAVE_PENDING' and value['body']==result['body']
    assert value['timing']['prestart_delivery_ready'] is False
    assert value['storage_hold']['code']=='PRIVATE_STORAGE_TOOLS_UNAVAILABLE'


@pytest.mark.parametrize('after_cutoff',[False,True])
def test_published_original_readback_keeps_original_and_records_current_delivery_time(after_cutoff):
    result=work_scenario(published=True,start_late=after_cutoff);value=result['result']
    assert value['status']=='EXACT_COMPLETED_READBACK_REUSED' and value['body']==result['body']
    assert value['calculation_executed'] is False and value['storage_writes']==0
    assert not result['calls']
    assert value['timing']['body_return_before_cutoff'] is (not after_cutoff)
    assert value['timing']['prestart_delivery_ready'] is (not after_cutoff)
    assert not any('runtime.local_race_entry' in command or ' prepare --query' in command for command in result['commands'])
