#!/usr/bin/env bash
set -e

echo "========================================"
echo " Collecting Incident Evidence"
echo "========================================"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="../docs/evidence_$TIMESTAMP"

mkdir -p "$OUTPUT_DIR"

echo "Saving Docker container status..."
docker ps > "$OUTPUT_DIR/docker_ps.txt"

echo "Saving Kafka logs..."
KAFKA_CONTAINER=$(docker ps -aqf "name=kafka")

if [ -n "$KAFKA_CONTAINER" ]; then
  docker logs "$KAFKA_CONTAINER" --tail 200 > "$OUTPUT_DIR/kafka_logs.txt"
else
  echo "Kafka container not found." > "$OUTPUT_DIR/kafka_logs.txt"
fi

echo "Evidence saved to $OUTPUT_DIR"
