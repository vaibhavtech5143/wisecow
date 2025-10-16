@echo off
echo 🚀 Wisecow Windows Deployment
echo =============================

echo.
echo Choose deployment option:
echo 1. Basic deployment (recommended)
echo 2. Deployment with KubeArmor zero-trust security
echo 3. Help
echo.

set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo.
    echo 📋 Starting basic deployment...
    python scripts\windows-deploy.py
) else if "%choice%"=="2" (
    echo.
    echo 📋 Starting deployment with KubeArmor...
    python scripts\windows-deploy.py --with-kubearmor
) else if "%choice%"=="3" (
    echo.
    echo 📚 Deployment Options:
    echo.
    echo Option 1 - Basic Deployment:
    echo   - Builds Docker image
    echo   - Deploys to Kubernetes
    echo   - Sets up monitoring
    echo   - No additional security policies
    echo.
    echo Option 2 - With KubeArmor:
    echo   - Everything from Option 1
    echo   - Installs KubeArmor operator
    echo   - Applies zero-trust security policies
    echo   - Enhanced container security
    echo.
    echo 💡 Recommendation: Start with Option 1, add KubeArmor later if needed
    echo.
    pause
    goto :eof
) else (
    echo.
    echo ❌ Invalid choice. Please run the script again.
    pause
    goto :eof
)

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Deployment completed successfully!
    echo 💡 You can now test the application at: http://localhost:4499
    echo.
    echo 🔄 To run the container:
    echo    docker run -p 4499:4499 wisecow:local
    echo.
    echo 📊 To monitor the application:
    echo    python scripts\app-health-checker.py http://localhost:4499
    echo.
    if "%choice%"=="2" (
        echo 🔒 KubeArmor Security:
        echo    kubectl get kubearmor-policy
        echo    kubectl logs -n kubearmor -l app=kubearmor
        echo.
    )
) else (
    echo.
    echo ❌ Deployment failed!
    echo 💡 Please check the errors above and try again.
    echo.
)

pause