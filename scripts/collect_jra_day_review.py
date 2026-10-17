"""Read-only official result collection. No prediction or runtime activation."""
from __future__ import annotations
import argparse, hashlib, json, re, sys, time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'runtime'), str(ROOT / 'runtime/jra_source_runtime')]
from jra_pedigree_harvest import _Client, _calendar
from bs4 import BeautifulSoup

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def collect(day):
    out = ROOT / 'evidence' / ('jra_day_review_' + day.replace('-', '')) / 'official'
    out.mkdir(parents=True, exist_ok=True)
    client = _Client(deadline_monotonic=time.monotonic() + 600)
    calendar = client.get(_calendar(day))
    (out / 'calendar.html').write_text(calendar)
    tokens = re.findall(r"doAction\('/JRADB/accessS\.html'\s*,\s*'([^']+)'\)", calendar)
    entry = next(t for t in tokens if t.startswith('pw01sli00'))
    index = client.post('/JRADB/accessS.html', entry)
    (out / 'result_index.html').write_text(index)
    daytokens = sorted(set(re.findall(r'pw01srl00\d{10}' + day.replace('-', '') + r'/[0-9A-Fa-f]{2}', index)))
    inventory = {'collected_at': datetime.now(timezone.utc).isoformat(), 'date': day,
                 'source_authority': 'JRA_OFFICIAL', 'days': [], 'races': [], 'errors': [],
                 'hash_basis': 'decoded HTML saved as UTF-8; not original wire bytes'}
    save(out / 'collection.json', inventory)
    for token in daytokens:
        try:
            listing = client.post('/JRADB/accessS.html', token)
            key = token[9:19]
            (out / (key + '_day.html')).write_text(listing)
            soup = BeautifulSoup(listing, 'html.parser')
            inventory['days'].append({'token': token, 'meeting_key': key, 'text': soup.get_text(' ', strip=True)[:2000]})
            racetokens = sorted(set(re.findall(r'pw01sde01\d{12}' + day.replace('-', '') + r'/[0-9A-Fa-f]{2}', listing)))
            for rt in racetokens:
                racekey = rt[9:21]
                p = out / (racekey + '.html')
                try:
                    html = p.read_text() if p.exists() else client.post('/JRADB/accessS.html', rt)
                    if '着順' not in html or '払戻' not in html:
                        raise ValueError('OFFICIAL_RESULT_NOT_PUBLISHED_OR_WRONG_RESPONSE')
                    p.write_text(html)
                    record = {'race_key': racekey, 'token': rt, 'path': str(p.relative_to(ROOT)),
                              'url': 'https://www.jra.go.jp/JRADB/accessS.html',
                              'method': 'POST', 'captured_at': datetime.now(timezone.utc).isoformat(),
                              'decoded_utf8_sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                    inventory['races'].append(record)
                    print(racekey, 'OK', flush=True)
                except Exception as exc:
                    inventory['errors'].append({'race_key': racekey, 'class': type(exc).__name__, 'error': str(exc)})
                    print(racekey, str(exc), flush=True)
                save(out / 'collection.json', inventory)
        except Exception as exc:
            inventory['errors'].append({'day_token': token, 'class': type(exc).__name__, 'error': str(exc)})
            save(out / 'collection.json', inventory)
    return inventory

if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--date', default='2026-10-17')
    a = p.parse_args(); collect(a.date)
