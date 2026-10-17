import unittest, copy, json, math, itertools, tempfile
from pathlib import Path
import app
DEMO = json.loads((Path(__file__).parents[1]/"fixtures/demo.json").read_text())
class Tests(unittest.TestCase):
    def test_shortest(self):
        r=app.plan(['...','.#.','...'],[0,0],[2,2]);self.assertEqual(r['cost'],4)
    def test_path_edges(self):
        p=app.run(DEMO)['trace'];self.assertTrue(all(abs(a[0]-b[0])+abs(a[1]-b[1])==1 for a,b in zip(p,p[1:])))
    def test_closed_cells_avoided(self):
        self.assertFalse(any(c in app.run(DEMO)['trace'] for c in DEMO['closed']))
    def test_unreachable(self): self.assertEqual(app.plan(['.#.'],[0,0],[0,2])['cost'],-1)
    def test_same_endpoint(self): self.assertEqual(app.plan(['.'],[0,0],[0,0])['cost'],0)
    def test_ragged(self):
        with self.assertRaises(ValueError): app.plan(['..','.'],[0,0],[0,1])
    def test_blocked(self):
        with self.assertRaises(ValueError): app.plan(['.#'],[0,0],[0,1])
    def test_invalid_coordinate(self):
        with self.assertRaises(ValueError): app.plan(['..'],[0,0],[0,1.0])

if __name__ == "__main__": unittest.main()
