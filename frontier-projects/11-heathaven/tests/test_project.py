import unittest, copy, json, math, itertools, tempfile
from pathlib import Path
import app
DEMO = json.loads((Path(__file__).parents[1]/"fixtures/demo.json").read_text())
class Tests(unittest.TestCase):
    def test_expected_selection(self): self.assertEqual(app.run(DEMO)['selected_centers'],['North','East'])
    def test_coverage(self): self.assertEqual(app.run(DEMO)['metrics']['covered_demand'],110)
    def test_uncovered_explicit(self): self.assertEqual(app.run(DEMO)['uncovered_areas'],['E'])
    def test_budget_zero(self):
        d=copy.deepcopy(DEMO);d['budget']=0;self.assertEqual(app.run(d)['metrics']['covered_demand'],0)
    def test_radius_boundary(self):
        d={'radius':3,'budget':1,'areas':[{'id':'A','x':3,'y':0,'weight':5}],'centers':[{'id':'C','x':0,'y':0}]};self.assertEqual(app.run(d)['metrics']['covered_demand'],5)
    def test_no_double_count(self):
        d=copy.deepcopy(DEMO);d['centers'][1]['x']=2;d['centers'][1]['y']=0;self.assertLessEqual(app.run(d)['metrics']['covered_demand'],125)
    def test_exact_not_worse_than_greedy(self):
        m=app.run(DEMO)['metrics'];self.assertGreaterEqual(m['covered_demand'],m['greedy_covered_demand'])
    def test_negative_demand(self):
        d=copy.deepcopy(DEMO);d['areas'][0]['weight']=-1
        with self.assertRaises(ValueError): app.run(d)

if __name__ == "__main__": unittest.main()
