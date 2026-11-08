"""Materialize the byte-verified audit payload, without executing its content."""
import hashlib,json,tarfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BUNDLE=ROOT/'evidence/jra_day_review_20261017/payload.tar.gz'
MANIFEST=ROOT/'evidence/jra_day_review_20261017/payload_manifest.json'

def unpack(root=ROOT):
    root=Path(root).resolve();manifest=json.loads(MANIFEST.read_text())
    if hashlib.sha256(BUNDLE.read_bytes()).hexdigest()!=manifest['archive_sha256']:
        raise ValueError('AUDIT_ARCHIVE_HASH_MISMATCH')
    expected={x['path']:x for x in manifest['files']}
    with tarfile.open(BUNDLE,'r:gz') as archive:
        if {m.name for m in archive.getmembers()}!=set(expected):raise ValueError('AUDIT_ARCHIVE_MEMBERS_MISMATCH')
        for member in archive.getmembers():
            path=(root/member.name).resolve()
            if not member.isfile() or not path.is_relative_to(root):raise ValueError('UNSAFE_AUDIT_MEMBER')
            raw=archive.extractfile(member).read()
            if hashlib.sha256(raw).hexdigest()!=expected[member.name]['sha256']:raise ValueError('AUDIT_MEMBER_HASH_MISMATCH')
            if path.exists() and path.read_bytes()!=raw:raise ValueError('EXISTING_AUDIT_FILE_CONFLICT:'+member.name)
            path.parent.mkdir(parents=True,exist_ok=True)
            if not path.exists():path.write_bytes(raw)
    return len(expected)

if __name__=='__main__':print('Verified audit payload files:',unpack())
