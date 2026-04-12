# ขั้นที่ 6: การแก้ปัญหาที่พบบ่อย

## 6.1 helm repo หา chart ไม่เจอ

**อาการ:**
```
Error: repo open5gs not found
```

**วิธีแก้:** ใช้ไฟล์จาก repo แทน
```bash
cd ~/nriis2026-manifests/server1-open5gs
helm install open5gs open5gs-2.2.0.tgz -f trinergy_values.yaml
```

---

## 6.2 Pod restart เยอะ

**อาการ:** RESTARTS สูงใน `kubectl get pods`

**สาเหตุ:** NF start ก่อน dependency พร้อม

**วิธีแก้:** เพิ่ม initContainer
```bash
# ตัวอย่าง wait-mongodb สำหรับ PCF/UDR
cat > /tmp/wait-mongodb-patch.yaml << 'EOF'
spec:
  template:
    spec:
      initContainers:
      - name: wait-mongodb
        image: busybox:1.36
        command:
        - sh
        - -c
        - "until nc -z open5gs-mongodb 27017; do echo waiting-mongodb; sleep 3; done"
EOF

kubectl patch deployment open5gs-pcf --patch-file /tmp/wait-mongodb-patch.yaml
kubectl patch deployment open5gs-udr --patch-file /tmp/wait-mongodb-patch.yaml
```

---

## 6.3 AMF เชื่อมต่อไม่ได้จากนอก cluster

**อาการ:** OAI CU เชื่อม AMF ไม่ได้

**วิธีแก้:** patch hostPort
```bash
kubectl patch deployment open5gs-amf --type=json -p='[{
  "op": "add",
  "path": "/spec/template/spec/containers/0/ports/2/hostPort",
  "value": 38412}]'
```

---

## 6.4 SMF ค้างที่ Init:0/2

**อาการ:** SMF pod ไม่ขึ้น Running

**สาเหตุ:** initContainer รอ UPF PFCP แต่ปิด 4G อยู่

**วิธีแก้:** rollback
```bash
kubectl rollout undo deployment/open5gs-smf
```

---

## 6.5 Script indent หายตอน paste ลง terminal

**วิธีแก้:** เขียนไฟล์ก่อนแล้วค่อยรัน
```bash
cat > /tmp/fix.py << 'EOF'
# Python code here (indent ปลอดภัย)
EOF
python3 /tmp/fix.py
```

---

## 6.6 git push ไม่ได้

**อาการ:**
```
remote: Invalid username or token
```

**วิธีแก้:** ใช้ SSH key แทน
```bash
ssh-keygen -t ed25519 -C "your-email@example.com"
cat ~/.ssh/id_ed25519.pub
# นำ public key ไปใส่ใน GitHub Settings → SSH Keys
git remote set-url origin git@github.com:NSS-Network/nriis2026-manifests.git
```

---

## 6.7 NodePort port ไม่อยู่ใน range

**อาการ:**
```
The range of valid ports is 30000-32767
```

**วิธีแก้:** ใช้ hostPort แทน NodePort สำหรับ AMF N2

---

## 6.8 คำสั่ง kubectl ใช้ไม่ได้หลัง reboot

**วิธีแก้:**
```bash
export KUBECONFIG=$HOME/.kube/config
# หรือใส่ใน ~/.bashrc ให้ถาวร
echo 'export KUBECONFIG=$HOME/.kube/config' >> ~/.bashrc
```
