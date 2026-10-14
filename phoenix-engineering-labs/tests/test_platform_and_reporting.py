import copy
import unittest

from phoenix_common import InputError
from tests.helpers import NOW, sample, codes


class KubernetesTests(unittest.TestCase):
    def setUp(self):self.app,self.data=sample(10)

    def healthy(self):
        status=self.data["deployment"]["status"]
        status.update(observedGeneration=3,replicas=2,updatedReplicas=2,readyReplicas=2,availableReplicas=2,conditions=[])
        self.data["pods"][0]["status"]["containerStatuses"][0].update(ready=True,state={"running":{}})

    def test_stale_generation_retains_crash_and_deadline(self):
        out=self.app.evaluate(self.data,NOW);self.assertEqual(out["exit_code"],2)
        self.assertTrue({"controller_not_current","container_waiting","progress_deadline"}<=codes(out))

    def test_current_ready_objects_clear_within_scope(self):
        self.healthy();self.assertEqual(self.app.evaluate(self.data,NOW)["exit_code"],0)

    def test_available_replicas_do_not_hide_old_generation(self):
        self.healthy();self.data["deployment"]["status"]["observedGeneration"]=2
        self.assertEqual(self.app.evaluate(self.data,NOW)["exit_code"],2)

    def test_impossible_controller_generation_rejected(self):
        self.data["deployment"]["status"]["observedGeneration"]=4
        with self.assertRaises(InputError):self.app.evaluate(self.data,NOW)

    def test_missing_pod_evidence_incomplete(self):
        self.healthy();self.data["pods"]=[]
        self.assertIn("no_pod_evidence",codes(self.app.evaluate(self.data,NOW)))

    def test_missing_active_container_evidence_incomplete(self):
        self.healthy();self.data["pods"][0]["status"]["containerStatuses"]=[]
        self.assertIn("container_evidence_missing",codes(self.app.evaluate(self.data,NOW)))

    def test_pending_pod_visible(self):
        self.healthy();self.data["pods"][0]["status"]["phase"]="Pending"
        self.assertIn("pod_pending",codes(self.app.evaluate(self.data,NOW)))

    def test_scaled_to_zero_is_inactive_within_metadata_scope(self):
        self.healthy();self.data["deployment"]["spec"]["replicas"]=0;self.data["pods"]=[]
        self.data["deployment"]["status"].update(replicas=0,updatedReplicas=0,readyReplicas=0,availableReplicas=0)
        out=self.app.evaluate(self.data,NOW);self.assertEqual(out["exit_code"],0);self.assertEqual(out["desired_replicas"],0)

    def test_old_replica_surge_not_completed_rollout(self):
        self.healthy();self.data["deployment"]["status"]["replicas"]=3
        self.assertIn("rollout_not_complete",codes(self.app.evaluate(self.data,NOW)))

    def test_duplicate_pod_rejected(self):
        self.data["pods"].append(copy.deepcopy(self.data["pods"][0]))
        with self.assertRaises(InputError):self.app.evaluate(self.data,NOW)


class CertificateTests(unittest.TestCase):
    def setUp(self):self.app,self.data=sample(11)

    def test_expiry_ownership_and_approaching_rotation_visible(self):
        self.assertTrue({"expired","rotation_due","rotation_owner_missing"}<=codes(self.app.evaluate(self.data,NOW)))

    def test_rotation_order_is_expiry_order(self):
        self.assertEqual([r["id"] for r in self.app.evaluate(self.data,NOW)["rotation_order"]],["lab-cert-a","lab-cert-b","lab-cert-c"])

    def test_warning_boundary_included(self):
        self.data["certificates"]=[self.data["certificates"][2]]
        self.data["certificates"][0]["valid_to"]="2026-11-12T12:00:00Z"
        self.assertIn("rotation_due",codes(self.app.evaluate(self.data,NOW)))

    def test_current_owned_future_certificate_clear(self):
        self.data["certificates"]=[self.data["certificates"][2]]
        self.assertEqual(self.app.evaluate(self.data,NOW)["exit_code"],0)

    def test_inverted_dates_rejected(self):
        self.data["certificates"][0]["valid_from"]="2027-01-01T00:00:00Z"
        with self.assertRaises(InputError):self.app.evaluate(self.data,NOW)

    def test_not_yet_valid_interval_visible(self):
        self.data["certificates"][2]["valid_from"]="2026-10-14T00:00:00Z"
        self.assertIn("not_yet_valid",codes(self.app.evaluate(self.data,NOW)))


