#!/bin/bash
# patch-all.sh
# ต้องรันทุกครั้งหลัง helm upgrade
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== [1/4] Patching AMF ConfigMap ==="
kubectl create configmap -n open5gs open5gs-amf \
  --from-file=amf.yaml=${SCRIPT_DIR}/amf-config.yaml \
  --dry-run=client -o json | kubectl apply -f -
kubectl rollout restart deployment -n open5gs open5gs-amf

echo "=== [2/4] Patching NRF ConfigMap ==="
kubectl create configmap -n open5gs open5gs-nrf \
  --from-file=nrf.yaml=${SCRIPT_DIR}/nrf-config.yaml \
  --dry-run=client -o json | kubectl apply -f -
kubectl rollout restart deployment -n open5gs open5gs-nrf

echo "=== [3/4] Patching NSSF ConfigMap ==="
kubectl create configmap -n open5gs open5gs-nssf \
  --from-file=nssf.yaml=${SCRIPT_DIR}/nssf-config.yaml \
  --dry-run=client -o json | kubectl apply -f -
kubectl rollout restart deployment -n open5gs open5gs-nssf

echo "=== [4/4] Patching SMF ConfigMap ==="
kubectl create configmap -n open5gs open5gs-smf \
  --from-file=smf.yaml=${SCRIPT_DIR}/smf-config.yaml \
  --dry-run=client -o json | kubectl apply -f -
kubectl rollout restart deployment -n open5gs open5gs-smf

echo ""
echo "=== Waiting for all deployments ==="
kubectl rollout status deployment -n open5gs open5gs-amf --timeout=120s
kubectl rollout status deployment -n open5gs open5gs-nrf --timeout=120s
kubectl rollout status deployment -n open5gs open5gs-nssf --timeout=120s
kubectl rollout status deployment -n open5gs open5gs-smf --timeout=120s

echo ""
echo "=== Done! Pod status ==="
kubectl get pods -n open5gs
