#!/bin/bash

echo "=== [1] Kernel Modules ==="
sudo modprobe overlay
sudo modprobe br_netfilter
sudo sysctl --system > /dev/null 2>&1
echo "✅ kernel modules loaded"

echo "=== [2] Flannel subnet.env ==="
if [ ! -f /run/flannel/subnet.env ]; then
  echo "❌ subnet.env หาย — restart flannel"
  kubectl rollout restart daemonset -n kube-flannel kube-flannel-ds
  sleep 15
else
  echo "✅ subnet.env OK"
fi

echo "=== [3] CoreDNS ==="
COREDNS=$(kubectl get pods -n kube-system -l k8s-app=kube-dns \
  --no-headers | grep Running | wc -l)
if [ "$COREDNS" -eq 0 ]; then
  echo "❌ CoreDNS ไม่ Running — restart"
  kubectl rollout restart deployment -n kube-system coredns
  sleep 15
else
  echo "✅ CoreDNS Running ($COREDNS pods)"
fi

echo "=== [4] Fix stuck pods ==="
kubectl get pods -A --field-selector=status.phase!=Running \
  -o jsonpath='{range .items[*]}{.metadata.namespace}{" "}{.metadata.name}{"\n"}{end}' \
  | while read ns name; do
    [ -z "$ns" ] && continue
    echo "Deleting $ns/$name"
    kubectl delete pod -n $ns $name --force --grace-period=0
  done

echo "=== [5] AMF NRF ClusterIP ==="
NRF_IP=$(kubectl get svc -n open5gs open5gs-nrf-sbi \
  -o jsonpath='{.spec.clusterIP}')
AMF_NRF=$(grep "uri:" ~/nriis2026-manifests/server1-open5gs/amf-config.yaml \
  | grep -oP '(?<=http://)[\d.]+')
if [ "$NRF_IP" != "$AMF_NRF" ]; then
  echo "❌ NRF IP ไม่ตรง ($AMF_NRF → $NRF_IP) — patch"
  sed -i "s|http://${AMF_NRF}:7777|http://${NRF_IP}:7777|g" \
    ~/nriis2026-manifests/server1-open5gs/amf-config.yaml
  cd ~/nriis2026-manifests/server1-open5gs
  bash patch-all.sh
else
  echo "✅ NRF IP ตรง ($NRF_IP)"
fi

echo "=== Done ==="
kubectl get pods -n open5gs
