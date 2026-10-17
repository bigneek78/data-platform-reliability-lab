import unittest, copy, json, math, itertools, tempfile
from pathlib import Path
import app
DEMO = json.loads((Path(__file__).parents[1]/"fixtures/demo.json").read_text())
class Tests(unittest.TestCase):
    def test_balance(self):
        for x in app.run(DEMO)['trace']: self.assertEqual(x['solar']+x['grid']+x['soc_before'],x['demand']+x['curtailed']+x['soc_after'])
    def test_reserve(self): self.assertTrue(all(DEMO['reserve']<=x['soc_after']<=DEMO['capacity'] for x in app.run(DEMO)['trace']))
    def test_rate(self): self.assertTrue(all(abs(x['soc_after']-x['soc_before'])<=DEMO['rate'] for x in app.run(DEMO)['trace']))
    def test_terminal(self): self.assertGreaterEqual(app.run(DEMO)['metrics']['terminal_soc'],DEMO['terminal'])
    def test_tiny_optimum(self):
        d={'demand':[1,1],'solar':[0,0],'price':[1,10],'capacity':1,'initial':0,'reserve':0,'terminal':0,'rate':1,'grid_limit':2};self.assertEqual(app.run(d)['metrics']['dispatch_cost_units'],2)
    def test_infeasible(self):
        d=copy.deepcopy(DEMO);d['grid_limit']=0
        with self.assertRaises(ValueError): app.run(d)
    def test_invalid_soc(self):
        d=copy.deepcopy(DEMO);d['initial']=99
        with self.assertRaises(ValueError): app.run(d)
    def test_cost_at_most_idle(self):
        m=app.run(DEMO)['metrics'];self.assertLessEqual(m['dispatch_cost_units'],m['no_battery_cost_units'])

if __name__ == "__main__": unittest.main()
