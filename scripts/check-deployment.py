#!/usr/bin/env python
"""
Wisecow Deployment Status Checker
Check the current status of all Wisecow components
"""

import subprocess
import sys
import time

class DeploymentChecker:
    def __init__(self):
        self.success_count = 0
        self.total_checks = 0
        
    def run_command(self, command, description):
        """Run command and return success status"""
        self.total_checks += 1
        print(f"🔍 {description}")
        
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"✅ {description} - OK")
                if result.stdout.strip():
                    # Show relevant output
                    lines = result.stdout.strip().split('\n')
                    for line in lines[:3]:  # Show first 3 lines
                        print(f"   📄 {line}")
                    if len(lines) > 3:
                        print(f"   📄 ... and {len(lines)-3} more lines")
                self.success_count += 1
                return True
            else:
                print(f"❌ {description} - FAILED")
                if result.stderr.strip():
                    print(f"   🚨 Error: {result.stderr.strip()}")
                return False
                
        except Exception as e:
            print(f"❌ {description} - ERROR: {e}")
            return False
    
    def check_docker_status(self):
        """Check Docker containers"""
        print("\n🐳 DOCKER STATUS")
        print("=" * 40)
        
        self.run_command("docker --version", "Docker version")
        self.run_command("docker ps --filter name=wisecow", "Wisecow containers")
        self.run_command("docker images wisecow", "Wisecow images")
    
    def check_kubernetes_status(self):
        """Check Kubernetes deployment"""
        print("\n☸️ KUBERNETES STATUS")
        print("=" * 40)
        
        if not self.run_command("kubectl cluster-info --request-timeout=10s", "Cluster connectivity"):
            print("⚠️  Kubernetes cluster not accessible")
            return False
        
        # Check Wisecow components
        self.run_command("kubectl get deployment wisecow", "Wisecow deployment")
        self.run_command("kubectl get service wisecow", "Wisecow service")
        self.run_command("kubectl get ingress wisecow-ingress", "Wisecow ingress")
        self.run_command("kubectl get pods -l app=wisecow", "Wisecow pods")
        
        # Check certificates
        self.run_command("kubectl get certificates", "TLS certificates")
        self.run_command("kubectl get clusterissuer", "Certificate issuers")
        
        return True
    
    def check_application_health(self):
        """Check application accessibility"""
        print("\n🌐 APPLICATION HEALTH")
        print("=" * 40)
        
        # Check if port-forward is possible
        print("🔗 Testing Kubernetes service accessibility...")
        
        try:
            # Try to get service endpoint
            result = subprocess.run("kubectl get endpoints wisecow", 
                                  shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ Service endpoints available")
                print(f"   📄 {result.stdout.strip()}")
                
                # Suggest port-forward command
                print("\n💡 To access the application:")
                print("   kubectl port-forward svc/wisecow 8080:4499")
                print("   Then visit: http://localhost:8080")
                
            else:
                print("❌ Service endpoints not available")
                
        except Exception as e:
            print(f"❌ Service check failed: {e}")
    
    def check_monitoring_tools(self):
        """Check monitoring scripts"""
        print("\n📊 MONITORING TOOLS")
        print("=" * 40)
        
        # Check Python and dependencies
        self.run_command("python --version", "Python availability")
        
        # Test monitoring scripts
        scripts = [
            ("python scripts/app-health-checker.py --help", "App health checker"),
            ("python scripts/system-health-monitor.py --help", "System health monitor")
        ]
        
        for cmd, desc in scripts:
            self.run_command(cmd, desc)
    
    def check_security_components(self):
        """Check security components"""
        print("\n🔒 SECURITY COMPONENTS")
        print("=" * 40)
        
        # Check cert-manager
        if self.run_command("kubectl get namespace cert-manager", "cert-manager namespace"):
            self.run_command("kubectl get pods -n cert-manager", "cert-manager pods")
        
        # Check KubeArmor (optional)
        if self.run_command("kubectl get namespace kubearmor", "KubeArmor namespace"):
            self.run_command("kubectl get pods -n kubearmor", "KubeArmor pods")
            self.run_command("kubectl get kubearmor-policy", "KubeArmor policies")
        else:
            print("⚠️  KubeArmor not installed (optional security component)")
            print("💡 To install KubeArmor:")
            print("   curl -s https://raw.githubusercontent.com/kubearmor/KubeArmor/main/getting-started/install_kubearmor.sh | bash")
    
    def provide_next_steps(self):
        """Provide next steps based on current status"""
        print("\n🚀 NEXT STEPS")
        print("=" * 40)
        
        print("Based on your current deployment status:")
        print()
        
        if self.success_count > self.total_checks * 0.8:  # 80% success rate
            print("🎉 Your Wisecow deployment is mostly successful!")
            print()
            print("✅ Recommended actions:")
            print("1. 🌐 Access your application:")
            print("   kubectl port-forward svc/wisecow 8080:4499")
            print("   Open: http://localhost:8080")
            print()
            print("2. 📊 Monitor your application:")
            print("   python scripts/app-health-checker.py http://localhost:8080 --continuous")
            print()
            print("3. 🔒 Optional - Install KubeArmor for enhanced security:")
            print("   curl -s https://raw.githubusercontent.com/kubearmor/KubeArmor/main/getting-started/install_kubearmor.sh | bash")
            print("   kubectl apply -f k8s/kubearmor-policy.yaml")
            
        else:
            print("⚠️  Some components need attention:")
            print()
            print("🔧 Troubleshooting steps:")
            print("1. Check if Docker is running")
            print("2. Verify Kubernetes cluster is accessible")
            print("3. Ensure all manifests are applied: kubectl apply -f k8s/")
            print("4. Check pod logs: kubectl logs -l app=wisecow")
        
        print()
        print("📚 For detailed help, see:")
        print("- README.md - Main documentation")
        print("- DEPLOYMENT_GUIDE.md - Comprehensive deployment guide")
        print("- WINDOWS_SETUP.md - Windows-specific instructions")
    
    def run_full_check(self):
        """Run complete deployment status check"""
        print("🔍 WISECOW DEPLOYMENT STATUS CHECK")
        print("=" * 50)
        
        self.check_docker_status()
        self.check_kubernetes_status()
        self.check_application_health()
        self.check_monitoring_tools()
        self.check_security_components()
        
        # Summary
        print(f"\n📋 SUMMARY")
        print("=" * 40)
        print(f"✅ Successful checks: {self.success_count}/{self.total_checks}")
        print(f"📊 Success rate: {(self.success_count/self.total_checks)*100:.1f}%")
        
        self.provide_next_steps()

def main():
    checker = DeploymentChecker()
    checker.run_full_check()

if __name__ == '__main__':
    main()