"""Research adapter over existing JRA rank features. No Production or money authority.

Role temperatures fit disjoint earlier calibration races. Exclusion-conditioned
sequential probabilities are a hypothesis, not SSR, verified calibration or EV.
"""
import math,sys,statistics,hashlib,re
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'runtime'))
from jra_conditional_rank_shadow import FEATURES,vectors,sha
ID='JRA-CONDITIONAL-PROBABILITY-20261018-R1'
GRID=(.125,.25,.5,1.,2.,4.,8.)
POLICY={'candidate_id':ID,'temperature_grid':GRID,'temperature_loss':'race-mean conditional NLL on disjoint chronological calibration split',
 'joint':'P(W=h) P(P2=s|h excluded) P(P3=t|h,s excluded); no learned interactions',
 'marginals':'sum full distinct ordered joint; no oracle outcome input',
 'calibration_claim':False,'purchase_authority':False,'production_effect':'NONE','automatic_promotion':False}
def instant(s):
 d=datetime.fromisoformat(s.replace('Z','+00:00'))
 if d.tzinfo is None:raise ValueError('PROBABILITY_TIMEZONE')
 return d

def scores(runners,rank_model):
 x=vectors(runners)
 if any(not h.isdigit() or str(int(h))!=h or not 1<=int(h)<=18 for h in x):raise ValueError('PROBABILITY_RUNNER_ID')
 if rank_model.get('features')!=list(FEATURES) or set(rank_model.get('coefficients',{}))!=set(('W','P2','P3')):raise ValueError('PROBABILITY_RANK_SCHEMA')
 if any(len(w)!=len(FEATURES) or any(type(v) not in (int,float) or not math.isfinite(v) for v in w) for w in rank_model['coefficients'].values()):raise ValueError('PROBABILITY_RANK_WEIGHTS')
 return {role:{h:sum(a*b for a,b in zip(v,rank_model['coefficients'][role])) for h,v in x.items()} for role in ('W','P2','P3')}

def softmax(values,temperature,exclude=()):
 if type(temperature) not in (float,int) or not math.isfinite(temperature) or temperature<=0:raise ValueError('PROBABILITY_TEMPERATURE')
 kept={h:v for h,v in values.items() if h not in exclude}
 if not kept or any(type(v) not in (int,float) or not math.isfinite(v) for v in kept.values()):raise ValueError('PROBABILITY_FINITE_SCORES_REQUIRED')
 high=max(kept.values());exps={h:math.exp(max(-700.,(v-high)/temperature)) for h,v in kept.items()};z=sum(exps.values())
 return {h:e/z for h,e in exps.items()}

def conditional_nll(sc,actual,temperatures):
 return {role:-math.log(softmax(sc[role],temperatures[role],actual[:i])[actual[i]]) for i,role in enumerate(('W','P2','P3'))}

def fit_temperatures(calibration_rows,rank_model):
 if not calibration_rows:raise ValueError('EMPTY_PROBABILITY_CALIBRATION')
 ids=[r['race_id'] for r in calibration_rows]
 if len(ids)!=len(set(ids)):raise ValueError('DUPLICATE_PROBABILITY_CALIBRATION_RACE')
 if set(ids)&{r['race_id'] for r in rank_model['training_manifest']}:raise ValueError('PROBABILITY_TRAIN_CALIBRATION_OVERLAP')
 for row in calibration_rows:
  if any(instant(m['result_captured_at'])>=instant(row['q']['source_snapshot']['source_freeze_at']) for m in rank_model['training_manifest']):raise ValueError('PROBABILITY_TRAIN_RESULT_UNAVAILABLE')
 cache=[(scores(r['runners'],rank_model),r['top3']) for r in calibration_rows];temperatures={};losses={}
 for i,role in enumerate(('W','P2','P3')):
  losses[role]={str(t):statistics.mean(-math.log(softmax(sc[role],t,actual[:i])[actual[i]]) for sc,actual in cache) for t in GRID}
  temperatures[role]=min(GRID,key=lambda t:(losses[role][str(t)],abs(math.log(t)),t))
 return temperatures,losses

def distribution(sc,temperatures):
 universe=set(sc['W'])
 if len(universe)<3 or any(set(sc[r])!=universe for r in ('W','P2','P3')):raise ValueError('PROBABILITY_ROLE_UNIVERSE')
 p=softmax(sc['W'],temperatures['W']);p2={h:softmax(sc['P2'],temperatures['P2'],(h,)) for h in p};p3={};joint={}
 marginal={r:{h:0. for h in p} for r in ('W','P2','P3')}
 for h,ph in p.items():
  marginal['W'][h]=ph
  for s,ps in p2[h].items():
   key=h+'>'+s;p3[key]=softmax(sc['P3'],temperatures['P3'],(h,s));marginal['P2'][s]+=ph*ps
   for t,pt in p3[key].items():joint[key+'>'+t]=ph*ps*pt;marginal['P3'][t]+=ph*ps*pt
 return {'marginals':marginal,'head_p2':p2,'pair_third':p3,'ordered_joint':joint}

def measures(prob,target):
 if target not in prob:raise ValueError('PROBABILITY_TARGET_OUTSIDE_UNIVERSE')
 return {'log_loss':-math.log(prob[target]),'brier_sum':sum((p-(h==target))**2 for h,p in prob.items()),
  'rank_mid':1+sum(p>prob[target] for p in prob.values())+(sum(p==prob[target] for p in prob.values())-1)/2,
  'top1_correct':int(max(prob,key=lambda h:(prob[h],-int(h)))==target),'top1_confidence':max(prob.values())}

