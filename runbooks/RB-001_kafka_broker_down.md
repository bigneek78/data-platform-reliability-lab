# RB-001: Kafka Broker Down

## Purpose
Provide a consistent, evidence-driven workflow to diagnose and recover from Kafka broker unavailability, with clear escalation criteria and documentation guidance.

---

## Symptoms
- Producers experience timeouts or connection errors
- Consumer lag increases rapidly
- Monitoring indicates broker health check failures
- Broker container/process not running

---

## Immediate Questions (first 2–3 minutes)
1. Is the broker actually down (process/container stopped), or is it unreachable (network)?
2. Is impact isolated to one broker or system-wide?
3. Are producers failing, consumers failing, or both?

---

## Evidence to Collect
Capture evidence before applying changes whenever possible.

### Commands
- Container state:
  - `docker ps`
- Kafka logs (tail):
  - `docker logs <kafka_container_id> --tail 200`
- Timestamp + customer impact summary:
  - what broke, when, who is impacted, what errors are reported

### Automation (preferred)
- Run the evidence capture script:
  - `bash scripts/collect_evidence.sh`

---

## Verification Steps
1. Confirm Kafka container exists and is running:
   - `docker ps | grep kafka`
2. If not running, check last known logs:
   - `docker logs <kafka_container_id> --tail 200`

---

## Mitigation / Recovery
### If broker is stopped
- Start the broker:
  - `docker start <kafka_container_id>`

### If broker is unstable (restarts/crashes)
- Check host resource pressure:
  - CPU, memory, disk availability
- Review logs for repeated failure patterns
- Collect evidence and escalate if repeating

---

## Validate Recovery
- Producer errors stop
- Consumer lag stops rising and begins falling
- Broker remains stable after restart
- No recurring crash loop in logs

---

## Escalation Criteria
Escalate to Platform Engineering when:
- Broker repeatedly crashes after restart
- Data loss risk is suspected
- Multiple components fail simultaneously
- Recovery requires partition reassignment or deeper configuration changes

---

## Ticket / Incident Notes Template
Use this format for consistent reporting:

- Start time (UTC):
- Reported symptoms:
- Impact / affected users:
- Evidence collected (links or file paths):
- Mitigation performed:
- Current status:
- Follow-up actions:
