import unittest, copy, json, math, itertools, tempfile
from pathlib import Path
import app
DEMO = json.loads((Path(__file__).parents[1]/"fixtures/demo.json").read_text())
class Tests(unittest.TestCase):
    def test_fefo(self): self.assertEqual(app.run(DEMO)['allocations'][0]['lot'],'L1')
    def test_expiry_boundary_excluded(self):
        self.assertFalse(any(x['lot']=='L1' and x['time']>=3 for x in app.run(DEMO)['allocations']))
    def test_conservation(self):
        m=app.run(DEMO)['metrics'];self.assertEqual(m['allocated_units']+m['remaining_units'],17)
    def test_demand_accounting(self):
        m=app.run(DEMO)['metrics'];self.assertEqual(m['allocated_units']+m['unmet_units'],16)
    def test_future_lot_not_used(self):
        self.assertFalse(any(x['lot']=='L3' and x['time']<4 for x in app.run(DEMO)['allocations']))
    def test_expected_unmet(self): self.assertEqual(app.run(DEMO)['metrics']['unmet_units'],0)
    def test_parameterized_identifier(self):
        d=copy.deepcopy(DEMO);d['lots'][0]['id']="lot'; DROP TABLE lot;--";self.assertEqual(app.run(d)['metrics']['allocated_units'],16)
    def test_negative_units(self):
        d=copy.deepcopy(DEMO);d['lots'][0]['units']=-1
        with self.assertRaises(ValueError): app.run(d)

if __name__ == "__main__": unittest.main()
