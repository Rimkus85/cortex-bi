@echo off
REM ========================================
REM CÓRTEX BI - Reiniciar com Nova Configuração
REM ========================================

echo 🔄 CÓRTEX BI - Reiniciando com Nova Configuração
echo ==========================================

echo [INFO] Parando servidor atual...
echo 🛑 Finalizando processos Python...

REM Parar todos os processos Python relacionados
taskkill /f /im python.exe 2>nul
if %errorLevel% equ 0 (
    echo ✅ Processos Python finalizados
) else (
    echo ℹ️  Nenhum processo Python ativo
)

echo.
echo [INFO] Aguardando 3 segundos...
timeout /t 3 /nobreak >nul

echo.
echo [INFO] Iniciando servidor com nova configuração...
echo 🚀 Host: 0.0.0.0 (permite localhost + IP específico)
echo 🚀 Porta: 5000
echo.

echo ✅ CÓRTEX BI v2.0 - Iniciando com configuração corrigida...
echo ==========================================

python main_ai.py

echo.
echo 🎯 APÓS INICIALIZAÇÃO:
echo ==========================================
echo.
echo 🌐 TESTE ESTAS URLs:
echo • http://localhost:5000/docs
echo • http://127.0.0.1:5000/docs
echo • http://10.124.100.57:5000/docs
echo.
echo 🔍 HEALTH CHECK:
echo • http://localhost:5000/health
echo.
echo 🎛️ ADMIN DASHBOARD:
echo • http://localhost:5000/admin/admin_dashboard.html
echo.
pause

