import unittest, copy, json, math, itertools, tempfile
from pathlib import Path
import app
DEMO = json.loads((Path(__file__).parents[1]/"fixtures/demo.json").read_text())
class Tests(unittest.TestCase):
    def test_valid_gate(self): self.assertTrue(app.run(DEMO)['eligible'])
    def test_wrong_hash_blocks(self):
        d=copy.deepcopy(DEMO);d['artifacts'][0]['sha256']='0'*64;self.assertFalse(app.run(d)['eligible'])
    def test_missing_artifact_blocks(self):
        d=copy.deepcopy(DEMO);d['artifacts'][0]['path']='missing.txt';self.assertFalse(app.run(d)['eligible'])
    def test_path_traversal_blocks(self):
        d=copy.deepcopy(DEMO);d['artifacts'][0]['path']='../app.py';self.assertIn('UNSAFE_PATH',[x['code'] for x in app.run(d)['findings']])
    def test_test_accounting_blocks(self):
        d=copy.deepcopy(DEMO);d['test_record']['passed']=7;self.assertFalse(app.run(d)['eligible'])
    def test_commit_mismatch_blocks(self):
        d=copy.deepcopy(DEMO);d['test_record']['commit']='other';self.assertFalse(app.run(d)['eligible'])
    def test_stale_or_future_blocks(self):
        for t in (0,1001):
            d=copy.deepcopy(DEMO);d['test_record']['time']=t;self.assertFalse(app.run(d)['eligible'])
    def test_zero_tests_blocks(self):
        d=copy.deepcopy(DEMO);d['test_record'].update(total=0,passed=0,failed=0);self.assertFalse(app.run(d)['eligible'])

if __name__ == "__main__": unittest.main()
