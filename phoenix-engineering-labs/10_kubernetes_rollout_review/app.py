"""Review supplied Deployment and selected Pod objects without changing a cluster."""
from phoenix_common import InputError, Report, flag, number, obj, rows, text


def evaluate(data, now):
    obj(data)
    report = Report()
    report.observe(data, now)
    deployment = obj(data.get("deployment"), "deployment")
    meta = obj(deployment.get("metadata"), "metadata")
    ident = text(meta.get("name"), "deployment name")
    generation = number(meta.get("generation"), "generation", minimum=1, integer=True)
    spec = obj(deployment.get("spec"), "spec")
    desired = number(spec.get("replicas", 1), "replicas", integer=True)
    status = obj(deployment.get("status", {}), "status")
    observed = status.get("observedGeneration")
    if observed is None:
        report.gap(ident, "generation_unknown", "No controller observedGeneration was supplied.")
    else:
        number(observed, "observedGeneration", integer=True)
        if observed > generation:
            raise InputError("observedGeneration exceeds metadata.generation")
        if observed < generation:
            report.gap(ident, "controller_not_current", "The controller has not reported the current generation.")
    counters = {k: number(status.get(k, 0), k, integer=True) for k in ("replicas", "updatedReplicas", "readyReplicas", "availableReplicas")}
    if counters["updatedReplicas"] < desired or counters["readyReplicas"] < desired or counters["availableReplicas"] < desired or counters["replicas"] != desired:
        report.issue(ident, "rollout_not_complete", "The supplied replica counters do not show a completed rollout.")
    for condition in rows(status.get("conditions", []), "conditions", nonempty=False):
        obj(condition, "condition")
        if condition.get("type") == "Progressing" and condition.get("status") == "False" and condition.get("reason") == "ProgressDeadlineExceeded":
            report.issue(ident, "progress_deadline", "The controller reported ProgressDeadlineExceeded.")
    if not flag(data.get("pods_complete"), "pods_complete"):
        report.gap(ident, "pod_collection_partial", "Verify the selected Pod inventory is complete.")
    pods = rows(data.get("pods"), "pods", nonempty=False)
    seen = set()
    for pod in pods:
        obj(pod, "pod")
        name = text(obj(pod.get("metadata"), "pod metadata").get("name"), "pod name")
        if name in seen:
            raise InputError("duplicate Pod name")
        seen.add(name)
        pod_status = obj(pod.get("status"), "pod status")
        if pod_status.get("phase") == "Pending":
            report.issue(name, "pod_pending", "Review scheduling and supplied Pod events before changing capacity.")
        containers = rows(pod_status.get("containerStatuses", []), "containerStatuses", nonempty=False)
        if pod_status.get("phase") not in ("Succeeded", "Failed") and not containers:
            report.gap(name, "container_evidence_missing", "No active container status was supplied.")
        for container in containers:
            obj(container, "container status")
            cname = text(container.get("name"), "container name")
            if not flag(container.get("ready"), "ready"):
                report.issue(name, "container_not_ready", "Container " + cname + " is not ready.")
            state = obj(container.get("state", {}), "container state")
            waiting = state.get("waiting", {})
            obj(waiting, "waiting")
            reason = waiting.get("reason")
            if reason in ("CrashLoopBackOff", "ImagePullBackOff", "ErrImagePull", "CreateContainerConfigError"):
                report.issue(name, "container_waiting", "Container " + cname + " reports " + reason + ".")
    if desired and not pods:
        report.gap(ident, "no_pod_evidence", "No selected Pod evidence was supplied for a nonzero Deployment.")
    elif len(pods) < desired:
        report.gap(ident, "pod_inventory_short", "The selected Pod inventory has fewer entries than the desired replica count.")
    return report.finish(desired_replicas=desired, counters=counters, pods=len(pods),
                         policy_scope="Supplied rollout objects; labels/ownership and actual user traffic must be verified separately.")
