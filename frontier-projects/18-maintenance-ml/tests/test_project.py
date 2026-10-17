import unittest, copy, json, math, itertools, tempfile
from pathlib import Path
import app
DEMO = json.loads((Path(__file__).parents[1]/"fixtures/demo.json").read_text())
class Tests(unittest.TestCase):
    def test_holdout_accounting(self):
        r=app.run(DEMO);self.assertEqual(sum(r['confusion'].values()),80)
    def test_loss_falls(self):
        m=app.run(DEMO)['metrics'];self.assertLess(m['final_log_loss'],m['initial_log_loss'])
    def test_holdout_quality_on_fixture(self): self.assertGreater(app.run(DEMO)['metrics']['holdout_accuracy'],.85)
    def test_shift_review(self): self.assertTrue(app.run(DEMO)['drift_review'])
    def test_deterministic(self): self.assertEqual(app.run(DEMO),app.run(DEMO))
    def test_scaler_reference(self):
        mean,scale=app.fit_scaler([[0,10],[2,14]]);self.assertEqual(mean,[1,12]);self.assertEqual(scale,[1,2])
    def test_split_counts(self):
        m=app.run(DEMO)['metrics'];self.assertEqual(m['training_rows']+m['holdout_rows'],320)
    def test_invalid_rate(self):
        d=copy.deepcopy(DEMO);d['learning_rate']=0
        with self.assertRaises(ValueError): app.run(d)

if __name__ == "__main__": unittest.main()
