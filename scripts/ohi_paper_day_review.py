"""Read-only OHI frozen PAPER review. No SOURCE admission or Runtime calls.

The input is a saved rendered official-page retrieval, explicitly not raw HTTP
HTML and not a signed RESULT. Original forecasts and user provisional totals
are retained separately. No result information enters prediction/selection.
"""
from __future__ import annotations
import argparse,hashlib,json,re,sys,unicodedata
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from runtime.ohi_single_race_research import readback,write,private_root
from runtime.local_result_settlement import settle_structured_research,STRUCTURED_RESEARCH_PROFILE

KINDS={'単勝':'WIN','複勝':'PLACE','枠複':'BRACKET_QUINELLA','普通馬複':'QUINELLA',
       '枠単':'BRACKET_EXACTA','馬単':'EXACTA','ワイド':'WIDE','三連複':'TRIO','三連単':'TRIFECTA'}
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def clean(s):return unicodedata.normalize('NFKC',re.sub(r'【\d+†([^】]*)】',r'\1',s)).strip()

def parse_rendered_result(document,frozen):
    text=document['text'];race=frozen['race'];rid=race['provider_race_id']
    url='https://www.nankankeiba.com/result/'+rid+'.do'
    if url not in text or document.get('race_no')!=race['race_no']:
        raise ValueError('OHI_RESULT_URL_RACE_IDENTITY')
    lines=[re.sub(r'^L\d+:\s?','',s) for s in text.splitlines() if re.match(r'^L\d+:',s)]
    day=race['race_date'].split('-');header=f"{race['race_no']}R {int(day[0])}年{int(day[1])}月{int(day[2])}日"
    if not any(header in clean(s) and '大井競馬' in s for s in lines):
        raise ValueError('OHI_RESULT_DATED_VENUE_HEADER')
    before=text.encode();runners={str(f['runner_id']):f for f in frozen['all_runners']}
    rows=[];in_finish=False;last_rank=None
    for s in lines:
        cells=[clean(c) for c in s.split('|')]
        if cells[:3]==['着','枠','馬番']:in_finish=True;continue
        if in_finish and s.startswith('####'):in_finish=False
        if in_finish and len(cells)>=15 and cells[2].isdigit():
            if cells[0].isdigit():rank=int(cells[0]);last_rank=rank;status='FINISHED'
            elif cells[0]=='同着' and last_rank is not None:rank=last_rank;status='FINISHED'
            elif cells[0] in ('中止','失格','取消','除外'):
                rank=None;status={'中止':'DNF','失格':'DQ','取消':'CANCELLED','除外':'EXCLUDED'}[cells[0]]
            else:raise ValueError('OHI_RESULT_RUNNER_STATUS_UNKNOWN')
            no=cells[2]
            if no not in runners or clean(runners[no]['name'])!=cells[3]:
                raise ValueError('OHI_RESULT_RUNNER_IDENTITY')
            rows.append({'runner_id':no,'rank':rank,'status':status,'name':cells[3],
                'provider_horse_id':runners[no]['provider_horse_id'],'body_weight':cells[6],
                'body_weight_change':cells[7],'finish_time':cells[10],'last3f':cells[12],
                'popularity':int(cells[14]) if cells[14].isdigit() else None})
    if len(rows)!=len(runners) or {r['runner_id'] for r in rows}!=set(runners):
        raise ValueError('OHI_RESULT_COMPLETE_RUNNER_UNIVERSE_REQUIRED')
    groups=[]
    for row in rows:
        if row['rank'] is None:continue
        if groups and groups[-1]['rank']==row['rank']:groups[-1]['runners'].append(row['runner_id'])
        else:groups.append({'rank':row['rank'],'runners':[row['runner_id']]})
    # Use the last responsive payout table, not both desktop + mobile copies.
    sections=[i for i,s in enumerate(lines) if s.strip()=='#### 払戻金']
    if not sections:raise ValueError('OHI_RESULT_PAYOUT_SECTION_REQUIRED')
    active=None;payouts=[];remarks=[]
    for s in lines[sections[-1]+1:]:
        cells=[clean(c) for c in s.split('|')]
        if cells[0]=='備考':remarks.append('|'.join(cells[1:]));break
        if len(cells)==4 and cells[0] in KINDS:
            active=KINDS[cells[0]];selection,amount=cells[1:3]
        elif len(cells)==3 and re.fullmatch(r'\d+(?:-\d+)*',cells[0]):
            selection,amount=cells[:2]
        else:continue
        if selection=='-' and amount=='-':continue
        if active is None or not re.fullmatch(r'\d+(?:-\d+)*',selection) or not re.fullmatch(r'[\d,]+',amount):
            raise ValueError('OHI_RESULT_PAYOUT_UNKNOWN')
        pay=int(amount.replace(',',''))
        if pay<=0:raise ValueError('OHI_RESULT_PAYOUT_NONPOSITIVE')
        payouts.append({'bet_type':active,'selection':selection.split('-'),'payout_per_100':pay})
    if not remarks or any(remarks):raise ValueError('OHI_RESULT_SPECIAL_REMARK_REQUIRES_ADAPTER')
    # Refunds need their explicit official authority; do not guess from a gap.
    if any(r['status'] in ('CANCELLED','EXCLUDED') for r in rows):
        raise ValueError('OHI_RESULT_REFUND_AUTHORITY_NOT_PARSED')
    official={'finish_rank_groups':groups,'winning_selections':{
        k:[{n:r[n] for n in ('selection','payout_per_100')} for r in payouts if r['bet_type']==k]
        for k in ('EXACTA','TRIO','TRIFECTA')},'refund_runner_ids':[],
        'nonfinishers':[{'runner_id':r['runner_id'],'status':r['status']} for r in rows if r['status'] in ('DNF','DQ')]}
    # Existing strict settlement validates complete winning combinations,
    # rank-group sequences and payout multiplicity even for a NO-BET owner.
    settle_structured_research({'tickets':[],'total_investment':0},official,
        profile=STRUCTURED_RESEARCH_PROFILE,runner_ids=list(runners))
    return {'race_no':race['race_no'],'provider_race_id':rid,'source_url':url,
        'retrieval_kind':'OFFICIAL_WEB_RENDERED_PAGE_NOT_RAW_HTTP_HTML',
        'retrieval_text_sha256':hashlib.sha256(before).hexdigest(),
        'observed_at':document['retrieved_at'],'source_ref':re.search(r'【(turn\w+)】',text)[1],
        'official_page_independently_matched':True,'formal_signed_result':False,
        'finish_groups':[g['runners'] for g in groups],'finish_rank_groups':groups,
        'runners':rows,'payouts':payouts,'official':official,
        'post_result_fields_not_prestart_evidence':True}

