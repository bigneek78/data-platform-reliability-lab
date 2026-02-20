import json
import os
import random
import time
from datetime import datetime
from kafka import KafkaProducer

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
TOPIC = os.getenv("KAFKA_TOPIC", "events")

producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    acks="all",
    linger_ms=5,
)

apps = ["streaming", "analytics", "recommendation", "billing", "ingest"]
severities = ["info", "warn", "error"]

print(f"Producing messages to topic '{TOPIC}'... Press Ctrl+C to stop.")

counter = 0

while True:
    counter += 1

    event = {
        "id": counter,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "application": random.choice(apps),
        "severity": random.choices(severities, weights=[80, 15, 5])[0],
        "latency_ms": random.randint(5, 500),
        "message": "synthetic event for reliability testing"
    }

    producer.send(TOPIC, event)

    if counter % 200 == 0:
        producer.flush()
        print(f"Sent {counter} events")

    time.sleep(0.01)
