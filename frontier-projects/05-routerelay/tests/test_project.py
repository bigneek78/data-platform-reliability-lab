import unittest, copy, json, math, itertools, tempfile
from pathlib import Path
import app
DEMO = json.loads((Path(__file__).parents[1]/"fixtures/demo.json").read_text())
class Tests(unittest.TestCase):
    def test_closure_detour(self): self.assertEqual(app.run(DEMO)['cost'],7)
    def test_open_shortest(self):
        d=copy.deepcopy(DEMO);d['closed']=[];self.assertEqual(app.run(d)['cost'],6)
    def test_path(self): self.assertEqual(app.run(DEMO)['path'],['Depot','A','Clinic'])
    def test_unreachable(self):
        d=copy.deepcopy(DEMO);d['closed']=['e1','e3'];self.assertIsNone(app.run(d)['cost'])
    def test_same_node(self):
        d=copy.deepcopy(DEMO);d['goal']='Depot';self.assertEqual(app.run(d)['cost'],0)
    def test_negative(self):
        d=copy.deepcopy(DEMO);d['edges'][0]['cost']=-1
        with self.assertRaises(ValueError): app.run(d)
    def test_unknown_closure(self):
        d=copy.deepcopy(DEMO);d['closed']=['fake']
        with self.assertRaises(ValueError): app.run(d)
    def test_unknown_node(self):
        d=copy.deepcopy(DEMO);d['edges'][0]['target']='missing'
        with self.assertRaises(ValueError): app.run(d)

if __name__ == "__main__": unittest.main()
