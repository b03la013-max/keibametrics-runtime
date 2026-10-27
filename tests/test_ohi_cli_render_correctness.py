"""Focused offline tests: CLI cwd/asset identity and immutable-render compatibility."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import pytest

from runtime import ohi_single_race_research as n
CODE=Path(n.__file__).resolve().parents[1]
ORIGINAL=Path(n.__file__).resolve()

def fixture_result():
    """Authored schema fixture; no official Raw or live calculation is asserted."""
    ids=['1','2','3','4','5']
    roles={i:(['W','P2','P3'] if i in ('1','2') else []) for i in ids}
    owners={'BASELINE':{'ranking':ids,'roles':deepcopy(roles)},
            'OHI_FIXED_CANDIDATE':{'ranking':ids,'role_columns':deepcopy(roles)}}
    portfolio={'tickets':[{'stake':100}],
        'tree':{'text':'AUTHORED SCHEMA ONLY'},
        'capital':{'capital_limit':10000,'unused_budget':9900,'no_bet':False,
                   'reason':'AUTHORED_SCHEMA_ONLY','required_capital':100}}
    summary={'required_count':len(ids)*29,'calculated_count':len(ids)*29,
        'ruled_neutral_count':0,'unresolved_count':0,'full_numerical_complete':True,
        'required_indices':list(n.REQUIRED)}
    cells={i:{k:{'terminal_status':'CALCULATED','value':52.0} for k in n.REQUIRED} for i in ids}
    krs={'receipt':{'runs':5000,'seed':1},
        'output':{'summary':[{'horse_no':int(i),'SSR-W':.2,'SSR-P2':.2,'SSR-P3':.2,'LSR':.2} for i in ids]}}
    return {'race':{'race_date':'2026-10-27','race_no':1,'race_name':'AUTHORED SCHEMA ONLY',
        'scheduled_post_at':'2026-10-27T14:20:00+09:00','prediction_cutoff':'2026-10-27T14:15:00+09:00'},
        'classification':'AUTHORED_SCHEMA_ONLY_NO_LIVE_CLAIM','source_fetched_at':'2026-10-27T12:00:00+09:00',
        'freeze_at':'2026-10-27T12:05:00+09:00','source_sha256':'a'*64,'sha256':'b'*64,
        'numerical_summary':summary,'owners':owners,'numerical_cells':cells,
        'all_runners':[{'runner_id':i,'name':'AUTHORED '+i,'starts':[],'missingness':['AUTHORED_UNKNOWN'],
            'current_body_weight':None,'current_body_weight_change':None} for i in ids],
        'changes_status':'AUTHORED_UNKNOWN','price_status':{'status':'AUTHORED_UNKNOWN'},
        'portfolios':{k:deepcopy(portfolio) for k in owners},'krs':{k:deepcopy(krs) for k in owners}}

def cli_setup(tmp_path,monkeypatch,mod,*,query=False,raises=False):
    invoke=tmp_path/'caller';invoke.mkdir()
    paths={}
    for name,content in [('model.json','caller-model'),('engine.py','caller-engine'),('params.json','caller-params')]:
        (invoke/name).write_text(content);paths[name]=content
    source=tmp_path/'private-source';source.mkdir();(source/'observation.json').write_text('{}')
    output=tmp_path/'private-output'
    argv=['ohi.py',('--query' if query else '--source-dir'),('大井1R' if query else str(source)),
        '--output',str(output),'--model','model.json','--engine','engine.py','--params','params.json']
    monkeypatch.setattr(sys,'argv',argv)
    monkeypatch.setattr(mod,'__file__',str(ORIGINAL))  # candidate installed into the unchanged code layout
    seen={}
    def run(observation,out,model,engine,params,**kwargs):
        seen.update(cwd=Path.cwd(),assets=[model,engine,params],source_dir=kwargs['source_dir'])
        for path in (model,engine,params):
            assert Path(path).is_absolute() and Path(path).read_text()==paths[Path(path).name]
        # Actual frozen registries are opened; no mocked registry or numerical rule.
        seen['equivalence']=mod._assert_registry_equivalence()
        if raises:raise RuntimeError('AUTHORED_CALCULATION_FAILURE')
        return {'classification':'TEST_ONLY','sha256':'a'*64,'race':{},'numerical_summary':{}}
    monkeypatch.setattr(mod,'run',run);monkeypatch.setattr(mod,'render',lambda result:'TEST_ONLY')
    if query:
        monkeypatch.setitem(sys.modules,'runtime.local_race_entry',SimpleNamespace(resolve_chat_intent=lambda text:
            {'venue_id':'OHI','race_date':'2026-10-27','race_no':1}))
        def capture(day,number,directory,**kwargs):
            seen['capture_directory']=directory;Path(directory).mkdir()
            return {'profile':'AUTHORED_CLI_CAPTURE_ONLY'}
        monkeypatch.setattr(mod,'capture',capture)
    monkeypatch.chdir(invoke)
    return invoke,source,output,seen


@pytest.mark.parametrize('query',[False,True])
def test_cli_calc_uses_code_cwd_and_original_asset_identity(tmp_path,monkeypatch,query):
    invoke,source,output,seen=cli_setup(tmp_path,monkeypatch,n,query=query)
    n.main()
    assert seen['cwd']==CODE and seen['equivalence']['transform_equivalent'] is True
    assert all(Path(path).parent==invoke for path in seen['assets'])
    assert Path(seen['source_dir']).is_absolute() and Path.cwd()==invoke
    if query:assert seen['capture_directory']==str(output)+'.source'

def test_cli_failure_restores_invocation_cwd(tmp_path,monkeypatch):
    invoke,source,output,seen=cli_setup(tmp_path,monkeypatch,n,raises=True)
    with pytest.raises(RuntimeError,match='AUTHORED_CALCULATION'):n.main()
    assert seen['cwd']==CODE and Path.cwd()==invoke

@pytest.mark.parametrize('flag',['--source-dir','--output','--readback'])
def test_private_relative_paths_not_resolved_into_acceptance(tmp_path,monkeypatch,flag):
    invoke,source,output,seen=cli_setup(tmp_path,monkeypatch,n)
    if flag=='--readback':argv=['ohi.py','--readback','relative-readback']
    else:
        argv=list(sys.argv);argv[argv.index(flag)+1]='relative-private-path'
    monkeypatch.setattr(sys,'argv',argv)
    with pytest.raises(ValueError,match='PRIVATE_PATH_REQUIRED'):n.main()
    assert Path.cwd()==invoke and not seen

@pytest.mark.parametrize('flag',['--source-dir','--output','--readback'])
def test_private_symlink_paths_not_resolved_into_acceptance(tmp_path,monkeypatch,flag):
    invoke,source,output,seen=cli_setup(tmp_path,monkeypatch,n)
    link=tmp_path/'symlink-private';link.symlink_to(source,target_is_directory=True)
    if flag=='--readback':argv=['ohi.py','--readback',str(link)]
    else:
        argv=list(sys.argv);argv[argv.index(flag)+1]=str(link)
    monkeypatch.setattr(sys,'argv',argv)
    with pytest.raises(ValueError,match='PRIVATE_PATH_REQUIRED'):n.main()
    assert Path.cwd()==invoke and not seen

def test_renderer_before_bug_and_new_complete_weight_display():
    result=fixture_result();before=deepcopy(result)
    for horse in result['all_runners']:
        horse['current_body_weight']=500;horse['current_body_weight_change']=0
    assert '馬体重・当日馬場は未観測で、' in n._render_v1_1(result)
    result_before=deepcopy(result);body=n.render(result);count=len(result['all_runners'])
    assert f'馬体重は{count}/{count}頭、増減は{count}/{count}頭で観測済み' in body
    assert '当日馬場は未観測です。' in body
    assert '馬体重・当日馬場は未観測で、' not in body
    assert result==result_before and before['numerical_cells']==result['numerical_cells']

def test_renderer_partial_weight_and_zero_change_keep_unknowns():
    result=fixture_result()
    for horse in result['all_runners']:
        horse['current_body_weight']=None;horse['current_body_weight_change']=None
    result['all_runners'][0].update(current_body_weight=500,current_body_weight_change=0)
    body=n.render(result);count=len(result['all_runners'])
    assert f'馬体重は1/{count}頭、増減は1/{count}頭で観測済み' in body

def test_renderer_all_unknown_weights_are_not_marked_measured():
    result=fixture_result()
    for horse in result['all_runners']:
        horse['current_body_weight']=None;horse['current_body_weight_change']=None
    assert f'馬体重・増減は全{len(result["all_runners"])}頭で未観測' in n.render(result)

@pytest.mark.parametrize('location',['race','source'])
def test_renderer_going_only_from_explicit_current_observation(location):
    result=fixture_result()
    if location=='race':result['race']['going']='不良'
    else:result['source']={'normalized_evidence':{'track_condition':{'value':'不良'}}}
    assert '当日馬場は「不良」と観測されています。' in n.render(result)

def test_renderer_conflicting_current_going_not_arbitrarily_chosen():
    result=fixture_result();result['race']['going']='不良';result['current_state']={'official_going':'良'}
    assert '当日馬場は原本内の観測値が矛盾しています。' in n.render(result)



@pytest.mark.parametrize('no_bet',[False,True])
def test_legacy_v1_1_readback_accepts_bet_and_no_bet_without_rewriting(tmp_path,no_bet):
    result=fixture_result()
    if no_bet:
        for port in result['portfolios'].values():
            port['capital'].update(no_bet=True,required_capital=12000,unused_budget=-2000)
            port['tickets']=[]
    result=n.seal({k:v for k,v in result.items() if k!='sha256'})
    prediction=json.dumps(result,ensure_ascii=False,sort_keys=True).encode()
    body=n._render_v1_1(result)
    (tmp_path/'prediction-original.json').write_bytes(prediction)
    (tmp_path/'answer.md').write_text(body)
    manifest=n.seal({'prediction_sha256':result['sha256'],
        'answer_sha256':hashlib.sha256(body.encode()).hexdigest(),
        'files':{'prediction-original.json':hashlib.sha256(prediction).hexdigest(),
                 'answer.md':hashlib.sha256(body.encode()).hexdigest()}})
    (tmp_path/'readback-manifest.json').write_text(json.dumps(manifest))
    frozen={p.name:p.read_bytes() for p in tmp_path.iterdir()}
    actual,display=n.readback(tmp_path)
    assert actual==result and display==n.render(result)
    if no_bet:assert 'NO-BET理由' in body and 'NO-BET理由' in display
    assert frozen=={p.name:p.read_bytes() for p in tmp_path.iterdir()}
