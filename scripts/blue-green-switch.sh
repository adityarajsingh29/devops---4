#!/usr/bin/env bash
# Switch live traffic between the blue and green environments.
# Usage: scripts/blue-green-switch.sh <blue|green> [namespace]
set -euo pipefail
TARGET="$1"
NS="${2:-lab4-bg}"

echo "Checking that app-${TARGET} is fully ready before switching..."
kubectl -n "$NS" rollout status deployment/"app-${TARGET}" --timeout=60s

kubectl -n "$NS" patch service bg-app -p "{\"spec\":{\"selector\":{\"app\":\"bg-app\",\"slot\":\"${TARGET}\"}}}"
echo "Live traffic now goes to: ${TARGET}"
kubectl -n "$NS" get endpointslices -l kubernetes.io/service-name=bg-app -o wide
