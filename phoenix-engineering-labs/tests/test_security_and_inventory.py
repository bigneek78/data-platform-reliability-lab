import copy
import csv
import io
import json
import unittest

from phoenix_common import InputError
from tests.helpers import NOW, sample, codes


class ReplicationTests(unittest.TestCase):
    def setUp(self): self.app,self.raw=sample(4)

    def change(self, **fields):
        reader=csv.DictReader(io.StringIO(self.raw)); names=reader.fieldnames; records=list(reader)
        records[0].update(fields); out=io.StringIO(); writer=csv.DictWriter(out,fieldnames=names);writer.writeheader();writer.writerows(records)
        return out.getvalue()

    def test_error_and_age_both_visible(self):
        self.assertTrue({"replication_error","success_age"}<=codes(self.app.evaluate(self.raw,NOW)))

    def test_current_successful_links_clear(self):
        self.assertEqual(self.app.evaluate(self.change(result=0,last_success="2026-10-13T11:40:00Z"),NOW)["exit_code"],0)

    def test_missing_success_is_unknown(self):
        self.assertIn("success_unknown",codes(self.app.evaluate(self.change(last_success=""),NOW)))

    def test_future_attempt_rejected(self):
        with self.assertRaises(InputError):self.app.evaluate(self.change(last_attempt="2026-10-13T13:00:00Z"),NOW)

    def test_success_later_than_attempt_rejected(self):
        with self.assertRaises(InputError):self.app.evaluate(self.change(last_success="2026-10-13T11:50:00Z"),NOW)

    def test_stale_export_retains_error(self):
        out=self.app.evaluate(self.change(observed_at="2026-10-13T10:00:00Z"),NOW)
        self.assertEqual(out["exit_code"],2);self.assertIn("replication_error",codes(out))

    def test_unsupported_header_rejected(self):
        with self.assertRaises(InputError):self.app.evaluate("source,destination\na,b\n",NOW)


class XccdfTests(unittest.TestCase):
    def setUp(self): self.app,self.raw=sample(6)

    def test_failed_and_unchecked_rules_retained(self):
        out=self.app.evaluate(self.raw,NOW);self.assertEqual(out["exit_code"],2);self.assertIn("rule_failed",codes(out))

    def test_all_pass_clear_within_scope(self):
        raw=self.raw.replace("<result>fail</result>","<result>pass</result>").replace("<result>notchecked</result>","<result>pass</result>")
        self.assertEqual(self.app.evaluate(raw,NOW)["exit_code"],0)

    def test_all_not_applicable_is_not_assessed(self):
        raw=self.raw.replace("<result>pass</result>","<result>notapplicable</result>").replace("<result>fail</result>","<result>notapplicable</result>").replace("<result>notchecked</result>","<result>notapplicable</result>")
        self.assertIn("no_assessed_controls",codes(self.app.evaluate(raw,NOW)))

    def test_fixed_rule_requests_verification(self):
        self.assertIn("rule_unverified",codes(self.app.evaluate(self.raw.replace("<result>fail</result>","<result>fixed</result>"),NOW)))

    def test_unsafe_xml_declaration_rejected(self):
        with self.assertRaises(InputError):self.app.evaluate('<!DOCTYPE a [<!ENTITY b "x">]><a/>',NOW)

    def test_duplicate_rule_rejected(self):
        with self.assertRaises(InputError):self.app.evaluate(self.raw.replace("rule_02","rule_01"),NOW)

    def test_missing_test_result_rejected(self):
        with self.assertRaises(InputError):self.app.evaluate("<Benchmark/>",NOW)

    def test_stale_scan_retains_failed_rule(self):
        out=self.app.evaluate(self.raw.replace("2026-10-13T11:30:00Z","2026-10-11T11:30:00Z"),NOW)
        self.assertIn("stale_evidence",codes(out));self.assertIn("rule_failed",codes(out))


