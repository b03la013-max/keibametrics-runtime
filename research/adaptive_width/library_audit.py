"""Inventory and parse Library structured history without promoting fixtures."""
import argparse, collections, csv, hashlib, io, json, pathlib, re, zipfile

def audit(root, inventory):
    items=inventory;native=[];archive=[];legacy=[];seen=set();errors=[]
    def inspect(name,data,origin):
        sha=hashlib.sha256(data).hexdigest()
        if sha in seen:return
        seen.add(sha)
        rec={'path':name,'origin':origin,'sha256':sha,'bytes':len(data)}
        if name.lower().endswith('.csv'):
            try:
                rows=list(csv.DictReader(io.StringIO(data.decode('utf-8-sig'))))
                rec['rows']=len(rows);rec['columns']=list(rows[0]) if rows else []
                if rows and any(any(w in c.lower() for w in ['result','payout','return','pfs']) for c in rows[0]):
                    rec['history_class']='DECLARED_LEGACY_OR_RECON_NOT_SIGNED_FORWARD'
                    rec['records']=rows;legacy.append(rec)
            except Exception as e:errors.append({'path':name,'error':type(e).__name__})
        elif name.lower().endswith('.json'):
            try:
                obj=json.loads(data)
                rec['root_keys']=list(obj)[:40] if isinstance(obj,dict) else ['ARRAY']
                # A date or synthetic race_id is not proof of an actual forecast.
                text=json.dumps(obj,ensure_ascii=False).lower()
                rec['fixture_or_template_marker']=any(x in name.lower() for x in ['fixture','template','synthetic','selftest','adversarial'])
                rec['prediction_result_marker']=any(x in text for x in ['actual_top3','finish_order','payout_per_100','winning_tickets','frozen_recommendation'])
            except Exception as e:errors.append({'path':name,'error':type(e).__name__})
        (archive if origin=='archive_member' else native).append(rec)
    zips=0;duplicate_zips=0;zip_seen=set();members=0
    for path in sorted(root.rglob('*')):
        if not path.is_file():continue
        rel=str(path.relative_to(root))
        if path.suffix.lower()=='.zip':
            data=path.read_bytes();sha=hashlib.sha256(data).hexdigest()
            if sha in zip_seen:duplicate_zips+=1;continue
            zip_seen.add(sha);zips+=1
            try:
                with zipfile.ZipFile(io.BytesIO(data)) as z:
                    for info in z.infolist():
                        if info.filename.lower().endswith(('.json','.csv')):
                            members+=1
                            if info.file_size>25_000_000:errors.append({'path':rel+'!'+info.filename,'error':'MEMBER_TOO_LARGE'});continue
                            inspect(rel+'!'+info.filename,z.read(info), 'archive_member')
            except Exception as e:errors.append({'path':rel,'error':type(e).__name__})
        elif path.suffix.lower() in {'.json','.csv'}:inspect(rel,path.read_bytes(),'native')
    # Exact same CSV bytes in a ZIP/native export count once because of seen.
    return {'status':'LIBRARY_HISTORY_INVENTORY_NOT_A_PREDICTION_ACCURACY_DATASET',
            'inventory_items':len(items),'metadata_extension_counts':dict(collections.Counter(pathlib.Path(x['name']).suffix.lower() for x in items if x.get('kind')=='file')),
            'unique_zip_archives_read':zips,'duplicate_zip_copies':duplicate_zips,
            'structured_archive_members_read':members,'unique_structured_contents':len(seen),
            'native_structured_inventory':native,'archive_structured_inventory':archive,
            'legacy_declared_tables':legacy,'errors':errors,
            'exclusion_policy':'Fixtures/templates/specifications/source Web archives are not independent pre-result predictions. Legacy or RECON tables lack a canonical ticket+FINAL time binding and are descriptive only.'}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);ap.add_argument('--inventory',required=True,nargs='+');ap.add_argument('--output',required=True);args=ap.parse_args()
    inv=[]
    for path in args.inventory:inv.extend(json.loads(pathlib.Path(path).read_text()))
    report=audit(pathlib.Path(args.root),inv);pathlib.Path(args.output).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['native_structured_inventory','archive_structured_inventory','legacy_declared_tables']}|{'legacy_tables':[(x['path'],x['rows']) for x in report['legacy_declared_tables']]},ensure_ascii=False))
