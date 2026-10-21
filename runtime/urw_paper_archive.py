"""Read-only integrity checks for private, already-extracted PAPER originals.

The archive digest still needs an independently trusted witness. Comparing an
archive with its extraction proves byte agreement, not origin or a timestamp.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path, PurePosixPath
import stat
from zipfile import BadZipFile, ZipFile


def _private_path(value, *, directory):
    path = Path(value)
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('RESEARCH_ARCHIVE_PRIVATE_ABSOLUTE_PATH_REQUIRED')
    for ancestor in (path, *path.parents):
        if ancestor.is_symlink():
            raise ValueError('RESEARCH_ARCHIVE_SYMLINK_FORBIDDEN')
        marker = ancestor / '.git'
        if marker.exists() or marker.is_symlink():
            raise ValueError('RESEARCH_ARCHIVE_INSIDE_GIT_FORBIDDEN')
    info = path.lstat()  # Missing inputs must not be created during verification.
    correct_type = stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode)
    if not correct_type:
        raise ValueError('RESEARCH_ARCHIVE_UNSUPPORTED_FILESYSTEM_ENTRY')
    if stat.S_IMODE(info.st_mode) != (0o700 if directory else 0o600):
        raise ValueError('RESEARCH_ARCHIVE_PRIVATE_PERMISSIONS_REQUIRED')
    return path


def _digest(stream):
    digest = hashlib.sha256()
    size = 0
    while chunk := stream.read(1024 * 1024):
        digest.update(chunk)
        size += len(chunk)
    return size, digest.hexdigest()


def _identity(info):
    # Reads may update access time; identity and content metadata must stay fixed.
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def _open_private(path):
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) != 0o600:
            raise ValueError('RESEARCH_ARCHIVE_PRIVATE_REGULAR_FILE_REQUIRED')
        return os.fdopen(descriptor, 'rb')
    except BaseException:
        os.close(descriptor)
        raise


def _member(info):
    name = info.orig_filename
    directory = info.is_dir()
    path = PurePosixPath(name)
    canonical = path.as_posix() + ('/' if directory else '')
    if (not name or '\\' in name or '\x00' in name or info.filename != name
            or path.is_absolute() or '..' in path.parts or name != canonical
            or path.as_posix() == '.' or ':' in path.parts[0]):
        raise ValueError('RESEARCH_ARCHIVE_MEMBER_PATH_INVALID')
    kind = stat.S_IFMT(info.external_attr >> 16)
    if (kind not in (0, stat.S_IFREG, stat.S_IFDIR)
            or kind == stat.S_IFDIR and not directory
            or kind == stat.S_IFREG and directory or info.flag_bits & 1):
        raise ValueError('RESEARCH_ARCHIVE_MEMBER_TYPE_FORBIDDEN')
    return path.as_posix(), directory


def verify_extracted_archive(archive_zip, extracted):
    """Verify every private Zip member against an exact extracted file tree.

    Never extract, chmod, rewrite or create input files. Reject undeclared files,
    unsafe paths, unsupported entry types and symlinks before reading members.
    CRC checks remain enabled by fully consuming each Zip member stream.
    """
    archive_zip = _private_path(archive_zip, directory=False)
    extracted = _private_path(extracted, directory=True)
    if archive_zip.is_relative_to(extracted):
        raise ValueError('RESEARCH_ARCHIVE_ZIP_INSIDE_EXTRACTED_TREE')
    with _open_private(archive_zip) as original:
        original_stat = os.fstat(original.fileno())
        _, archive_sha = _digest(original)
        original.seek(0)
        try:
            with ZipFile(original) as archive:
                entries = []
                names = set()
                expected_files = set()
                expected_directories = set()
                for info in archive.infolist():
                    name, directory = _member(info)
                    if name in names:
                        raise ValueError('RESEARCH_ARCHIVE_DUPLICATE_MEMBER_PATH')
                    names.add(name)
                    entries.append((info, name, directory))
                    (expected_directories if directory else expected_files).add(name)
                    expected_directories.update(str(p) for p in PurePosixPath(name).parents if str(p) != '.')
                if expected_files & expected_directories:
                    raise ValueError('RESEARCH_ARCHIVE_FILE_DIRECTORY_CONFLICT')
                actual_files = set()
                actual_directories = set()
                def unreadable(error):
                    raise error
                for folder, directories, files in os.walk(extracted, followlinks=False, onerror=unreadable):
                    for name in directories:
                        path = _private_path(Path(folder) / name, directory=True)
                        actual_directories.add(path.relative_to(extracted).as_posix())
                    for name in files:
                        path = _private_path(Path(folder) / name, directory=False)
                        actual_files.add(path.relative_to(extracted).as_posix())
                if actual_files != expected_files or actual_directories != expected_directories:
                    raise ValueError('RESEARCH_ARCHIVE_EXTRACTED_MEMBER_UNIVERSE_MISMATCH')
                members = []
                for info, name, directory in entries:
                    with archive.open(info) as member:
                        size, digest = _digest(member)
                    if size != info.file_size or directory and size:
                        raise ValueError('RESEARCH_ARCHIVE_MEMBER_BYTES_MISMATCH')
                    if not directory:
                        path = extracted / name
                        with _open_private(path) as stream:
                            before = os.fstat(stream.fileno())
                            observed = _digest(stream)
                            after = os.fstat(stream.fileno())
                        if (_identity(before) != _identity(after)
                                or _identity(path.lstat()) != _identity(after)
                                or observed != (size, digest)):
                            raise ValueError('RESEARCH_ARCHIVE_EXTRACTED_BYTES_MISMATCH')
                    members.append({'path': info.filename, 'kind': 'DIRECTORY' if directory else 'FILE',
                                    'bytes': size, 'sha256': digest})
        except (BadZipFile, RuntimeError, NotImplementedError) as error:
            raise ValueError('RESEARCH_ARCHIVE_ZIP_INTEGRITY_FAILURE') from error
        if (_identity(original_stat) != _identity(os.fstat(original.fileno()))
                or _identity(archive_zip.lstat()) != _identity(original_stat)):
            raise ValueError('RESEARCH_ARCHIVE_CHANGED_DURING_VERIFICATION')
    return {'schema': 'URW-PRIVATE-ARCHIVE-VERIFICATION-v1', 'archive_sha256': archive_sha,
            'member_count': len(members), 'members': sorted(members, key=lambda m: m['path']),
            'extracted_tree_matches_archive': True, 'external_manifest_verified': False,
            'independent_timestamp_verified': False}