class VulnerabilityTests(unittest.TestCase):
    def setUp(self): self.app,self.data=sample(7)

    def test_exploitation_can_outrank_higher_cvss(self):
        out=self.app.evaluate(self.data,NOW);self.assertEqual(out["prioritized"][0]["id"],"LAB-VULN-001")

    def test_missing_context_is_provisional(self):
        out=self.app.evaluate(self.data,NOW);self.assertEqual(out["exit_code"],2);self.assertTrue(out["prioritized"][2]["provisional"])

    def test_critical_public_boundary_is_p1(self):
        record=self.data["vulnerabilities"][1];record.update(cvss=9,public_facing=True)
        self.assertEqual(next(r for r in self.app.evaluate(self.data,NOW)["prioritized"] if r["id"]==record["id"])["priority"],"P1")

    def test_unverified_remediation_stays_in_review(self):
        self.data["vulnerabilities"][0].update(state="remediated",remediation_verified=False)
        self.assertIn("unverified_remediation",codes(self.app.evaluate(self.data,NOW)))

    def test_verified_remediation_removes_open_findings(self):
        for r in self.data["vulnerabilities"]:r.update(state="remediated",remediation_verified=True)
        self.assertEqual(self.app.evaluate(self.data,NOW)["exit_code"],0)

    def test_cvss_out_of_range_rejected(self):
        self.data["vulnerabilities"][0]["cvss"]=10.1
        with self.assertRaises(InputError):self.app.evaluate(self.data,NOW)

    def test_duplicate_finding_rejected(self):
        self.data["vulnerabilities"].append(copy.deepcopy(self.data["vulnerabilities"][0]))
        with self.assertRaises(InputError):self.app.evaluate(self.data,NOW)


class TerraformTests(unittest.TestCase):
    def setUp(self): self.app,self.data=sample(8)

    def ingress(self):return self.data["resource_changes"][0]["change"]["after"]["ingress"][0]

    def test_public_admin_and_wildcard_grant_visible(self):
        self.assertTrue({"public_admin_ingress","wildcard_allow_review"}<=codes(self.app.evaluate(self.data,NOW)))

    def test_private_admin_range_not_flagged_as_public(self):
        self.ingress()["cidr_blocks"]=["192.0.2.0/24"]
        self.assertNotIn("public_admin_ingress",codes(self.app.evaluate(self.data,NOW)))

    def test_public_ipv6_admin_flagged(self):
        self.ingress().update(cidr_blocks=[],ipv6_cidr_blocks=["::/0"])
        self.assertIn("public_admin_ingress",codes(self.app.evaluate(self.data,NOW)))

    def test_all_protocols_includes_admin_ports(self):
        self.ingress().update(protocol="-1",from_port=0,to_port=0)
        self.assertIn("public_admin_ingress",codes(self.app.evaluate(self.data,NOW)))

    def test_udp_is_not_tcp_admin_policy(self):
        self.ingress()["protocol"]="udp"
        self.assertNotIn("public_admin_ingress",codes(self.app.evaluate(self.data,NOW)))

    def test_icmp_negative_type_code_not_tcp_ports(self):
        self.ingress().update(protocol="icmp",from_port=-1,to_port=-1)
        self.assertNotIn("public_admin_ingress",codes(self.app.evaluate(self.data,NOW)))

    def test_known_exposure_survives_unknown_values(self):
        self.data["resource_changes"][0]["change"]["after_unknown"]={"ingress":True}
        out=self.app.evaluate(self.data,NOW);self.assertEqual(out["exit_code"],2);self.assertIn("public_admin_ingress",codes(out))

    def test_unknown_null_acl_is_incomplete(self):
        change=self.data["resource_changes"][1]["change"];change.update(after={"acl":None},after_unknown={"acl":True})
        self.assertEqual(self.app.evaluate(self.data,NOW)["exit_code"],2)

    def test_unknown_nested_cidr_is_incomplete(self):
        self.ingress()["cidr_blocks"]=None
        self.data["resource_changes"][0]["change"]["after_unknown"]={"ingress":[{"cidr_blocks":True}]}
        self.assertEqual(self.app.evaluate(self.data,NOW)["exit_code"],2)

    def test_deleted_only_plan_not_reported_comprehensively_clear(self):
        self.data["resource_changes"]=self.data["resource_changes"][:1]
        self.data["resource_changes"][0]["change"]["actions"]=["delete"]
        self.assertIn("no_modeled_resources",codes(self.app.evaluate(self.data,NOW)))

    def test_deny_is_not_wildcard_allow(self):
        self.data["resource_changes"][2]["change"]["after"]["policy"]["Statement"][0]["Effect"]="Deny"
        self.assertNotIn("wildcard_allow_review",codes(self.app.evaluate(self.data,NOW)))

    def test_notaction_requests_unmodeled_statement_review(self):
        statement=self.data["resource_changes"][2]["change"]["after"]["policy"]["Statement"][0]
        del statement["Action"];statement["NotAction"]="iam:*"
        self.assertIn("iam_statement_unmodeled",codes(self.app.evaluate(self.data,NOW)))

    def test_raw_policy_values_not_echoed(self):
        self.data["resource_changes"][2]["change"]["after"]["policy"]["Statement"][0]["Condition"]={"StringEquals":{"lab":"SYNTHETIC-SENSITIVE-MARKER"}}
        self.assertNotIn("SYNTHETIC-SENSITIVE-MARKER",json.dumps(self.app.evaluate(self.data,NOW)))

    def test_unsupported_format_major_rejected(self):
        self.data["format_version"]="2.0"
        with self.assertRaises(InputError):self.app.evaluate(self.data,NOW)

    def test_invalid_cidr_rejected(self):
        self.ingress()["cidr_blocks"]=["invalid-network"]
        with self.assertRaises(InputError):self.app.evaluate(self.data,NOW)

    def test_reviewed_private_values_clear_within_scope(self):
        self.ingress()["cidr_blocks"]=["192.0.2.0/24"]
        self.data["resource_changes"][2]["change"]["after"]["policy"]["Statement"][0]["Resource"]="lab-resource"
        self.assertEqual(self.app.evaluate(self.data,NOW)["exit_code"],0)


