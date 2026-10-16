"""Private browser-observed Keibabook facts. No login secrets or signature creation.

A digest proves content integrity, not signer identity or Production approval.
Historical captures are explicitly Replay; raw paid data stays outside Git.
"""
from datetime import date, datetime
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup

PROFILE='JRA-KEIBABOOK-PRIVATE-FACT-INTAKE-v1'


def text(node):
    return node.get_text(' ',strip=True) if node else ''


def norm(value):
    return re.sub(r'\s+','',value or '').replace('(地)','').replace('（地）','')


def parse_ability(raw, race_date):
    soup=BeautifulSoup(raw,'html.parser'); out=[]
    for row in soup.select('tr'):
        number=row.find('td',class_='umaban',recursive=False)
        namecell=row.find('td',class_='bamei',recursive=False)
        if number is None or namecell is None: continue
        number=text(number)
        if not re.fullmatch(r'\d{1,2}',number):raise ValueError('BOOK_RUNNER_NUMBER_INVALID')
        paragraphs=namecell.find_all('p',recursive=False)
        if len(paragraphs)<4:raise ValueError('BOOK_ABILITY_SCHEMA_INCOMPLETE')
        link=paragraphs[1].find('a')
        if link is None:raise ValueError('BOOK_RUNNER_NAME_REQUIRED')
        runs=[]
        for cell in row.find_all('td',class_='zensou',recursive=False):
            ps=cell.select('div.inner > p') or cell.find_all('p',recursive=False)
            if len(ps)!=4:continue
            a=ps[0].find('a',href=re.compile(r'/cyuou/seiseki/\d{12}$'))
            dm=re.search(r'(\d{1,2})[･・](\d{1,2})',text(ps[0]))
            sm=re.search(r'\bS(\d+(?:\.\d+)?)\b',text(ps[2]))
            cm=re.search(r'(\d{3,4})(芝|ダ)',text(ps[1]))
            if not (a and dm and cm):continue
            year=int(a['href'].split('/')[-1][:4])
            day=date(year,int(dm[1]),int(dm[2]))
            if day>=date.fromisoformat(race_date):raise ValueError('BOOK_TARGET_OR_FUTURE_RESULT_FORBIDDEN')
            runs.append({'date':day.isoformat(),'distance_m':int(cm[1]),'surface':cm[2],
                         'speed_index':float(sm[1]) if sm else None,
                         'result_url':'https://s.keibabook.co.jp'+a['href']})
        out.append({'runner_id':number,'name':text(link),'sire':text(paragraphs[0].find('a')),
                    'dam':text(paragraphs[2].find('span')),'damsire':text(paragraphs[3].find('span')),
                    'prior_runs':sorted(runs,key=lambda r:r['date'],reverse=True)})
    if not out:raise ValueError('BOOK_ABILITY_NO_RUNNERS')
    return out


def parse_workout(raw):
    soup=BeautifulSoup(raw,'html.parser');out=[]
    for row in soup.select('tr'):
        namecell=row.find('td',class_='kbamei',recursive=False)
        if namecell is None:continue
        number=text(row.find('td',class_='umaban',recursive=False))
        if not re.fullmatch(r'\d{1,2}',number):raise ValueError('BOOK_WORKOUT_NUMBER_INVALID')
        details=row.find_next_sibling('tr');work=[]
        if details:
            for dl in details.select('dl.dl-table'):
                ts=dl.find_all('dt',recursive=False)
                if len(ts)!=3:continue
                table=dl.find_next_sibling('table')
                if table is None:continue
                laps=[float(text(c)) for c in table.find_all('td') if re.fullmatch(r'\d{1,3}\.\d+',text(c))]
                work.append({'date_course':text(ts[1]),'previous_workout':text(ts[0])=='(前回)',
                             'gait':text(ts[2]),'final1f':laps[-1] if laps else None})
        out.append({'runner_id':number,'name':text(namecell),'assessment':text(row.find('td',class_='tanpyo',recursive=False)),
                    'observed_workouts':work})
    if not out:raise ValueError('BOOK_WORKOUT_NO_RUNNERS')
    return out


def parse_stable(raw):
    soup=BeautifulSoup(raw,'html.parser');out=[]
    for row in soup.select('tr'):
        no=row.find('td',class_='umaban',recursive=False)
        if no is None:continue
        link=row.find('a',href=re.compile(r'/db/uma/\d+$'))
        if link is None:continue
        detail=row.find_next_sibling('tr')
        cell=detail.find('td',class_='danwa') if detail else None
        if cell is None:raise ValueError('BOOK_STABLE_COMMENT_REQUIRED')
        out.append({'runner_id':text(no),'name':text(link),'trainer_comment':text(cell)})
    if not out:raise ValueError('BOOK_STABLE_NO_RUNNERS')
    return out


def validate_universe(rows, official):
    expected={str(r.get('runner_id') or r.get('horse_no')):norm(r.get('name')) for r in official}
    actual={r['runner_id']:norm(r['name']) for r in rows}
    if len(actual)!=len(rows) or len(expected)!=len(official) or actual!=expected:
        raise ValueError('BOOK_OFFICIAL_RUNNER_UNIVERSE_MISMATCH')
    return True


