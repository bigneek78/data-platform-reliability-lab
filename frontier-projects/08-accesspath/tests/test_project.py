import unittest, copy, json, math, itertools, tempfile
from pathlib import Path
import app
DEMO = json.loads((Path(__file__).parents[1]/"fixtures/demo.json").read_text())
class Tests(unittest.TestCase):
    def test_expected_route(self): self.assertEqual(app.run(DEMO)['path'],['Entry','Lift','Exit'])
    def test_cost(self): self.assertEqual(app.run(DEMO)['metrics']['route_length'],17)
    def test_exclusion_reasons(self): self.assertEqual(app.run(DEMO)['excluded'],[{'id':'stairs','reasons':['stairs']},{'id':'c','reasons':['slope']}])
    def test_strict_width_no_route(self):
        d=copy.deepcopy(DEMO);d['min_width']=3;self.assertEqual(app.run(d)['path'],[])
    def test_slope_boundary(self):
        d=copy.deepcopy(DEMO);d['max_slope']=.12;self.assertEqual(app.run(d)['metrics']['route_length'],12)
    def test_width_boundary(self):
        d=copy.deepcopy(DEMO);d['min_width']=1.2;self.assertTrue(app.run(d)['path'])
    def test_negative_length(self):
        d=copy.deepcopy(DEMO);d['edges'][0]['length']=-1
        with self.assertRaises(ValueError): app.run(d)
    def test_unknown_node(self):
        d=copy.deepcopy(DEMO);d['goal']='missing'
        with self.assertRaises(ValueError): app.run(d)

if __name__ == "__main__": unittest.main()
