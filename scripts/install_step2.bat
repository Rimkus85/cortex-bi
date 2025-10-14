@echo off
REM ========================================
REM CÓRTEX BI - ETAPA 2: Dependências Básicas
REM ========================================

echo 🧠 CÓRTEX BI - ETAPA 2: Dependências Básicas
echo ==========================================

REM 1. Instalar dependências CORE (uma por vez)
echo [1/8] Instalando FastAPI...
pip install fastapi
if %errorLevel% neq 0 (
    echo ❌ ERRO: Falha ao instalar FastAPI
    pause
    exit /b 1
)
echo ✅ FastAPI instalado

echo [2/8] Instalando Uvicorn...
pip install uvicorn
if %errorLevel% neq 0 (
    echo ❌ ERRO: Falha ao instalar Uvicorn
    pause
    exit /b 1
)
echo ✅ Uvicorn instalado

echo [3/8] Instalando Pandas...
pip install pandas
if %errorLevel% neq 0 (
    echo ❌ ERRO: Falha ao instalar Pandas
    pause
    exit /b 1
)
echo ✅ Pandas instalado

echo [4/8] Instalando NumPy...
pip install numpy
if %errorLevel% neq 0 (
    echo ❌ ERRO: Falha ao instalar NumPy
    pause
    exit /b 1
)
echo ✅ NumPy instalado

echo [5/8] Instalando OpenPyXL...
pip install openpyxl
if %errorLevel% neq 0 (
    echo ❌ ERRO: Falha ao instalar OpenPyXL
    pause
    exit /b 1
)
echo ✅ OpenPyXL instalado

echo [6/8] Instalando Python-PPTX...
pip install python-pptx
if %errorLevel% neq 0 (
    echo ❌ ERRO: Falha ao instalar Python-PPTX
    pause
    exit /b 1
)
echo ✅ Python-PPTX instalado

echo [7/8] Instalando Loguru...
pip install loguru
if %errorLevel% neq 0 (
    echo ❌ ERRO: Falha ao instalar Loguru
    pause
    exit /b 1
)
echo ✅ Loguru instalado

echo [8/8] Instalando Python-Multipart...
pip install python-multipart
if %errorLevel% neq 0 (
    echo ❌ ERRO: Falha ao instalar Python-Multipart
    pause
    exit /b 1
)
echo ✅ Python-Multipart instalado

echo.
echo 🎉 ETAPA 2 CONCLUÍDA COM SUCESSO!
echo.
echo 📋 Próximo passo: Execute install_step3.bat
echo.
pause

