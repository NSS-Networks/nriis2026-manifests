# ขั้นที่ 1: ติดตั้ง Kubernetes

## ข้อมูล Server
| รายการ | ค่า |
|--------|-----|
| OS | Ubuntu 24.04 LTS |
| IP | 10.162.0.1 |
| Role | K8s Master + 5G Core |
| K8s Version | v1.28.15 |

---

## 1.1 ติดตั้ง kubeadm, kubelet, kubectl

```bash
sudo apt update
sudo apt install -y apt-transport-https ca-certificates curl

curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.28/deb/Release.key | \
  sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg

echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] \
  https://pkgs.k8s.io/core:/stable:/v1.28/deb/ /" | \
  sudo tee /etc/apt/sources.list.d/kubernetes.list

sudo apt update
sudo apt install -y kubeadm kubelet kubectl
sudo apt-mark hold kubeadm kubelet kubectl
```

---

## 1.2 ปิด Swap

```bash
sudo swapoff -a
sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab
```

---

## 1.3 ติดตั้ง containerd

```bash
sudo apt install -y containerd
sudo mkdir -p /etc/containerd
containerd config default | sudo tee /etc/containerd/config.toml
sudo systemctl restart containerd
sudo systemctl enable containerd
```

---

## 1.4 Init Cluster

```bash
sudo kubeadm init --pod-network-cidr=10.244.0.0/16
```

---

## 1.5 Setup kubeconfig

```bash
mkdir -p $HOME/.kube
sudo cp /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

---

## 1.6 ติดตั้ง Flannel CNI

```bash
kubectl apply -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml
```

ตรวจสอบ:
```bash
kubectl get pods -n kube-flannel
# ต้องเห็น kube-flannel-ds-xxx Running
```

---

## 1.7 ติดตั้ง Multus CNI

```bash
kubectl apply -f https://raw.githubusercontent.com/k8snetworkplumbingwg/multus-cni/master/deployments/multus-daemonset.yml
```

ตรวจสอบ:
```bash
kubectl get pods -n kube-system | grep multus
# ต้องเห็น kube-multus-ds-xxx Running
```

---

## 1.8 ติดตั้ง metrics-server

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

ตรวจสอบ:
```bash
kubectl get pods -n kube-system | grep metrics
# ต้องเห็น metrics-server-xxx Running
```

---

## 1.9 ตรวจสอบ Node พร้อมใช้งาน

```bash
kubectl get nodes
# ต้องเห็น STATUS: Ready
```

---

## หมายเหตุ
- ตั้ง nano เป็น default editor: `echo 'export EDITOR=nano' >> ~/.bashrc && source ~/.bashrc`
- Single node cluster — control-plane ต้องปลด taint ก่อน pod จะรันได้:
  `kubectl taint nodes --all node-role.kubernetes.io/control-plane-`
