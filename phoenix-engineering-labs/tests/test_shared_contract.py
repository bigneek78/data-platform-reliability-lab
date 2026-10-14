import unittest
from datetime import datetime

from phoenix_common import InputError, Report, number, strict_json, stamp, elapsed
from tests.helpers import NOW


class SharedContractTests(unittest.TestCase):
    def test_naive_time_rejected(self):
        with self.assertRaises(InputError): stamp("2026-10-13T12:00:00")

    def test_timezone_offsets_equivalent(self):
        self.assertEqual(stamp("2026-10-13T08:00:00-04:00"), NOW)

    def test_future_observation_rejected(self):
        with self.assertRaises(InputError): elapsed("2026-10-13T12:01:00Z", NOW)

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(InputError): strict_json('{"approved":false,"approved":true}')

    def test_json_nan_rejected(self):
        with self.assertRaises(InputError): strict_json('{"value":NaN}')

    def test_json_infinity_rejected(self):
        with self.assertRaises(InputError): strict_json('{"value":Infinity}')

    def test_boolean_is_not_numeric_evidence(self):
        with self.assertRaises(InputError): number(True)

    def test_fraction_is_not_integer_evidence(self):
        with self.assertRaises(InputError): number(1.5, integer=True)

    def test_incomplete_preserves_known_failure(self):
        r=Report(); r.issue("a","failed","Known failure"); r.gap("b","unknown","Unknown evidence")
        out=r.finish(); self.assertEqual(out["exit_code"],2); self.assertEqual(len(out["findings"]),1)

    def test_freshness_boundary_is_inclusive(self):
        r=Report();r.observe({"observed_at":"2026-10-13T11:00:00Z","max_age_minutes":60},NOW)
        self.assertEqual(r.finish()["exit_code"],0)

    def test_older_evidence_is_incomplete(self):
        r=Report();r.observe({"observed_at":"2026-10-13T10:59:59Z","max_age_minutes":60},NOW)
        self.assertEqual(r.finish()["exit_code"],2)
