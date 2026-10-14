import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from run_sample import ROOT, catalog
from tests.helpers import NOW, sample, codes


class CliContractTests(unittest.TestCase):
    def run_cli(self, ident, path=None):
        args=[sys.executable,str(ROOT/"run_sample.py"),str(ident),"--now",NOW.isoformat()]
        if path is not None:args += ["--input",str(path)]
        return subprocess.run(args,cwd=ROOT,text=True,capture_output=True,timeout=15)

    def test_all_fifteen_clis_return_their_documented_status(self):
        for record in catalog():
            with self.subTest(sample=record["id"]):
                run=self.run_cli(record["id"]);out=json.loads(run.stdout)
                self.assertEqual(run.returncode,record["expected_fixture_exit"]);self.assertEqual(out["exit_code"],run.returncode)

    def test_missing_input_returns_structured_error(self):
        run=self.run_cli(1,ROOT/"does-not-exist.json")
        self.assertEqual(run.returncode,3);self.assertEqual(json.loads(run.stdout)["status"],"invalid_input")

    def test_duplicate_json_rejected_through_cli(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"bad.json";path.write_text('{"approved":false,"approved":true}',encoding="utf-8")
            run=self.run_cli(13,path);self.assertEqual(run.returncode,3);self.assertEqual(json.loads(run.stdout)["status"],"invalid_input")

    def test_naive_evaluation_time_rejected_through_cli(self):
        run=subprocess.run([sys.executable,str(ROOT/"run_sample.py"),"1","--now","2026-10-13T12:00:00"],cwd=ROOT,text=True,capture_output=True,timeout=15)
        self.assertEqual(run.returncode,3);self.assertEqual(json.loads(run.stdout)["status"],"invalid_input")

    def test_utf8_bom_json_export_supported(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"evidence.json";path.write_text('{"candidates":["strict"]}',encoding="utf-8-sig")
            run=self.run_cli(15,path);self.assertEqual(run.returncode,0);self.assertEqual(json.loads(run.stdout)["status"],"clear")

    def test_input_size_limit_enforced(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"large.json";path.write_bytes(b" "*(2*1024*1024+1))
            self.assertEqual(self.run_cli(1,path).returncode,3)

    def test_utf8_bom_replication_export_supported(self):
        app,raw=sample(4)
        self.assertEqual(app.evaluate("\ufeff"+raw,NOW),app.evaluate(raw,NOW))

    def test_no_services_collected_is_incomplete_not_healthy(self):
        app,data=sample(3);data["hosts"]=data["hosts"][:1];data["hosts"][0]["services"]=[]
        out=app.evaluate(data,NOW);self.assertEqual(out["exit_code"],2);self.assertIn("service_missing",codes(out))

    def test_ansible_example_contains_only_readonly_modules(self):
        plays=json.loads((ROOT/"05_rhel_patch_readiness"/"collect_readonly_facts.yml").read_text(encoding="utf-8"))
        self.assertFalse(plays[0]["gather_facts"])
        modules={k for task in plays[0]["tasks"] for k in task if k.startswith("ansible.builtin.")}
        self.assertEqual(modules,{"ansible.builtin.setup","ansible.builtin.debug"})
