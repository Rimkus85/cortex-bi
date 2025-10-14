@echo off
REM ========================================
REM CÓRTEX BI - Liberar Firewall (ADMIN)
REM ========================================

echo 🔐 CÓRTEX BI - Liberando Firewall (Requer ADMIN)
echo ==========================================

REM Verificar se está rodando como administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ ERRO: Este script precisa ser executado como ADMINISTRADOR
    echo.
    echo 💡 COMO EXECUTAR COMO ADMIN:
    echo 1. Clique direito no arquivo
    echo 2. Selecione "Executar como administrador"
    echo 3. Clique "Sim" na janela de confirmação
    echo.
    pause
    exit /b 1
)

echo ✅ Executando como administrador
echo.

echo [1/5] Liberando porta 5000 TCP (entrada)...
netsh advfirewall firewall add rule name="CORTEX BI - Porta 5000 TCP IN" dir=in action=allow protocol=TCP localport=5000
if %errorLevel% equ 0 (
    echo ✅ Regra de entrada criada com sucesso
) else (
    echo ⚠️  Falha ao criar regra de entrada
)

echo.
echo [2/5] Liberando porta 5000 TCP (saída)...
netsh advfirewall firewall add rule name="CORTEX BI - Porta 5000 TCP OUT" dir=out action=allow protocol=TCP localport=5000
if %errorLevel% equ 0 (
    echo ✅ Regra de saída criada com sucesso
) else (
    echo ⚠️  Falha ao criar regra de saída
)

echo.
echo [3/5] Liberando Python.exe no firewall...
netsh advfirewall firewall add rule name="CORTEX BI - Python.exe" dir=in action=allow program="python.exe"
if %errorLevel% equ 0 (
    echo ✅ Python.exe liberado no firewall
) else (
    echo ⚠️  Falha ao liberar Python.exe
)

echo.
echo [4/5] Verificando regras criadas...
echo 📋 Regras do CÓRTEX BI no firewall:
netsh advfirewall firewall show rule name="CORTEX BI*"

echo.
echo [5/5] Testando conectividade após liberação...
echo 🧪 Aguarde 5 segundos para aplicar mudanças...
timeout /t 5 /nobreak >nul

echo 🧪 Testando acesso local...
telnet localhost 5000 2>nul
if %errorLevel% equ 0 (
    echo ✅ Conectividade local: OK
) else (
    echo ❌ Conectividade local: AINDA COM PROBLEMA
)

echo.
echo ==========================================
echo 🎉 FIREWALL CONFIGURADO!
echo ==========================================
echo.
echo ✅ Porta 5000 liberada no Windows Firewall
echo ✅ Python.exe autorizado
echo ✅ Regras de entrada e saída criadas
echo.
echo 🌐 TESTE AGORA ESTAS URLs:
echo • http://localhost:5000/docs
echo • http://127.0.0.1:5000/docs
echo.
echo 💡 SE AINDA NÃO FUNCIONAR:
echo 1. Reinicie o navegador
echo 2. Tente outro navegador
echo 3. Verifique antivírus
echo 4. Execute: diagnosticar_acesso.bat
echo.
pause

