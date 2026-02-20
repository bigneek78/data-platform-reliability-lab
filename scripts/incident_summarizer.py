import glob
from pathlib import Path
from datetime import datetime

RUNBOOK_PATH = Path("../runbooks/RB-001_kafka_broker_down.md")
OUTPUT_PATH = Path("../docs/incident_summary_draft.txt")

def latest_evidence_dir():
    dirs = sorted(glob.glob("../docs/evidence_*"))
    return Path(dirs[-1]) if dirs else None

def safe_read(path: Path, max_chars: int = 2500) -> str:
    try:
        return path.read_text(errors="ignore")[:max_chars]
    except Exception:
        return ""

evidence_dir = latest_evidence_dir()
if not evidence_dir:
    print("No evidence folder found. Run scripts/collect_evidence.sh first.")
    raise SystemExit(1)

docker_ps = safe_read(evidence_dir / "docker_ps.txt", 2000)
kafka_logs = safe_read(evidence_dir / "kafka_logs.txt", 2000)
runbook_excerpt = safe_read(RUNBOOK_PATH, 1500) if RUNBOOK_PATH.exists() else "Runbook not found."

now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")

summary = f"""INCIDENT SUMMARY (DRAFT)
Timestamp (UTC): {now}

Title:
Kafka broker outage simulation → consumer lag impact and recovery validation

What happened:
A controlled broker shutdown was executed as part of reliability testing. The objective was to validate observability signals,
evidence capture workflows, and runbook-driven remediation.

Evidence Collected:
--- docker ps (excerpt) ---
{docker_ps}

--- kafka logs (tail excerpt) ---
{kafka_logs}

Runbook Reference (excerpt):
{runbook_excerpt}

Mitigation:
- Restart Kafka container to restore broker availability.
- Confirm stabilization through lag behavior and error reduction.

Follow-ups / Improvements:
- Add broker health + consumer lag alert thresholds.
- Auto-trigger evidence capture on alert.
- Expand runbook with known failure patterns and escalation criteria.
"""

OUTPUT_PATH.write_text(summary)
print(f"Wrote incident summary to: {OUTPUT_PATH}")