class ChangeTests(unittest.TestCase):
    def setUp(self):self.app,self.data=sample(13)

    def test_dependency_waves_and_reverse_rollback(self):
        out=self.app.evaluate(self.data,NOW)
        self.assertEqual(out["execution_waves"],[["capture"],["identity","update"],["workflow"]])
        self.assertEqual(out["rollback_order"],["workflow","update","identity","capture"])

    def test_cycle_never_emits_partial_execution_plan(self):
        self.data["tasks"][0]["depends_on"]=["workflow"]
        out=self.app.evaluate(self.data,NOW);self.assertFalse(out["graph_valid"]);self.assertEqual(out["execution_waves"],[])

    def test_missing_dependency_rejected(self):
        self.data["tasks"][1]["depends_on"]=["missing"]
        with self.assertRaises(InputError):self.app.evaluate(self.data,NOW)

    def test_unknown_owner_and_approval_incomplete(self):
        self.data["approved"]=None;self.data["tasks"][0]["owner"]=None
        self.assertEqual(self.app.evaluate(self.data,NOW)["exit_code"],2)

    def test_missing_validation_blocks_clear_result(self):
        self.data["tasks"][0]["validation"]=[]
        self.assertIn("validation_missing",codes(self.app.evaluate(self.data,NOW)))

    def test_missing_rollback_blocks_clear_result(self):
        self.data["tasks"][0]["rollback"]=None
        self.assertIn("rollback_missing",codes(self.app.evaluate(self.data,NOW)))

    def test_duplicate_dependency_rejected(self):
        self.data["tasks"][1]["depends_on"]=["capture","capture"]
        with self.assertRaises(InputError):self.app.evaluate(self.data,NOW)

    def test_unapproved_plan_flagged(self):
        self.data["approved"]=False
        self.assertIn("not_approved",codes(self.app.evaluate(self.data,NOW)))


class IncidentTests(unittest.TestCase):
    def setUp(self):self.app,self.data=sample(14)

    def test_hypothesis_explicit_and_known_identifiers_redacted(self):
        text=self.app.evaluate(self.data,NOW)["markdown"]
        self.assertIn("hypothesis (unconfirmed)",text);self.assertNotIn("demo@example.invalid",text);self.assertNotIn("192.0.2.10",text)

    def test_open_incident_preserves_owner_and_next_action(self):
        out=self.app.evaluate(self.data,NOW);self.assertIn("incident_open",codes(out));self.assertIn("Next action:",out["markdown"])

    def test_failed_validation_cannot_support_resolved_state(self):
        self.data["state"]="resolved"
        self.assertIn("validation_failed",codes(self.app.evaluate(self.data,NOW)))

    def test_missing_validation_is_incomplete(self):
        self.data["state"]="resolved";self.data["events"]=self.data["events"][:-1]
        self.assertIn("closure_unverified",codes(self.app.evaluate(self.data,NOW)))

    def test_later_failure_prevents_closure(self):
        self.data["state"]="resolved";self.data["events"][-1]["successful"]=True
        self.data["events"].append({"id":"later","at":"2026-10-13T11:40:00Z","kind":"finding","severity":"error","summary":"The demo action fails again"})
        self.assertIn("failure_after_validation",codes(self.app.evaluate(self.data,NOW)))

    def test_conflicting_simultaneous_validations_incomplete(self):
        self.data["state"]="resolved";other=copy.deepcopy(self.data["events"][-1]);other.update(id="other",successful=True);self.data["events"].append(other)
        self.assertIn("validation_conflict",codes(self.app.evaluate(self.data,NOW)))

    def test_order_is_stable_for_shuffled_events(self):
        initial=self.app.evaluate(self.data,NOW)["markdown"];self.data["events"].reverse()
        self.assertEqual(initial,self.app.evaluate(self.data,NOW)["markdown"])

    def test_successful_final_validation_clear(self):
        self.data["state"]="resolved";self.data["events"][-1]["successful"]=True
        self.assertEqual(self.app.evaluate(self.data,NOW)["exit_code"],0)

    def test_token_patterns_redacted(self):
        value=self.app.redact("Bearer LABTOKEN token=DEMO-TOKEN password=DEMO-PASSWORD")
        for token in ("LABTOKEN","DEMO-TOKEN","DEMO-PASSWORD"):self.assertNotIn(token,value)


class AiHarnessTests(unittest.TestCase):
    def setUp(self):self.app,self.data=sample(15)

    def test_strict_candidate_passes_every_defined_case(self):
        self.data["candidates"]=["strict"];out=self.app.evaluate(self.data,NOW)
        self.assertEqual(out["exit_code"],0);self.assertEqual(out["assessments"][0]["passed"],10)

    def test_mutants_are_detected(self):
        out=self.app.evaluate(self.data,NOW)
        self.assertEqual(out["exit_code"],1)
        for row in out["assessments"][1:]:self.assertLess(row["passed"],row["total"])

    def test_earlier_failed_process_is_preserved(self):
        jobs=[{"id":"one","exit_code":5,"validated":True},{"id":"two","exit_code":0,"validated":True}]
        self.assertEqual(self.app.strict_candidate(jobs),1);self.assertEqual(self.app.last_result_candidate(jobs),0)

    def test_missing_result_keeps_known_failure_incomplete(self):
        jobs=[{"id":"one","exit_code":1,"validated":False},{"id":"two","exit_code":None,"validated":None}]
        self.assertEqual(self.app.strict_candidate(jobs),2)

    def test_arbitrary_candidate_not_loaded(self):
        self.data["candidates"]=["external-file.py"]
        with self.assertRaises(InputError):self.app.evaluate(self.data,NOW)

    def test_non_string_candidate_rejected(self):
        self.data["candidates"]=[{"name":"strict"}]
        with self.assertRaises(InputError):self.app.evaluate(self.data,NOW)
