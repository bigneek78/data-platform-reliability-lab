import unittest, copy, json, math, itertools, tempfile
from pathlib import Path
import app
DEMO = json.loads((Path(__file__).parents[1]/"fixtures/demo.json").read_text())
class Tests(unittest.TestCase):
    def test_cheapest_slot(self):
        d={'prices':[10,1],'capacity':[1,1],'vehicles':[{'id':'A','arrival':0,'departure':2,'need':1,'rate':1}]};r=app.run(d);self.assertEqual(r['metrics']['cost_units'],1);self.assertEqual(r['schedule'][0]['hour'],1)
    def test_energy_conservation(self):
        r=app.run(DEMO);self.assertEqual(sum(r['trace']),r['metrics']['delivered_kwh']);self.assertEqual(r['metrics']['unmet_kwh'],0)
    def test_site_capacity(self): self.assertTrue(all(x<=c for x,c in zip(app.run(DEMO)['trace'],DEMO['capacity'])))
    def test_availability(self):
        for x in app.run(DEMO)['schedule']:
            v=next(v for v in DEMO['vehicles'] if v['id']==x['vehicle']);self.assertTrue(v['arrival']<=x['hour']<v['departure']);self.assertLessEqual(x['kwh'],v['rate'])
    def test_unmet_explicit(self):
        d=copy.deepcopy(DEMO);d['capacity']=[0]*4;self.assertEqual(app.run(d)['metrics']['unmet_kwh'],9)
    def test_residual_reassignment(self):
        d={'prices':[1,2],'capacity':[1,1],'vehicles':[{'id':'flex','arrival':0,'departure':2,'need':1,'rate':1},{'id':'urgent','arrival':0,'departure':1,'need':1,'rate':1}]};self.assertEqual(app.run(d)['metrics']['delivered_kwh'],2)
    def test_invalid_deadline(self):
        d=copy.deepcopy(DEMO);d['vehicles'][0]['departure']=0
        with self.assertRaises(ValueError): app.run(d)
    def test_fractional_energy_rejected(self):
        d=copy.deepcopy(DEMO);d['capacity'][0]=.5
        with self.assertRaises(ValueError): app.run(d)

if __name__ == "__main__": unittest.main()
