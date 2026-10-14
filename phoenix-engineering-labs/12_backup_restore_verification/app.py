"""Create and verify a small local ZIP backup with a SHA-256 manifest."""
from __future__ import annotations

import hashlib
import json
import stat
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

from phoenix_common import InputError, Report, obj, rows, strict_json, text

MAX_BYTES = 2 * 1024 * 1024
MAX_FILES = 200


def safe_name(name):
    text(name, "archive path")
    path = PurePosixPath(name)
    if path.is_absolute() or any(p in ("", ".", "..") for p in name.split("/")) or any(c in name for c in "\\:< >|?*\x00"):
        raise InputError("unsupported or unsafe archive path")
    if name == "manifest.json":
        raise InputError("manifest.json is reserved")
    return path


def validate_names(names):
    for name in names:
        safe_name(name)
    folded = [n.casefold() for n in names]
    if len(set(folded)) != len(folded):
        raise InputError("duplicate or case-aliased archive paths")
    paths = set(folded)
    for name in folded:
        if any(str(p) in paths for p in PurePosixPath(name).parents if str(p) != "."):
            raise InputError("a file is also the parent of another archive entry")


def snapshot(source, archive):
    source, archive = Path(source), Path(archive)
    if source.is_symlink() or not source.is_dir():
        raise InputError("source must be a real directory")
    if archive.resolve().is_relative_to(source.resolve()):
        raise InputError("archive must be outside the source tree")
    files = []
    total = 0
    for path in sorted(source.rglob("*")):
        if path.is_symlink():
            raise InputError("symlinks are not supported by this demonstration")
        if not path.is_file():
            continue
        name = path.relative_to(source).as_posix()
        safe_name(name)
        size = path.stat().st_size
        if size > MAX_BYTES or total + size > MAX_BYTES:
            raise InputError("backup exceeds the 2 MiB demonstration limit")
        body = path.read_bytes()
        if len(body) != size:
            raise InputError("source changed during collection")
        total += size
        files.append((name, body))
    if not files or len(files) > MAX_FILES:
        raise InputError("backup requires between 1 and 200 files")
    validate_names([name for name, _ in files])
    manifest = {"format": 1, "files": [{"path": n, "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()} for n, b in files]}
    archive.parent.mkdir(parents=True, exist_ok=True)
    try:
        with archive.open("xb") as stream:
            with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
                bundle.writestr("manifest.json", json.dumps(manifest, sort_keys=True))
                for name, body in files:
                    bundle.writestr(name, body)
    except FileExistsError as exc:
        raise InputError("archive already exists; refusing to overwrite it") from exc
    return manifest


def restore(archive, destination):
    destination = Path(destination)
    if destination.exists() or destination.is_symlink():
        raise InputError("restore destination must not exist")
    try:
        with zipfile.ZipFile(archive) as bundle:
            entries = bundle.infolist()
            names = [info.filename for info in entries]
            if len(set(names)) != len(names) or not 2 <= len(entries) <= MAX_FILES + 1 or names.count("manifest.json") != 1:
                raise InputError("invalid archive member inventory")
            if sum(info.file_size for info in entries) > MAX_BYTES + 128 * 1024:
                raise InputError("archive expands beyond the demonstration limit")
            for info in entries:
                if info.is_dir() or stat.S_ISLNK(info.external_attr >> 16) or info.flag_bits & 1:
                    raise InputError("directories, symlinks and encrypted entries are not supported")
                if info.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
                    raise InputError("only stored or Deflate-compressed members are supported")
            if bundle.getinfo("manifest.json").file_size > 128 * 1024:
                raise InputError("manifest exceeds its size limit")
            manifest = obj(strict_json(bundle.read("manifest.json").decode("utf-8")), "manifest")
            if type(manifest.get("format")) is not int or manifest["format"] != 1:
                raise InputError("unsupported backup manifest")
            records = rows(manifest.get("files"), "files")
            if not 1 <= len(records) <= MAX_FILES:
                raise InputError("invalid manifest file count")
            declared, checked = [], []
            for record in records:
                obj(record, "manifest entry")
                name = text(record.get("path"), "path")
                safe_name(name)
                declared.append(name)
                if name not in names:
                    raise InputError("declared backup member is missing")
                body = bundle.read(name)
                if record.get("bytes") != len(body) or record.get("sha256") != hashlib.sha256(body).hexdigest():
                    raise InputError("backup member checksum or byte count does not match")
                checked.append((name, body))
            validate_names(declared)
            if set(names) != set(declared) | {"manifest.json"}:
                raise InputError("archive contains an undeclared member")
    except (zipfile.BadZipFile, UnicodeError, KeyError, OSError) as exc:
        raise InputError("backup could not be verified") from exc
    # All member paths and bytes have been checked before destination creation.
    destination.mkdir(parents=True, exist_ok=False)
    for name, body in checked:
        target = destination.joinpath(*PurePosixPath(name).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as stream:
            stream.write(body)
    for name, body in checked:
        if hashlib.sha256(destination.joinpath(*PurePosixPath(name).parts).read_bytes()).digest() != hashlib.sha256(body).digest():
            raise InputError("restored file verification failed")
    return {"verified_files": len(checked), "verified_bytes": sum(len(b) for _, b in checked), "paths": sorted(declared)}


def evaluate(data, now):
    obj(data)
    mapping = obj(data.get("files"), "files")
    if not mapping:
        raise InputError("demo has no source files")
    validate_names(list(mapping))
    with tempfile.TemporaryDirectory(prefix="phoenix-backup-") as temp:
        root = Path(temp)
        source = root / "source"
        source.mkdir()
        for name, body in mapping.items():
            safe_name(name)
            if not isinstance(body, str):
                raise InputError("demo file bodies must be strings")
            target = source.joinpath(*PurePosixPath(name).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(body, encoding="utf-8", newline="\n")
        snapshot(source, root / "backup.zip")
        outcome = restore(root / "backup.zip", root / "restored")
    return Report().finish(**outcome, policy_scope="Real file and checksum operations on temporary synthetic files; no production recovery/RPO claim.")

