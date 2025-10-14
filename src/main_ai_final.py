"""
CÓRTEX BI v2.0 - Versão Final Robusta
Cognitive Operations & Real-Time EXpert Business Intelligence

Versão simplificada que funciona apenas com dependências básicas:
- FastAPI
- Uvicorn  
- Pandas
- NumPy
- OpenPyXL
- Python-PPTX
- Loguru
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
import json

# FastAPI e dependências web
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Logging
try:
    from loguru import logger
    LOGURU_AVAILABLE = True
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    LOGURU_AVAILABLE = False

# Configurar logging
if LOGURU_AVAILABLE:
    logger.add("logs/cortex_bi.log", rotation="1 day", retention="30 days")
else:
    logging.basicConfig(level=logging.INFO)

# Importar apenas módulos básicos que funcionam
try:
    from agents.data_loader import DataLoader
    DATA_LOADER_OK = True
except Exception as e:
    logger.warning(f"DataLoader não disponível: {e}")
    DATA_LOADER_OK = False

try:
    from agents.analytics_engine import AnalyticsEngine
    ANALYTICS_ENGINE_OK = True
except Exception as e:
    logger.warning(f"AnalyticsEngine não disponível: {e}")
    ANALYTICS_ENGINE_OK = False

try:
    from agents.pptx_generator import PPTXGenerator
    PPTX_GENERATOR_OK = True
except Exception as e:
    logger.warning(f"PPTXGenerator não disponível: {e}")
    PPTX_GENERATOR_OK = False

# Inicializar FastAPI
app = FastAPI(
    title="CÓRTEX BI v2.0",
    description="Cognitive Operations & Real-Time EXpert Business Intelligence",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Criar diretórios necessários
os.makedirs("data", exist_ok=True)
os.makedirs("output", exist_ok=True)
os.makedirs("uploads", exist_ok=True)
os.makedirs("logs", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Montar arquivos estáticos
if os.path.exists("admin"):
    app.mount("/admin", StaticFiles(directory="admin"), name="admin")

# Inicializar componentes básicos
data_loader = DataLoader() if DATA_LOADER_OK else None
analytics_engine = AnalyticsEngine() if ANALYTICS_ENGINE_OK else None
pptx_generator = PPTXGenerator() if PPTX_GENERATOR_OK else None

# ==========================================
# ENDPOINTS BÁSICOS
# ==========================================

@app.get("/")
async def root():
    """Endpoint raiz com informações do sistema"""
    return {
        "sistema": "CÓRTEX BI v2.0",
        "descricao": "Cognitive Operations & Real-Time EXpert Business Intelligence",
        "versao": "2.0.0",
        "status": "operacional",
        "timestamp": datetime.now().isoformat(),
        "componentes": {
            "data_loader": DATA_LOADER_OK,
            "analytics_engine": ANALYTICS_ENGINE_OK,
            "pptx_generator": PPTX_GENERATOR_OK
        },
        "endpoints": {
            "documentacao": "/docs",
            "health_check": "/health",
            "listar_arquivos": "/list-files",
            "admin_dashboard": "/admin/admin_dashboard.html"
        }
    }

@app.get("/health")
async def health_check():
    """Health check do sistema"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "sistema": "CÓRTEX BI v2.0",
        "componentes_ativos": {
            "data_loader": DATA_LOADER_OK,
            "analytics_engine": ANALYTICS_ENGINE_OK,
            "pptx_generator": PPTX_GENERATOR_OK
        }
    }

@app.get("/list-files")
async def list_files():
    """Lista arquivos disponíveis para análise"""
    files = {
        "csv_files": [],
        "excel_files": [],
        "pptx_templates": []
    }
    
    # Listar arquivos CSV
    data_dir = Path("data")
    if data_dir.exists():
        files["csv_files"] = [f.name for f in data_dir.glob("*.csv")]
        files["excel_files"] = [f.name for f in data_dir.glob("*.xlsx")]
    
    # Listar templates PPTX
    templates_dir = Path("templates")
    if templates_dir.exists():
        files["pptx_templates"] = [f.name for f in templates_dir.glob("*.pptx")]
    
    return files

# ==========================================
# ENDPOINTS DE ANÁLISE BÁSICA
# ==========================================

