#!/usr/bin/env bash
set -e

echo "========================================"
echo " Simulating Kafka Broker Failure"
echo "========================================"

# Find the Kafka container ID
KAFKA_CONTAINER=$(docker ps -qf "name=kafka")

if [ -z "$KAFKA_CONTAINER" ]; then
  echo "Kafka container not found. Make sure it is running."
  exit 1
fi

echo "Stopping Kafka container: $KAFKA_CONTAINER"

docker stop "$KAFKA_CONTAINER"

echo "Kafka broker has been stopped."
echo "You should now observe consumer lag increasing."
