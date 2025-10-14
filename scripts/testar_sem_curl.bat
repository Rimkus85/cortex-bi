@echo off
REM ========================================
REM CÓRTEX BI - Teste sem CURL
REM ========================================

echo 🧪 CÓRTEX BI - Teste sem CURL
echo ==========================================

echo [INFO] Este script testa o sistema sem usar o comando curl
echo.

echo [1/4] Verificando se servidor está rodando...
netstat -an | find ":5000" | find "LISTENING" >nul
if %errorLevel% equ 0 (
    echo ✅ Servidor está rodando na porta 5000
    set SERVER_RUNNING=1
) else (
    echo ❌ Servidor NÃO está rodando na porta 5000
    set SERVER_RUNNING=0
)

echo.
echo [2/4] Verificando processos Python...
tasklist | find "python" >nul
if %errorLevel% equ 0 (
    echo ✅ Processos Python encontrados:
    tasklist | find "python"
) else (
    echo ❌ Nenhum processo Python rodando
)

echo.
echo [3/4] Descobrindo IP da máquina...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /C:"IPv4" ^| findstr /V "127.0.0.1"') do (
    set REAL_IP=%%a
    set REAL_IP=!REAL_IP: =!
    echo 📍 IP encontrado: !REAL_IP!
    goto :found_ip
)
:found_ip

echo.
echo [4/4] Abrindo navegador para teste...

if %SERVER_RUNNING%==1 (
    echo ✅ Servidor rodando - Abrindo navegador...
    echo.
    echo 🌐 Abrindo URLs de teste:
    echo • http://localhost:5000/docs
    echo • http://localhost:5000/health
    echo.
    
    REM Abrir URLs no navegador padrão
    start http://localhost:5000/docs
    timeout /t 3 /nobreak >nul
    start http://localhost:5000/health
    
    echo ✅ Navegador aberto com as URLs de teste
    echo.
    echo 📋 O que você deve ver:
    echo • Documentação interativa da API (Swagger UI)
    echo • Status "healthy" na página de health
    
) else (
    echo ❌ Servidor não está rodando
    echo.
    echo 🔧 SOLUÇÕES:
    echo 1. Execute: corrigir_fastapi.bat
    echo 2. Ou execute: python main_ai.py
    echo 3. Depois execute este script novamente
)

echo.
echo ==========================================
echo 📋 RESUMO DO TESTE
echo ==========================================

if %SERVER_RUNNING%==1 (
    echo ✅ STATUS: Sistema funcionando
    echo 🌐 URLs para usar:
    echo   • Documentação: http://localhost:5000/docs
    echo   • Health Check: http://localhost:5000/health
    echo   • Admin Dashboard: http://localhost:5000/admin/admin_dashboard.html
    echo.
    echo 🎉 SUCESSO: CÓRTEX BI está operacional!
    echo 📋 Próximo passo: Integração com Copilot M365
) else (
    echo ❌ STATUS: Sistema não está funcionando
    echo 🔧 Execute: corrigir_fastapi.bat
    echo 💡 Depois tente: python main_ai.py
)

echo.
pause

