import unittest, copy, json, math, itertools, tempfile
from pathlib import Path
import app
DEMO = json.loads((Path(__file__).parents[1]/"fixtures/demo.json").read_text())
class Tests(unittest.TestCase):
    def test_acknowledged_once(self): self.assertEqual(app.run(DEMO)['delivered'],['M1'])
    def test_expiry(self): self.assertEqual(app.run(DEMO)['expired'],['M2'])
    def test_duplicate_suppression(self): self.assertEqual(app.run(DEMO)['metrics']['duplicate_enqueues'],1)
    def test_no_offline_send(self): self.assertFalse(any(x['op']=='send' and x['time']==1 for x in app.run(DEMO)['trace']))
    def test_retry_interval(self):
        d={'retry':3,'events':[{'time':0,'op':'enqueue','id':'A','ttl':20,'body':'x'}]+[{'time':t,'op':'tick','online':True} for t in range(7)]};self.assertEqual([x['time'] for x in app.run(d)['trace'] if x['op']=='send'],[0,3,6])
    def test_unknown_ack_not_delivered(self):
        r=app.run({'retry':1,'events':[{'time':0,'op':'ack','id':'unknown'}]});self.assertEqual(r['delivered'],[])
    def test_exact_expiry(self):
        d={'retry':1,'events':[{'time':0,'op':'enqueue','id':'A','ttl':2,'body':'x'},{'time':2,'op':'tick','online':True}]};self.assertEqual(app.run(d)['metrics']['send_attempts'],0)
    def test_negative_ttl(self):
        d=copy.deepcopy(DEMO);d['events'][0]['ttl']=-1
        with self.assertRaises(ValueError): app.run(d)

if __name__ == "__main__": unittest.main()
