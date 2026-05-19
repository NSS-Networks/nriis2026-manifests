#!/bin/bash
# patch-amf-configmap.sh
# แก้ปัญหา AMF CrashLoopBackOff เนื่องจาก Helm chart hardcode dev: eth0
# แต่ node นี้ใช้ enp1s0 (IP: 10.162.0.1)
# ต้องรันทุกครั้งหลัง helm upgrade

set -e

echo "[1/3] Patching AMF ConfigMap..."
kubectl patch configmap -n open5gs open5gs-amf --type=json -p='[
  {"op": "replace", "path": "/data/amf.yaml", "value": "logger:\n  level: info\n\nglobal:\n\namf:\n  sbi:\n    server:\n    - address: 10.162.0.1\n      port: 7777\n    client:\n      scp:\n      - uri: http://open5gs-scp-sbi:7777\n  ngap:\n    server:\n    - address: 10.162.0.1\n  guami:\n    - amf_id:\n        region: 2\n        set: 1\n      plmn_id:\n        mcc: \"001\"\n        mnc: \"01\"\n  tai:\n    - plmn_id:\n        mcc: \"001\"\n        mnc: \"01\"\n      tac:\n      - 1\n  plmn_support:\n    - plmn_id:\n        mcc: \"001\"\n        mnc: \"01\"\n      s_nssai:\n      - sst: 1\n  security:\n    integrity_order: [NIA2, NIA1, NIA0]\n    ciphering_order: [NEA0, NEA1, NEA2]\n  network_name:\n    full: Gradiant\n  amf_name: open5gs-amf\n  time:\n    t3512:\n      value: 540\n"}
]'

echo "[2/3] Restarting AMF deployment..."
kubectl rollout restart deployment -n open5gs open5gs-amf

echo "[3/3] Waiting for AMF to be ready..."
kubectl rollout status deployment -n open5gs open5gs-amf --timeout=120s

echo ""
echo "Done! AMF status:"
kubectl get pods -n open5gs | grep amf
