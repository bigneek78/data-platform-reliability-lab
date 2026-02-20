# RB-002: Consumer Lag Spike

## Purpose
Provide a structured approach to diagnosing and mitigating unexpected increases in Kafka consumer lag.

---

## Symptoms
- Lag metric rising continuously
- Delayed downstream processing
- No broker outage detected
- Consumers appear running but falling behind

---

## Immediate Questions
1. Is the broker healthy?
2. Is consumer throughput lower than producer throughput?
3. Has traffic volume increased unexpectedly?
4. Are consumers experiencing errors?

---

## Evidence to Collect
- Consumer lag metrics over time
- Producer throughput rate
- Consumer logs
- Broker health status
- Recent deployment or configuration changes

---

## Verification Steps
- Confirm consumers are running
  - `docker ps`
- Check consumer logs for errors
- Validate partition assignment
- Confirm no rebalance loop occurring

---

## Common Root Causes
- Traffic spike exceeding consumer capacity
- Consumer processing slowdown
- Resource saturation (CPU/memory)
- Partition imbalance

---

## Mitigation
- Scale consumer instances
- Increase consumer resources
- Investigate inefficient processing logic
- Review partition distribution

---

## Escalation Criteria
Escalate when:
- Lag continues increasing after scaling
- Consumers crash repeatedly
- Data loss risk is suspected
