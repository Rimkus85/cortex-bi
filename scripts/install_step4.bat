@echo off
REM ========================================
REM CÓRTEX BI - ETAPA 4: Configuração Final
REM ========================================

echo 🧠 CÓRTEX BI - ETAPA 4: Configuração Final
echo ==========================================

REM 1. Criar diretórios necessários
echo [1/5] Criando diretórios...
if not exist "logs" mkdir logs
if not exist "output" mkdir output
if not exist "uploads" mkdir uploads
if not exist "backups" mkdir backups
if not exist "config" mkdir config
echo ✅ Diretórios criados

REM 2. Criar arquivo .env básico
echo [2/5] Criando configuração básica...
if not exist ".env" (
    (
        echo # CÓRTEX BI - Configurações
        echo HOST=10.124.100.57
        echo PORT=5000
        echo DEBUG=False
        echo.
        echo # Administração
        echo ADMIN_USER=Redecorp\r337786
        echo.
        echo # SharePoint
        echo SHAREPOINT_URL=https://telefonicacorp-my.sharepoint.com/my?id=%%2Fpersonal%%2Fusr_mis_br_telefonica_com%%2FDocuments%%2FPython
        echo.
        echo # Logs
        echo LOG_LEVEL=INFO
        echo LOG_FILE=logs/cortexbi.log
    ) > .env
    echo ✅ Arquivo .env criado
) else (
    echo ✅ Arquivo .env já existe
)

REM 3. Testar importações básicas
echo [3/5] Testando importações básicas...
python -c "
try:
    import fastapi
    import uvicorn
    import pandas
    import numpy
    print('✅ Dependências básicas: OK')
except ImportError as e:
    print('❌ Erro nas dependências básicas:', e)
    exit(1)
"
if %errorLevel% neq 0 (
    echo ❌ ERRO: Dependências básicas falharam
    echo 📋 Execute novamente install_step2.bat
    pause
    exit /b 1
)

REM 4. Testar módulos do projeto
echo [4/5] Testando módulos do projeto...
python -c "
try:
    from agents.data_loader import DataLoader
    from agents.analytics_engine import AnalyticsEngine
    from agents.pptx_generator import PPTXGenerator
    print('✅ Módulos do projeto: OK')
except ImportError as e:
    print('⚠️  AVISO: Alguns módulos podem ter problemas:', e)
    print('💡 Sistema básico deve funcionar')
"

REM 5. Criar scripts de uso
echo [5/5] Criando scripts de uso...

REM Script de inicialização simples
(
    echo @echo off
    echo echo 🧠 CÓRTEX BI - Iniciando Sistema...
    echo echo 📍 Servidor: http://10.124.100.57:5000
    echo echo 📚 Docs: http://10.124.100.57:5000/docs
    echo echo.
    echo python main_ai.py
    echo pause
) > start_cortexbi.bat

REM Script de teste
(
    echo @echo off
    echo echo 🧪 CÓRTEX BI - Teste de Conectividade
    echo echo.
    echo curl http://10.124.100.57:5000/health
    echo echo.
    echo pause
) > test_cortexbi.bat

echo ✅ Scripts criados

echo.
echo 🎉 INSTALAÇÃO COMPLETA!
echo ==========================================
echo.
echo 📋 ARQUIVOS CRIADOS:
echo   • start_cortexbi.bat - Iniciar sistema
echo   • test_cortexbi.bat - Testar conectividade
echo   • .env - Configurações
echo.
echo 🚀 PRÓXIMOS PASSOS:
echo   1. Execute: start_cortexbi.bat
echo   2. Abra: http://10.124.100.57:5000/docs
echo   3. Teste: test_cortexbi.bat
echo.
echo 🔧 SE HOUVER PROBLEMAS:
echo   • Verifique logs em: logs/cortexbi.log
echo   • Execute: python main_ai.py (para ver erros)
echo.
pause

