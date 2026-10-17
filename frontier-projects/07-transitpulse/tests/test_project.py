import unittest, copy, json, math, itertools, tempfile
from pathlib import Path
import app
DEMO = json.loads((Path(__file__).parents[1]/"fixtures/demo.json").read_text())
class Tests(unittest.TestCase):
    def test_expected_departures(self): self.assertEqual(app.run(DEMO)['departures'],[0,10,20,27,39,49,60])
    def test_improves_fixture_headway_error(self):
        m=app.run(DEMO)['metrics'];self.assertLess(m['departure_headway_rmse'],m['arrival_headway_rmse'])
    def test_hold_bounded(self): self.assertTrue(all(0<=x['hold']<=DEMO['max_hold'] for x in app.run(DEMO)['trace']))
    def test_zero_hold(self):
        d=copy.deepcopy(DEMO);d['max_hold']=0;self.assertEqual(app.run(d)['departures'],d['arrivals'])
    def test_single_bus(self): self.assertEqual(app.run({'arrivals':[5],'target':10,'max_hold':6})['metrics']['total_hold_minutes'],0)
    def test_empty(self): self.assertEqual(app.run({'arrivals':[],'target':10,'max_hold':6})['departures'],[])
    def test_unordered(self):
        with self.assertRaises(ValueError): app.run({'arrivals':[3,2],'target':10,'max_hold':6})
    def test_invalid_target(self):
        with self.assertRaises(ValueError): app.run({'arrivals':[3],'target':0,'max_hold':6})

if __name__ == "__main__": unittest.main()
