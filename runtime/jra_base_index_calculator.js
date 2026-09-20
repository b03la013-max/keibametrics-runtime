const REGISTRY_URL = "https://raw.githubusercontent.com/b03la013-max/keibametrics-runtime/main/mapping/jra_base_index_mapping_registry_v0.1_20260920.json";
const BASE = ["HPI","SSI","CFI","RFI","BVI","JTI","CSI","TRI","BWI","GCI","PRI","KGI","VMI"];
const DERIVED = ["DCR","TPI","ZAI_WIN","ZAI_PLACE","SRI","F3S","T3I"];
let registry = null;
async function loadRegistry(){
  if (registry) return registry;
  const r = await fetch(REGISTRY_URL,{cache:"no-store"});
  if(!r.ok) throw new Error("REGISTRY_FETCH_"+r.status);
  registry = await r.json();
  return registry;
}
function canonicalItem(index, c){
  const ok = c && Number.isFinite(c.value) && c.rule_id && c.mapping_version;
  if(!ok) return null;
  return {
    index_name:index, required:true, terminal_status:"CALCULATED",
    formal_value:c.value, transport_value:c.value, missing_flag:false,
    calculation_rule_id:c.rule_id, mapping_version:c.mapping_version,
    evidence_refs:Array.isArray(c.evidence_refs)?c.evidence_refs:[],
    source_fact:c.source_fact??null, adjustments:c.adjustments??[]
  };
}
function holdItem(index, reason){
  return {
    index_name:index, required:true, terminal_status:"RULED-HOLD",
    formal_value:null, transport_value:50, missing_flag:true,
    calculation_rule_id:"JRA-UNKNOWN-NEUTRAL-50-v1",
    mapping_version:"JRA-BASE-INDEX-MAPPING-REGISTRY-v0.1-20260920",
    hold_reason:reason || "CANONICAL_NUMERIC_MAPPING_UNAVAILABLE",
    semantics:"transport-neutral only; not ability/probability/weakness"
  };
}
function notApplicable(index, reason){
  return {
    index_name:index, required:true, terminal_status:"NOT-APPLICABLE",
    formal_value:null, transport_value:50, missing_flag:true,
    calculation_rule_id:"JRA-NOT-APPLICABLE-v1",
    mapping_version:"JRA-BASE-INDEX-MAPPING-REGISTRY-v0.1-20260920",
    hold_reason:reason || "CANON_DECLARED_NOT_APPLICABLE"
  };
}
function positiveGroups(e){
  const groups = [];
  if(!e || typeof e!=="object") return groups;
  const keys=["gate","dash_position_acquisition","workout_capability","distance_fit","pedigree_physical","jockey_tactical_fit","sustain_reserve","body_condition_growth","stable_trainer_state","course_fit"];
  for(const k of keys){
    const v=e[k];
    if(v===true || v==="POSITIVE" || v==="STRONG" || (typeof v==="object" && ["POSITIVE","STRONG"].includes(v.status))) groups.push(k);
  }
  return groups;
}
function calculateRunner(r){
  const canonical=r.canonical_components||{};
  const notApplicableSet=new Set(r.not_applicable_indices||[]);
  const items=[];
  for(const idx of [...BASE,...DERIVED]){
    if(notApplicableSet.has(idx)){ items.push(notApplicable(idx)); continue; }
    const ci=canonicalItem(idx,canonical[idx]);
    if(ci) items.push(ci);
    else items.push(holdItem(idx, r.newcomer ? "NEWCOMER_OR_MAPPING_UNAVAILABLE" : "CANONICAL_NUMERIC_MAPPING_UNAVAILABLE"));
  }
  const groups=positiveGroups(r.raw_evidence);
  return {
    runner_id:String(r.runner_id??r.horse_no),
    name:r.name||"",
    newcomer:!!r.newcomer,
    evidence_groups:groups,
    winner_reaudit_trigger:groups.length>=2,
    items
  };
}
function json(body,status=200){return new Response(JSON.stringify(body),{status,headers:{"content-type":"application/json; charset=utf-8"}});}
Bun.serve({
  port:Number(process.env.PORT||3000),
  async fetch(req){
    const u=new URL(req.url);
    if(req.method==="GET" && u.pathname==="/health"){
      const reg=await loadRegistry();
      return json({status:"READY",service:"JRA_BASE_INDEX_CALCULATOR",registry_id:reg.registry_id,mode:"CANONICAL_REPLAY_OR_RULED_HOLD",no_pseudo_precision:true});
    }
    if(req.method==="GET" && u.pathname==="/registry") return json(await loadRegistry());
    if(req.method==="POST" && u.pathname==="/calculate-jra-base"){
      try{
        const p=await req.json();
        if(!p.race_id || !Array.isArray(p.runners) || p.runners.length===0) return json({status:"FAIL",errors:["RACE_OR_RUNNERS_MISSING"]},422);
        const reg=await loadRegistry();
        const runners=p.runners.map(calculateRunner);
        const all=runners.flatMap(x=>x.items);
        const allowed=new Set(["CALCULATED","RULED-HOLD","NOT-APPLICABLE"]);
        const unresolved=all.filter(x=>!allowed.has(x.terminal_status)).length;
        const hold=all.filter(x=>x.terminal_status==="RULED-HOLD").length;
        const calc=all.filter(x=>x.terminal_status==="CALCULATED").length;
        return json({
          status:unresolved===0?"PASS":"FAIL",
          race_id:p.race_id,
          registry_id:reg.registry_id,
          required_count:all.length,
          calculated_count:calc,
          ruled_hold_count:hold,
          unresolved_count:unresolved,
          transport_semantics:"RULED-HOLD uses neutral 50 + missing flag for KRS adapter only",
          runners
        });
      }catch(e){ return json({status:"FAIL",errors:[String(e?.message||e)]},500); }
    }
    return json({status:"NOT_FOUND"},404);
  }
});