class InventoryTests(unittest.TestCase):
    def setUp(self): self.app,self.data=sample(9)

    def test_known_drift_missing_and_undeclared_visible(self):
        self.assertTrue({"attribute_drift","resource_not_observed","undeclared_resource"}<=codes(self.app.evaluate(self.data,NOW)))

    def test_equal_inventory_clear(self):
        self.data["observed"]=copy.deepcopy(self.data["desired"])
        self.assertEqual(self.app.evaluate(self.data,NOW)["exit_code"],0)

    def test_partial_inventory_does_not_assert_deletion(self):
        self.data["inventory_complete"]=False
        out=self.app.evaluate(self.data,NOW);self.assertEqual(out["exit_code"],2)
        self.assertFalse(any(r["code"]=="resource_not_observed" for r in out["findings"]))

    def test_missing_attribute_is_incomplete(self):
        del self.data["observed"][0]["attributes"]["environment"]
        self.assertIn("attribute_missing",codes(self.app.evaluate(self.data,NOW)))

    def test_empty_complete_observation_reports_missing_resources(self):
        self.data["observed"]=[]
        self.assertEqual(len(self.app.evaluate(self.data,NOW)["findings"]),2)

    def test_duplicate_resource_rejected(self):
        self.data["observed"].append(copy.deepcopy(self.data["observed"][0]))
        with self.assertRaises(InputError):self.app.evaluate(self.data,NOW)

    def test_attribute_values_not_exposed_in_report(self):
        self.data["desired"][0]["attributes"]["token"]="SYNTHETIC-SENSITIVE-MARKER"
        self.data["observed"][0]["attributes"]["token"]="another-value"
        self.assertNotIn("SYNTHETIC-SENSITIVE-MARKER",json.dumps(self.app.evaluate(self.data,NOW)))