def ece(rows,bins=5):
 if type(bins) is not int or bins<=0:raise ValueError('PROBABILITY_ECE_BINS')
 if not rows:return None
 value=0.
 for i in range(bins):
  cell=[r for r in rows if min(bins-1,int(r['top1_confidence']*bins))==i]
  if cell:value+=len(cell)/len(rows)*abs(statistics.mean(r['top1_correct'] for r in cell)-statistics.mean(r['top1_confidence'] for r in cell))
 return value

def forecast(request,model,*,observed_at=None):
 if model.get('sha256')!=sha({k:v for k,v in model.items() if k!='sha256'}):raise ValueError('PROBABILITY_MODEL_HASH')
 if model.get('candidate_id')!=ID or model.get('policy_sha256')!=sha(POLICY) or sha(model.get('policy'))!=sha(POLICY):raise ValueError('PROBABILITY_MODEL_POLICY')
 if not request['race_id'].startswith('KM-JRA-'):raise ValueError('PROBABILITY_JRA_ONLY')
 rank=model['rank_model']
 if rank.get('sha256')!=sha({k:v for k,v in rank.items() if k!='sha256'}):raise ValueError('PROBABILITY_RANK_HASH')
 temperatures=model['temperatures']
 if set(temperatures)!=set(('W','P2','P3')) or any(type(t) not in (int,float) or t not in GRID for t in temperatures.values()):raise ValueError('PROBABILITY_TEMPERATURE_POLICY')
 training=rank['training_manifest'];calibration=model['calibration_manifest']
 if not training or not calibration:raise ValueError('PROBABILITY_MANIFEST_REQUIRED')
 for m in training+calibration:
  if not re.fullmatch(r'KM-JRA-[A-Z]{3}-20[0-9]{6}-R[0-9]{2}',str(m.get('race_id',''))) or any(not re.fullmatch(r'[0-9a-f]{64}',str(m.get(k,''))) for k in ('source_sha256','final_sha256','result_sha256')):raise ValueError('PROBABILITY_MANIFEST_SCHEMA')
  if not instant(m['source_freeze_at'])<=instant(m['prediction_cutoff'])<instant(m['scheduled_post_at'])<=instant(m['result_captured_at']):raise ValueError('PROBABILITY_MANIFEST_TIME_ORDER')
 source=instant(request['source_snapshot']['source_freeze_at']);cutoff=instant(request['prediction_cutoff']);created=instant(model['created_at'])
 if not created<source<=cutoff:raise ValueError('PROBABILITY_MODEL_NOT_BEFORE_SOURCE')
 now=instant(observed_at) if observed_at else datetime.now(timezone.utc)
 if not source<=now<=cutoff:raise ValueError('PROBABILITY_FREEZE_CHRONOLOGY')
 if max(instant(m['result_captured_at']) for m in rank['training_manifest'])>=min(instant(m['source_freeze_at']) for m in model['calibration_manifest']):raise ValueError('PROBABILITY_TRAIN_CALIBRATION_CHRONOLOGY')
 manifests=model['rank_model']['training_manifest']+model['calibration_manifest']
 if len({m['race_id'] for m in manifests})!=len(manifests):raise ValueError('PROBABILITY_DUPLICATE_MANIFEST_RACE')
 if any(m['race_id']==request['race_id'] for m in manifests):raise ValueError('PROBABILITY_TRAIN_TARGET_OVERLAP')
 if any(instant(m['result_captured_at'])>=created for m in manifests):raise ValueError('PROBABILITY_LABEL_AFTER_MODEL')
 sc=scores(request['runners'],model['rank_model']);out=distribution(sc,model['temperatures'])
 out.update(candidate_id=ID,race_id=request['race_id'],model_sha256=model['sha256'],code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),policy_sha256=sha(POLICY),
  observed_at=now.isoformat(),source_sha256=request['source_snapshot_sha256'],runner_universe_sha256=sha(sorted(sc['W'])),prediction_cutoff=request['prediction_cutoff'],
  status='PROVISIONAL_PROBABILITY_MAPPING_NOT_FORWARD_CALIBRATED',oos_eligible=False,production_effect='NONE',purchase_authority=False,ev_kelly_authority=False,tickets_created=0)
 out['sha256']=sha(out);return out

def race_vector(row):
 runners=row['runners']
 return [statistics.mean(r['canonical_components'][k]['value'] for r in runners) for k in FEATURES]+[len(runners)]

def fit_ood(train,calibration):
 if len(train)<2 or not calibration:raise ValueError('OOD_DATA_REQUIRED')
 ids=[r['race_id'] for r in train+calibration]
 if len(ids)!=len(set(ids)):raise ValueError('OOD_DUPLICATE_OR_SPLIT_OVERLAP')
 xs=[race_vector(r) for r in train];means=[statistics.mean(v) for v in zip(*xs)];scales=[max(1.,statistics.pstdev(v)) for v in zip(*xs)]
 spec={'means':means,'scales':scales,'features':list(FEATURES)+['FIELD_SIZE'],'training_races':[r['race_id'] for r in train],
  'calibration_races':[r['race_id'] for r in calibration],'alpha':.1,'method':'max absolute standardized race mean; diagonal only, correlated features retained'}
 values=sorted(ood_score(r,spec) for r in calibration);k=math.ceil((len(values)+1)*.9)
 spec['threshold']=values[k-1] if k<=len(values) else None;spec['finite_sample_order']=k;return spec

def ood_score(row,spec):
 x=race_vector(row)
 if len(spec['means'])!=len(x) or len(spec['scales'])!=len(x) or any(not math.isfinite(v) for v in spec['means']) or any(not math.isfinite(v) or v<=0 for v in spec['scales']):raise ValueError('OOD_SCHEMA')
 return max(abs((v-m)/s) for v,m,s in zip(x,spec['means'],spec['scales']))
