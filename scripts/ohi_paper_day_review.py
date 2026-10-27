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

def parse_rendered_result(document,frozen,*,prestart_observation=None):
    if (document.get('provider')!='NANKAN_OFFICIAL' or document.get('classification')!=
            'OFFICIAL_WEB_RENDERED_RETRIEVAL_NOT_RAW_HTML_NOT_SIGNED_RESULT'):
        raise ValueError('OHI_RESULT_RENDERED_PROVENANCE_REQUIRED')
    text=document['text'];race=frozen['race'];rid=race['provider_race_id']
    url='https://www.nankankeiba.com/result/'+rid+'.do'
    if url not in text or document.get('race_no')!=race['race_no']:
        raise ValueError('OHI_RESULT_URL_RACE_IDENTITY')
    lines=[re.sub(r'^L\d+:\s?','',s) for s in text.splitlines() if re.match(r'^L\d+:',s)]
    day=race['race_date'].split('-');header=f"{race['race_no']}R {int(day[0])}年{int(day[1])}月{int(day[2])}日"
    if not any(header in clean(s) and '大井競馬' in s for s in lines):
        raise ValueError('OHI_RESULT_DATED_VENUE_HEADER')
    before=text.encode();runners={str(f['runner_id']):f for f in frozen['all_runners']}
    preexcluded={}
    if prestart_observation is not None:
        obs=prestart_observation
        if (obs.get('sha256')!=frozen['source_sha256']
                or digest({k:v for k,v in obs.items() if k!='sha256'})!=obs['sha256']):
            raise ValueError('OHI_RESULT_PRESTART_SOURCE_SHA')
        for item in obs.get('changes',{}).get('items',[]):
            no=str(item.get('runner_id') or '')
            if item.get('status')=='CANCELLED' and no.isdigit() and no not in runners:
                if not item.get('provider_horse_id') or no in preexcluded:
                    raise ValueError('OHI_RESULT_PREEXCLUSION_IDENTITY')
                preexcluded[no]=item
    rows=[];extra=[];seen=set();in_finish=False;last_rank=None
    for s in lines:
        cells=[clean(c) for c in s.split('|')]
        if cells[:3]==['着','枠','馬番']:in_finish=True;continue
        if in_finish and s.startswith('####'):in_finish=False
        if in_finish and len(cells)>=15 and cells[2].isdigit():
            markers={'出走取消':'CANCELLED','競走除外':'EXCLUDED','競走中止':'DNF','失格':'DQ'}
            if cells[0].isdigit():
                if cells[11] in markers:raise ValueError('OHI_RESULT_CONTRADICTORY_RUNNER_STATUS')
                rank=int(cells[0]);last_rank=rank;status='FINISHED'
            elif cells[0]=='同着' and last_rank is not None:rank=last_rank;status='FINISHED'
            elif cells[0] in ('中止','失格','取消','除外'):
                rank=None;status={'中止':'DNF','失格':'DQ','取消':'CANCELLED','除外':'EXCLUDED'}[cells[0]]
            elif cells[0]=='-' and cells[11] in markers:
                rank=None;status=markers[cells[11]]
            else:raise ValueError('OHI_RESULT_RUNNER_STATUS_UNKNOWN')
            no=cells[2]
            if no in seen:raise ValueError('OHI_RESULT_DUPLICATE_RUNNER')
            seen.add(no)
            expected=runners.get(no) or preexcluded.get(no)
            if expected is None or clean(expected['name'])!=cells[3]:
                raise ValueError('OHI_RESULT_RUNNER_IDENTITY')
            if no not in runners:
                if status!='CANCELLED':raise ValueError('OHI_RESULT_PREEXCLUSION_STATUS_CONFLICT')
                extra.append({'runner_id':no,'name':cells[3],'status':status,
                    'provider_horse_id':expected['provider_horse_id'],
                    'basis':'FROZEN_PRESTART_DATED_OFFICIAL_CHANGE_NOT_IN_BETTING_UNIVERSE'})
                continue
            rows.append({'runner_id':no,'rank':rank,'status':status,'name':cells[3],
                'provider_horse_id':runners[no]['provider_horse_id'],'body_weight':cells[6],
                'body_weight_change':cells[7],'finish_time':cells[10],'last3f':cells[12],
                'popularity':int(cells[14]) if cells[14].isdigit() else None})
    if len(rows)!=len(runners) or {r['runner_id'] for r in rows}!=set(runners):
        raise ValueError('OHI_RESULT_COMPLETE_RUNNER_UNIVERSE_REQUIRED')
    if {r['runner_id'] for r in extra}!=set(preexcluded):
        raise ValueError('OHI_RESULT_PREEXCLUDED_RUNNER_STATE_REQUIRED')
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
    if not remarks:raise ValueError('OHI_RESULT_REMARK_SECTION_REQUIRED')
    refund_ids=[]
    for remark in remarks:
        if not remark:continue
        match=re.fullmatch(r'返還:\s*(\d+(?:[,、]\d+)*)号馬',remark)
        if not match:raise ValueError('OHI_RESULT_SPECIAL_REMARK_REQUIRES_ADAPTER')
        refund_ids.extend(re.split(r'[,、]',match[1]))
    if len(set(refund_ids))!=len(refund_ids):raise ValueError('OHI_RESULT_DUPLICATE_REFUND_RUNNER')
    excluded={r['runner_id'] for r in rows if r['status'] in ('CANCELLED','EXCLUDED')}
    if set(refund_ids)-set(preexcluded)!=excluded:
        raise ValueError('OHI_RESULT_REFUND_AUTHORITY_NOT_PARSED')
    official={'finish_rank_groups':groups,'winning_selections':{
        k:[{n:r[n] for n in ('selection','payout_per_100')} for r in payouts if r['bet_type']==k]
        for k in ('EXACTA','TRIO','TRIFECTA')},'refund_runner_ids':sorted(excluded,key=int),
        'nonfinishers':[{'runner_id':r['runner_id'],'status':r['status']} for r in rows if r['status'] in ('DNF','DQ')]}
    if excluded:
        official['refund_authority']=url+' | '+'; '.join(remarks)
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
        'runners':rows,'prestart_excluded_outside_frozen_universe':extra,
        'official_observed_state_count':len(rows)+len(extra),
        'frozen_runner_count':len(runners),'payouts':payouts,'official':official,
        'official_refund_remarks':remarks,
        'corner_passages':{clean(s.split('|')[0]):clean(s.split('|')[1]) for s in lines
            if len(s.split('|'))==2 and re.fullmatch(r'[1234]角',clean(s.split('|')[0]))},
        'result_header_post_time':next((re.search(r'発走時刻\s*(\d{1,2}:\d{2})',clean(s))[1]
            for s in lines if header in clean(s) and re.search(r'発走時刻\s*(\d{1,2}:\d{2})',clean(s))),None),
        'actual_off_time_independently_observed':False,
        'post_result_fields_not_prestart_evidence':True}

