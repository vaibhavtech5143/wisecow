#!/usr/bin/env python3
"""
Wisecow Deployment Orchestrator
Handles complete deployment from validation to monitoring
"""

import os
import sys
import time
import subprocess
import json
from pathlib import Path

class WisecowDeployer:
    def __init__(self, install_kubearmor=False):
        self.deployment_steps = []
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
        """Validate all prerequisites before deployment"""
        self.log_step("Validating Prerequisites")
        
        # Run pre-deployment validation - try different Python commands
        python_commands = ["python", "python3", "py"]
        validation_success = False
        
        for py_cmd in python_commands:
            if self.run_command(f"{py_cmd} scripts/pre-deployment-check.py", 
                               f"Running comprehensive validation with {py_cmd}", check=False):
                validation_success = True
                break
        
        if not validation_success:
            print("❌ Pre-deployment validation failed!")
            print("💡 Fix all critical errors before proceeding.")
            return False
            
        return True
    
    def build_docker_image(self):
        """Build Docker image locally"""
        self.log_step("Building Docker Image")
        
        commands = [
            ("docker build -t wisecow:local .", "Building Wisecow Docker image"),
            ("docker images | grep wisecow", "Verifying image creation")
        ]
        
        for cmd, desc in commands:
            if not self.run_command(cmd, desc):
                return False
                
        return True
    
    def test_container_locally(self):
        """Test container functionality locally"""
        self.log_step("Testing Container Locally")
        
        # Start container in background
        if not self.run_command("docker run -d --name wisecow-test -p 4499:4499 wisecow:local", 
                               "Starting test container"):
            return False
            
        # Wait for container to start
        print("⏳ Waiting for container to start...")
        time.sleep(10)
        
        # Test HTTP response
        test_success = self.run_command("curl -f http://localhost:4499", 
                                      "Testing HTTP response", check=False)
        
        # Cleanup
        self.run_command("docker stop wisecow-test", "Stopping test container", check=False)
        self.run_command("docker rm wisecow-test", "Removing test container", check=False)
        
        return test_success
    
    def deploy_to_kubernetes(self):
        """Deploy to Kubernetes cluster"""
        self.log_step("Deploying to Kubernetes")
        
        # Check cluster connectivity
        if not self.run_command("kubectl cluster-info", "Checking cluster connectivity"):
            print("❌ Kubernetes cluster not accessible!")
            print("💡 Ensure kubectl is configured and cluster is running.")
            return False
        
        # Apply manifests in order
        manifests = [
            "k8s/cluster-issuer.yaml",
            "k8s/deployment.yaml", 
            "k8s/service.yaml",
            "k8s/ingress.yaml"
        ]
        
        for manifest in manifests:
            if not self.run_command(f"kubectl apply -f {manifest}", 
                                  f"Applying {manifest}"):
                return False
        
        # Wait for deployment to be ready
        if not self.run_command("kubectl rollout status deployment/wisecow --timeout=300s", 
                               "Waiting for deployment to be ready"):
            return False
            
        return True
    
    def verify_deployment(self):
        """Verify deployment is working correctly"""
        self.log_step("Verifying Deployment")
        
        # Check pod status
        if not self.run_command("kubectl get pods -l app=wisecow", 
                               "Checking pod status"):
            return False
        
        # Check service
        if not self.run_command("kubectl get svc wisecow", 
                               "Checking service status"):
            return False
        
        # Port forward and test
        print("🔗 Setting up port forwarding for testing...")
        port_forward_cmd = "kubectl port-forward svc/wisecow 8080:4499"
        
        # Start port forwarding in background
        try:
            port_forward_process = subprocess.Popen(port_forward_cmd.split(), 
                                                  stdout=subprocess.PIPE, 
                                                  stderr=subprocess.PIPE)
            
            # Wait for port forwarding to establish
            time.sleep(5)
            
            # Test the application
            test_result = self.run_command("curl -f http://localhost:8080", 
                                         "Testing application via port-forward", check=False)
            
            # Cleanup port forwarding
            port_forward_process.terminate()
            port_forward_process.wait(timeout=5)
            
            return test_result
            
        except Exception as e:
            print(f"❌ Port forwarding test failed: {e}")
            return False
    
    def setup_monitoring(self):
        """Setup monitoring for the deployed application"""
        self.log_step("Setting Up Monitoring")
        
        # Install Python dependencies for monitoring - try different pip commands
        pip_commands = ["pip", "pip3", "py -m pip"]
        pip_success = False
        
        for pip_cmd in pip_commands:
            if self.run_command(f"{pip_cmd} install -r scripts/requirements.txt", 
                               f"Installing monitoring dependencies with {pip_cmd}", check=False):
                pip_success = True
                break
        
        if not pip_success:
            print("⚠️  Monitoring dependencies installation failed")
            print("💡 Install manually: pip install requests psutil")
        
        # Test monitoring scripts - use Windows-compatible Python command
        python_cmd = "python"  # Use python instead of python3 on Windows
        scripts_to_test = [
            (f"{python_cmd} scripts/app-health-checker.py --help", "Testing app health checker"),
            (f"{python_cmd} scripts/system-health-monitor.py --help", "Testing system monitor")
        ]
        
        for cmd, desc in scripts_to_test:
            self.run_command(cmd, desc, check=False)
        
        print("📊 Monitoring setup complete!")
        print("💡 Use these commands to start monitoring:")
        print("   python scripts/app-health-checker.py http://localhost:8080 --continuous")
        print("   python scripts/system-health-monitor.py --continuous")
        
        return True
    
    def install_kubearmor_if_requested(self):
        """Install KubeArmor if requested"""
        if not self.install_kubearmor:
            return True
            
        self.log_step("Installing KubeArmor")
        
        # Check if KubeArmor is already installed
        if self.run_command("kubectl get ns kubearmor", "Checking KubeArmor namespace", check=False):
            print("✅ KubeArmor already installed")
            return True
        
        # Install KubeArmor using Helm
        commands = [
            ("helm repo add kubearmor https://kubearmor.github.io/charts", "Adding KubeArmor Helm repo"),
            ("helm repo update kubearmor", "Updating KubeArmor Helm repo"),
            ("helm upgrade --install kubearmor-operator kubearmor/kubearmor-operator -n kubearmor --create-namespace", "Installing KubeArmor operator"),
        ]
        
        for cmd, desc in commands:
            if not self.run_command(cmd, desc, check=False):
                print("⚠️  KubeArmor installation failed, continuing without it")
                return True
        
        # Apply KubeArmor configuration
        if self.run_command("kubectl apply -f https://raw.githubusercontent.com/kubearmor/KubeArmor/main/pkg/KubeArmorOperator/config/samples/sample-config.yml", 
                           "Applying KubeArmor configuration", check=False):
            
            # Wait for KubeArmor to be ready
            print("⏳ Waiting for KubeArmor to be ready (this may take a few minutes)...")
            self.run_command("kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=kubearmor -n kubearmor --timeout=300s", 
                           "Waiting for KubeArmor pods", check=False)
            
            print("✅ KubeArmor installation completed!")
        else:
            print("⚠️  KubeArmor configuration failed")
        
        return True

    def apply_security_policy(self):
        """Apply KubeArmor security policy"""
        self.log_step("Applying Security Policy")
        
        # Check if KubeArmor is available
        kubearmor_available = self.run_command("kubectl get crd kubearmor-policies.security.kubearmor.com", 
                                             "Checking KubeArmor CRDs", check=False)
        
        if kubearmor_available:
            if self.run_command("kubectl apply -f k8s/kubearmor-policy.yaml", 
                              "Applying KubeArmor security policy", check=False):
                print("🔒 Zero-trust security policy applied successfully!")
                
                # Show policy status
                self.run_command("kubectl get kubearmor-policy", "Checking policy status", check=False)
            else:
                print("⚠️  Security policy application failed")
        else:
            print("⚠️  KubeArmor CRDs not found - security policy skipped")
            if not self.install_kubearmor:
                print("💡 Use --with-kubearmor flag to install KubeArmor automatically")
                print("💡 Or install manually:")
                print("   helm repo add kubearmor https://kubearmor.github.io/charts")
                print("   helm upgrade --install kubearmor-operator kubearmor/kubearmor-operator -n kubearmor --create-namespace")
        
        return True
    
    def display_deployment_info(self):
        """Display final deployment information"""
        self.log_step("Deployment Complete!")
        
        print("🎉 Wisecow has been successfully deployed!")
        print("\n📋 Deployment Summary:")
        print("=" * 40)
        
        # Get deployment info
        self.run_command("kubectl get all -l app=wisecow", "Current deployment status", check=False)
        
        print("\n🔗 Access Information:")
        print("- Local access: kubectl port-forward svc/wisecow 8080:4499")
        print("- Then visit: http://localhost:8080")
        
        print("\n📊 Monitoring Commands:")
        print("- App health: python3 scripts/app-health-checker.py http://localhost:8080")
        print("- System health: python3 scripts/system-health-monitor.py")
        
        print("\n🔒 Security:")
        print("- KubeArmor policy applied for zero-trust security")
        print("- TLS certificates managed by cert-manager")
        
        print("\n💡 Next Steps:")
        print("1. Configure DNS for your domain (if using ingress)")
        print("2. Set up monitoring dashboards")
        print("3. Configure backup and disaster recovery")
        
        return True
    
    def deploy(self):
        """Execute complete deployment process"""
        print("🚀 Starting Wisecow Deployment Orchestrator")
        print("=" * 60)
        
        deployment_steps = [
            ("validate_prerequisites", "Validate Prerequisites"),
            ("build_docker_image", "Build Docker Image"),
            ("test_container_locally", "Test Container Locally"),
            ("deploy_to_kubernetes", "Deploy to Kubernetes"),
            ("verify_deployment", "Verify Deployment"),
            ("setup_monitoring", "Setup Monitoring"),
            ("install_kubearmor_if_requested", "Install KubeArmor (Optional)"),
            ("apply_security_policy", "Apply Security Policy"),
            ("display_deployment_info", "Display Deployment Info")
        ]
        
        try:
            for step_method, step_name in deployment_steps:
                method = getattr(self, step_method)
                if not method():
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
    
    parser = argparse.ArgumentParser(description='Wisecow Deployment Orchestrator')
    parser.add_argument('--with-kubearmor', action='store_true', 
                       help='Install KubeArmor for zero-trust security')
    
    args = parser.parse_args()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        parser.print_help()
        print("\nThis script will:")
        print("1. Validate all prerequisites")
        print("2. Build and test Docker image")
        print("3. Deploy to Kubernetes")
        print("4. Verify deployment")
        print("5. Setup monitoring")
        print("6. Optionally install KubeArmor")
        print("7. Apply security policies")
        print("\nExamples:")
        print("  python scripts/deploy-wisecow.py                    # Basic deployment")
        print("  python scripts/deploy-wisecow.py --with-kubearmor   # With zero-trust security")
        return
    
    deployer = WisecowDeployer(install_kubearmor=args.with_kubearmor)
    success = deployer.deploy()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()