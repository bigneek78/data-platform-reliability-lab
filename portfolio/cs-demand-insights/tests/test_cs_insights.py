import tempfile
import unittest
from pathlib import Path
from cs_insights import overlay_forecast, forecast_quality, summarize_drivers

class AnalyticsTests(unittest.TestCase):
    def test_central_overlay(self):
        self.assertEqual(overlay_forecast(10000, .12, .08), 10304)
    def test_sensitivity(self):
        self.assertEqual(overlay_forecast(10000, .05, .10), 9450)
        self.assertEqual(overlay_forecast(10000, .20, .05), 11400)
    def test_invalid_inputs(self):
        with self.assertRaises(ValueError): overlay_forecast(-1, .1, .1)
        with self.assertRaises(ValueError): overlay_forecast(10, .1, 1.5)
    def test_forecast_quality(self):
        m = forecast_quality([90,110], [100,100])
        self.assertAlmostEqual(m["wape"], .10)
        self.assertAlmostEqual(m["signed_bias"], 0.0)
    def test_underforecasting(self):
        self.assertAlmostEqual(forecast_quality([90],[100])["signed_bias"], -.10)
    def test_zero_actual_raises(self):
        with self.assertRaises(ValueError): forecast_quality([0],[0])
    def test_driver_summary(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"contacts.csv"
            p.write_text("driver,contacts\nPlayback,7\nAccount,3\nPlayback,2\n")
            x=summarize_drivers(p)
            self.assertEqual(x[0][0], "Playback")
            self.assertEqual(x[0][1], 9)
            self.assertAlmostEqual(x[0][2], .75)

if __name__=="__main__":
    unittest.main()
