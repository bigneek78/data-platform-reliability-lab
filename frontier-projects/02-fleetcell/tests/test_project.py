import unittest, copy, json, math, itertools, tempfile
from pathlib import Path
import app
DEMO = json.loads((Path(__file__).parents[1]/"fixtures/demo.json").read_text())
class Tests(unittest.TestCase):
    def test_optimum(self): self.assertEqual(app.run(DEMO)['metrics']['optimal_distance'],3)
    def test_one_robot_per_job(self):
        r=app.run(DEMO)['assignments'];self.assertEqual(len({x['robot'] for x in r}),len(r))
    def test_capabilities(self):
        r=app.run(DEMO);lookup={x['id']:x for x in DEMO['robots']}
        for a in r['assignments']: self.assertIn(next(j['skill'] for j in DEMO['jobs'] if j['id']==a['job']),lookup[a['robot']]['skills'])
    def test_exhaustive_reference(self):
        candidates=[]
        for perm in itertools.permutations(DEMO['robots']):
            if all(j['skill'] in r['skills'] for j,r in zip(DEMO['jobs'],perm)): candidates.append(sum(abs(j['x']-r['x'])+abs(j['y']-r['y']) for j,r in zip(DEMO['jobs'],perm)))
        self.assertEqual(app.run(DEMO)['metrics']['optimal_distance'],min(candidates))
    def test_infeasible(self):
        d=copy.deepcopy(DEMO);d['jobs'][0]['skill']='fly'
        with self.assertRaises(ValueError): app.run(d)
    def test_empty(self): self.assertEqual(app.run({'robots':[],'jobs':[]})['assignments'],[])
    def test_duplicate(self):
        d=copy.deepcopy(DEMO);d['robots'][1]['id']='R1'
        with self.assertRaises(ValueError): app.run(d)
    def test_nonfinite(self):
        d=copy.deepcopy(DEMO);d['robots'][0]['x']=float('nan')
        with self.assertRaises(ValueError): app.run(d)

if __name__ == "__main__": unittest.main()
