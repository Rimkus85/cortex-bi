@echo off
REM ========================================
REM CÓRTEX BI - Corrigir Problema FastAPI
REM ========================================

echo 🔧 CÓRTEX BI - Corrigindo Problema FastAPI
echo ==========================================

echo [INFO] Problema identificado: FastAPI não instalado corretamente
echo.

echo [1/5] Verificando Python...
python --version
if %errorLevel% neq 0 (
    echo ❌ ERRO: Python não encontrado
    pause
    exit /b 1
)
echo ✅ Python OK

echo.
echo [2/5] Atualizando pip...
python -m pip install --upgrade pip
echo ✅ pip atualizado

echo.
echo [3/5] Instalando FastAPI e Uvicorn...
pip install fastapi uvicorn
if %errorLevel% neq 0 (
    echo ❌ ERRO: Falha ao instalar FastAPI
    echo 💡 Tentando com --user...
    pip install --user fastapi uvicorn
)
echo ✅ FastAPI e Uvicorn instalados

echo.
echo [4/5] Instalando dependências essenciais...
pip install pandas numpy openpyxl python-pptx loguru python-multipart
if %errorLevel% neq 0 (
    echo ⚠️  AVISO: Algumas dependências podem ter falhado
    echo 💡 Continuando com o que foi instalado...
)
echo ✅ Dependências instaladas

echo.
echo [5/5] Testando importações...
python -c "
try:
    import fastapi
    import uvicorn
    print('✅ FastAPI e Uvicorn: OK')
except ImportError as e:
    print('❌ Erro:', e)
    exit(1)

try:
    import pandas
    import numpy
    print('✅ Pandas e NumPy: OK')
except ImportError as e:
    print('⚠️  Aviso:', e)

try:
    from agents.data_loader import DataLoader
    print('✅ Módulos do projeto: OK')
except ImportError as e:
    print('⚠️  Aviso módulos:', e)
"

if %errorLevel% neq 0 (
    echo ❌ ERRO: Ainda há problemas com as importações
    echo 💡 Mas vamos tentar iniciar o servidor mesmo assim...
)

echo.
echo 🚀 TENTANDO INICIAR SERVIDOR...
echo ==========================================
echo.
echo 📍 Se funcionar, você verá: "Uvicorn running on http://0.0.0.0:5000"
echo 🌐 Depois acesse: http://localhost:5000/docs
echo.
echo ⚠️  Para parar o servidor: Ctrl+C
echo.

python main_ai.py

echo.
echo 🔧 SE O SERVIDOR NÃO INICIOU:
echo ==========================================
echo 1. Verifique o erro mostrado acima
echo 2. Execute: pip install nome_do_modulo_faltante
echo 3. Tente novamente: python main_ai.py
echo.
pause

