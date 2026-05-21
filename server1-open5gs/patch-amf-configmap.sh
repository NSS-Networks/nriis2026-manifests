#!/bin/bash
# patch-amf-configmap.sh
# ต้องรันทุกครั้งหลัง helm upgrade
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[1/3] Patching AMF ConfigMap..."
kubectl create configmap -n open5gs open5gs-amf \
  --from-file=amf.yaml=${SCRIPT_DIR}/amf-config.yaml \
  --dry-run=client -o json | \
  kubectl apply -f -

echo "[2/3] Restarting AMF deployment..."
kubectl rollout restart deployment -n open5gs open5gs-amf

echo "[3/3] Waiting for AMF to be ready..."
kubectl rollout status deployment -n open5gs open5gs-amf --timeout=120s

echo ""
echo "Done! AMF status:"
kubectl get pods -n open5gs | grep amf
