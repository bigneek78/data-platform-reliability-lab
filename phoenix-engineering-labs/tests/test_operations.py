import copy
import unittest

from phoenix_common import InputError
from tests.helpers import NOW, sample, codes


class QueueTests(unittest.TestCase):
    def setUp(self): self.app,self.data=sample(1)

    def test_ownership_routing_and_closure_all_visible(self):
        self.assertTrue({"unassigned","routing_review","unverified_closure","sla_threshold"} <= codes(self.app.evaluate(self.data,NOW)))

    def test_exact_sla_boundary_flagged(self):
        self.data["tickets"][0]["opened_at"]="2026-10-13T08:00:00Z"
        self.assertIn("sla_threshold",codes(self.app.evaluate(self.data,NOW)))

    def test_below_sla_boundary_not_flagged(self):
        self.data["tickets"][0]["opened_at"]="2026-10-13T08:00:01Z"
        self.assertNotIn("sla_threshold",codes(self.app.evaluate(self.data,NOW)))

    def test_verified_closed_ticket_has_no_open_age_finding(self):
        ticket=self.data["tickets"][1];ticket["resolution_verified"]=True;ticket["opened_at"]="2026-01-01T00:00:00Z"
        self.data["tickets"]=[ticket]
        self.assertEqual(self.app.evaluate(self.data,NOW)["exit_code"],0)

    def test_duplicate_ticket_rejected(self):
        self.data["tickets"].append(copy.deepcopy(self.data["tickets"][0]))
        with self.assertRaises(InputError):self.app.evaluate(self.data,NOW)

    def test_unknown_severity_rejected(self):
        self.data["tickets"][0]["severity"]="emergency"
        with self.assertRaises(InputError):self.app.evaluate(self.data,NOW)

    def test_stale_queue_retains_failures(self):
        self.data["observed_at"]="2026-10-13T09:00:00Z"
        out=self.app.evaluate(self.data,NOW);self.assertEqual(out["exit_code"],2);self.assertIn("unverified_closure",codes(out))

    def test_healthy_queue_clear(self):
        self.data["tickets"]=[{"id":"one","state":"open","opened_at":"2026-10-13T11:00:00Z","severity":"normal","owner":"ops","queue":"ops"}]
        self.assertEqual(self.app.evaluate(self.data,NOW)["exit_code"],0)


class IdentityTests(unittest.TestCase):
    def setUp(self): self.app,self.data=sample(2)

    def test_later_success_does_not_hide_failed_cluster(self):
        out=self.app.evaluate(self.data,NOW);self.assertEqual(out["recent_failures"],3);self.assertIn("failure_cluster",codes(out));self.assertIn("expired",codes(out))

    def test_missing_mapping_retains_expiry(self):
        out=self.app.evaluate(self.data,NOW);self.assertEqual(out["exit_code"],2);self.assertIn("expired",codes(out))

    def test_exact_event_window_is_included(self):
        self.data["events"]=[{"id":"one","at":"2026-10-13T11:30:00Z","outcome":"failure"}]
        self.assertEqual(self.app.evaluate(self.data,NOW)["recent_failures"],1)

    def test_outside_event_window_excluded(self):
        self.data["events"]=[{"id":"one","at":"2026-10-13T11:29:59Z","outcome":"failure"}]
        self.assertEqual(self.app.evaluate(self.data,NOW)["recent_failures"],0)

    def test_exact_expiry_is_expired(self):
        self.data["certificate"]["valid_to"]="2026-10-13T12:00:00Z"
        self.assertIn("expired",codes(self.app.evaluate(self.data,NOW)))

    def test_valid_metadata_and_success_clear(self):
        self.data["certificate"].update(valid_to="2027-01-01T00:00:00Z",mapping_valid=True)
        self.data["events"]=[{"id":"one","at":"2026-10-13T11:59:00Z","outcome":"success"}]
        self.assertEqual(self.app.evaluate(self.data,NOW)["exit_code"],0)

    def test_failed_chain_not_hidden(self):
        self.data["certificate"]["chain_valid"]=False
        self.assertIn("chain_valid",codes(self.app.evaluate(self.data,NOW)))

    def test_inverted_validity_rejected(self):
        self.data["certificate"]["valid_from"]="2027-01-01T00:00:00Z"
        with self.assertRaises(InputError):self.app.evaluate(self.data,NOW)


