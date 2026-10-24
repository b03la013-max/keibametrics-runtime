// Work code-mode caller. Evaluates to a function; installs no worker or service.
// `tools` is the currently authorized Work tool object, never a token extractor.
// Invoke once for an ordinary query. Private bytes never enter Git.
(async function urwWorkTransport(tools, options) {
  const stages=[];
  const mark=stage=>{const ms=Date.now();const event={stage,at:new Date(ms).toISOString()};stages.push(event);return ms;};
  mark('REQUEST_RECEIVED');
  let local=null;
  const finish=(result,admitted=false,newDelivery=false)=>{
    const ready=mark('BODY_RETURN_READY');
    const cutoff=local?.prediction_cutoff ? Date.parse(local.prediction_cutoff) : NaN;
    const before=Number.isFinite(cutoff) ? ready<cutoff : null;
    const prestart=local?.classification==='SINGLE_RACE_PRESTART_NONPRODUCTION_NOT_REGISTERED_OOS';
    if(newDelivery && admitted && prestart && before!==true){
      result.status='CALCULATION_SAVED_DELIVERY_WINDOW_MISSED';result.completion=false;
    }
    return {...result,timing:{request_received_at:stages[0].at,source_fetched_at:local?.source_fetched_at||null,
      calculation_created_at:local?.calculation_created_at||null,prediction_cutoff:local?.prediction_cutoff||null,
      body_return_ready_at:stages.at(-1).at,body_return_before_cutoff:before,
      prestart_delivery_ready:admitted && prestart && before===true,stages,
      scope:'BODY_RETURN_READY_NOT_SCREEN_OR_USER_ACK'}};
  };
  const unwrap = value => {
    for (let i=0; i<10; i++) {
      if (value?.structuredContent) { value=value.structuredContent; continue; }
      const c=Array.isArray(value?.content) ? value.content.find(x=>x.type==='text' && x.text?.trim().startsWith('{')) : null;
      if(c){try{value=JSON.parse(c.text);continue;}catch{}}
      break;
    }
    return value;
  };
  const quote = value => "'"+String(value).replace(/'/g,"'\\''")+"'";
  const shell = async (cmd, budget=20000) => {
    let r=await tools.exec_command({cmd,workdir:options.repo,yield_time_ms:1000,max_output_tokens:budget});
    let output=r.output;
    while(r.session_id){r=await tools.write_stdin({session_id:r.session_id,chars:'',yield_time_ms:1000,max_output_tokens:budget});output+=r.output;}
    if(r.exit_code!==0)throw new Error('WORK_TRANSPORT_COMMAND_HOLD: '+output.slice(-1800));
    return output;
  };
  const json = output => JSON.parse(output.trim().split('\n').at(-1));
  const python=quote(options.python || 'python3');
  const base=python+' -m runtime.urw_registered_paper_entry --config '+quote(options.config);
  const query=' --query '+quote(options.query);
  const selectors = target => [['classification','classification'],['artifact_sha256','artifact-sha256'],
    ['source_sha256','source-sha256'],['revision','revision']]
    .filter(([key])=>target?.[key]!==undefined && target[key]!==null)
    .map(([key,arg])=>' --'+arg+' '+quote(target[key])).join('');
  let complete=options.completed;
  const requested=complete || options.readback || {};
  let saved,calculationExecuted=false,prepareInvoked=false,ordinaryInvoked=false;
  const invocation=Date.now().toString(36)+'-'+Math.random().toString(36).slice(2);
  const ordinaryOutput=options.privateDirectory+'/ordinary-'+String(options.requestId||'request').replace(/[^A-Za-z0-9_-]/g,'_')+'-'+invocation;
  const ordinary='KM_URW_SINGLE_RACE_CONNECTION='+quote(options.config)+' '+python+' -m runtime.local_race_entry'+query
    +' --output '+quote(ordinaryOutput)+' --run-id '+quote(options.requestId||'ordinary-single-race');
  if(complete || selectors(requested) || options.executionMode!=='SINGLE_RACE_NONPRODUCTION') {
    saved=json(await shell(base+' read'+query+selectors(requested)));
    if(saved){local=saved;return finish({status:'EXACT_COMPLETED_READBACK_REUSED',publication:saved,body:saved.body,
      calculation_executed:false,storage_writes:0},true);}
    if(!complete && selectors(requested))throw new Error('WORK_REQUESTED_ORIGINAL_NOT_FOUND_NO_RECOMPUTATION');
  }
  if(!complete && options.executionMode==='SINGLE_RACE_NONPRODUCTION') {
    // One natural request enters the existing caller, then resumes the same
    // result through actual storage. No registered-v2 admission is inferred.
    ordinaryInvoked=true;
    mark('ORDINARY_ENTRY_STARTED');
    await shell(ordinary+' >/dev/null || test -f '+quote(ordinaryOutput+'/chat_entry_report.json'));
    const report=JSON.parse(await shell('cat '+quote(ordinaryOutput+'/chat_entry_report.json')));
    mark('ORDINARY_ENTRY_COMPLETED');
    if(report.status==='FORMAL_VERIFIED' || report.status==='FORMAL_HOLD_SINGLE_RACE_READBACK_VERIFIED'){
      local=report.research||null;
      return finish({status:'ORDINARY_COMPLETED_READBACK_REUSED',report,body:report.message,
        ordinary_output:ordinaryOutput,calculation_executed:false,storage_writes:0},true);
    }
    complete=report.research_execution;
    if(report.status!=='SINGLE_RACE_CALCULATED_PRIVATE_SAVE_PENDING')throw new Error('WORK_ORDINARY_ENTRY_EXECUTION_FAILED: '+JSON.stringify(complete));
    calculationExecuted=(report.prediction_reexecution===true ? true : report.prediction_reexecution===false ? false : null);
    prepareInvoked=report.research_execution_invocation?.prepare_invoked===true;
  }
  if(!complete){complete=json(await shell(base+' prepare'+query));prepareInvoked=true;calculationExecuted=null;}
  if(complete.status!=='PRIVATE_SAVE_REQUIRED')throw new Error('WORK_TRANSPORT_NO_COMPLETED_CALCULATION');
  // Validate exact saved bytes with the ordinary entry's existing reader.
  // This read never invokes SOURCE capture, Owner, KRS, or a ledger writer.
  mark('LOCAL_READBACK_STARTED');
  local=json(await shell(python+' -c '+quote(
    'import json,sys; from pathlib import Path; from runtime import urw_registered_paper_entry as p; '+
    'from runtime.local_race_entry import resolve_chat_intent,_prepared_paper_answer; '+
    'c=json.loads(sys.argv[1]); body,_=_prepared_paper_answer(c,resolve_chat_intent(sys.argv[2])); '+
    "a=p.read(Path(c['folder'])/'calculation.json'); p._check_sha(a); "+
    "assert a['sha256']==c['artifact_sha256'],'WORK_TRANSPORT_LOCAL_ARTIFACT_CHANGED'; "+
    "print(json.dumps({'body':body,'artifact_sha256':c['artifact_sha256'],'classification':a['classification'],"+
    "'prediction_cutoff':a['prediction_cutoff'],'source_fetched_at':a['source']['fetched_at'],"+
    "'calculation_created_at':a['created_at']},ensure_ascii=False))")+
    ' '+quote(JSON.stringify(complete))+' '+quote(options.query)));
  mark('LOCAL_READBACK_COMPLETED');
  const requiredStorage=['mcp__codex_apps__google_drive_upload_file','mcp__codex_apps__google_drive_get_file_metadata',
    'mcp__codex_apps__google_drive_fetch'];
  const missing=requiredStorage.filter(name=>typeof tools[name]!=='function');
  let storageStage='PREFLIGHT',storageId=null,storageWrites=0,roundtripVerified=false,nativePublicationVerified=false;
  let verifiedReadbackPath=null,receiptPath=null;
  const pending=hold=>finish({status:'CALCULATED_PRIVATE_SAVE_PENDING',
    completed:complete,body:local.body,calculation_executed:calculationExecuted,prepare_invoked:prepareInvoked,
    ordinary_output:ordinaryInvoked?ordinaryOutput:null,completion:false,
    storage_writes:storageWrites,external_storage_roundtrip_verified:roundtripVerified,
    native_publication_verified:nativePublicationVerified,independent_external_anchor_verified:false,
    formal_quality_credit:0,chat_render_verified:false,user_acknowledgement_verified:false,
    storage_attempt:{stage:storageStage,storage_id:storageId,verified_readback_path:verifiedReadbackPath,
      receipt_attempt_path:receiptPath},storage_hold:hold});
  if(missing.length || !options.driveFolder)return pending({
    code:missing.length?'PRIVATE_STORAGE_TOOLS_UNAVAILABLE':'PRIVATE_STORAGE_FOLDER_UNCONFIGURED',missing_tools:missing});
  if(options.executionMode==='SINGLE_RACE_NONPRODUCTION'
      && local.classification==='SINGLE_RACE_PRESTART_NONPRODUCTION_NOT_REGISTERED_OOS') {
    const cutoff=Date.parse(local.prediction_cutoff);
    if(!Number.isFinite(cutoff))return pending({code:'PRESTART_CUTOFF_UNRESOLVED',stage:storageStage});
    if(Date.now()>=cutoff)return pending({code:'PRESTART_EXTERNAL_SAVE_WINDOW_ELAPSED',stage:storageStage});
  }
  try {
  storageStage='UPLOAD';mark('UPLOAD_STARTED');
  // A provider may fail after creating a file but before returning its ID.
  // Until creation is confirmed, the number of remote writes is unknown.
  storageWrites=null;
  const upload=unwrap(await tools.mcp__codex_apps__google_drive_upload_file({file_uri:complete.archive,
    file_name:complete.race_id+'-'+complete.artifact_sha256.slice(0,12)+'.zip',mime_type:'application/zip',parent_folder_id:options.driveFolder}));
  storageId=upload?.id||null;
  if(!upload?.success || !upload?.id)throw new Error('WORK_TRANSPORT_PRIVATE_UPLOAD_NOT_CONFIRMED');
  storageId=upload.id;storageWrites=1;mark('UPLOAD_COMPLETED');storageStage='METADATA';
  const meta=unwrap(await tools.mcp__codex_apps__google_drive_get_file_metadata({fileId:upload.id}));
  if(meta.id!==upload.id)throw new Error('WORK_TRANSPORT_STORAGE_FILE_ID_MISMATCH');
  if(meta.shared!==false || (meta.permissions||[]).some(x=>x.type==='anyone'))throw new Error('WORK_TRANSPORT_PRIVATE_SHARING_NOT_VERIFIED');
  mark('METADATA_COMPLETED');storageStage='FETCH';
  const raw=unwrap(await tools.mcp__codex_apps__google_drive_fetch({url:meta.url,download_raw_file:true,include_base64:false}));
  if(!raw.file_uri?.download_url)throw new Error('WORK_TRANSPORT_PRIVATE_BYTES_UNAVAILABLE');
  mark('FETCH_COMPLETED');storageStage='DOWNLOAD';
  const prefix=options.privateDirectory+'/readback-'+complete.artifact_sha256+'-'+invocation;
  const file=prefix+'.zip', receipt=prefix+'.receipt.json';
  const actual=json(await shell('set -e\nset -C\numask 077\ncurl --fail --silent --show-error --location '+quote(raw.file_uri.download_url)+' > '+quote(file)
    +'\n'+python+' -c '+quote("import hashlib,json,pathlib; p=pathlib.Path("+JSON.stringify(file)+"); print(json.dumps({'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}))")));
  if(actual.sha256!==complete.archive_sha256 || actual.bytes!==Number(meta.size))throw new Error('WORK_TRANSPORT_PRIVATE_BYTE_MISMATCH');
  roundtripVerified=true;
  verifiedReadbackPath=file;
  mark('READBACK_BYTES_VERIFIED');storageStage='RECEIPT';
  const proof={storage_provider:'Google Drive',storage_id:meta.id,url:meta.url,provider_created_at:meta.created_time,
    provider_modified_at:meta.modified_time,provider_shared:meta.shared,bytes:actual.bytes,readback_sha256:actual.sha256,
    verified_at:new Date().toISOString(),scope:'PRIVATE_BYTE_READBACK_NOT_A_SIGNED_FORMAL_RECEIPT'};
  await tools.apply_patch('*** Begin Patch\n*** Add File: '+receipt+'\n+'+JSON.stringify(proof,null,2).split('\n').join('\n+')+'\n*** End Patch');
  receiptPath=receipt;
  mark('READBACK_RECEIPT_WRITTEN');storageStage='PUBLISH';
  await shell(base+' publish --complete '+quote(complete.folder+'/complete.json')+' --readback '+quote(file)+' --receipt '+quote(receipt));
  nativePublicationVerified=true;
  mark('NATIVE_PUBLICATION_COMPLETED');storageStage='CATALOG_READBACK';
  saved=json(await shell(base+' read'+query+selectors(complete)));
  if(!saved || saved.race_id!==complete.race_id || saved.artifact_sha256!==complete.artifact_sha256)throw new Error('WORK_TRANSPORT_RACE_READBACK_NOT_ADMITTED');
  if(options.executionMode==='SINGLE_RACE_NONPRODUCTION') {
    storageStage='ORDINARY_BODY_READBACK';
    await shell(ordinary+selectors(complete)+' >/dev/null');
    const report=JSON.parse(await shell('cat '+quote(ordinaryOutput+'/chat_entry_report.json')));
    if(report.status!=='FORMAL_HOLD_SINGLE_RACE_READBACK_VERIFIED' || !report.message.includes(saved.body))
      throw new Error('WORK_ORDINARY_ENTRY_COMPLETE_BODY_MISMATCH');
  }
  mark('FINAL_BODY_VERIFIED');
  return finish({status:'CALCULATION_PRIVATE_SAVE_READBACK_AND_INDEX_CONNECTED',publication:saved,body:saved.body,
    calculation_executed:calculationExecuted,prepare_invoked:prepareInvoked,
    storage_writes:storageWrites,external_storage_roundtrip_verified:roundtripVerified,
    native_publication_verified:nativePublicationVerified,independent_external_anchor_verified:false,
    formal_quality_credit:0,chat_render_verified:false,user_acknowledgement_verified:false},true,true);
  } catch(error) {
    mark(storageStage+'_FAILED');
    // Retain the verified original and the precise failed stage. External
    // exceptions can contain credentials or signed URLs, so expose only our
    // controlled error codes, never arbitrary provider exception text.
    const internalCodes=new Set(['WORK_TRANSPORT_COMMAND_HOLD','WORK_TRANSPORT_PRIVATE_UPLOAD_NOT_CONFIRMED',
      'WORK_TRANSPORT_STORAGE_FILE_ID_MISMATCH',
      'WORK_TRANSPORT_PRIVATE_SHARING_NOT_VERIFIED','WORK_TRANSPORT_PRIVATE_BYTES_UNAVAILABLE','WORK_TRANSPORT_PRIVATE_BYTE_MISMATCH',
      'WORK_TRANSPORT_RACE_READBACK_NOT_ADMITTED','WORK_ORDINARY_ENTRY_COMPLETE_BODY_MISMATCH']);
    const candidate=/^WORK_[A-Z0-9_]+/.exec(String(error?.message||''))?.[0];
    const code=internalCodes.has(candidate)?candidate:'EXTERNAL_TOOL_ERROR';
    const deadlineCode='PAPER_EXTERNAL_SAVE_OR_READBACK_AFTER_CUTOFF';
    return pending({code:'PRIVATE_STORAGE_PATH_INCOMPLETE',stage:storageStage,error_code:code,
      native_deadline_code:String(error?.message||'').includes(deadlineCode)?deadlineCode:null});
  }
})
