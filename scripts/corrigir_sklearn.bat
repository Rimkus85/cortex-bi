@echo off
REM ========================================
REM CÓRTEX BI - Corrigir Problema Sklearn
REM ========================================

echo 🔧 CÓRTEX BI - Corrigindo Problema Sklearn
echo ==========================================

echo [INFO] Problema: sklearn (scikit-learn) não encontrado
echo [INFO] Vamos instalar ou desabilitar módulos de IA temporariamente
echo.

echo [OPÇÃO 1] Tentando instalar sklearn...
pip install scikit-learn
if %errorLevel% equ 0 (
    echo ✅ Sklearn instalado com sucesso!
    echo 🧪 Testando importação...
    python -c "import sklearn; print('✅ Sklearn funcionando!')"
    if %errorLevel% equ 0 (
        echo ✅ Sklearn OK - Tentando iniciar servidor...
        goto :start_server
    )
)

echo.
echo [OPÇÃO 2] Sklearn falhou - Criando versão sem IA...
echo 💡 Vamos criar uma versão simplificada do main_ai.py sem módulos de IA

REM Criar backup do main_ai.py original
copy main_ai.py main_ai_original.py >nul 2>&1

REM Criar versão simplificada
(
echo # CÓRTEX BI - Versão Simplificada ^(sem IA avançada^)
echo from fastapi import FastAPI, File, UploadFile, HTTPException
echo from fastapi.responses import HTMLResponse, FileResponse
echo from fastapi.staticfiles import StaticFiles
echo import uvicorn
echo import os
echo import json
echo from datetime import datetime
echo.
echo # Importar apenas módulos básicos
echo try:
echo     from agents.data_loader import DataLoader
echo     from agents.analytics_engine import AnalyticsEngine
echo     from agents.pptx_generator import PPTXGenerator
echo     BASIC_MODULES = True
echo except ImportError as e:
echo     print^(f"Aviso: Alguns módulos não disponíveis: {e}"^)
echo     BASIC_MODULES = False
echo.
echo app = FastAPI^(
echo     title="CÓRTEX BI",
echo     description="Cognitive Operations ^& Real-Time EXpert Business Intelligence",
echo     version="2.0.0"
echo ^)
echo.
echo # Servir arquivos estáticos
echo if os.path.exists^("admin"^):
echo     app.mount^("/admin", StaticFiles^(directory="admin"^), name="admin"^)
echo.
echo @app.get^("/"^)
echo async def root^(^):
echo     return {
echo         "message": "CÓRTEX BI v2.0 - Sistema Operacional",
echo         "status": "healthy",
echo         "timestamp": datetime.now^(^).isoformat^(^),
echo         "modules": {
echo             "basic": BASIC_MODULES,
echo             "ai_advanced": False
echo         }
echo     }
echo.
echo @app.get^("/health"^)
echo async def health_check^(^):
echo     return {
echo         "status": "healthy",
echo         "timestamp": datetime.now^(^).isoformat^(^),
echo         "services": {
echo             "data_loader": "active" if BASIC_MODULES else "disabled",
echo             "analytics_engine": "active" if BASIC_MODULES else "disabled",
echo             "pptx_generator": "active" if BASIC_MODULES else "disabled",
echo             "ai_modules": "disabled"
echo         }
echo     }
echo.
echo @app.get^("/list-files"^)
echo async def list_files^(^):
echo     files = []
echo     data_dir = "data"
echo     if os.path.exists^(data_dir^):
echo         for file in os.listdir^(data_dir^):
echo             if file.endswith^(^('.csv', '.xlsx', '.xls'^)^):
echo                 files.append^(file^)
echo     return {"files": files}
echo.
echo if __name__ == "__main__":
echo     print^("🧠 CÓRTEX BI v2.0 - Iniciando ^(Versão Simplificada^)..."^)
echo     print^("📍 Servidor: http://localhost:5000"^)
echo     print^("📚 Documentação: http://localhost:5000/docs"^)
echo     print^("⚠️  Módulos de IA avançada desabilitados"^)
echo     uvicorn.run^(app, host="0.0.0.0", port=5000^)
) > main_ai_simple.py

echo ✅ Versão simplificada criada: main_ai_simple.py

:start_server
echo.
echo 🚀 INICIANDO SERVIDOR...
echo ==========================================
echo.
echo [TENTATIVA 1] Servidor completo...
python main_ai.py
if %errorLevel% equ 0 (
    echo ✅ Servidor completo funcionou!
    goto :end
)

echo.
echo [TENTATIVA 2] Servidor simplificado...
python main_ai_simple.py
if %errorLevel% equ 0 (
    echo ✅ Servidor simplificado funcionou!
    goto :end
)

echo.
echo ❌ AMBAS TENTATIVAS FALHARAM
echo 💡 Execute manualmente e veja o erro:
echo    python main_ai_simple.py

:end
echo.
echo 🎯 SE O SERVIDOR INICIOU:
echo ==========================================
echo • Abra: http://localhost:5000/docs
echo • Teste: http://localhost:5000/health
echo • Admin: http://localhost:5000/admin/admin_dashboard.html
echo.
pause

