import unittest, copy, json, math, itertools, tempfile
from pathlib import Path
import app
DEMO = json.loads((Path(__file__).parents[1]/"fixtures/demo.json").read_text())
class Tests(unittest.TestCase):
    def test_maximum_bookings(self): self.assertEqual(app.run(DEMO)['metrics']['booked'],3)
    def test_specialized_slot_preserved(self): self.assertEqual(next(x['slot'] for x in app.run(DEMO)['bookings'] if x['request']=='Q2'),'S1')
    def test_unbooked_explicit(self): self.assertEqual(app.run(DEMO)['unbooked'],['Q4'])
    def test_unique_slots(self):
        b=app.run(DEMO)['bookings'];self.assertEqual(len({x['slot'] for x in b}),len(b))
    def test_wait_objective(self): self.assertEqual(app.run(DEMO)['metrics']['total_wait_units'],6)
    def test_window_boundary(self):
        d={'slots':[{'id':'S','time':10,'resources':[]}],'requests':[{'id':'Q','earliest':10,'latest':10,'resources':[]}]};self.assertEqual(app.run(d)['metrics']['booked'],1)
    def test_empty_slots(self):
        d=copy.deepcopy(DEMO);d['slots']=[];self.assertEqual(app.run(d)['metrics']['booked'],0)
    def test_bad_window(self):
        d=copy.deepcopy(DEMO);d['requests'][0]['latest']=0
        with self.assertRaises(ValueError): app.run(d)

if __name__ == "__main__": unittest.main()
