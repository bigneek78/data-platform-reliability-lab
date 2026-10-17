import unittest, copy, json, math, itertools, tempfile
from pathlib import Path
import app
DEMO = json.loads((Path(__file__).parents[1]/"fixtures/demo.json").read_text())
class Tests(unittest.TestCase):
    def test_valid_subset(self): self.assertTrue(app.run(DEMO)['subset_pass'])
    def test_duplicate_fullurl(self):
        d=copy.deepcopy(DEMO);d['bundle']['entry'][1]['fullUrl']=d['bundle']['entry'][0]['fullUrl'];self.assertIn('DUPLICATE_FULLURL',[x['code'] for x in app.run(d)['findings']])
    def test_unresolved_reference(self):
        d=copy.deepcopy(DEMO);d['bundle']['entry'][1]['resource']['subject']['reference']='Patient/missing';self.assertFalse(app.run(d)['subset_pass'])
    def test_urn_resolution(self):
        d=copy.deepcopy(DEMO);d['bundle']['entry'][1]['resource']['subject']['reference']='urn:uuid:123e4567-e89b-12d3-a456-426614174001';self.assertTrue(app.run(d)['subset_pass'])
    def test_missing_status(self):
        d=copy.deepcopy(DEMO);del d['bundle']['entry'][1]['resource']['status'];self.assertFalse(app.run(d)['subset_pass'])
    def test_duplicate_resource(self):
        d=copy.deepcopy(DEMO);e=copy.deepcopy(d['bundle']['entry'][0]);e['fullUrl']='urn:uuid:other';d['bundle']['entry'].append(e);self.assertFalse(app.run(d)['subset_pass'])
    def test_unsupported_type(self):
        d=copy.deepcopy(DEMO);d['bundle']['entry'][0]['resource']['resourceType']='Medication';self.assertFalse(app.run(d)['subset_pass'])
    def test_non_collection_rejected(self):
        d=copy.deepcopy(DEMO);d['bundle']['type']='transaction'
        with self.assertRaises(ValueError): app.run(d)

if __name__ == "__main__": unittest.main()
