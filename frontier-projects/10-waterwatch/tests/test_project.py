import unittest, copy, json, math, itertools, tempfile
from pathlib import Path
import app
DEMO = json.loads((Path(__file__).parents[1]/"fixtures/demo.json").read_text())
class Tests(unittest.TestCase):
    def test_flags(self): self.assertEqual([x['sample'] for x in app.run(DEMO)['trace'] if x['state']=='REVIEW'],[5,6])
    def test_unknown_not_normal(self): self.assertEqual(app.run(DEMO)['trace'][3]['state'],'UNKNOWN')
    def test_constant_baseline(self):
        d=copy.deepcopy(DEMO);d['baseline']=[50]*5;self.assertEqual(app.run(d)['baseline']['scale'],.5)
    def test_median_robust_to_single_spike(self):
        d=copy.deepcopy(DEMO);d['baseline'][-1]=1000;self.assertEqual(app.run(d)['baseline']['median'],50)
    def test_threshold_boundary(self):
        d={'baseline':[10]*5,'readings':[12],'threshold':4,'resolution':.5};self.assertEqual(app.run(d)['trace'][0]['state'],'WITHIN_BASELINE')
    def test_negative_pressure(self):
        d=copy.deepcopy(DEMO);d['readings'][0]=-1
        with self.assertRaises(ValueError): app.run(d)
    def test_bad_resolution(self):
        d=copy.deepcopy(DEMO);d['resolution']=0
        with self.assertRaises(ValueError): app.run(d)
    def test_short_baseline(self):
        d=copy.deepcopy(DEMO);d['baseline']=[1,2]
        with self.assertRaises(ValueError): app.run(d)

if __name__ == "__main__": unittest.main()
