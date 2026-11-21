import subprocess

from runtime.local_autopilot import run


def _git(d, *a):
    return subprocess.run(['git', '-C', str(d), *a], capture_output=True, text=True, check=True).stdout


def test_publish_now_commits_and_pushes(tmp_path, monkeypatch):
    remote = tmp_path / 'remote.git'
    subprocess.run(['git', 'init', '-q', '--bare', str(remote)], check=True)
    seed = tmp_path / 'seed'
    subprocess.run(['git', 'init', '-q', '-b', 'local-autopilot-data', str(seed)], check=True)
    _git(seed, 'config', 'user.email', 'a@b'); _git(seed, 'config', 'user.name', 'a')
    (seed / 'output').mkdir(); (seed / 'output' / 'x').write_text('1')
    _git(seed, 'add', '-A'); _git(seed, 'commit', '-q', '-m', 'init')
    _git(seed, 'push', '-q', str(remote), 'HEAD:local-autopilot-data')
    data = tmp_path / 'data'
    subprocess.run(['git', 'clone', '-q', '-b', 'local-autopilot-data', str(remote), str(data)], check=True)
    _git(data, 'config', 'user.email', 'a@b'); _git(data, 'config', 'user.name', 'a')
    monkeypatch.setattr(run, 'ROOT', data / 'output')
    monkeypatch.setattr(run, 'log', lambda *a: None)
    monkeypatch.delenv('KM_LOCAL_PUBLISH_MIDTICK', raising=False)
    (data / 'output' / 'rev.json').write_text('{}')
    assert run.publish_now('SAG_03 直前版') is True
    assert 'prestart: SAG_03' in _git(remote, 'log', '-1', '--format=%s', 'local-autopilot-data')
    assert run.publish_now('nothing new') is False
    monkeypatch.setenv('KM_LOCAL_PUBLISH_MIDTICK', '0')
    (data / 'output' / 'rev2.json').write_text('{}')
    assert run.publish_now('off') is False
