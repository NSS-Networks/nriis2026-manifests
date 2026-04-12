# ขั้นที่ 5: การอัปเดต Config

## 5.1 วิธีแก้ไข Deployment

### แบบที่ 1: kubectl edit (แก้ด่วน)
```bash
kubectl edit deployment open5gs-amf
# nano จะเปิดขึ้นมา แก้แล้ว save
```

### แบบที่ 2: kubectl patch (แก้เฉพาะจุด)
```bash
kubectl patch deployment open5gs-amf --type=json -p='[{
  "op": "add",
  "path": "/path/to/field",
  "value": "new-value"}]'
```

### แบบที่ 3: kubectl apply (แนะนำ)
```bash
# แก้ไฟล์ก่อน
nano server1-open5gs/manifests/amf-deployment.yaml

# apply
kubectl apply -f server1-open5gs/manifests/amf-deployment.yaml
```

---

## 5.2 Export และ Push ขึ้น GitHub

ทุกครั้งที่แก้ไข config ใน cluster:

```bash
cd ~/nriis2026-manifests

# export manifests ที่แก้ไขแล้ว
for nf in smf pcf udr upf amf ausf nrf nssf bsf scp udm; do
  kubectl get deployment open5gs-$nf -o yaml \
    > server1-open5gs/manifests/${nf}-deployment.yaml
done

kubectl get svc -o yaml > server1-open5gs/manifests/all-services.yaml
kubectl get configmap -o yaml > server1-open5gs/manifests/all-configmaps.yaml

# push ขึ้น GitHub
git add .
git commit -m "update: อธิบายว่าแก้อะไร"
git push
```

---

## 5.3 ดู History

```bash
git log --oneline
```

---

## 5.4 ย้อนกลับ Version เก่า

```bash
# ดู hash ที่ต้องการ
git log --oneline

# ย้อนกลับไฟล์เดียว
git checkout <hash> -- server1-open5gs/manifests/amf-deployment.yaml

# ย้อนกลับทั้งหมด
git checkout <hash>
```

---

## 5.5 ตั้งค่า nano เป็น Default Editor

```bash
echo 'export EDITOR=nano' >> ~/.bashrc
source ~/.bashrc
```
