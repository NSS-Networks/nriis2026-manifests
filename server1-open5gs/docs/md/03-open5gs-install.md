# ขั้นที่ 3: ติดตั้ง Open5GS

## 3.1 ติดตั้งด้วย Helm จากไฟล์ใน repo

```bash
cd ~/nriis2026-manifests/server1-open5gs
helm install open5gs open5gs-2.2.0.tgz -f trinergy_values.yaml
```

> **หมายเหตุ:** ใช้ `open5gs-2.2.0.tgz` และ `trinergy_values.yaml` จาก repo ของเรา
> ไม่ต้องโหลดจาก internet หรือ helm repo อื่น

---

## 3.2 รอ pods พร้อม

```bash
kubectl get pods -w
```

รอจนทุก pod เป็น Running:
```
open5gs-amf-xxx      1/1   Running   0
open5gs-smf-xxx      1/1   Running   0
open5gs-upf-xxx      1/1   Running   0
open5gs-nrf-xxx      1/1   Running   0
open5gs-udm-xxx      1/1   Running   0
open5gs-udr-xxx      1/1   Running   0
open5gs-ausf-xxx     1/1   Running   0
open5gs-pcf-xxx      1/1   Running   0
open5gs-nssf-xxx     1/1   Running   0
open5gs-bsf-xxx      1/1   Running   0
open5gs-scp-xxx      1/1   Running   0
open5gs-mongodb-xxx  1/1   Running   0
```

---

## 3.3 แก้ AMF hostPort สำหรับ N2 interface

```bash
kubectl patch deployment open5gs-amf --type=json -p='[{
  "op": "add",
  "path": "/spec/template/spec/containers/0/ports/2/hostPort",
  "value": 38412}]'
```

ตรวจสอบ:
```bash
kubectl describe deployment open5gs-amf | grep -A3 "Host Ports"
# ต้องเห็น: Host Ports: 0/TCP, 0/TCP, 38412/SCTP
```

---

## 3.4 ตรวจสอบ services

```bash
kubectl get svc
```

---

## 3.5 Container Images ที่ใช้

| Image | Source |
|-------|--------|
| Open5GS 2.7.0 | ghcr.io/nss-network/open5gs:2.7.0 |
| MongoDB 6.0 | ghcr.io/nss-network/mongo:6.0 |

---

## หมายเหตุสำคัญ
- ถ้าต้องการปิด 4G ให้แก้ `trinergy_values.yaml` ปิด UPF ก่อน install
- SMF ต้องการ NRF พร้อมก่อน start
- PCF และ UDR ต้องการ MongoDB พร้อมก่อน start
