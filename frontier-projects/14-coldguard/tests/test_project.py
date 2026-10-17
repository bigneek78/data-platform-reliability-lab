import unittest, copy, json, math, itertools, tempfile
from pathlib import Path
import app
DEMO = json.loads((Path(__file__).parents[1]/"fixtures/demo.json").read_text())
class Tests(unittest.TestCase):
    def test_outside_duration(self): self.assertEqual(app.run(DEMO)['metrics']['outside_minutes'],5)
    def test_missing_intervals(self): self.assertEqual(app.run(DEMO)['metrics']['unknown_minutes'],10)
    def test_interval_conservation(self):
        m=app.run(DEMO)['metrics'];self.assertEqual(m['outside_minutes']+m['unknown_minutes']+m['within_minutes'],30)
    def test_hold(self): self.assertEqual(app.run(DEMO)['status'],'HOLD_FOR_REVIEW')
    def test_large_gap_unknown(self):
        d=copy.deepcopy(DEMO);d['readings']=[{'minute':0,'temp':5},{'minute':20,'temp':5}];self.assertEqual(app.run(d)['metrics']['unknown_minutes'],20)
    def test_duplicate_time(self):
        d=copy.deepcopy(DEMO);d['readings'][1]['minute']=0
        with self.assertRaises(ValueError): app.run(d)
    def test_single_sample_insufficient(self):
        d=copy.deepcopy(DEMO);d['readings']=d['readings'][:1];self.assertEqual(app.run(d)['status'],'INSUFFICIENT_EVIDENCE')
    def test_band_boundary(self):
        d=copy.deepcopy(DEMO);d['readings']=[{'minute':0,'temp':2},{'minute':5,'temp':8}];self.assertEqual(app.run(d)['metrics']['outside_minutes'],0)

if __name__ == "__main__": unittest.main()
