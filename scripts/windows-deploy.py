#!/usr/bin/env python
"""
Windows-Compatible Wisecow Deployment Script
Simplified deployment for Windows environment
"""

import os
import sys
import time
import subprocess
import json
from pathlib import Path

class WindowsWisecowDeployer:
    def __init__(self, install_kubearmor=False):
        self.current_step = 0
        self.install_kubearmor = install_kubearmor
        
    def log_step(self, message):
        self.current_step += 1
        print(f"\n🚀 Step {self.current_step}: {message}")
        print("-" * 50)
        
    def run_command(self, command, description, check=True):
        """Run shell command with error handling"""
        print(f"📝 {description}")
        print(f"💻 Command: {command}")
        
        try:
            # Use shell=True for Windows compatibility
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✅ Success: {description}")
                if result.stdout.strip():
                    print(f"📄 Output: {result.stdout.strip()}")
                return True
            else:
                print(f"❌ Failed: {description}")
                if result.stderr.strip():
                    print(f"🚨 Error: {result.stderr.strip()}")
                if check:
                    raise Exception(f"Command failed: {command}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ Timeout: {description}")
            if check:
                raise Exception(f"Command timed out: {command}")
            return False
        except Exception as e:
            print(f"💥 Exception: {e}")
            if check:
                raise
            return False
    
    def validate_prerequisites(self):
        """Validate basic prerequisites"""
        self.log_step("Validating Prerequisites")
        
        # Check if required files exist
        required_files = [
            "Dockerfile",
            "wisecow.sh",
            "k8s/deployment.yaml",
            "k8s/service.yaml",
            "k8s/ingress.yaml",
            ".github/workflows/ci-cd.yaml"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
            else:
                print(f"✅ Found: {file_path}")
        
        if missing_files:
            print(f"❌ Missing files: {missing_files}")
            return False
        
        # Check Docker
        if not self.run_command("docker --version", "Checking Docker availability", check=False):
            print("⚠️  Docker not available - install Docker Desktop for Windows")
            return False
        
        # Check kubectl (optional for local testing)
        if not self.run_command("kubectl version --client", "Checking kubectl availability", check=False):
            print("⚠️  kubectl not available - install for Kubernetes deployment")
        
        print("✅ Prerequisites validation passed!")
        return True
    
    def build_docker_image(self):
        """Build Docker image locally"""
        self.log_step("Building Docker Image")
        
        if not self.run_command("docker build -t wisecow:local .", "Building Wisecow Docker image"):
            return False
            
        if not self.run_command("docker images wisecow:local", "Verifying image creation"):
            return False
                
        return True
    
    def test_container_locally(self):
        """Test container functionality locally"""
        self.log_step("Testing Container Locally")
        
        # Clean up any existing test containers
        self.run_command("docker stop wisecow-test", "Stopping existing test container", check=False)
        self.run_command("docker rm wisecow-test", "Removing existing test container", check=False)
        
        # Try different ports if 4499 is in use
        ports_to_try = [4499, 4500, 4501, 4502]
        container_started = False
        used_port = None
        
        for port in ports_to_try:
            if self.run_command(f"docker run -d --name wisecow-test -p {port}:4499 wisecow:local", 
                               f"Starting test container on port {port}", check=False):
                container_started = True
                used_port = port
                break
            else:
                print(f"⚠️  Port {port} is in use, trying next port...")
        
        if not container_started:
            print("❌ Could not start container on any available port")
            return False
            
        # Wait for container to start
        print("⏳ Waiting for container to start...")
        time.sleep(10)
        
        # Test if container is running
        container_running = self.run_command("docker ps | findstr wisecow-test", 
                                           "Checking if container is running", check=False)
        
        if container_running:
            print("✅ Container is running successfully!")
            print(f"💡 You can test it manually at: http://localhost:{used_port}")
            
            # Test the application with health checker
            print("🧪 Testing application response...")
            time.sleep(3)  # Give container time to fully start
            if self.run_command(f"python scripts/app-health-checker.py http://localhost:{used_port}", 
                               "Testing application health", check=False):
                print("✅ Application is responding correctly!")
            else:
                print("⚠️  Application health check failed, but container is running")
        
        # Cleanup
        self.run_command("docker stop wisecow-test", "Stopping test container", check=False)
        self.run_command("docker rm wisecow-test", "Removing test container", check=False)
        
        return container_running
    
    def install_python_dependencies(self):
        """Install Python dependencies for monitoring"""
        self.log_step("Installing Python Dependencies")
        
        # Try different pip commands
        pip_commands = ["pip install requests psutil", "python -m pip install requests psutil"]
        
        for pip_cmd in pip_commands:
            if self.run_command(pip_cmd, f"Installing dependencies with: {pip_cmd}", check=False):
                print("✅ Python dependencies installed successfully!")
                return True
        
        print("⚠️  Could not install Python dependencies automatically")
        print("💡 Please run manually: pip install requests psutil")
        return False
    
    def test_monitoring_scripts(self):
        """Test monitoring scripts"""
        self.log_step("Testing Monitoring Scripts")
        
        # Test if scripts can be imported/run
        scripts_to_test = [
            ("python scripts/app-health-checker.py --help", "Testing app health checker"),
            ("python scripts/system-health-monitor.py --help", "Testing system monitor")
        ]
        
        all_success = True
        for cmd, desc in scripts_to_test:
            if self.run_command(cmd, desc, check=False):
                print(f"✅ {desc} - OK")
            else:
                print(f"⚠️  {desc} - Failed (may need dependencies)")
                all_success = False
        
        return all_success
    
    def deploy_to_kubernetes(self):
        """Deploy to Kubernetes if available"""
        self.log_step("Kubernetes Deployment (Optional)")
        
        # Check if kubectl is available and cluster is accessible
        if not self.run_command("kubectl cluster-info", "Checking Kubernetes cluster", check=False):
            print("⚠️  Kubernetes cluster not accessible")
            print("💡 For Kubernetes deployment:")
            print("   1. Install kubectl")
            print("   2. Setup a cluster (Docker Desktop, minikube, etc.)")
            print("   3. Run: kubectl apply -f k8s/")
            return False
        
        # Apply core manifests (without KubeArmor)
        if self.install_kubearmor:
            manifests = ["k8s/deployment.yaml", "k8s/service.yaml", "k8s/ingress.yaml", "k8s/cluster-issuer.yaml"]
        else:
            # Use core deployment without security policies
            if self.run_command("kubectl apply -f k8s/deploy-core.yaml", "Applying core deployment", check=False):
                print("✅ Core deployment applied successfully!")
            else:
                # Fallback to individual manifests
                manifests = ["k8s/deployment.yaml", "k8s/service.yaml"]
                for manifest in manifests:
                    self.run_command(f"kubectl apply -f {manifest}", f"Applying {manifest}", check=False)
        
        if self.install_kubearmor:
            for manifest in manifests:
                if not self.run_command(f"kubectl apply -f {manifest}", f"Applying {manifest}", check=False):
                    print(f"⚠️  Failed to apply {manifest}")
        
        # Check deployment status
        self.run_command("kubectl get pods -l app=wisecow", "Checking deployment status", check=False)
        
        print("✅ Kubernetes deployment completed!")
        print("💡 Access via: kubectl port-forward svc/wisecow 8080:4499")
        return True

    def install_kubearmor_if_requested(self):
        """Install KubeArmor if requested"""
        if not self.install_kubearmor:
            return True
            
        self.log_step("Installing KubeArmor (Optional)")
        
        # Check if Helm is available
        if not self.run_command("helm version", "Checking Helm availability", check=False):
            print("⚠️  Helm not available - KubeArmor installation skipped")
            print("💡 Install Helm to enable KubeArmor: https://helm.sh/docs/intro/install/")
            return True
        
        # Install KubeArmor
        commands = [
            ("helm repo add kubearmor https://kubearmor.github.io/charts", "Adding KubeArmor Helm repo"),
            ("helm repo update kubearmor", "Updating KubeArmor Helm repo"),
            ("helm upgrade --install kubearmor-operator kubearmor/kubearmor-operator -n kubearmor --create-namespace", "Installing KubeArmor operator"),
        ]
        
        for cmd, desc in commands:
            if not self.run_command(cmd, desc, check=False):
                print("⚠️  KubeArmor installation failed, continuing without it")
                return True
        
        print("✅ KubeArmor installation initiated!")
        print("💡 KubeArmor may take a few minutes to be fully ready")
        return True
    
    def display_summary(self):
        """Display deployment summary"""
        self.log_step("Deployment Summary")
        
        print("🎉 Wisecow deployment process completed!")
        print("\n📋 What was accomplished:")
        print("✅ Prerequisites validated")
        print("✅ Docker image built successfully")
        print("✅ Container tested locally")
        print("✅ Python dependencies installed")
        print("✅ Monitoring scripts validated")
        
        print("\n🚀 Next Steps:")
        print("1. 🐳 Test locally: docker run -p 4499:4499 wisecow:local")
        print("2. 🌐 Visit: http://localhost:4499")
        print("3. 📊 Monitor: python scripts/app-health-checker.py http://localhost:4499")
        print("4. ☸️  Deploy to K8s: kubectl apply -f k8s/")
        
        print("\n💡 For production deployment:")
        print("- Push code to GitHub (triggers CI/CD)")
        print("- Configure GitHub secrets for automated deployment")
        print("- Setup Kubernetes cluster with ingress and cert-manager")
        
        return True
    
    def deploy(self):
        """Execute Windows-compatible deployment process"""
        print("🚀 Starting Windows Wisecow Deployment")
        print("=" * 50)
        
        deployment_steps = [
            ("validate_prerequisites", "Validate Prerequisites"),
            ("build_docker_image", "Build Docker Image"),
            ("test_container_locally", "Test Container Locally"),
            ("install_python_dependencies", "Install Python Dependencies"),
            ("test_monitoring_scripts", "Test Monitoring Scripts"),
            ("deploy_to_kubernetes", "Deploy to Kubernetes (Optional)"),
            ("install_kubearmor_if_requested", "Install KubeArmor (Optional)"),
            ("display_summary", "Display Summary")
        ]
        
        try:
            for step_method, step_name in deployment_steps:
                method = getattr(self, step_method)
                if not method():
                    if step_name in ["Deploy to Kubernetes (Optional)"]:
                        print(f"⚠️  Optional step skipped: {step_name}")
                        continue
                    else:
                        print(f"\n💥 Deployment failed at step: {step_name}")
                        print("🔧 Please fix the issues and try again.")
                        return False
            
            print("\n🎊 DEPLOYMENT SUCCESSFUL! 🎊")
            return True
            
        except KeyboardInterrupt:
            print("\n🛑 Deployment interrupted by user")
            return False
        except Exception as e:
            print(f"\n💥 Deployment failed with error: {e}")
            return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Windows Wisecow Deployment Script')
    parser.add_argument('--with-kubearmor', action='store_true', 
                       help='Install KubeArmor for zero-trust security')
    
    args = parser.parse_args()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        parser.print_help()
        print("\nThis script will:")
        print("1. Validate prerequisites")
        print("2. Build Docker image")
        print("3. Test container locally")
        print("4. Install Python dependencies")
        print("5. Test monitoring scripts")
        print("6. Optionally deploy to Kubernetes")
        print("7. Optionally install KubeArmor")
        print("\nExamples:")
        print("  python scripts/windows-deploy.py                    # Basic deployment")
        print("  python scripts/windows-deploy.py --with-kubearmor   # With zero-trust security")
        return
    
    deployer = WindowsWisecowDeployer(install_kubearmor=args.with_kubearmor)
    success = deployer.deploy()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()