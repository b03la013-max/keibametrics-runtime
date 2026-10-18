"""Result-blind, regularized role ranking comparison; no ticket/Production authority."""
import hashlib,json,math
from pathlib import Path
from datetime import datetime

FEATURES=('HPI','SSI','CFI','RFI','BVI','JTI','CSI','TRI','BWI','GCI','PRI','KGI','VMI','DCR','TPI','ZAI_WIN','ZAI_PLACE','SRI','F3S','T3I')
ID='JRA-CONDITIONAL-RANK-20261018-R1'
def sha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def vectors(runners):
 ids=[str(r['runner_id']) for r in runners]
 if len(ids)!=len(set(ids)):raise ValueError('RANK_DUPLICATE_RUNNER')
 vals={str(r['runner_id']):[r['canonical_components'][k]['value'] for k in FEATURES] for r in runners}
 if any(type(v) not in (int,float) or not math.isfinite(v) or not 0<=v<=100 for row in vals.values() for v in row):raise ValueError('RANK_FULL20_REQUIRED')
 means=[sum(v[j] for v in vals.values())/len(vals) for j in range(len(FEATURES))]
 scales=[max(1.,math.sqrt(sum((v[j]-means[j])**2 for v in vals.values())/len(vals))) for j in range(len(FEATURES))]
 return {h:[(v[j]-means[j])/scales[j] for j in range(len(FEATURES))] for h,v in vals.items()}
def compare(request,model):
 if model.get('sha256')!=sha({k:v for k,v in model.items() if k!='sha256'}):raise ValueError('RANK_MODEL_HASH')
 if model.get('candidate_id')!=ID or model.get('features')!=list(FEATURES):raise ValueError('RANK_MODEL_SCHEMA')
 cutoff=datetime.fromisoformat(request['prediction_cutoff'].replace('Z','+00:00'))
 generated=datetime.fromisoformat(model['created_at'].replace('Z','+00:00'))
 source_time=datetime.fromisoformat(request['source_snapshot']['source_freeze_at'].replace('Z','+00:00'))
 if generated.tzinfo is None or cutoff.tzinfo is None or generated>=source_time or source_time>cutoff:raise ValueError('RANK_MODEL_NOT_AVAILABLE_BEFORE_SOURCE')
 if any(datetime.fromisoformat(r['result_captured_at'].replace('Z','+00:00'))>=generated for r in model['training_manifest']):raise ValueError('RANK_TRAIN_RESULT_AFTER_MODEL_FREEZE')
 if request['race_id'] in {x['race_id'] for x in model['training_manifest']}:raise ValueError('RANK_TRAIN_TARGET_OVERLAP')
 if not request['race_id'].startswith('KM-JRA-'):raise ValueError('RANK_JRA_ONLY')
 x=vectors(request['runners']);scores={}
 for role,w in model['coefficients'].items():
  if role not in ('W','P2','P3') or len(w)!=len(FEATURES) or any(type(v) not in (float,int) or not math.isfinite(v) for v in w):raise ValueError('RANK_WEIGHTS')
  scores[role]={h:sum(a*b for a,b in zip(v,w)) for h,v in x.items()}
 if set(scores)!=set(('W','P2','P3')):raise ValueError('RANK_ROLES_REQUIRED')
 rankings={role:sorted(values,key=lambda h:(-values[h],int(h))) for role,values in scores.items()}
 # Exclusion is conditional on each hypothetical head/pair, never the actual result.
 p2={h:[s for s in rankings['P2'] if s!=h] for h in x}
 third={h+'>'+s:[t for t in rankings['P3'] if t not in (h,s)] for h in x for s in x if h!=s}
 out={'candidate_id':ID,'model_sha256':model['sha256'],'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'training_manifest_sha256':sha(model['training_manifest']),'source_sha256':request['source_snapshot_sha256'],
 'runner_universe_sha256':sha(sorted(x)),'prediction_cutoff':request['prediction_cutoff'],
 'scores':scores,'role_rankings':rankings,'head_local_p2':p2,'pair_conditioned_third':third,
 'calibrated_probabilities':False,'production_effect':'NONE','tickets_created':0,'promotion':'HOLD',
 'scope':'RANK_ONLY; no automatic Role, Ticket or Capital substitution','sha256':None}
 out.pop('sha256');out['sha256']=sha(out);return out
