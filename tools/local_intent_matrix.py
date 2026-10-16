"""Resolve all committed LOCAL intents; no schedule synthesis or prediction generation."""
import json
import os
from pathlib import Path
import re
import subprocess


def resolve(paths, *, root=Path('.')):
    rows = []
    ids = set()
    for name in sorted(set(paths)):
        if not re.fullmatch(r'runtime/formal_intents/[A-Za-z0-9_-]+\.json', name):
            raise ValueError('LOCAL_INTENT_PATH_INVALID')
        path = root / name
        if path.is_symlink() or not path.is_file():
            raise ValueError('LOCAL_INTENT_FILE_INVALID')
        req = json.loads(path.read_text(encoding='utf-8'))
        # Preserve canonical execution-store IDs, including historical acceptance IDs.
        eid = req.get('execution_id') or ('LOCAL-' + str(req.get('race_id') or '') + '-EXEC')
        if req.get('family_id') != 'LOCAL' or not isinstance(eid, str) or not re.fullmatch(r'(?:KM-)?LOCAL-[A-Z0-9-]+', eid):
            raise ValueError('LOCAL_INTENT_IDENTITY_INVALID')
        race_id = str(req.get('race_id') or '')
        valid_ids = {race_id, 'LOCAL-' + race_id + '-EXEC', race_id.removeprefix('KM-')}
        if path.stem != race_id or eid not in valid_ids or eid in ids:
            raise ValueError('LOCAL_INTENT_IDENTITY_CONFLICT')
        ids.add(eid)
        rows.append({'intent_path': name, 'execution_id': eid})
    if not rows or len(rows) > 256:
        raise ValueError('LOCAL_INTENT_BATCH_SIZE_INVALID')
    return {'include': rows}


if __name__ == '__main__':
    selected = os.environ.get('INTENT_INPUT_PATH')
    if selected:
        paths = [selected]
    else:
        # push.before covers every commit in the push, including merge commits.
        event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text())
        before = event.get('before')
        if not before or set(before) == {'0'}:
            raise SystemExit('LOCAL_INTENT_PUSH_BASE_REQUIRED')
        changed = subprocess.check_output(['git', 'diff', '--name-only', '--diff-filter=AM',
                                          before, os.environ['GITHUB_SHA'], '--',
                                          'runtime/formal_intents/*.json'], text=True)
        paths = changed.splitlines()
    matrix = resolve(paths)
    with open(os.environ['GITHUB_OUTPUT'], 'a') as out:
        out.write('matrix=' + json.dumps(matrix, separators=(',', ':')) + '\n')
