@echo off
REM ========================================
REM CÓRTEX BI - ETAPA 1: Verificação Básica
REM ========================================

echo 🧠 CÓRTEX BI - ETAPA 1: Verificação Básica
echo ==========================================

REM 1. Verificar Python
echo [1/4] Verificando Python...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ ERRO: Python não encontrado
    echo 📥 SOLUÇÃO: Instale Python 3.8+ de https://python.org/downloads/
    echo ⚠️  IMPORTANTE: Marque "Add Python to PATH" durante instalação
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% encontrado

REM 2. Verificar pip
echo [2/4] Verificando pip...
pip --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ ERRO: pip não encontrado
    echo 📥 SOLUÇÃO: Reinstale Python com pip incluído
    pause
    exit /b 1
)
echo ✅ pip encontrado

REM 3. Atualizar pip
echo [3/4] Atualizando pip...
python -m pip install --upgrade pip
if %errorLevel% neq 0 (
    echo ⚠️  AVISO: Erro ao atualizar pip, mas continuando...
)
echo ✅ pip atualizado

REM 4. Verificar diretório
echo [4/4] Verificando arquivos do projeto...
if not exist "main_ai.py" (
    echo ❌ ERRO: Arquivo main_ai.py não encontrado
    echo 📁 Certifique-se de estar no diretório correto do projeto
    pause
    exit /b 1
)
echo ✅ Arquivos do projeto encontrados

echo.
echo 🎉 ETAPA 1 CONCLUÍDA COM SUCESSO!
echo.
echo 📋 Próximo passo: Execute install_step2.bat
echo.
pause

