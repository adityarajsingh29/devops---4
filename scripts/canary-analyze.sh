#!/usr/bin/env bash
# Canary analysis: send traffic, measure the error rate, and roll back automatically if it is above the threshold.
# Usage: scripts/canary-analyze.sh [namespace] [max-error-percent] [requests]
set -euo pipefail
NS="${1:-lab4-canary}"; MAX_ERR="${2:-5}"; N="${3:-100}"
DIR="$(cd "$(dirname "$0")" && pwd)"

RESULT="$("$DIR/traffic.sh" canary-app "$NS" "$N" 0.05)"
echo "$RESULT"
FAILED=$(echo "$RESULT" | awk '/FAILED/ {print $1}'); FAILED=${FAILED:-0}
ERR=$(( FAILED * 100 / N ))
echo "Error rate: ${ERR}%  (threshold ${MAX_ERR}%)"

if [ "$ERR" -gt "$MAX_ERR" ]; then
  echo "ROLLBACK TRIGGERED: error rate above threshold - scaling canary to 0"
  kubectl -n "$NS" scale deployment/app-canary --replicas=0
  exit 1
fi
echo "CANARY HEALTHY: safe to continue the rollout"