class WindowsTests(unittest.TestCase):
    def setUp(self): self.app,self.data=sample(3)

    def test_failed_host_not_reported_healthy(self):
        out=self.app.evaluate(self.data,NOW);self.assertEqual(out["exit_code"],2);self.assertIn("collection_failed",codes(out))

    def test_stopped_service_retained_with_failed_host(self):
        self.assertIn("service_not_running",codes(self.app.evaluate(self.data,NOW)))

    def test_missing_expected_service_incomplete(self):
        self.data["hosts"]=self.data["hosts"][:1];self.data["hosts"][0]["services"]=self.data["hosts"][0]["services"][:1]
        self.assertIn("service_missing",codes(self.app.evaluate(self.data,NOW)))

    def test_all_expected_services_running_clear(self):
        self.data["hosts"]=self.data["hosts"][:1]
        for s in self.data["hosts"][0]["services"]:s["state"]="Running"
        self.assertEqual(self.app.evaluate(self.data,NOW)["exit_code"],0)

    def test_duplicate_service_rejected(self):
        self.data["hosts"][0]["services"].append(copy.deepcopy(self.data["hosts"][0]["services"][0]))
        with self.assertRaises(InputError):self.app.evaluate(self.data,NOW)

    def test_unknown_state_is_incomplete(self):
        self.data["hosts"][0]["services"][0]["state"]="Unknown"
        self.assertIn("state_unknown",codes(self.app.evaluate(self.data,NOW)))

    def test_service_name_case_does_not_create_missing_evidence(self):
        self.data["hosts"]=self.data["hosts"][:1]
        self.data["expected_services"]=["w32time","eventlog"]
        self.assertNotIn("service_missing",codes(self.app.evaluate(self.data,NOW)))

    def test_case_aliased_expected_names_rejected(self):
        self.data["expected_services"]=["W32Time","w32time"]
        with self.assertRaises(InputError):self.app.evaluate(self.data,NOW)

    def test_case_aliased_collected_names_rejected(self):
        self.data["hosts"][0]["services"].append({"name":"w32time","state":"Running"})
        with self.assertRaises(InputError):self.app.evaluate(self.data,NOW)


class PatchTests(unittest.TestCase):
    def setUp(self): self.app,self.data=sample(5)

    def healthy(self):
        self.data["hosts"][0].update(root_free_gib=2,backup_verified=True,reboot_authorized=True)

    def test_missing_backup_does_not_hide_disk_or_reboot(self):
        out=self.app.evaluate(self.data,NOW);self.assertEqual(out["exit_code"],2);self.assertTrue({"disk_capacity","reboot_not_authorized","backup_verified_unknown"}<=codes(out))

    def test_exact_disk_requirement_accepted(self):
        self.healthy();self.assertEqual(self.app.evaluate(self.data,NOW)["exit_code"],0)

    def test_window_end_is_not_authorized_time(self):
        self.data["maintenance_window"]["end"]="2026-10-13T12:00:00Z"
        self.assertIn("outside_window",codes(self.app.evaluate(self.data,NOW)))

    def test_window_start_is_inside(self):
        self.healthy();self.data["maintenance_window"]["start"]="2026-10-13T12:00:00Z"
        self.assertNotIn("outside_window",codes(self.app.evaluate(self.data,NOW)))

    def test_unapproved_change_flagged(self):
        self.data["maintenance_window"]["approved"]=False
        self.assertIn("not_approved",codes(self.app.evaluate(self.data,NOW)))

    def test_unsupported_os_flagged(self):
        self.data["hosts"][0]["os_family"]="Debian"
        self.assertIn("unsupported_os",codes(self.app.evaluate(self.data,NOW)))

    def test_no_reboot_needed_does_not_require_authorization(self):
        self.healthy();self.data["hosts"][0].update(reboot_required=False,reboot_authorized=False)
        self.assertNotIn("reboot_not_authorized",codes(self.app.evaluate(self.data,NOW)))
