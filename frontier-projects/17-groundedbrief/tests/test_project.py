import unittest, copy, json, math, itertools, tempfile
from pathlib import Path
import app
DEMO = json.loads((Path(__file__).parents[1]/"fixtures/demo.json").read_text())
class Tests(unittest.TestCase):
    def test_correct_source(self): self.assertEqual(app.run(DEMO)['evidence']['citation'],'RB-01')
    def test_quote_is_original_span(self):
        e=app.run(DEMO)['evidence'];self.assertIn(e['quote'],next(x['text'] for x in DEMO['documents'] if x['id']==e['citation']))
    def test_abstains_unknown(self):
        d=copy.deepcopy(DEMO);d['query']='lunar geology zircon';self.assertEqual(app.run(d)['decision'],'ABSTAIN')
    def test_empty_query_abstains(self):
        d=copy.deepcopy(DEMO);d['query']='';self.assertIsNone(app.run(d)['evidence'])
    def test_similarity_bounds(self): self.assertTrue(all(0<=x['score']<=1+1e-12 for x in app.run(DEMO)['trace']))
    def test_deterministic(self): self.assertEqual(app.run(DEMO),app.run(DEMO))
    def test_duplicate_sources(self):
        d=copy.deepcopy(DEMO);d['documents'][1]['id']='RB-01'
        with self.assertRaises(ValueError): app.run(d)
    def test_threshold_invalid(self):
        d=copy.deepcopy(DEMO);d['threshold']=2
        with self.assertRaises(ValueError): app.run(d)

if __name__ == "__main__": unittest.main()
