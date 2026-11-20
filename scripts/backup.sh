#!/usr/bin/env bash
# Backup: Kubernetes objects (YAML) + Redis data snapshot into backups/<timestamp>/
# Usage: scripts/backup.sh [namespace]
set -euo pipefail
NS="${1:-lab4-dr}"
DIR="backups/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$DIR"

kubectl -n "$NS" get deployment,service,pvc -o yaml > "$DIR/resources.yaml"

POD=$(kubectl -n "$NS" get pod -l app=redis -o jsonpath='{.items[0].metadata.name}')
kubectl -n "$NS" exec "$POD" -- redis-cli SAVE >/dev/null
kubectl -n "$NS" cp "$POD:/data/dump.rdb" "$DIR/dump.rdb" >/dev/null

echo "Backup written to $DIR"
ls -l "$DIR"
