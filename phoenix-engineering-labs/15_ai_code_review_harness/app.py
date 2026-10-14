"""Evaluate reviewed local candidate functions against failure-preservation cases."""
from phoenix_common import InputError, Report, obj, rows, text


def strict_candidate(jobs):
    if not isinstance(jobs, list) or not jobs:
        return 3
    seen = set()
    failure = incomplete = False
    for job in jobs:
        if not isinstance(job, dict) or not isinstance(job.get("id"), str) or not job["id"].strip() or job["id"] in seen:
            return 3
        seen.add(job["id"])
        code = job.get("exit_code")
        validated = job.get("validated")
        if code is not None and (isinstance(code, bool) or not isinstance(code, int)):
            return 3
        if validated is not None and not isinstance(validated, bool):
            return 3
        incomplete |= code is None or validated is None
        failure |= (code is not None and code != 0) or validated is False
    return 2 if incomplete else 1 if failure else 0


def false_success_candidate(jobs):
    # Intentionally defective: a process wrapper that always reports success.
    return 0


def last_result_candidate(jobs):
    # Intentionally defective: loses an earlier failure when the last job succeeds.
    return 0 if jobs and jobs[-1].get("exit_code") == 0 else 1


CANDIDATES = {"strict": strict_candidate, "false_success": false_success_candidate, "last_result": last_result_candidate}
CASES = [
    ("verified_success", [{"id": "a", "exit_code": 0, "validated": True}], 0),
    ("earlier_failure", [{"id": "a", "exit_code": 1, "validated": False}, {"id": "b", "exit_code": 0, "validated": True}], 1),
    ("unverified_workflow", [{"id": "a", "exit_code": 0, "validated": False}], 1),
    ("missing_exit_code", [{"id": "a", "exit_code": None, "validated": True}], 2),
    ("missing_validation", [{"id": "a", "exit_code": 0}], 2),
    ("empty_evidence", [], 3),
    ("boolean_exit_code", [{"id": "a", "exit_code": False, "validated": True}], 3),
    ("string_exit_code", [{"id": "a", "exit_code": "0", "validated": True}], 3),
    ("terminated_process", [{"id": "a", "exit_code": -9, "validated": True}], 1),
    ("duplicate_jobs", [{"id": "a", "exit_code": 0, "validated": True}, {"id": "a", "exit_code": 0, "validated": True}], 3),
]


def evaluate(data, now):
    obj(data)
    selected = [text(x, "candidate") for x in rows(data.get("candidates"), "candidates")]
    if len(set(selected)) != len(selected):
        raise InputError("duplicate candidate")
    report = Report()
    assessments = []
    for name in selected:
        text(name, "candidate")
        if name not in CANDIDATES:
            raise InputError("candidate is not in the reviewed local allowlist")
        results = []
        for case, evidence, expected in CASES:
            actual = CANDIDATES[name](evidence)
            passed = actual == expected
            results.append({"case": case, "expected": expected, "actual": actual, "passed": passed})
            if not passed:
                report.issue(name, "candidate_case_failed", "Candidate failed evaluation case " + case + ".")
        assessments.append({"candidate": name, "passed": sum(r["passed"] for r in results), "total": len(results), "cases": results})
    return report.finish(assessments=assessments,
                         policy_scope="Reviewed bundled functions and ten local cases; no LLM calls, arbitrary-code execution or production quality score.")
