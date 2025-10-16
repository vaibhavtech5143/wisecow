# 🪟 Windows Setup Guide for Wisecow

## 🚀 Quick Start for Windows Users

### Option 1: Simple Batch File (Recommended)
```cmd
# Run the Windows deployment script
deploy-windows.bat
```

### Option 2: Python Script
```cmd
# Run the Python deployment script
python scripts\windows-deploy.py
```

### Option 3: Manual Steps
```cmd
# 1. Build Docker image
docker build -t wisecow .

# 2. Run container
docker run -p 4499:4499 wisecow

# 3. Test application
# Open browser to http://localhost:4499
```

## 📋 Prerequisites for Windows

### Required Software
1. **Docker Desktop for Windows**
   - Download: https://www.docker.com/products/docker-desktop
   - Ensure it's running before deployment

2. **Python 3.x**
   - Download: https://www.python.org/downloads/
   - Or install from Microsoft Store
   - Ensure `python` command works in CMD/PowerShell

3. **Git** (for cloning repository)
   - Download: https://git-scm.com/download/win

### Optional Software
4. **kubectl** (for Kubernetes deployment)
   - Install via: `choco install kubernetes-cli`
   - Or download from: https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/

5. **Minikube** (for local Kubernetes)
   - Download: https://minikube.sigs.k8s.io/docs/start/

## 🔧 Common Windows Issues & Solutions

### Issue 1: Python Command Not Found
```cmd
# Error: 'python' is not recognized as an internal or external command

# Solutions:
# 1. Use py command instead
py scripts\windows-deploy.py

# 2. Or install Python from Microsoft Store
# 3. Or add Python to PATH environment variable
```

### Issue 2: Docker Not Running
```cmd
# Error: Cannot connect to the Docker daemon

# Solution: Start Docker Desktop
# 1. Open Docker Desktop application
# 2. Wait for it to start completely
# 3. Try deployment again
```

### Issue 3: Port Already in Use
```cmd
# Error: Port 4499 is already allocated

# Solution: Stop existing containers
docker stop $(docker ps -q)
# Or use different port
docker run -p 8080:4499 wisecow
```

### Issue 4: PowerShell Execution Policy
```powershell
# Error: Execution of scripts is disabled on this system

# Solution: Allow script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 📊 Testing & Monitoring on Windows

### Application Health Check
```cmd
# Install dependencies first
pip install requests psutil

# Single health check
python scripts\app-health-checker.py http://localhost:4499

# Continuous monitoring
python scripts\app-health-checker.py http://localhost:4499 --continuous
```

### System Health Monitoring
```cmd
# System resource monitoring
python scripts\system-health-monitor.py

# Continuous system monitoring
python scripts\system-health-monitor.py --continuous
```

## ☸️ Kubernetes on Windows

### Using Docker Desktop Kubernetes
```cmd
# 1. Enable Kubernetes in Docker Desktop
# Settings > Kubernetes > Enable Kubernetes

# 2. Deploy to Kubernetes
kubectl apply -f k8s\

# 3. Check deployment
kubectl get pods

# 4. Access application
kubectl port-forward svc/wisecow 8080:4499
# Then visit: http://localhost:8080
```

### Using Minikube
```cmd
# 1. Start Minikube
minikube start

# 2. Load Docker image into Minikube
minikube image load wisecow:local

# 3. Deploy application
kubectl apply -f k8s\

# 4. Access via Minikube
minikube service wisecow --url
```

## 🎯 Windows-Specific Commands

### Docker Commands
```cmd
# Build image
docker build -t wisecow .

# Run container (detached)
docker run -d -p 4499:4499 --name wisecow wisecow

# View logs
docker logs wisecow

# Stop container
docker stop wisecow

# Remove container
docker rm wisecow
```

### File Operations
```cmd
# Navigate to project directory
cd C:\path\to\wisecow

# List files
dir

# View file content
type Dockerfile
type wisecow.sh
```

### Network Testing
```cmd
# Test application (if curl is available)
curl http://localhost:4499

# Or use PowerShell
Invoke-WebRequest -Uri http://localhost:4499

# Or open in browser
start http://localhost:4499
```

## 🚀 Complete Windows Deployment Example

```cmd
# 1. Clone repository (if not already done)
git clone <repository-url>
cd wisecow

# 2. Run deployment
deploy-windows.bat

# 3. Test application
start http://localhost:4499

# 4. Monitor application
python scripts\app-health-checker.py http://localhost:4499 --continuous

# 5. Deploy to Kubernetes (optional)
kubectl apply -f k8s\
kubectl port-forward svc/wisecow 8080:4499
start http://localhost:8080
```

## 💡 Pro Tips for Windows Users

1. **Use Windows Terminal** for better command-line experience
2. **Enable WSL2** for better Docker performance
3. **Use Docker Desktop** instead of Docker Toolbox
4. **Install Windows Subsystem for Linux** for Linux-like experience
5. **Use PowerShell** instead of CMD for better scripting capabilities

## 🆘 Getting Help

If you encounter issues:

1. **Check Docker Desktop** is running and healthy
2. **Verify Python installation**: `python --version`
3. **Check port availability**: `netstat -an | findstr 4499`
4. **View container logs**: `docker logs <container-name>`
5. **Restart Docker Desktop** if containers won't start

## 📞 Support Commands

```cmd
# System information
systeminfo

# Docker information
docker info
docker version

# Python information
python --version
pip --version

# Network information
ipconfig
netstat -an | findstr 4499
```

---

**🎊 You're all set for Windows deployment!** The Wisecow application is fully compatible with Windows and will run smoothly using the provided scripts and commands.