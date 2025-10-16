# 🐄 Wisecow - Containerized Wisdom Server

A containerized web application that serves random wisdom quotes with ASCII cow art, deployed on Kubernetes with complete CI/CD pipeline, monitoring, and security.

![Wisecow Demo](https://github.com/nyrahul/wisecow/assets/9133227/8d6bfde3-4a5a-480e-8d55-3fef60300d98)

## 🚀 Quick Start (One-Command Deployment)

### Option 1: Basic Deployment (Recommended)
```bash
# Complete validation and deployment
python scripts/deploy-wisecow.py
```

### Option 2: Deployment with Zero-Trust Security
```bash
# Deployment with KubeArmor security policies
python scripts/deploy-wisecow.py --with-kubearmor
```

### Option 3: Windows Users
```cmd
# Interactive deployment script
deploy-windows.bat
```

**What these commands do:**
- ✅ Validate all components
- 🐳 Build Docker image
- 🧪 Test container locally
- ☸️ Deploy to Kubernetes
- 📊 Setup monitoring
- 🔒 Optionally apply zero-trust security policies

## 📋 Manual Deployment Steps



### 2. Local Development
```bash
# Build and test locally
docker build -t wisecow .
docker run -p 4499:4499 wisecow
curl http://localhost:4499
```

### 3. Kubernetes Deployment
```bash
# Deploy to cluster
kubectl apply -f k8s/

# Verify deployment
kubectl get pods,svc,ingress -l app=wisecow
kubectl rollout status deployment/wisecow
```

### 4. Access Application
```bash
# Port forward for local access
kubectl port-forward svc/wisecow 8080:4499

# Test application
curl http://localhost:8080
```

## 📊 Monitoring & Health Checks

### Application Health Monitoring
```bash
# Single health check
python3 scripts/app-health-checker.py http://localhost:8080

# Continuous monitoring
python3 scripts/app-health-checker.py http://localhost:8080 --continuous --interval 30

# With logging
python3 scripts/app-health-checker.py http://localhost:8080 --continuous --log-file health.log
```

### System Resource Monitoring
```bash
# Single system check
python3 scripts/system-health-monitor.py

# Continuous monitoring with custom thresholds
python3 scripts/system-health-monitor.py --continuous --cpu-threshold 70 --memory-threshold 80

# With alert logging
python3 scripts/system-health-monitor.py --continuous --alert-file alerts.json
```

## 🔒 Security Features

### TLS/HTTPS
- Automatic SSL certificate provisioning via cert-manager
- Let's Encrypt integration for free certificates
- HTTPS enforcement through Ingress

### Zero-Trust Security

#### Option 1: Automatic KubeArmor Installation (Recommended)
```bash
# Use the automated deployment script (includes KubeArmor)
python scripts/deploy-wisecow.py --with-kubearmor
```

#### Option 2: Manual KubeArmor Installation
```bash
# Install KubeArmor using Helm
helm repo add kubearmor https://kubearmor.github.io/charts
helm repo update kubearmor
helm upgrade --install kubearmor-operator kubearmor/kubearmor-operator -n kubearmor --create-namespace
kubectl apply -f https://raw.githubusercontent.com/kubearmor/KubeArmor/main/pkg/KubeArmorOperator/config/samples/sample-config.yml

# Wait for KubeArmor to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=kubearmor -n kubearmor --timeout=300s

# Apply security policy
kubectl apply -f k8s/kubearmor-policy.yaml

# Monitor policy violations
kubectl logs -n kubearmor -l app=kubearmor
```

#### Option 3: Deploy without KubeArmor
```bash
# Use core deployment (without security policies)
kubectl apply -f k8s/deploy-core.yaml
```

## 🔄 CI/CD Pipeline

The GitHub Actions workflow automatically:

1. **Build**: Creates Docker image on code changes
2. **Test**: Validates container functionality
3. **Deploy**: Pushes to Docker Hub and deploys to Kubernetes
4. **Monitor**: Sets up health checks and monitoring

### Required GitHub Secrets
- `DOCKERHUB_USERNAME` - Docker Hub username
- `DOCKERHUB_PASSWORD` - Docker Hub password/token
- `EC2_HOST` - Deployment server IP
- `EC2_SSH_KEY` - SSH private key for deployment

## 📁 Project Structure

```
wisecow/
├── 🐳 Dockerfile                    # Container definition
├── 📜 wisecow.sh                   # Main application script
├── ☸️  k8s/                        # Kubernetes manifests
│   ├── deployment.yaml             # App deployment with probes
│   ├── service.yaml               # ClusterIP service
│   ├── ingress.yaml               # TLS ingress
│   ├── cluster-issuer.yaml        # cert-manager issuer
│   ├── kubearmor-policy.yaml      # Zero-trust policy
│   └── k8.yml                     # All-in-one manifest
├── 🔄 .github/workflows/          # CI/CD pipeline
│   └── ci-cd.yaml                 # GitHub Actions workflow
├── 📊 scripts/                    # Monitoring & deployment
│   ├── app-health-checker.py     # Application monitoring
│   ├── system-health-monitor.py  # System monitoring
│   ├── deploy-wisecow.py         # Deployment orchestrator  
├── |-- check-deployment.py       # Last check to verify all things of k8s is working 
│   └── requirements.txt          # Python dependencies
```

## 🔒 KubeArmor Zero-Trust Security

KubeArmor provides runtime security for Kubernetes workloads with zero-trust policies.

### Automated Installation (Recommended)
```bash
# Deploy with KubeArmor automatically
python scripts/deploy-wisecow.py --with-kubearmor

# Or for Windows users
deploy-windows.bat  # Choose option 2
```

### Manual Installation
```bash
# Add KubeArmor Helm repository
helm repo add kubearmor https://kubearmor.github.io/charts
helm repo update kubearmor

# Install KubeArmor operator
helm upgrade --install kubearmor-operator kubearmor/kubearmor-operator -n kubearmor --create-namespace

# Apply KubeArmor configuration
kubectl apply -f https://raw.githubusercontent.com/kubearmor/KubeArmor/main/pkg/KubeArmorOperator/config/samples/sample-config.yml

# Wait for KubeArmor to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=kubearmor -n kubearmor --timeout=300s

# Apply Wisecow security policy
kubectl apply -f k8s/kubearmor-policy.yaml
```

### Security Policy Features
Our KubeArmor policy provides:
- **Process Control**: Blocks unauthorized executables (apt, wget, curl, etc.)
- **File System Protection**: Read-only access to system directories
- **Network Restrictions**: Limited protocol access
- **Capability Restrictions**: Blocks dangerous system capabilities
- **Runtime Monitoring**: Real-time security violation detection

### Monitoring Security Violations
```bash
# Check policy status
kubectl get kubearmor-policy

# Monitor security violations
kubectl logs -n kubearmor -l app=kubearmor

# View policy details
kubectl describe kubearmor-policy wisecow-zero-trust-policy
```

## 🎯 Problem Statement Solutions

### ✅ Problem Statement 1: Complete Containerization & Deployment
- **Dockerization**: Optimized multi-stage Dockerfile
- **Kubernetes**: Production-ready manifests with probes
- **CI/CD**: Automated GitHub Actions pipeline with KubeArmor support
- **TLS**: cert-manager with Let's Encrypt integration
- **Monitoring**: Comprehensive health checks
- **Security**: Zero-trust KubeArmor policies (automated installation)

### ✅ Problem Statement 2: Monitoring Scripts (2 implementations)
1. **Application Health Checker**: HTTP-based uptime monitoring
2. **System Health Monitor**: CPU/Memory/Disk monitoring with alerts

### ✅ Problem Statement 3: Zero-Trust Security (Enhanced)
- **KubeArmor Policy**: Comprehensive security controls
- **Automated Installation**: One-command KubeArmor deployment
- **CI/CD Integration**: Automatic security policy application
- **Process restrictions**: Limited executable access
- **File system controls**: Read-only system directories
- **Network policies**: Protocol-level restrictions
- **Violation monitoring**: Real-time security event tracking

## 🧪 Testing & Validation



# Individual component tests
docker build -t wisecow-test .           # Docker build
kubectl apply --dry-run=client -f k8s/   # Manifest validation
```

## 🔧 Configuration

### Application Settings
- **Port**: 4499 (configurable)
- **Resources**: 100m CPU, 128Mi memory (requests)
- **Limits**: 500m CPU, 256Mi memory
- **Probes**: Liveness and readiness checks

### Monitoring Thresholds
- **CPU**: 80% (configurable)
- **Memory**: 80% (configurable)
- **Disk**: 80% (configurable)
- **Check Interval**: 30s (app), 60s (system)

## 🆘 Troubleshooting

### Common Issues
```bash
# Check pod logs
kubectl logs -l app=wisecow

# Verify service connectivity
kubectl get endpoints wisecow

# Test DNS resolution
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup wisecow

# Monitor resource usage
kubectl top pods -l app=wisecow
```

### Health Check Commands
```bash
# Application health
python3 scripts/app-health-checker.py http://localhost:8080

# System health
python3 scripts/system-health-monitor.py

# Deployment status
kubectl rollout status deployment/wisecow
```

## 🎊 Success Metrics

- ✅ **100% Automated Deployment**: Single command deployment
- ✅ **Zero Downtime**: Rolling updates with health checks
- ✅ **Security Hardened**: Zero-trust policies applied
- ✅ **Fully Monitored**: Application and system monitoring
- ✅ **TLS Secured**: Automatic HTTPS with valid certificates
- ✅ **Production Ready**: Resource limits, probes, and scaling

---

**🎯 Mission Accomplished**: Complete containerization and deployment of Wisecow application with automated CI/CD pipeline, comprehensive monitoring, and enterprise-grade security! 🚀
