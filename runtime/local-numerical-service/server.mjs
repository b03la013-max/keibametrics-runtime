const WEIGHTS={
"HPI-L":{recent_finish:20,finish_margin:15,passing_position_content:20,class_level:15,opponent_strength:15,repeatability:15},
"CFIg-L":{same_venue:25,same_distance:20,similar_distance:15,course_geometry:15,turn_direction:10,draw_style_fit:10,going_fit:5},
"RFIg-L":{running_style_repro:15,position_acquisition:15,position_maintenance:15,third_corner_progression:15,leadership_stalk_acceptance:10,kickback_traffic_tolerance:10,going_adaptation:10,jockey_reproducibility:10},
"BVIg-L":{sire_fit:30,damsire_fit:20,distance_sustain:15,distance_trait:10,surface_sand_fit:15,venue_stat:5,physical_style_fit:5},
"JTI-L":{venue_recent:25,distance_record:15,stable_combo:15,position_acquisition_skill:15,progression_timing_skill:10,favorite_reliability:10,longshot_record:10},
"CSI-L":{stable_venue_class_distance:25,transfer_preparation:15,layoff_preparation:15,jockey_use_continuity:10,cci_specificity:15,tri_vertical_comparison:15,rotation_management:5},
"BWI-L":{good_weight_range:25,weight_change_reason_rate:15,carried_weight:15,age_growth:10,interval:10,fatigue_rebound:10,transport_season:5,paddock:10},
"DCR":{official_recent_coverage:25,same_venue_distance_comparability:20,training_comment_trial:15,bodyweight_range_coverage:15,same_day_gci_coverage:15,late_odds_changes_coverage:10},
"NCI":{current_class:20,previous_class:15,recent_opponent_class:20,race_set_level:15,class_change_pressure:10,transfer_class:10,class_relative_time:10}
};
const REG="LOCAL-BASE-INDEX-MAPPING-REGISTRY-v1.0-20260922";
function err(s){throw new Error(s)}
function validFeature(n,x){
 if(!x||typeof x!=="object")err("FEATURE_NOT_OBJECT:"+n);
 for(const k of ["score","rule_id","evidence_refs","source_fact","source_timestamp"])if(!(k in x))err("FEATURE_FIELDS_MISSING:"+n+":"+k);
 if(typeof x.score!=="number"||!Number.isFinite(x.score)||x.score<0||x.score>100)err("SCORE_NOT_0_100:"+n);
 if(!String(x.rule_id||"").trim())err("RULE_ID_REQUIRED:"+n);
 if(!Array.isArray(x.evidence_refs)||!x.evidence_refs.length)err("EVIDENCE_REFS_REQUIRED:"+n);
 if(!String(x.source_fact||"").trim())err("SOURCE_FACT_REQUIRED:"+n);
 if(!String(x.source_timestamp||"").trim())err("SOURCE_TIMESTAMP_REQUIRED:"+n);
 return x;
}
function weighted(name,feats){
 let total=0,den=0,refs=[],facts=[],parts=[];
 for(const [f,w] of Object.entries(WEIGHTS[name])){
  if(!(f in feats))err("REQUIRED_COMPONENT_MISSING:"+name+":"+f);
  const x=validFeature(f,feats[f]); total+=x.score*w; den+=w; refs.push(...x.evidence_refs);
  facts.push(f+"="+x.score+":"+x.source_fact); parts.push({feature:f,weight:w,...x});
 }
 return {value:+(total/den).toFixed(6),rule_id:"LOCAL-v4.12R3-"+name+"-WEIGHTED",mapping_version:REG,evidence_refs:[...new Set(refs)].sort(),source_fact:facts.join(" | "),components:parts};
}
function externalIndex(name,spec,allowed){
 if(!spec||typeof spec!=="object")err("EXTERNAL_INDEX_MISSING:"+name);
 if(typeof spec.value!=="number"||!Number.isFinite(spec.value)||spec.value<0||spec.value>100)err("EXTERNAL_INDEX_VALUE_INVALID:"+name);
 if(!Array.isArray(allowed)||!allowed.includes(String(spec.rule_id||"")))err("UNREGISTERED_VENUE_RULE:"+name+":"+String(spec.rule_id||""));
 if(!Array.isArray(spec.evidence_refs)||!spec.evidence_refs.length||!String(spec.source_fact||"").trim())err("EXTERNAL_INDEX_PROVENANCE_MISSING:"+name);
 return {value:+spec.value.toFixed(6),rule_id:String(spec.rule_id),mapping_version:REG,evidence_refs:spec.evidence_refs.map(String),source_fact:String(spec.source_fact),venue_formula_registry:String(spec.venue_formula_registry||"")};
}
function materializeRunner(r,vr){
 const feats=r.evidence_features||{}, c={};
 for(const idx of Object.keys(WEIGHTS))c[idx]=weighted(idx,feats);
 const ext=r.canonical_external_indices||{}, allowed=vr.allowed_rule_ids||{};
 const evi=externalIndex("EVI/CEV",ext["EVI/CEV"],allowed["EVI/CEV"]); c["EVI/CEV"]=evi;
 const v=Object.fromEntries(Object.keys(WEIGHTS).map(k=>[k,c[k].value])), ev=evi.value;
 const linear=.18*v["HPI-L"]+.16*v["CFIg-L"]+.14*v["RFIg-L"]+.08*v["BVIg-L"]+.08*v["JTI-L"]+.08*v["CSI-L"]+.08*v["BWI-L"]+.10*v["NCI"]+.10*ev;
 const mm=Math.min(v["HPI-L"],v["CFIg-L"],v["RFIg-L"],v["NCI"],ev,v["BWI-L"]);
 const pen=Math.max(0,(60-mm)*.5);
 c["TPI-L"]={value:+Math.max(0,Math.min(100,linear-pen)).toFixed(6),rule_id:"LOCAL-TPI-L-v4.12R3",mapping_version:REG,evidence_refs:[...new Set(["HPI-L","CFIg-L","RFIg-L","BVIg-L","JTI-L","CSI-L","BWI-L","NCI","EVI/CEV"].flatMap(k=>c[k].evidence_refs))].sort(),source_fact:`TPI_linear=${linear.toFixed(6)};min_major=${mm.toFixed(6)};penalty=${pen.toFixed(6)}`};
 for(const [name,spec] of Object.entries(ext))if(name!=="EVI/CEV")c[name]=externalIndex(name,spec,allowed[name]);
 return {...r,canonical_components:c,local_mapping_registry:REG};
}
function calculate(p){
 const req=p.required_indices;if(!Array.isArray(req)||!req.length)err("REQUIRED_INDEX_MANIFEST_REQUIRED");
 const vr=p.venue_formula_registry;if(!vr||!String(vr.registry_id||""))err("VENUE_FORMULA_REGISTRY_REQUIRED");
 const rs=p.runners;if(!Array.isArray(rs)||!rs.length)err("RUNNERS_REQUIRED");
 const runners=rs.map(r=>materializeRunner(r,vr)), unresolved=[];
 for(const r of runners)for(const idx of req)if(!(idx in r.canonical_components))unresolved.push({runner_id:String(r.runner_id),index:idx,reason:"FORMULA-UNRESOLVED"});
 return {status:unresolved.length?"PARTIAL":"PASS",family:"LOCAL",mapping_registry:REG,numeric_coverage:{required_count:rs.length*req.length,calculated_count:rs.length*req.length-unresolved.length,unresolved_count:unresolved.length,unresolved},full_numerical_calculation:!unresolved.length,runners};
}
const server=Bun.serve({port:Number(process.env.PORT||8080),hostname:"0.0.0.0",async fetch(req){
 const u=new URL(req.url);
 if(req.method==="GET"&&u.pathname==="/health")return Response.json({status:"READY",family:"LOCAL",profile:"KM-LOCAL-FULLPIPELINE-CORRECTNESS-HARDENING-20260922-R1",mapping_registry:REG,krs_authority:false});
 if(req.method==="POST"&&u.pathname==="/calculate-local"){try{return Response.json(calculate(await req.json()))}catch(e){return Response.json({status:"FAIL",detail:String(e.message||e)},{status:422})}}
 return Response.json({detail:"not found"},{status:404});
}});
console.log("LOCAL_NUMERICAL_RUNTIME_READY",server.port);
