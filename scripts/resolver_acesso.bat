@echo off
REM ========================================
REM CÓRTEX BI - Resolver Problemas de Acesso
REM ========================================

echo 🔧 CÓRTEX BI - Resolver Problemas de Acesso
echo ==========================================

echo [INFO] Este script ajuda a resolver problemas de acesso aos links
echo.

echo [1/5] Verificando firewall do Windows...
echo 💡 Liberando porta 5000 no firewall...

REM Tentar liberar porta no firewall (requer admin)
netsh advfirewall firewall add rule name="CORTEX BI Port 5000" dir=in action=allow protocol=TCP localport=5000 2>nul
if %errorLevel% equ 0 (
    echo ✅ Porta 5000 liberada no firewall
) else (
    echo ⚠️  Não foi possível liberar automaticamente
    echo 📋 Execute como administrador ou libere manualmente:
    echo    - Painel de Controle → Firewall → Permitir aplicativo
    echo    - Adicionar porta 5000 TCP
)

echo.
echo [2/5] Verificando se servidor está no IP correto...
echo 📋 Configuração atual:
findstr /C:"HOST" /C:"PORT" .env 2>nul
if %errorLevel% neq 0 (
    echo ❌ Arquivo .env não encontrado ou sem configuração HOST
    echo 💡 Criando configuração correta...
    (
        echo HOST=0.0.0.0
        echo PORT=5000
    ) >> .env
    echo ✅ Configuração adicionada ao .env
)

echo.
echo [3/5] Testando diferentes formas de acesso...

echo 🧪 Testando localhost:5000...
curl -s -I http://localhost:5000/health 2>nul | find "200"
if %errorLevel% equ 0 (
    echo ✅ localhost:5000 funciona
) else (
    echo ❌ localhost:5000 não funciona
)

echo 🧪 Testando 127.0.0.1:5000...
curl -s -I http://127.0.0.1:5000/health 2>nul | find "200"
if %errorLevel% equ 0 (
    echo ✅ 127.0.0.1:5000 funciona
) else (
    echo ❌ 127.0.0.1:5000 não funciona
)

echo 🧪 Testando IP da máquina...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /C:"IPv4"') do (
    set IP=%%a
    set IP=!IP: =!
    echo Testando !IP!:5000...
    curl -s -I http://!IP!:5000/health 2>nul | find "200"
    if !errorLevel! equ 0 (
        echo ✅ !IP!:5000 funciona
        echo 🌐 Use este IP: http://!IP!:5000
    )
)

echo.
echo [4/5] Verificando outros agentes Python...
echo 📋 Processos Python rodando:
tasklist | find "python" | find /V "find"

echo 📋 Portas ocupadas por Python:
netstat -ano | find ":500" | find "LISTENING"

echo.
echo [5/5] Sugestões de solução...
echo.
echo 🔧 SE NÃO CONSEGUIR ACESSAR OS LINKS:
echo ==========================================
echo.
echo 1️⃣ FIREWALL:
echo    • Execute este script como ADMINISTRADOR
echo    • Ou libere porta 5000 manualmente no Windows Firewall
echo.
echo 2️⃣ IP CORRETO:
echo    • Use o IP da sua máquina ao invés de 10.124.100.57
echo    • Execute: ipconfig para ver o IP real
echo.
echo 3️⃣ CONFLITO DE PORTA:
echo    • Se outro agente usa porta 5000, mude no .env:
echo    • PORT=5001 (ou outra porta livre)
echo.
echo 4️⃣ REINICIAR SERVIDOR:
echo    • Pare: taskkill /f /im python.exe
echo    • Inicie: start_cortexbi.bat
echo.
echo 5️⃣ TESTAR LOCALMENTE:
echo    • Primeiro teste: http://localhost:5000/docs
echo    • Se funcionar, problema é de rede
echo.
pause