def settle_owner(frozen,owner,result):
    port=frozen['portfolios'][owner];tickets=port['tickets']
    settled=settle_structured_research({'tickets':tickets,'total_investment':sum(t['stake'] for t in tickets)},
        result['official'],profile=STRUCTURED_RESEARCH_PROFILE,
        runner_ids=[f['runner_id'] for f in frozen['all_runners']])
    return {**settled,'execution_status':'CALCULATED_NO_BET' if port['capital']['no_bet'] else 'CALCULATED_SELECTED_PAPER',
        'prediction_sha256':frozen['sha256'],'ticket_sha256':digest(tickets),
        'result_sha256':digest(result),'actual_purchase':False,'formal_pfs':None,
        'minimum_required_mec':port['capital'].get('minimum_required_investment'),
        'candidate_ticket_count':len(port['mec']['tickets']),'selected_ticket_count':len(tickets),
        'unused_research_cap':port['capital']['capital_limit']-settled['investment']}

def review_day(index_path,original_root,results_root):
    index=json.loads(Path(index_path).read_text());root=Path(original_root);data={};rows=[]
    for row in index['rows']:
        frozen,_=readback(root/row['revision'])
        if frozen['sha256']!=row['prediction_sha256']:raise ValueError('OHI_ORIGINAL_INDEX_SHA_MISMATCH')
        doc=json.loads((Path(results_root)/f"r{row['race_no']:02d}-official-rendered.json").read_text())
        result=parse_rendered_result(doc,frozen);data[str(row['race_no'])]=result
        rows.append({'race_no':row['race_no'],'provider_race_id':row['race_id'],
            'freeze_at':frozen['freeze_at'],'source_sha256':frozen['source_sha256'],
            'prediction_sha256':frozen['sha256'],'result_sha256':digest(result),
            'owners':{owner:settle_owner(frozen,owner,result) for owner in frozen['owners']}})
    totals={}
    for owner in ('BASELINE','OHI_FIXED_CANDIDATE'):
        stats=[r['owners'][owner] for r in rows];stake=sum(s['investment'] for s in stats);ret=sum(s['return'] for s in stats)
        cumulative=peak=drawdown=0
        for s in stats:cumulative+=s['profit_loss'];peak=max(peak,cumulative);drawdown=max(drawdown,peak-cumulative)
        largest=max(stats,key=lambda s:s['return']);kept_stake=stake-largest['investment'];kept_return=ret-largest['return']
        totals[owner]={'investment':stake,'return':ret,'profit_loss':ret-stake,'pfs':ret*100/stake if stake else None,
            'no_bet_races':sum(s['execution_status']=='CALCULATED_NO_BET' for s in stats),
            'hit_races':sum(bool(s['winning_tickets']) for s in stats),
            'hit_but_loss_races':sum(bool(s['winning_tickets']) and s['profit_loss']<0 for s in stats),
            'max_drawdown_from_zero_common_start':drawdown,'common_research_initial_bankroll':120000,
            'final_research_bankroll':120000+ret-stake,'unused_day_cap':120000-stake,
            'largest_return_race_removed_pfs':kept_return*100/kept_stake if kept_stake else None,
            'largest_race_return_share':largest['return']/ret if ret else None}
    out={'classification':'POSTRESULT_RESEARCH_REVIEW_NOT_FORMAL_NOT_FORWARD_OOS',
        'race_date':'2026-10-26','rows':rows,'results':data,'totals':totals,
        'source_results_basis':'INDEPENDENT_OFFICIAL_RENDERED_RETRIEVAL_NOT_SIGNED_RESULT',
        'formal_signed_result_count':0,'registered_oos_credit':0,'originals_changed':False}
    out['sha256']=digest(out);return out

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--index',required=True);p.add_argument('--original-root',required=True)
    p.add_argument('--results-root',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    target=private_root(a.output)
    if target.exists():raise ValueError('OHI_REVIEW_ALREADY_SAVED_REUSE_READER')
    result=review_day(a.index,a.original_root,a.results_root);write(target,result)
    print(json.dumps({'sha256':result['sha256'],'totals':result['totals']},ensure_ascii=False))
if __name__=='__main__':main()
