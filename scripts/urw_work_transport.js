// Work code-mode caller. Evaluates to a function; installs no worker or service.
// `tools` is the currently authorized Work tool object, never a token extractor.
// Invoke once for an ordinary query. Private bytes never enter Git.
(async function urwWorkTransport(tools, options) {
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
  const base='python3 -m runtime.urw_registered_paper_entry --config '+quote(options.config);
  const query=' --query '+quote(options.query);
  let saved=json(await shell(base+' read'+query));
  if(saved)return {status:'EXACT_COMPLETED_READBACK_REUSED',publication:saved,calculation_executed:false,storage_writes:0};
  let complete=options.completed;
  const ordinaryOutput=options.privateDirectory+'/ordinary-'+String(options.requestId||'request').replace(/[^A-Za-z0-9_-]/g,'_');
  const ordinary='KM_URW_SINGLE_RACE_CONNECTION='+quote(options.config)+' python3 -m runtime.local_race_entry'+query
    +' --output '+quote(ordinaryOutput)+' --run-id '+quote(options.requestId||'ordinary-single-race');
  if(!complete && options.executionMode==='SINGLE_RACE_NONPRODUCTION') {
    // One natural request enters the existing caller, then resumes the same
    // result through actual storage. No registered-v2 admission is inferred.
    await shell(ordinary+' >/dev/null || test -f '+quote(ordinaryOutput+'/chat_entry_report.json'));
    const report=JSON.parse(await shell('cat '+quote(ordinaryOutput+'/chat_entry_report.json')));
    complete=report.research_execution;
    if(report.status!=='SINGLE_RACE_CALCULATED_PRIVATE_SAVE_PENDING')throw new Error('WORK_ORDINARY_ENTRY_EXECUTION_FAILED: '+JSON.stringify(complete));
  }
  complete=complete || json(await shell(base+' prepare'+query));
  if(complete.status!=='PRIVATE_SAVE_REQUIRED')throw new Error('WORK_TRANSPORT_NO_COMPLETED_CALCULATION');
  const upload=unwrap(await tools.mcp__codex_apps__google_drive_upload_file({file_uri:complete.archive,
    file_name:complete.race_id+'-'+complete.artifact_sha256.slice(0,12)+'.zip',mime_type:'application/zip',parent_folder_id:options.driveFolder}));
  if(!upload.success || !upload.id)throw new Error('WORK_TRANSPORT_PRIVATE_UPLOAD_NOT_CONFIRMED');
  const meta=unwrap(await tools.mcp__codex_apps__google_drive_get_file_metadata({fileId:upload.id}));
  if(meta.shared===true || (meta.permissions||[]).some(x=>x.type==='anyone'))throw new Error('WORK_TRANSPORT_UNEXPECTED_SHARING');
  const raw=unwrap(await tools.mcp__codex_apps__google_drive_fetch({url:meta.url,download_raw_file:true,include_base64:false}));
  if(!raw.file_uri?.download_url)throw new Error('WORK_TRANSPORT_PRIVATE_BYTES_UNAVAILABLE');
  const prefix=options.privateDirectory+'/readback-'+complete.artifact_sha256;
  const file=prefix+'.zip', receipt=prefix+'.receipt.json';
  const actual=json(await shell('umask 077\ncurl --fail --silent --show-error --location --output '+quote(file)+' '+quote(raw.file_uri.download_url)
    +'\npython3 -c '+quote("import hashlib,json,pathlib; p=pathlib.Path("+JSON.stringify(file)+"); print(json.dumps({'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}))")));
  if(actual.sha256!==complete.archive_sha256 || actual.bytes!==Number(meta.size))throw new Error('WORK_TRANSPORT_PRIVATE_BYTE_MISMATCH');
  const proof={storage_provider:'Google Drive',storage_id:meta.id,url:meta.url,provider_created_at:meta.created_time,
    provider_modified_at:meta.modified_time,provider_shared:meta.shared,bytes:actual.bytes,readback_sha256:actual.sha256,
    verified_at:new Date().toISOString(),scope:'PRIVATE_BYTE_READBACK_NOT_A_SIGNED_FORMAL_RECEIPT'};
  await tools.apply_patch('*** Begin Patch\n*** Add File: '+receipt+'\n+'+JSON.stringify(proof,null,2).split('\n').join('\n+')+'\n*** End Patch');
  await shell(base+' publish --complete '+quote(complete.folder+'/complete.json')+' --readback '+quote(file)+' --receipt '+quote(receipt));
  saved=json(await shell(base+' read'+query));
  if(!saved || saved.race_id!==complete.race_id || saved.artifact_sha256!==complete.artifact_sha256)throw new Error('WORK_TRANSPORT_RACE_READBACK_NOT_ADMITTED');
  if(options.executionMode==='SINGLE_RACE_NONPRODUCTION') {
    await shell(ordinary+' >/dev/null');
    const report=JSON.parse(await shell('cat '+quote(ordinaryOutput+'/chat_entry_report.json')));
    if(report.status!=='FORMAL_HOLD_SINGLE_RACE_READBACK_VERIFIED' || !report.message.includes(saved.body))
      throw new Error('WORK_ORDINARY_ENTRY_COMPLETE_BODY_MISMATCH');
  }
  return {status:'CALCULATION_PRIVATE_SAVE_READBACK_AND_INDEX_CONNECTED',publication:saved,calculation_executed:!options.completed,
    storage_writes:1,chat_render_verified:false,user_acknowledgement_verified:false};
})