def settle_owner(frozen,owner,result):
    port=frozen['portfolios'][owner];tickets=port['tickets']
    settled=settle_structured_research({'tickets':tickets,'total_investment':sum(t['stake'] for t in tickets)},
        result['official'],profile=STRUCTURED_RESEARCH_PROFILE,
        runner_ids=[f['runner_id'] for f in frozen['all_runners']])
    return {**settled,'execution_status':'CALCULATED_NO_BET' if port['capital']['no_bet'] else 'CALCULATED_SELECTED_PAPER',
        'prediction_sha256':frozen['sha256'],'ticket_sha256':digest(tickets),
        'result_sha256':digest(result),'actual_purchase':False,'formal_pfs':None,
        'minimum_required_mec':port['capital']['required_capital'],
        'candidate_ticket_count':len(port['mec']['tickets']),'selected_ticket_count':len(tickets),
        'unused_research_cap':port['capital']['capital_limit']-settled['investment']}

def review_day(index_path,original_root,results_root):
    index=json.loads(Path(index_path).read_text());root=Path(original_root);data={};rows=[]
    seen={key:set() for key in ('race_no','race_id','revision','prediction_sha256')}
    for row in index['rows']:
        if type(row.get('race_no')) is not int or not 1<=row['race_no']<=12:
            raise ValueError('OHI_REVIEW_INDEX_RACE_NUMBER')
        for key in seen:
            value=row.get(key)
            if not value or value in seen[key]:raise ValueError('OHI_REVIEW_INDEX_DUPLICATE_OR_MISSING:'+key)
            seen[key].add(value)
    for row in index['rows']:
        frozen,_=readback(root/row['revision'])
        if (frozen['race']['race_date']!=index['race_date']
                or frozen['race']['race_no']!=row['race_no']
                or frozen['race']['provider_race_id']!=row['race_id']):
            raise ValueError('OHI_REVIEW_INDEX_RACE_IDENTITY')
        if frozen['sha256']!=row['prediction_sha256']:raise ValueError('OHI_ORIGINAL_INDEX_SHA_MISMATCH')
        doc=json.loads((Path(results_root)/f"r{row['race_no']:02d}-official-rendered.json").read_text())
        observation_path=root/row['revision']/'observation.json'
        observation=json.loads(observation_path.read_text()) if observation_path.exists() else None
        result=parse_rendered_result(doc,frozen,prestart_observation=observation);data[str(row['race_no'])]=result
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
        'race_date':index['race_date'],'rows':rows,'results':data,'totals':totals,
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
