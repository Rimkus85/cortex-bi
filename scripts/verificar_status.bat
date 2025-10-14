@echo off
REM ========================================
REM CÓRTEX BI - Verificação de Status
REM ========================================

echo 🧠 CÓRTEX BI - Verificação de Status
echo ==========================================

echo [1/6] Verificando se o servidor está rodando...
netstat -an | find ":5000" | find "LISTENING"
if %errorLevel% equ 0 (
    echo ✅ Servidor está rodando na porta 5000
) else (
    echo ❌ Servidor NÃO está rodando na porta 5000
    echo 💡 Execute: start_cortexbi.bat
)

echo.
echo [2/6] Verificando processos Python...
tasklist | find "python"
if %errorLevel% equ 0 (
    echo ✅ Processos Python encontrados
) else (
    echo ❌ Nenhum processo Python rodando
)

echo.
echo [3/6] Testando conectividade local...
curl -s http://localhost:5000/health 2>nul
if %errorLevel% equ 0 (
    echo ✅ Servidor responde em localhost:5000
) else (
    echo ❌ Servidor não responde em localhost:5000
)

echo.
echo [4/6] Testando conectividade IP específico...
curl -s http://10.124.100.57:5000/health 2>nul
if %errorLevel% equ 0 (
    echo ✅ Servidor responde em 10.124.100.57:5000
) else (
    echo ❌ Servidor não responde em 10.124.100.57:5000
    echo 💡 Verificar configuração de rede/firewall
)

echo.
echo [5/6] Verificando logs...
if exist "logs\cortexbi.log" (
    echo ✅ Arquivo de log encontrado
    echo 📋 Últimas 5 linhas do log:
    powershell -command "Get-Content logs\cortexbi.log -Tail 5"
) else (
    echo ❌ Arquivo de log não encontrado
)

echo.
echo [6/6] Verificando configuração...
if exist ".env" (
    echo ✅ Arquivo .env encontrado
    echo 📋 Configurações principais:
    findstr /C:"HOST" /C:"PORT" /C:"ADMIN_USER" .env
) else (
    echo ❌ Arquivo .env não encontrado
)

echo.
echo ==========================================
echo 🔧 COMANDOS ÚTEIS:
echo ==========================================
echo • Iniciar servidor: start_cortexbi.bat
echo • Parar servidor: taskkill /f /im python.exe
echo • Ver logs: type logs\cortexbi.log
echo • Testar local: curl http://localhost:5000/health
echo • Testar IP: curl http://10.124.100.57:5000/health
echo.
echo 🌐 LINKS PARA TESTAR:
echo ==========================================
echo • Health Check: http://10.124.100.57:5000/health
echo • Documentação: http://10.124.100.57:5000/docs
echo • Admin Dashboard: http://10.124.100.57:5000/admin/admin_dashboard.html
echo.
pause

