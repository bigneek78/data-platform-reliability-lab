import unittest, copy, json, math, itertools, tempfile
from pathlib import Path
import app
DEMO = json.loads((Path(__file__).parents[1]/"fixtures/demo.json").read_text())
class Tests(unittest.TestCase):
    def test_detects_injected_change(self): self.assertEqual(app.run(DEMO)['alerts'],[12,13,14,15])
    def test_normal_constant(self):
        d=copy.deepcopy(DEMO);d['readings']=[10]*18;self.assertEqual(app.run(d)['alerts'],[])
    def test_freeze(self):
        t=app.run(DEMO)['trace'];self.assertEqual(t[12]['baseline'],t[15]['baseline'])
    def test_recovers(self): self.assertFalse(app.run(DEMO)['trace'][-1]['flag'])
    def test_threshold_boundary(self):
        d={'readings':[10,10,13],'calibration':2,'alpha':.5,'threshold':3};self.assertEqual(app.run(d)['alerts'],[])
    def test_bad_alpha(self):
        d=copy.deepcopy(DEMO);d['alpha']=0
        with self.assertRaises(ValueError): app.run(d)
    def test_missing(self):
        d=copy.deepcopy(DEMO);d['readings'][9]=None
        with self.assertRaises(ValueError): app.run(d)
    def test_short_calibration(self):
        d=copy.deepcopy(DEMO);d['calibration']=99
        with self.assertRaises(ValueError): app.run(d)

if __name__ == "__main__": unittest.main()
