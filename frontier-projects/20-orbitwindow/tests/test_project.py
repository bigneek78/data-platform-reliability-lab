import unittest, copy, json, math, itertools, tempfile
from pathlib import Path
import app
DEMO = json.loads((Path(__file__).parents[1]/"fixtures/demo.json").read_text())
class Tests(unittest.TestCase):
    def test_expected_optimum(self): self.assertEqual(app.run(DEMO)['metrics']['total_value'],18)
    def test_expected_contacts(self): self.assertEqual(app.run(DEMO)['selected'],['SAT-A','SAT-C','SAT-F'])
    def test_blackout_excludes(self): self.assertEqual(app.run(DEMO)['excluded_by_blackout'],['SAT-D','SAT-E'])
    def test_no_overlap(self):
        xs=app.run(DEMO)['trace'];self.assertTrue(all(a['end']<=b['start'] for a,b in zip(xs,xs[1:])))
    def test_bruteforce_reference(self):
        ws=[w for w in DEMO['windows'] if w['id'] not in app.run(DEMO)['excluded_by_blackout']];best=0
        for mask in range(1<<len(ws)):
            xs=sorted([w for i,w in enumerate(ws) if mask>>i&1],key=lambda x:x['start'])
            if all(a['end']<=b['start'] for a,b in zip(xs,xs[1:])):best=max(best,sum(x['value'] for x in xs))
        self.assertEqual(app.run(DEMO)['metrics']['total_value'],best)
    def test_touching_blackout_allowed(self):
        d={'windows':[{'id':'A','start':0,'end':5,'value':3}],'blackouts':[{'start':5,'end':10}]};self.assertEqual(app.run(d)['selected'],['A'])
    def test_empty(self): self.assertEqual(app.run({'windows':[],'blackouts':[]})['selected'],[])
    def test_bad_interval(self):
        with self.assertRaises(ValueError): app.run({'windows':[{'id':'A','start':1,'end':1,'value':1}],'blackouts':[]})

if __name__ == "__main__": unittest.main()
