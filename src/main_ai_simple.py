# CÓRTEX BI - Versão Simplificada (sem IA avançada)
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import json
from datetime import datetime

# Importar apenas módulos básicos
try:
    from agents.data_loader import DataLoader
    from agents.analytics_engine import AnalyticsEngine
    from agents.pptx_generator import PPTXGenerator
    BASIC_MODULES = True
    print("✅ Módulos básicos carregados com sucesso")
except ImportError as e:
    print(f"⚠️ Aviso: Alguns módulos não disponíveis: {e}")
    BASIC_MODULES = False

app = FastAPI(
    title="CÓRTEX BI",
    description="Cognitive Operations & Real-Time EXpert Business Intelligence",
    version="2.0.0"
)

# Servir arquivos estáticos
if os.path.exists("admin"):
    app.mount("/admin", StaticFiles(directory="admin"), name="admin")

@app.get("/")
async def root():
    return {
        "message": "CÓRTEX BI v2.0 - Sistema Operacional",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "modules": {
            "basic": BASIC_MODULES,
            "ai_advanced": False
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "data_loader": "active" if BASIC_MODULES else "disabled",
            "analytics_engine": "active" if BASIC_MODULES else "disabled", 
            "pptx_generator": "active" if BASIC_MODULES else "disabled",
            "ai_modules": "disabled"
        }
    }

@app.get("/list-files")
async def list_files():
    files = []
    data_dir = "data"
    if os.path.exists(data_dir):
        for file in os.listdir(data_dir):
            if file.endswith(('.csv', '.xlsx', '.xls')):
                files.append(file)
    return {"files": files}

@app.post("/analyze-basic")
async def analyze_basic(file_path: str):
    """Análise básica sem IA avançada"""
    if not BASIC_MODULES:
        raise HTTPException(status_code=503, detail="Módulos básicos não disponíveis")
    
    try:
        # Carregar dados
        loader = DataLoader()
        data = loader.load_csv(f"data/{file_path}")
        
        # Análise simples
        result = {
            "file": file_path,
            "rows": len(data),
            "columns": list(data.columns),
            "summary": data.describe().to_dict() if hasattr(data, 'describe') else {},
            "timestamp": datetime.now().isoformat()
        }
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-pptx-basic")
async def generate_pptx_basic(template_name: str = "template_relatorio.pptx"):
    """Geração básica de PPTX"""
    if not BASIC_MODULES:
        raise HTTPException(status_code=503, detail="Módulos básicos não disponíveis")
    
    try:
        generator = PPTXGenerator()
        output_file = f"output/relatorio_basico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"
        
        # Gerar PPTX básico
        result = generator.generate_basic_report(
            template_path=f"templates/{template_name}",
            output_path=output_file
        )
        
        return {
            "message": "PPTX gerado com sucesso",
            "file": output_file,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🧠 CÓRTEX BI v2.0 - Iniciando (Versão Simplificada)...")
    print("📍 Servidor: http://localhost:5000")
    print("📚 Documentação: http://localhost:5000/docs")
    print("⚠️ Módulos de IA avançada desabilitados")
    print("✅ Sistema básico de análise e PPTX disponível")
    uvicorn.run(app, host="0.0.0.0", port=5000)

