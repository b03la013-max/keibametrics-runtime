"""Authored bytes only; no actual PAPER archive or original private tickets."""
import hashlib
import stat
import struct
from zipfile import ZipFile, ZipInfo

import pytest

from runtime.urw_paper_archive import verify_extracted_archive


def authored(tmp_path, members=None):
    tmp_path.chmod(0o700)
    archive = tmp_path / 'original.zip'
    extracted = tmp_path / 'extracted'
    extracted.mkdir(mode=0o700)
    members = members or {'frozen/source.json': b'{"synthetic":true}', 'paper/tickets.json': b'[]'}
    with ZipFile(archive, 'w') as target:
        for name, raw in members.items():
            target.writestr(name, raw)
            path = extracted / name
            path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            path.write_bytes(raw)
            path.chmod(0o600)
    archive.chmod(0o600)
    return archive, extracted


def test_every_original_byte_is_verified_without_mutation_or_provenance_claim(tmp_path):
    archive, extracted = authored(tmp_path)
    before = {str(p): (p.read_bytes(), p.stat().st_mode) for p in [archive, *extracted.rglob('*.json')]}
    value = verify_extracted_archive(archive, extracted)
    assert value['archive_sha256'] == hashlib.sha256(archive.read_bytes()).hexdigest()
    assert value['member_count'] == 2
    assert [m['path'] for m in value['members']] == ['frozen/source.json', 'paper/tickets.json']
    for member in value['members']:
        raw = (extracted / member['path']).read_bytes()
        assert member['bytes'] == len(raw)
        assert member['sha256'] == hashlib.sha256(raw).hexdigest()
    assert not value['external_manifest_verified'] and not value['independent_timestamp_verified']
    assert before == {str(p): (p.read_bytes(), p.stat().st_mode) for p in [archive, *extracted.rglob('*.json')]}


@pytest.mark.parametrize('change', ['tamper', 'missing', 'extra', 'file_symlink', 'directory_symlink', 'permissions'])
def test_extracted_tree_changes_are_rejected(tmp_path, change):
    archive, extracted = authored(tmp_path)
    target = extracted / 'frozen/source.json'
    if change == 'tamper':
        target.write_bytes(b'changed')
    elif change == 'missing':
        target.unlink()
    elif change == 'extra':
        target = extracted / 'extra.json'
        target.write_bytes(b'[]')
        target.chmod(0o600)
    elif change == 'file_symlink':
        target.unlink()
        target.symlink_to(extracted / 'paper/tickets.json')
    elif change == 'directory_symlink':
        target.unlink()
        target.parent.rmdir()
        target.parent.symlink_to(extracted / 'paper', target_is_directory=True)
    else:
        target.chmod(0o644)
    with pytest.raises(ValueError):
        verify_extracted_archive(archive, extracted)


@pytest.mark.parametrize('name', ['../escape', '/absolute', 'C:/windows', 'folder\\escape', 'x//file', './file', 'x/../file'])
def test_zip_member_path_attacks_are_rejected_without_extraction(tmp_path, name):
    archive, extracted = authored(tmp_path)
    with ZipFile(archive, 'a') as target:
        target.writestr(name, b'synthetic attack')
    with pytest.raises(ValueError, match='MEMBER_PATH_INVALID'):
        verify_extracted_archive(archive, extracted)
    assert not (tmp_path / 'escape').exists()


def test_duplicate_symlink_and_device_zip_entries_are_rejected(tmp_path):
    for index, kind in enumerate(('duplicate', stat.S_IFLNK, stat.S_IFIFO)):
        root = tmp_path / str(index)
        root.mkdir(mode=0o700)
        archive, extracted = authored(root)
        with ZipFile(archive, 'a') as target:
            if kind == 'duplicate':
                with pytest.warns(UserWarning, match='Duplicate name'):
                    target.writestr('paper/tickets.json', b'[]')
            else:
                info = ZipInfo('unsupported')
                info.create_system = 3
                info.external_attr = (kind | 0o600) << 16
                target.writestr(info, b'paper/tickets.json')
        with pytest.raises(ValueError):
            verify_extracted_archive(archive, extracted)


def test_archive_crc_failure_and_nul_member_are_rejected(tmp_path):
    archive, extracted = authored(tmp_path, {'a.json': b'synthetic-original'})
    raw = bytearray(archive.read_bytes())
    name_len, extra_len = struct.unpack_from('<HH', raw, 26)
    raw[30 + name_len + extra_len] ^= 1
    archive.write_bytes(raw)
    with pytest.raises(ValueError, match='ZIP_INTEGRITY_FAILURE'):
        verify_extracted_archive(archive, extracted)
    # Build a syntactically valid Zip, then insert a NUL into both stored names.
    with ZipFile(archive, 'w') as target:
        target.writestr('a.json', b'synthetic-original')
    archive.write_bytes(archive.read_bytes().replace(b'a.json', b'a\x00json'))
    with pytest.raises(ValueError, match='MEMBER_PATH_INVALID'):
        verify_extracted_archive(archive, extracted)


def test_missing_inputs_git_ancestors_and_private_archive_mode(tmp_path):
    archive, extracted = authored(tmp_path)
    missing = tmp_path / 'not-created'
    with pytest.raises(FileNotFoundError):
        verify_extracted_archive(archive, missing)
    assert not missing.exists()
    archive.chmod(0o644)
    with pytest.raises(ValueError, match='PERMISSIONS'):
        verify_extracted_archive(archive, extracted)
    archive.chmod(0o600)
    (tmp_path / '.git').mkdir(mode=0o700)
    with pytest.raises(ValueError, match='INSIDE_GIT'):
        verify_extracted_archive(archive, extracted)


def test_explicit_empty_zip_directory_is_verified(tmp_path):
    archive, extracted = authored(tmp_path)
    (extracted / 'empty').mkdir(mode=0o700)
    with ZipFile(archive, 'a') as target:
        target.writestr('empty/', b'')
    value = verify_extracted_archive(archive, extracted)
    directory = next(m for m in value['members'] if m['path'] == 'empty/')
    assert directory['kind'] == 'DIRECTORY' and directory['bytes'] == 0


def test_symlink_in_input_ancestor_is_rejected(tmp_path):
    source = tmp_path / 'source'
    source.mkdir(mode=0o700)
    archive, extracted = authored(source)
    alias = tmp_path / 'alias'
    alias.symlink_to(source, target_is_directory=True)
    with pytest.raises(ValueError, match='SYMLINK_FORBIDDEN'):
        verify_extracted_archive(alias / archive.name, extracted)
