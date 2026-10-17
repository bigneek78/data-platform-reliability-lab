import unittest, copy, json, math, itertools, tempfile
from pathlib import Path
import app
DEMO = json.loads((Path(__file__).parents[1]/"fixtures/demo.json").read_text())
class Tests(unittest.TestCase):
    def test_latch(self): self.assertEqual([x['state'] for x in app.run(DEMO)['trace']],['READY','READY','STOP','STOP','STOP','READY'])
    def test_exact_age(self):
        d={'max_age':2,'events':[{'time':0,'age':2,'estop':False,'reset':False}]};self.assertEqual(app.run(d)['trace'][0]['state'],'READY')
    def test_stale_reset_rejected(self):
        d={'max_age':2,'events':[{'time':0,'age':3,'estop':False,'reset':True}]};self.assertEqual(app.run(d)['trace'][0]['state'],'STOP')
    def test_healthy_reset(self): self.assertEqual(app.run(DEMO)['trace'][-1]['state'],'READY')
    def test_empty(self): self.assertEqual(app.run({'max_age':1,'events':[]})['trace'],[])
    def test_negative_age(self):
        d=copy.deepcopy(DEMO);d['events'][0]['age']=-1
        with self.assertRaises(ValueError): app.run(d)
    def test_time_reversal(self):
        d=copy.deepcopy(DEMO);d['events'][2]['time']=0
        with self.assertRaises(ValueError): app.run(d)
    def test_bool_controls(self):
        d=copy.deepcopy(DEMO);d['events'][0]['estop']='false'
        with self.assertRaises(ValueError): app.run(d)

if __name__ == "__main__": unittest.main()