@app.post("/analyze/basic")
async def analyze_basic(
    file_path: str = Form(...),
    analysis_type: str = Form(default="summary")
):
    """Análise básica de dados"""
    if not DATA_LOADER_OK or not ANALYTICS_ENGINE_OK:
        raise HTTPException(
            status_code=503, 
            detail="Componentes de análise não disponíveis"
        )
    
    try:
        # Carregar dados
        if file_path.endswith('.csv'):
            df = data_loader.load_csv(f"data/{file_path}")
        elif file_path.endswith('.xlsx'):
            df = data_loader.load_excel(f"data/{file_path}")
        else:
            raise HTTPException(status_code=400, detail="Formato de arquivo não suportado")
        
        # Análise básica
        result = {
            "arquivo": file_path,
            "linhas": len(df),
            "colunas": len(df.columns),
            "colunas_nomes": df.columns.tolist(),
            "tipos_dados": df.dtypes.to_dict(),
            "resumo_estatistico": df.describe().to_dict(),
            "valores_nulos": df.isnull().sum().to_dict(),
            "timestamp": datetime.now().isoformat()
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Erro na análise básica: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na análise: {str(e)}")

@app.post("/generate/pptx-basic")
async def generate_pptx_basic(
    title: str = Form(...),
    data_summary: str = Form(...)
):
    """Gera PPTX básico com dados fornecidos"""
    if not PPTX_GENERATOR_OK:
        raise HTTPException(
            status_code=503,
            detail="Gerador de PPTX não disponível"
        )
    
    try:
        # Dados básicos para PPTX
        analysis_data = {
            "title": title,
            "summary": data_summary,
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "generated_by": "CÓRTEX BI v2.0"
        }
        
        # Gerar PPTX
        output_path = f"output/cortex_bi_basic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"
        pptx_generator.generate_presentation(analysis_data, output_path)
        
        return {
            "status": "success",
            "message": "Apresentação gerada com sucesso",
            "file_path": output_path,
            "download_url": f"/download/{os.path.basename(output_path)}"
        }
        
    except Exception as e:
        logger.error(f"Erro na geração de PPTX: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na geração: {str(e)}")

# ==========================================
# ENDPOINTS DE DOWNLOAD
# ==========================================

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download de arquivos gerados"""
    file_path = f"output/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )

# ==========================================
# ENDPOINTS DE UPLOAD
# ==========================================

@app.post("/upload/csv")
async def upload_csv(file: UploadFile = File(...)):
    """Upload de arquivo CSV"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Apenas arquivos CSV são aceitos")
    
    try:
        # Salvar arquivo
        file_path = f"data/{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return {
            "status": "success",
            "message": "Arquivo CSV enviado com sucesso",
            "filename": file.filename,
            "path": file_path
        }
        
    except Exception as e:
        logger.error(f"Erro no upload: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no upload: {str(e)}")

@app.post("/upload/excel")
async def upload_excel(file: UploadFile = File(...)):
    """Upload de arquivo Excel"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Apenas arquivos Excel são aceitos")
    
    try:
        # Salvar arquivo
        file_path = f"data/{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return {
            "status": "success",
            "message": "Arquivo Excel enviado com sucesso",
            "filename": file.filename,
            "path": file_path
        }
        
    except Exception as e:
        logger.error(f"Erro no upload: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no upload: {str(e)}")

# ==========================================
# INICIALIZAÇÃO
# ==========================================

if __name__ == "__main__":
    print("🧠 CÓRTEX BI v2.0 - Versão Final Robusta")
    print("=" * 50)
    print("Cognitive Operations & Real-Time EXpert Business Intelligence")
    print()
    
    # Status dos componentes
    print("📊 Status dos Componentes:")
    print(f"• DataLoader: {'✅ OK' if DATA_LOADER_OK else '❌ Indisponível'}")
    print(f"• AnalyticsEngine: {'✅ OK' if ANALYTICS_ENGINE_OK else '❌ Indisponível'}")
    print(f"• PPTXGenerator: {'✅ OK' if PPTX_GENERATOR_OK else '❌ Indisponível'}")
    print()
    
    print("🚀 Iniciando servidor...")
    print("📍 URLs de acesso:")
    print("• Documentação: http://localhost:5000/docs")
    print("• Health Check: http://localhost:5000/health")
    print("• Admin Dashboard: http://localhost:5000/admin/admin_dashboard.html")
    print()
    
    # Iniciar servidor
    uvicorn.run(
        "main_ai_final:app",
        host="0.0.0.0",        # Permite acesso via localhost e IP específico
        port=5000,             # Porta do servidor
        reload=False,          # Desabilitado para produção
        log_level="info"
    )

