# 🚀 Wisecow Deployment Options Quick Reference

## 📋 Deployment Methods

### 🎯 **Option 1: Automated Deployment (Recommended)**

#### Basic Deployment
```bash
# Linux/macOS
python3 scripts/deploy-wisecow.py

# Windows
python scripts/deploy-wisecow.py
```

#### With Zero-Trust Security
```bash
# Linux/macOS
python3 scripts/deploy-wisecow.py --with-kubearmor

# Windows
python scripts/deploy-wisecow.py --with-kubearmor
```

### 🪟 **Option 2: Windows Interactive**
```cmd
# Run interactive deployment
deploy-windows.bat

# Choose from menu:
# 1. Basic deployment
# 2. With KubeArmor security
# 3. Help
```

### ⚡ **Option 3: Quick Kubernetes Deploy**
```bash
# Core components only (no security policies)
kubectl apply -f k8s/deploy-core.yaml

# All components (requires KubeArmor)
kubectl apply -f k8s/
```

### 🔄 **Option 4: CI/CD Automated**
```bash
# Push to main branch triggers automatic deployment
git add .
git commit -m "Deploy Wisecow"
git push origin main
```

---

## 🔒 KubeArmor Installation Options

### **Automatic (Recommended)**
- ✅ Included in deployment scripts with `--with-kubearmor` flag
- ✅ Integrated in CI/CD pipeline
- ✅ No manual steps required

### **Manual Installation**
```bash
# Install KubeArmor
helm repo add kubearmor https://kubearmor.github.io/charts
helm repo update kubearmor
helm upgrade --install kubearmor-operator kubearmor/kubearmor-operator -n kubearmor --create-namespace
kubectl apply -f https://raw.githubusercontent.com/kubearmor/KubeArmor/main/pkg/KubeArmorOperator/config/samples/sample-config.yml

# Apply security policy
kubectl apply -f k8s/kubearmor-policy.yaml
```

### **Skip KubeArmor**
- Use basic deployment commands without `--with-kubearmor` flag
- Deploy using `k8s/deploy-core.yaml` manifest
- KubeArmor can be added later if needed

---

## 📊 Monitoring Options

### **Application Health Monitoring**
```bash
# Single check
python scripts/app-health-checker.py http://localhost:8080

# Continuous monitoring
python scripts/app-health-checker.py http://localhost:8080 --continuous --interval 30

# With logging
python scripts/app-health-checker.py http://localhost:8080 --continuous --log-file health.log
```

### **System Resource Monitoring**
```bash
# Single check
python scripts/system-health-monitor.py

# Continuous monitoring
python scripts/system-health-monitor.py --continuous

# Custom thresholds
python scripts/system-health-monitor.py --continuous --cpu-threshold 70 --memory-threshold 80

# With alert logging
python scripts/system-health-monitor.py --continuous --alert-file alerts.json
```

---

## 🧪 Testing & Validation

### **Pre-Deployment Validation**
```bash
# Comprehensive validation
python scripts/pre-deployment-check.py

# Windows validation
validate-deployment.bat

# Deployment status check
python scripts/check-deployment.py
```

### **Application Testing**
```bash
# Local Docker testing
docker build -t wisecow .
docker run -p 4499:4499 wisecow
curl http://localhost:4499

# Kubernetes testing
kubectl port-forward svc/wisecow 8080:4499
curl http://localhost:8080
```

---

## 🎯 Deployment Decision Matrix

| **Scenario** | **Recommended Option** | **Command** |
|--------------|----------------------|-------------|
| **First-time deployment** | Automated Basic | `python scripts/deploy-wisecow.py` |
| **Production deployment** | Automated with Security | `python scripts/deploy-wisecow.py --with-kubearmor` |
| **Windows users** | Interactive Script | `deploy-windows.bat` |
| **Quick testing** | Core Kubernetes | `kubectl apply -f k8s/deploy-core.yaml` |
| **CI/CD pipeline** | Git push | `git push origin main` |
| **Development** | Local Docker | `docker run -p 4499:4499 wisecow` |

---

## 🆘 Troubleshooting Quick Fixes

### **Common Issues**

#### Port Already in Use
```bash
# Find and stop conflicting containers
docker ps | grep 4499
docker stop <container-id>

# Or use different port
docker run -p 4500:4499 wisecow
```

#### KubeArmor Installation Failed
```bash
# Skip KubeArmor and deploy core components
kubectl apply -f k8s/deploy-core.yaml

# Or install KubeArmor manually later
helm repo add kubearmor https://kubearmor.github.io/charts
helm upgrade --install kubearmor-operator kubearmor/kubearmor-operator -n kubearmor --create-namespace
```

#### Python Command Not Found (Windows)
```cmd
# Try alternative Python commands
py scripts/deploy-wisecow.py
python3 scripts/deploy-wisecow.py

# Or use batch file
deploy-windows.bat
```

#### Kubernetes Cluster Not Accessible
```bash
# Check cluster status
kubectl cluster-info

# For Docker Desktop users
# Enable Kubernetes in Docker Desktop settings

# For Minikube users
minikube start
```

---

## 📞 Support Commands

### **Status Checks**
```bash
# Complete deployment status
python scripts/check-deployment.py

# Kubernetes status
kubectl get all -l app=wisecow

# Security policy status
kubectl get kubearmor-policy

# Certificate status
kubectl get certificates
```

### **Logs and Debugging**
```bash
# Application logs
kubectl logs -l app=wisecow

# KubeArmor logs
kubectl logs -n kubearmor -l app=kubearmor

# cert-manager logs
kubectl logs -n cert-manager -l app=cert-manager
```

---

**🎊 Choose the deployment option that best fits your needs and environment!**