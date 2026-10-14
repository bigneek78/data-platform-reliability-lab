import hashlib
import json
import os
import stat
import tempfile
import unittest
import zipfile
from pathlib import Path

from phoenix_common import InputError
from tests.helpers import NOW, sample


class RestoreTests(unittest.TestCase):
    def setUp(self):
        self.app,self.data=sample(12);self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)

    def archive(self, declared, members=None, format=1):
        path=self.root/"test.zip"
        entries=[{"path":name,"bytes":len(body),"sha256":hashlib.sha256(body).hexdigest()} for name,body in declared]
        with zipfile.ZipFile(path,"w",compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr("manifest.json",json.dumps({"format":format,"files":entries}))
            for name,body in members if members is not None else declared:z.writestr(name,body)
        return path

    def test_real_demo_restores_and_verifies_all_files(self):
        out=self.app.evaluate(self.data,NOW);self.assertEqual(out["verified_files"],2);self.assertEqual(out["exit_code"],0)

    def test_snapshot_restore_matches_original_bytes(self):
        source=self.root/"source";source.mkdir();(source/"one.txt").write_bytes(b"original\n")
        self.app.snapshot(source,self.root/"backup.zip");self.app.restore(self.root/"backup.zip",self.root/"restored")
        self.assertEqual((self.root/"restored"/"one.txt").read_bytes(),b"original\n")

    def test_checksum_mismatch_before_destination_creation(self):
        archive=self.archive([("one.txt",b"good")],[("one.txt",b"bad")]);dest=self.root/"restore"
        with self.assertRaises(InputError):self.app.restore(archive,dest)
        self.assertFalse(dest.exists())

    def test_parent_traversal_rejected(self):
        archive=self.archive([("../escape.txt",b"bad")]);dest=self.root/"restore"
        with self.assertRaises(InputError):self.app.restore(archive,dest)
        self.assertFalse((self.root/"escape.txt").exists());self.assertFalse(dest.exists())

    def test_absolute_member_rejected(self):
        archive=self.archive([("/absolute.txt",b"bad")])
        with self.assertRaises(InputError):self.app.restore(archive,self.root/"restore")

    def test_case_aliases_rejected_portably(self):
        archive=self.archive([("A.txt",b"a"),("a.txt",b"b")])
        with self.assertRaises(InputError):self.app.restore(archive,self.root/"restore")

    def test_file_parent_collision_rejected(self):
        archive=self.archive([("folder",b"a"),("folder/child.txt",b"b")])
        with self.assertRaises(InputError):self.app.restore(archive,self.root/"restore")

    def test_undeclared_member_rejected(self):
        archive=self.archive([("one.txt",b"a")],[("one.txt",b"a"),("extra.txt",b"b")])
        with self.assertRaises(InputError):self.app.restore(archive,self.root/"restore")

    def test_missing_member_rejected(self):
        archive=self.archive([("one.txt",b"a")],[])
        with self.assertRaises(InputError):self.app.restore(archive,self.root/"restore")

    def test_existing_destination_preserved(self):
        archive=self.archive([("one.txt",b"a")]);dest=self.root/"restore";dest.mkdir();(dest/"owned.txt").write_bytes(b"keep")
        with self.assertRaises(InputError):self.app.restore(archive,dest)
        self.assertEqual((dest/"owned.txt").read_bytes(),b"keep")

    def test_existing_archive_preserved(self):
        source=self.root/"source";source.mkdir();(source/"one.txt").write_bytes(b"a")
        archive=self.root/"existing.zip";archive.write_bytes(b"keep")
        with self.assertRaises(InputError):self.app.snapshot(source,archive)
        self.assertEqual(archive.read_bytes(),b"keep")

    def test_boolean_manifest_version_rejected(self):
        archive=self.archive([("one.txt",b"a")],format=True)
        with self.assertRaises(InputError):self.app.restore(archive,self.root/"restore")

    def test_symlink_member_rejected(self):
        archive=self.root/"link.zip";body=b"target";entry={"path":"link","bytes":len(body),"sha256":hashlib.sha256(body).hexdigest()}
        with zipfile.ZipFile(archive,"w") as z:
            z.writestr("manifest.json",json.dumps({"format":1,"files":[entry]}));info=zipfile.ZipInfo("link");info.create_system=3;info.external_attr=(stat.S_IFLNK|0o777)<<16;z.writestr(info,body)
        with self.assertRaises(InputError):self.app.restore(archive,self.root/"restore")

    def test_archive_inside_source_rejected(self):
        source=self.root/"source";source.mkdir();(source/"one.txt").write_bytes(b"a")
        with self.assertRaises(InputError):self.app.snapshot(source,source/"inside.zip")

    def test_compression_outside_supported_format_rejected(self):
        archive=self.root/"unsupported.zip";body=b"a";entry={"path":"one.txt","bytes":1,"sha256":hashlib.sha256(body).hexdigest()}
        with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_BZIP2) as z:
            z.writestr("manifest.json",json.dumps({"format":1,"files":[entry]}));z.writestr("one.txt",body)
        with self.assertRaises(InputError):self.app.restore(archive,self.root/"restore")

    def test_expansion_limit_enforced_before_restore(self):
        archive=self.archive([("huge.txt",b"a"*(self.app.MAX_BYTES+128*1024+1))]);dest=self.root/"restore"
        with self.assertRaises(InputError):self.app.restore(archive,dest)
        self.assertFalse(dest.exists())