def ingest(manifest_path, *, official, race_date, book_race_id, prediction_cutoff):
    if not re.fullmatch(r'\d{12}', book_race_id) or book_race_id[:4] != race_date[:4]:
        raise ValueError('BOOK_RACE_ID_INVALID')
    path=Path(manifest_path); manifest=json.loads(path.read_text()); result={}; sources=[]
    cutoff=datetime.fromisoformat(prediction_cutoff.replace('Z','+00:00'))
    if cutoff.tzinfo is None:raise ValueError('BOOK_CUTOFF_TIMEZONE_REQUIRED')
    for kind,parser in [('ability',parse_ability),('workout',parse_workout),('stable',parse_stable)]:
        matches=[m for m in manifest if book_race_id in m['url'] and ('nouryoku_html_detail' if kind=='ability' else 'cyokyo' if kind=='workout' else 'danwa') in m['url']]
        if len(matches)!=1:raise ValueError('BOOK_CAPTURE_NOT_UNIQUE:'+kind)
        m=matches[0];url=urlparse(m['url'])
        if url.scheme!='https' or url.hostname!='s.keibabook.co.jp':raise ValueError('BOOK_SOURCE_HOST_INVALID')
        expected_path = '/cyuou/' + ('nouryoku_html_detail/' + book_race_id + '.html' if kind == 'ability' else ('cyokyo' if kind == 'workout' else 'danwa') + '/0/' + book_race_id)
        if url.path != expected_path or url.query or url.fragment:
            raise ValueError('BOOK_RACE_URL_MISMATCH')
        file=(path.parent/m['file']).resolve()
        if not file.is_relative_to(path.parent.resolve()):raise ValueError('BOOK_PRIVATE_PATH_ESCAPE')
        raw=file.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=m['sha256']:raise ValueError('BOOK_RAW_HASH_MISMATCH')
        captured=datetime.fromisoformat(m['captured_at'].replace('Z','+00:00'))
        if captured.tzinfo is None:raise ValueError('BOOK_CAPTURE_TIMEZONE_REQUIRED')
        if captured>datetime.now(captured.tzinfo):raise ValueError('BOOK_FUTURE_CAPTURE_FORBIDDEN')
        rows=parser(raw,race_date) if kind=='ability' else parser(raw)
        validate_universe(rows,official);result[kind]=rows
        sources.append({'kind':kind,'url':m['url'],'captured_at':m['captured_at'],'raw_sha256':m['sha256'],
                        'cutoff_relation':'PRE_CUTOFF' if captured<cutoff else 'POST_CUTOFF'})
    return {'profile':PROFILE,'provider':'KEIBABOOK_SMART_PREMIUM','race_date':race_date,
            'book_race_id':book_race_id,'runner_count':len(official),'official_universe_matched':True,
            'temporal_mode':'REPLAY' if any(s['cutoff_relation']=='POST_CUTOFF' for s in sources) else 'PRE_RACE_FACT_INTAKE',
            'sources':sources,'facts':result,'production_authority':False,'signed_source':False,
            'signed_final_issued':False,'oos_increment':0,
            'required_next_step':'Authentic Signed SOURCE and registered evaluator/provider conformance before Production use'}


def parse_pedigree(raw):
    """Keep observed population counts; zero starts means unknown, never zero fit."""
    soup = BeautifulSoup(raw, 'html.parser')
    populations = []
    for table in soup.select('table'):
        headers = [text(c) for c in table.select('th')]
        if not all(h in headers for h in ('1着', '2着', '3着', '着外')):
            continue
        heading = table.find_previous('p')
        for row in table.select('tr'):
            cells = row.find_all('td', recursive=False)
            values = [text(c) for c in cells]
            if len(values) != 8:
                continue
            if not all(re.fullmatch(r'\d+', v) for v in values[1:5]):
                raise ValueError('BOOK_PEDIGREE_COUNTS_INVALID')
            counts = list(map(int, values[1:5]))
            starts = sum(counts)
            published = list(map(float, values[5:8]))
            rates = [counts[0] / starts, sum(counts[:2]) / starts,
                     sum(counts[:3]) / starts] if starts else [None] * 3
            if starts and any(abs(a-b) > .001 for a,b in zip(rates,published)):
                raise ValueError('BOOK_PEDIGREE_RATE_MISMATCH')
            populations.append({'section':text(heading),'condition':values[0],
                                'counts':counts,'starts':starts,'rates':rates})
    if not populations:
        raise ValueError('BOOK_PEDIGREE_POPULATION_REQUIRED')
    return populations


def main():
    import argparse
    import os
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--official-runners', required=True,
                        help='JSON array of official runner_id/name records')
    parser.add_argument('--race-date', required=True)
    parser.add_argument('--book-race-id', required=True)
    parser.add_argument('--prediction-cutoff', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    result = ingest(args.manifest, official=json.loads(Path(args.official_runners).read_text()),
                    race_date=args.race_date, book_race_id=args.book_race_id,
                    prediction_cutoff=args.prediction_cutoff)
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, 'w') as stream:
        os.fchmod(stream.fileno(), 0o600)
        json.dump(result, stream, ensure_ascii=False, indent=2)
    print(json.dumps({'runner_count':result['runner_count'],
                      'temporal_mode':result['temporal_mode'], 'signed_final_issued':False}))


if __name__ == '__main__':
    main()
