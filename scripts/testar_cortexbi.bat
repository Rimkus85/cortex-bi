@echo off
REM ========================================
REM CÓRTEX BI - Teste Completo do Sistema
REM ========================================

echo 🧪 CÓRTEX BI - Teste Completo do Sistema
echo ==========================================

setlocal enabledelayedexpansion

echo [TESTE 1] Verificando se servidor está rodando...
netstat -an | find ":5000" | find "LISTENING" >nul
if %errorLevel% equ 0 (
    echo ✅ Servidor rodando na porta 5000
) else (
    echo ❌ Servidor NÃO está rodando
    echo 💡 Iniciando servidor...
    start /B python main_ai.py
    echo ⏳ Aguardando 10 segundos...
    timeout /t 10 /nobreak >nul
)

echo.
echo [TESTE 2] Descobrindo IP real da máquina...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /C:"IPv4" ^| findstr /V "127.0.0.1"') do (
    set REAL_IP=%%a
    set REAL_IP=!REAL_IP: =!
    echo 📍 IP encontrado: !REAL_IP!
    goto :found_ip
)
:found_ip

echo.
echo [TESTE 3] Testando conectividade...

echo 🧪 Teste 1: localhost:5000
curl -s http://localhost:5000/health 2>nul
if %errorLevel% equ 0 (
    echo ✅ localhost:5000 - OK
    set LOCAL_OK=1
) else (
    echo ❌ localhost:5000 - FALHOU
    set LOCAL_OK=0
)

echo 🧪 Teste 2: %REAL_IP%:5000
curl -s http://%REAL_IP%:5000/health 2>nul
if %errorLevel% equ 0 (
    echo ✅ %REAL_IP%:5000 - OK
    set IP_OK=1
) else (
    echo ❌ %REAL_IP%:5000 - FALHOU
    set IP_OK=0
)

echo 🧪 Teste 3: 10.124.100.57:5000
curl -s http://10.124.100.57:5000/health 2>nul
if %errorLevel% equ 0 (
    echo ✅ 10.124.100.57:5000 - OK
    set CONFIG_IP_OK=1
) else (
    echo ❌ 10.124.100.57:5000 - FALHOU
    set CONFIG_IP_OK=0
)

echo.
echo [TESTE 4] Testando endpoints principais...

if %LOCAL_OK%==1 (
    set BASE_URL=http://localhost:5000
) else if %IP_OK%==1 (
    set BASE_URL=http://%REAL_IP%:5000
) else (
    set BASE_URL=http://10.124.100.57:5000
)

echo 📍 Usando URL base: %BASE_URL%

echo 🧪 Testando /health...
curl -s %BASE_URL%/health | find "healthy" >nul
if %errorLevel% equ 0 (
    echo ✅ Health check - OK
) else (
    echo ❌ Health check - FALHOU
)

echo 🧪 Testando /docs...
curl -s -I %BASE_URL%/docs | find "200" >nul
if %errorLevel% equ 0 (
    echo ✅ Documentação - OK
) else (
    echo ❌ Documentação - FALHOU
)

echo 🧪 Testando /list-files...
curl -s %BASE_URL%/list-files | find "files" >nul
if %errorLevel% equ 0 (
    echo ✅ List files - OK
) else (
    echo ❌ List files - FALHOU
)

echo.
echo [TESTE 5] Verificando logs de erro...
if exist "logs\cortexbi.log" (
    echo 📋 Últimas linhas do log:
    powershell -command "Get-Content logs\cortexbi.log -Tail 3"
) else (
    echo ⚠️  Log não encontrado
)

echo.
echo ==========================================
echo 📊 RESULTADO DOS TESTES
echo ==========================================

if %LOCAL_OK%==1 (
    echo ✅ SUCESSO: Sistema funcionando localmente
    echo 🌐 Acesse: http://localhost:5000/docs
) else (
    echo ❌ PROBLEMA: Sistema não responde localmente
)

if %IP_OK%==1 (
    echo ✅ SUCESSO: Sistema acessível pela rede
    echo 🌐 Acesse: http://%REAL_IP%:5000/docs
) else (
    echo ❌ PROBLEMA: Sistema não acessível pela rede
    echo 💡 Verificar firewall e configuração de rede
)

echo.
echo 🎯 LINKS PARA USAR:
echo ==========================================
if %LOCAL_OK%==1 (
    echo • Documentação: http://localhost:5000/docs
    echo • Health Check: http://localhost:5000/health
    echo • Admin Dashboard: http://localhost:5000/admin/admin_dashboard.html
)
if %IP_OK%==1 (
    echo • Documentação: http://%REAL_IP%:5000/docs
    echo • Health Check: http://%REAL_IP%:5000/health
    echo • Admin Dashboard: http://%REAL_IP%:5000/admin/admin_dashboard.html
)

echo.
echo 🔧 PRÓXIMOS PASSOS:
echo ==========================================
if %LOCAL_OK%==1 (
    echo ✅ Sistema OK! Pode prosseguir com integração Copilot M365
) else (
    echo ❌ Resolver problemas de conectividade primeiro
    echo 💡 Execute: resolver_acesso.bat
)

echo.
pause

