@echo off
REM ========================================
REM CÓRTEX BI - Diagnosticar Problema de Acesso
REM ========================================

echo 🔍 CÓRTEX BI - Diagnosticando Problema de Acesso
echo ==========================================

echo [INFO] Servidor está rodando, mas links não abrem
echo [INFO] Vamos descobrir o problema específico
echo.

echo [1/8] Verificando se servidor responde localmente...
echo 🧪 Testando conectividade básica...

REM Teste básico de conectividade
netstat -an | find ":5000" | find "LISTENING"
if %errorLevel% equ 0 (
    echo ✅ Servidor está ouvindo na porta 5000
) else (
    echo ❌ Servidor NÃO está ouvindo na porta 5000
    echo 💡 Reinicie o servidor: python main_ai.py
    pause
    exit /b 1
)

echo.
echo [2/8] Descobrindo IP real da máquina...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /C:"IPv4" ^| findstr /V "127.0.0.1"') do (
    set REAL_IP=%%a
    set REAL_IP=!REAL_IP: =!
    echo 📍 IP encontrado: !REAL_IP!
    goto :found_ip
)
:found_ip

echo.
echo [3/8] Testando diferentes formas de acesso...

echo 🧪 Teste 1: Usando telnet para localhost:5000
telnet localhost 5000 2>nul
if %errorLevel% equ 0 (
    echo ✅ Telnet localhost:5000 - CONECTA
) else (
    echo ❌ Telnet localhost:5000 - FALHA
)

echo 🧪 Teste 2: Usando telnet para 127.0.0.1:5000
telnet 127.0.0.1 5000 2>nul
if %errorLevel% equ 0 (
    echo ✅ Telnet 127.0.0.1:5000 - CONECTA
) else (
    echo ❌ Telnet 127.0.0.1:5000 - FALHA
)

echo 🧪 Teste 3: Usando telnet para IP real
telnet %REAL_IP% 5000 2>nul
if %errorLevel% equ 0 (
    echo ✅ Telnet %REAL_IP%:5000 - CONECTA
) else (
    echo ❌ Telnet %REAL_IP%:5000 - FALHA
)

echo.
echo [4/8] Verificando firewall do Windows...
echo 📋 Regras de firewall para porta 5000:
netsh advfirewall firewall show rule name=all | find "5000"
if %errorLevel% neq 0 (
    echo ⚠️  Nenhuma regra de firewall encontrada para porta 5000
    echo 💡 Isso pode estar bloqueando o acesso
)

echo.
echo [5/8] Verificando se há proxy ou antivírus bloqueando...
echo 📋 Processos que podem interferir:
tasklist | find /I "kaspersky"
tasklist | find /I "avast"
tasklist | find /I "norton"
tasklist | find /I "mcafee"
tasklist | find /I "proxy"

echo.
echo [6/8] Testando navegadores disponíveis...
echo 🌐 Tentando abrir automaticamente...

REM Tentar abrir com diferentes navegadores
start "" "http://localhost:5000/docs" 2>nul
timeout /t 2 /nobreak >nul

start "" "http://127.0.0.1:5000/docs" 2>nul
timeout /t 2 /nobreak >nul

echo ✅ Tentativas de abertura realizadas

echo.
echo [7/8] Verificando configuração do servidor...
echo 📋 Configuração atual do CÓRTEX BI:
if exist ".env" (
    findstr /C:"HOST" /C:"PORT" .env
) else (
    echo ⚠️  Arquivo .env não encontrado
)

echo.
echo [8/8] Criando URLs alternativas para teste...
echo.
echo 🌐 TESTE ESTAS URLs NO NAVEGADOR:
echo ==========================================
echo.
echo 📚 DOCUMENTAÇÃO:
echo • http://localhost:5000/docs
echo • http://127.0.0.1:5000/docs
echo • http://%REAL_IP%:5000/docs
echo.
echo 🔍 HEALTH CHECK:
echo • http://localhost:5000/health
echo • http://127.0.0.1:5000/health
echo • http://%REAL_IP%:5000/health
echo.
echo 🎛️ ADMIN DASHBOARD:
echo • http://localhost:5000/admin/admin_dashboard.html
echo • http://127.0.0.1:5000/admin/admin_dashboard.html
echo • http://%REAL_IP%:5000/admin/admin_dashboard.html
echo.

echo ==========================================
echo 🔧 SOLUÇÕES MAIS COMUNS:
echo ==========================================
echo.
echo 1️⃣ FIREWALL BLOQUEANDO:
echo    • Execute como ADMINISTRADOR: resolver_acesso.bat
echo    • Ou libere porta 5000 manualmente no Windows Firewall
echo.
echo 2️⃣ ANTIVÍRUS BLOQUEANDO:
echo    • Adicione exceção para python.exe
echo    • Adicione exceção para pasta do projeto
echo.
echo 3️⃣ PROXY CORPORATIVO:
echo    • Configure proxy no navegador
echo    • Ou use IP direto ao invés de localhost
echo.
echo 4️⃣ NAVEGADOR COM PROBLEMA:
echo    • Tente outro navegador (Chrome, Firefox, Edge)
echo    • Limpe cache do navegador
echo.
echo 5️⃣ SERVIDOR BINDING INCORRETO:
echo    • Verifique se servidor está em 0.0.0.0:5000
echo    • Não deve estar em 127.0.0.1:5000
echo.

echo ==========================================
echo 📋 PRÓXIMOS PASSOS:
echo ==========================================
echo.
echo 1. Copie uma das URLs acima
echo 2. Cole no navegador manualmente
echo 3. Se não funcionar, execute como ADMIN: resolver_acesso.bat
echo 4. Se ainda não funcionar, me envie print do erro do navegador
echo.
pause

