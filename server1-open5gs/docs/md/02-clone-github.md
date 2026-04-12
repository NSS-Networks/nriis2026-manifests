# ขั้นที่ 2: Clone ไฟล์จาก GitHub

## 2.1 ติดตั้ง Git และ Helm

```bash
sudo apt install -y git
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

---

## 2.2 ตั้งค่า SSH Key สำหรับ GitHub (ครั้งแรกครั้งเดียว)

```bash
ssh-keygen -t ed25519 -C "your-email@example.com"
cat ~/.ssh/id_ed25519.pub
```

นำ public key ไปใส่ที่ GitHub → Settings → SSH Keys → New SSH key

---

## 2.3 Clone repo

```bash
cd ~
git clone git@github.com:NSS-Network/nriis2026-manifests.git
cd nriis2026-manifests
ls server1-open5gs/
```

ต้องเห็นไฟล์เหล่านี้:
```
open5gs-2.2.0.tgz        ← Helm chart
trinergy_values.yaml     ← Config ที่แก้ไขแล้ว
manifests/               ← K8s yaml files
docs/                    ← คู่มือ
```

---

## 2.4 ตั้งค่า Git identity (ครั้งแรกครั้งเดียว)

```bash
git config --global user.email "your-email@example.com"
git config --global user.name "Your Name"
```

---

## หมายเหตุ
- repo เป็น Private ต้องมี SSH key หรือได้รับ invite ก่อนถึงจะ clone ได้
- ติดต่อ admin เพื่อขอสิทธิ์เข้าถึง repo
