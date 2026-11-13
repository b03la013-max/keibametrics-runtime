"""Offline real-input Exact PAPER entry, one Owner, immutable new revision.

Never runs KRS, qualifies a provider/Active set, grants Production scope,
sends a message, or converts a local save into recipient acknowledgement.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import json
import os

from runtime import local_fnb_saved_paper_tickets as saved
from runtime import local_fnb_exact_orientation_research as exact

REVISION='R16-EXACT-SCENARIO-ORDINAL-PAPER'


def read_previous(folder):
    folder=Path(folder).resolve()
    receipt=json.loads((folder/'recovery_receipt.json').read_bytes())
    for name,proof in receipt['files'].items():
        raw=(folder/name).read_bytes()
        exact.require({'bytes':len(raw),'sha256':exact.sha(raw)}==proof,'PREVIOUS_PAPER_SHA_MISMATCH:'+name)
    previous=json.loads((folder/'recovered_paper_tickets.json').read_bytes())
    exact.require(previous['owner_count']==1 and not previous['independent_BC']
        and not previous['formal_selected_ticket'] and not previous['recipient_ack_verified'],
        'PREVIOUS_OWNER_OR_FORMAL_CLAIM_INVALID')
    return previous,json.loads((folder/'saved_inputs_inventory.json').read_bytes()),receipt


def render(inputs, previous, output):
    p=inputs['prediction'];r=output
    lines=['# 船橋｜Exact Orientation研究・全馬・全選択券面',
        '', '分類：'+r['classification'],
        'R16は新しい非Productionの着順方向選択仮説です。正式推薦・最終Active・独立B/C・実購入・登録OOS・本人ACKは成立していません。',
        '旧S1/S2は変更していません。末尾に旧R15本文を、その当時のRevision・分類とともに収録しています。',
        'KRSのScenario周辺出現率の大小を比較します。共同確率・実勝率・EV・予測精度の検証結果ではありません。',
        '過去のWorld/6 Stageは既存のProxyです。現在の戦術意図・実測加速・因果的な競合解消はUNKNOWNです。',
        '既存の古いSOURCE原本を再利用する選択研究であり、最新の天候・馬場・当日変更・最終Activeを確認した予測ではありません。',
        '', '|項目|値|','|---|---|']
    for k in ('race_id','revision','scheduled_post_at','prediction_cutoff','source_fetched_at',
              'raw_sha256','source_snapshot_sha256','owner_id','model_sha256','static_freeze_at',
              'static_prediction_sha256','KRS_requested_input_sha256','KRS_execution_input_sha256','KRS_output_sha256',
              'selection_profile','selection_profile_sha256','selection_module_sha256','rule_frozen_at','selected_at'):
        lines.append('|'+k+'|'+str(r[k])+'|')
    lines+=['|掲載・計算対象集合（最終Active未認証）|'+','.join(p['active_runners'])+'|',
        '', '## Exact Orientation判断',
        f"全{r['review']['evaluated_slots']}スロット・有効な異なる3頭の全{r['review']['distinct_ordered_triples']}方向を評価。Exact採用{r['review']['material_exact_count']}件。",
        '各3頭集合の全6方向比較、UNKNOWN・不採用理由、World・全5 Scenario Evidenceはexact_orientation_review.jsonに全件保存。',
        '採用条件：既知の元W Front・Head-local P2 Front・Pair-conditioned Third Front、World仮説の共存、全5 ScenarioでHeadのW優位・SecondのP2優位、各割当Role出現あり。',
        '全5 Scenarioの周辺出現率が整合しても、その三頭の同時成立や実戦的な優位を立証したことにはなりません。',
        '本線回収可能性：UNKNOWN。適格な発走前オッズSnapshotは使用していません。',
        '', '|1着→2着→3着|Terminal|理由|', '|---|---|---|']
    for row in r['review']['ledger']:
        if row['terminal']=='EXACT_PURCHASE':lines.append('|'+row['path_id']+'|'+row['terminal']+'|'+row['reason']+'|')
    if not r['review']['exact_selected']:lines+=['|該当なし|NO_EXACT_ORIENTATION_PASSES_FROZEN_RULE|UNKNOWN・Front条件・Scenario比較等をLedgerで分離|']
    lines+=['', '## R16研究案の3券種（各方式は独立試算）',
        '馬単・三連複はS2の全票を保持。三連単だけが新Exact仮説です。三方式やS1/S2を合算した購入案ではありません。']
    for name,method in r['portfolio']['methods'].items():
        lines+=['', '### '+{'EXACTA':'馬単','TRIO':'三連複','TRIFECTA':'三連単'}[name],
            f"{method['point_count']}点・各100円／PAPER必要額・最小MEC {method['required_MEC']:,}円／独立予算上限 {method['capital_limit']:,}円。",
            f"仮に全票を選んだ場合の未使用 {method['hypothetical_unused']:,}円／予算超過 {method['budget_shortfall']:,}円。",
            f"既存Capital判定 {method['capital_policy']['decision']}／上限内のPAPER選択可能額 {method['within_existing_cap_eligible_paper_amount']:,}円／資金非選択対象 {method['capital_nonselected_full_paper_amount']:,}円。",
            f"正式選択額0円・実購入0円・現金未使用 {method['cash_unused']:,}円。意味的被覆の無断圧縮なし。",
            '結論：'+(method['zero_reason']+'。この券種の計算済み0点でありRace全体NO-BETではありません。' if not method['tickets'] else
                '非ゼロPAPER券面計算済み。正式推薦ではありません。'),
            'Ticket SHA：'+method['ticket_sha256'],'Tree SHA：'+method['tree_sha256'],
            '', '```text',method['canonical_tree'],'```']
    lines+=['', '## Exact券面とMEC Coverageの対応', '|組番|Stake|Material Exact ID|MEC Coverage ID|Canonical Ticket ID|','|---|---:|---|---|---|']
    for t in r['portfolio']['methods']['TRIFECTA']['tickets']:
        path='>'.join(map(str,t['selection']))
        lines.append('|'+path+'|'+str(t['stake'])+'|'+exact.PROFILE+':'+path+'|EXACT_THIRD:'+path+'|'+t['canonical_ticket_id']+'|')
    lines+=['','## 保存・送達の区分',
        'この新Revisionの全券面・Strict MEC実Request/Plan・全判断は同梱JSONに保存。実バイト照合は検証Receiptで確認してください。',
        '保存・読戻しは本人受領ACKではありません。正式FINAL・自然起動・発走前本人Delivery・正式PFSはいずれも未成立です。',
        '', '## 継承したR15原本（以下の分類・FreezeはR15当時の値）','']
    # Keep full all-horse29/ranks/scenario summary and full original S1/S2 trees.
    return '\n'.join(lines)+'\n'+r.pop('_previous_complete_body')


def recover(source_folder, previous_folder, destination, *, freeze, authorization_ref, evaluated_at=None):
    exact.require(not any(os.environ.get(k,'').lower() not in ('','false','0') for k in ('CI','GITHUB_ACTIONS')),
        'REAL_PRIVATE_ORIGINALS_PUBLIC_CI_FORBIDDEN')
    exact.require(bool(authorization_ref),'CURRENT_EXACT_RESEARCH_AUTHORIZATION_REQUIRED')
    evaluated_at=evaluated_at or datetime.now(timezone.utc).isoformat()
    previous,inventory,old_receipt=read_previous(previous_folder)
    inputs=saved.verify_saved_run(source_folder,inventory,observed_at=evaluated_at)
    p=inputs['prediction'];s2=previous['studies']['S2']['paper_result']
    exact.require(previous['race_id']==p['race_id'] and previous['static_prediction_sha256']==p['sha256'],
        'PREVIOUS_PAPER_WRONG_PREDICTION')
    review=exact.evaluate(p,inputs['context'],inputs['krs_output'],s2,freeze=freeze,evaluated_at=evaluated_at)
    portfolio=exact.construct(p,inputs['context'],inputs['krs_output'],review,s2,freeze=freeze,evaluated_at=evaluated_at)
    post=exact.stamp(inputs['request']['scheduled_post_at'])
    cutoff=post-__import__('datetime').timedelta(seconds=300)
    expired=exact.stamp(evaluated_at)>=cutoff
    out={'profile':REVISION,'race_id':p['race_id'],'revision':REVISION,
        'classification':'POSTCUTOFF_DIAGNOSTIC_PAPER_NOT_OOS' if expired else
            'PRE_CUTOFF_UNQUALIFIED_LISTED_RUNNER_EXACT_RESEARCH_PAPER_NOT_OOS',
        'scheduled_post_at':post.isoformat(),'prediction_cutoff':cutoff.isoformat(),
        'source_fetched_at':previous['source_fetched_at'],'raw_sha256':previous['raw_sha256'],
        'source_snapshot_sha256':p['source_snapshot_sha256'],'owner_id':p['model_id'],
        'model_sha256':p['model_code_sha256'],'static_freeze_at':p['freeze_at'],
        'static_prediction_sha256':p['sha256'],'selection_profile':exact.PROFILE,
        'selection_profile_sha256':review['profile_sha256'],'selection_module_sha256':exact.MODULE_SHA,
        'rule_frozen_at':freeze['frozen_at'],'selected_at':evaluated_at,
        **{'KRS_'+n+'_sha256':exact.sha(inputs['raw']['krs/'+path]) for n,path in
           [('requested_input','requested_input.json'),('execution_input','execution_input.json'),('output','execution_output.json')]},
        'review':review,'portfolio':portfolio,'new_KRS':0,'owner_count':1,'independent_BC':False,
        'formal_SOURCE_Active':False,'formal_owner_selection':False,'formal_final':False,
        'recipient_ACK':False,'natural_delivery':False,'computed_whole_race_NO_BET':False,'actual_purchase':0,
        'registered_OOS_increment':0,'formal_PFS':None,'core_hit_recoverability':'UNKNOWN_NO_QUALIFIED_PRESTART_ODDS',
        'entry_code_sha256':exact.sha(Path(__file__).read_bytes()),'authorization_ref':authorization_ref,
        'previous_receipt_sha256':exact.sha((Path(previous_folder)/'recovery_receipt.json').read_bytes())}
    out['_previous_complete_body']=(Path(previous_folder)/'COMPLETE_PREDICTION_AND_ALL_TICKETS.md').read_text()
    body=render(inputs,previous,out)
    target=saved.original._private_root(Path(destination).resolve()/p['race_id'])
    files={'exact_orientation_review.json':exact.encoded(review),'exact_paper_portfolio.json':exact.encoded(out),
        'COMPLETE_PREDICTION_AND_ALL_TICKETS.md':body.encode(),
        'saved_inputs_inventory.json':exact.encoded(inventory),'previous_R15_receipt.json':exact.encoded(old_receipt),
        'POLICY_FREEZE.json':exact.encoded(freeze)}
    proofs={}
    for name,raw in files.items():
        saved.original._immutable(target/name,raw)
        exact.require((target/name).read_bytes()==raw,'PRIVATE_LOCAL_READBACK_MISMATCH')
        proofs[name]={'bytes':len(raw),'sha256':exact.sha(raw)}
    receipt={'profile':REVISION+'-BYTE-READBACK','race_id':p['race_id'],'revision':REVISION,
        'classification':out['classification'],'files':proofs,'local_readback':True,'new_KRS':0,
        'source_inputs_SHA_verified':True,'old_S1_S2_originals_modified':False,
        'formal_final':False,'recipient_ACK':False,'natural_delivery':False,'registered_OOS_increment':0}
    saved.original._immutable(target/'exact_recovery_receipt.json',exact.encoded(receipt))
    return out,receipt


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-folder',required=True)
    parser.add_argument('--previous-paper-folder',required=True)
    parser.add_argument('--policy-freeze',required=True)
    parser.add_argument('--destination',required=True)
    parser.add_argument('--authorization-ref',required=True)
    a=parser.parse_args(argv)
    out,receipt=recover(a.source_folder,a.previous_paper_folder,a.destination,
        freeze=json.loads(Path(a.policy_freeze).read_bytes()),authorization_ref=a.authorization_ref)
    print(json.dumps({'race_id':out['race_id'],'classification':out['classification'],
        'Exact_selected':out['review']['exact_selected'],
        'methods':{k:{'points':v['point_count'],'required_MEC':v['required_MEC'],
            'shortfall':v['budget_shortfall']} for k,v in out['portfolio']['methods'].items()},
        'local_readback':receipt['local_readback'],'new_KRS':0,'formal_final':False,'recipient_ACK':False}))


if __name__=='__main__':main()
