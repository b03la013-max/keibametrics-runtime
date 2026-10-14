"""Test-only execution of hash-verified historical code; never update old plan."""
import hashlib,importlib.util,json,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def restore_code(target):
 target=Path(target);base=ROOT/'evidence/local_aki_columns_20261012';manifest=json.loads((base/'forward_R2_frozen_implementation_manifest.json').read_text());archive=base/'forward_R2_frozen_implementation.tar.gz'
 assert hashlib.sha256(archive.read_bytes()).hexdigest()==manifest['archive_sha256']
 with tarfile.open(archive,'r:gz') as t:
  for member in t:
   assert member.isfile() and member.name in manifest['files'] and '..' not in Path(member.name).parts
   raw=t.extractfile(member).read();assert hashlib.sha256(raw).hexdigest()==manifest['files'][member.name]
   p=target/member.name;p.parent.mkdir(parents=True,exist_ok=True)
   if p.exists():assert p.read_bytes()==raw
   else:p.write_bytes(raw)
 for dirname in ['runtime','profiles','mapping','evidence']:
  folder=target/dirname;folder.mkdir(exist_ok=True)
  for original in (ROOT/dirname).iterdir():
   dest=folder/original.name
   if not dest.exists():dest.symlink_to(original,target_is_directory=original.is_dir())
 # Evidence parent already exists; attach its historical child if needed.
 b=target/'evidence/local_aki_columns_20261012'
 if not b.exists():b.mkdir(parents=True)
 att=b/'destination_verification.json'
 if not att.exists():att.write_bytes((base/att.name).read_bytes())
 spec=importlib.util.spec_from_file_location('frozen_aki_test',target/'runtime/local_aki_columns.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 return module
