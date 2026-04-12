# ขั้นที่ 4: ตรวจสอบระบบ

## 4.1 เช็ก Nodes

```bash
kubectl get nodes -o wide
```

ต้องเห็น STATUS: Ready

---

## 4.2 เช็ก Pods ทั้งหมด

```bash
kubectl get pods -o wide
```

---

## 4.3 เช็ก Services

```bash
kubectl get svc
```

---

## 4.4 เช็ก AMF N2 Port

```bash
ss -tnlp | grep 38412
```

ต้องเห็น port 38412 listening อยู่

---

## 4.5 เช็ก CNI

```bash
kubectl get pods -n kube-flannel
kubectl get pods -n kube-system | grep multus
```

---

## 4.6 เช็ก Log ของแต่ละ NF

```bash
# ดู log AMF
kubectl logs -f $(kubectl get pod -l app.kubernetes.io/name=amf -o name)

# ดู log SMF
kubectl logs -f $(kubectl get pod -l app.kubernetes.io/name=smf -o name)

# ดู log UPF
kubectl logs -f $(kubectl get pod -l app.kubernetes.io/name=upf -o name)
```

---

## 4.7 เช็ก Restart Count

```bash
kubectl get pods
# ถ้า RESTARTS สูง แสดงว่ามีปัญหา dependency
```

---

## Checklist ก่อนเชื่อม OAI

| รายการ | คำสั่งตรวจสอบ | ผลที่ต้องการ |
|--------|--------------|-------------|
| Nodes Ready | `kubectl get nodes` | Ready |
| Pods Running | `kubectl get pods` | All Running |
| AMF hostPort | `kubectl describe deployment open5gs-amf` | 38412/SCTP |
| Flannel | `kubectl get pods -n kube-flannel` | Running |
| Multus | `kubectl get pods -n kube-system \| grep multus` | Running |
| N2 Port | `ss -tnlp \| grep 38412` | LISTEN |
