"""
Analytics Agent - Servidor Principal FastAPI

Este é o servidor principal que integra todos os módulos do agente de analytics:
- Carregamento de dados de múltiplas fontes
- Análise de dados e cálculo de KPIs
- Geração automática de apresentações PPTX
- Integração com Microsoft Copilot M365

Instruções para personalização:
1. Configure as variáveis de ambiente no arquivo .env
2. Ajuste os endpoints conforme suas necessidades
3. Customize as validações de entrada
4. Adicione novos endpoints conforme necessário
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import json
import tempfile
import shutil
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
from datetime import datetime
import pandas as pd
from loguru import logger
import traceback

# Importa módulos do agente
from agents.data_loader import DataLoader
from agents.analytics_engine import AnalyticsEngine
from agents.pptx_generator import PPTXGenerator

# Configuração do logger
logger.add("logs/analytics_agent.log", rotation="1 day", retention="30 days")

# Inicializa FastAPI
app = FastAPI(
    title="Analytics Agent",
    description="Agente de Analytics com integração Microsoft Copilot M365",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração CORS - EDITE AQUI conforme necessário
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Monta diretórios estáticos
app.mount("/static", StaticFiles(directory="output"), name="static")

# Inicializa componentes do agente
data_loader = DataLoader()
analytics_engine = AnalyticsEngine()
pptx_generator = PPTXGenerator()

# Configurações globais - EDITE AQUI conforme necessário
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "output"
TEMPLATE_DIR = "templates"
DATA_DIR = "data"

# Cria diretórios se não existirem
for directory in [UPLOAD_DIR, OUTPUT_DIR, TEMPLATE_DIR, DATA_DIR]:
    os.makedirs(directory, exist_ok=True)


@app.get("/")
async def root():
    """
    Endpoint raiz com informações básicas do agente.
    """
    return {
        "message": "Analytics Agent - Servidor ativo",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "upload": "/upload",
            "analyze": "/analyze",
            "generate_pptx": "/generate-pptx",
            "download": "/download/{filename}"
        },
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """
    Endpoint de verificação de saúde do sistema.
    """
    try:
        # Verifica se os diretórios existem
        directories_status = {}
        for directory in [UPLOAD_DIR, OUTPUT_DIR, TEMPLATE_DIR, DATA_DIR]:
            directories_status[directory] = os.path.exists(directory)
        
        # Verifica se os módulos estão funcionando
        modules_status = {
            "data_loader": data_loader is not None,
            "analytics_engine": analytics_engine is not None,
            "pptx_generator": pptx_generator is not None
        }
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "directories": directories_status,
            "modules": modules_status,
            "uptime": "running"
        }
    except Exception as e:
        logger.error(f"Erro no health check: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Endpoint para upload de arquivos de dados (CSV, Excel).
    
    Args:
        file: Arquivo para upload
        
    Returns:
        Dict: Informações sobre o arquivo carregado
    """
    try:
        logger.info(f"Recebendo upload: {file.filename}")
        
        # Valida tipo de arquivo
        allowed_extensions = ['.csv', '.xlsx', '.xls']
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Tipo de arquivo não suportado. Use: {', '.join(allowed_extensions)}"
            )
        
        # Salva arquivo
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Carrega dados para validação
        if file_extension == '.csv':
            df = data_loader.load_csv(file_path)
        else:
            df = data_loader.load_excel(file_path)
        
        # Obtém informações do arquivo
        data_info = data_loader.get_data_info(df)
        
        logger.info(f"Upload concluído: {file.filename}")
        
        return {
            "message": "Arquivo carregado com sucesso",
            "filename": file.filename,
            "file_path": file_path,
            "data_info": data_info,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro no upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro no upload: {str(e)}")


@app.post("/analyze")
async def analyze_data(
    file_path: str = Form(...),
    analysis_type: str = Form(...),
    parameters: str = Form(...)
):
    """
    Endpoint para análise de dados.
    
    Args:
        file_path: Caminho para o arquivo de dados
        analysis_type: Tipo de análise (compare_periods, segment_groups, count_reasons, custom_kpis)
        parameters: Parâmetros da análise em JSON
        
    Returns:
        Dict: Resultado da análise
    """
    try:
        logger.info(f"Iniciando análise: {analysis_type}")
        
        # Valida se arquivo existe
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        
        # Carrega dados
        file_extension = Path(file_path).suffix.lower()
        if file_extension == '.csv':
            df = data_loader.load_csv(file_path)
        else:
            df = data_loader.load_excel(file_path)
        
        # Parse dos parâmetros
        try:
            params = json.loads(parameters)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Parâmetros JSON inválidos")
        
        # Executa análise conforme tipo
        result = None
        
        if analysis_type == "compare_periods":
            period1 = params.get('period1')
            period2 = params.get('period2')
            metrics = params.get('metrics', ['total', 'media', 'crescimento'])
            
            if not period1 or not period2:
                raise HTTPException(status_code=400, detail="Períodos obrigatórios para comparação")
            
            result = analytics_engine.compare_periods(df, period1, period2, metrics)
            
        elif analysis_type == "segment_groups":
            group_columns = params.get('group_columns', [])
            metrics = params.get('metrics', ['total', 'media', 'count'])
            
            if not group_columns:
                raise HTTPException(status_code=400, detail="Colunas de agrupamento obrigatórias")
            
            result = analytics_engine.segment_by_groups(df, group_columns, metrics)
            
        elif analysis_type == "count_reasons":
            reason_column = params.get('reason_column')
            result = analytics_engine.count_contact_reasons(df, reason_column)
            
        elif analysis_type == "custom_kpis":
            kpi_definitions = params.get('kpi_definitions', {})
            
            if not kpi_definitions:
                raise HTTPException(status_code=400, detail="Definições de KPI obrigatórias")
            
            result = analytics_engine.calculate_custom_kpis(df, kpi_definitions)
            
        else:
            raise HTTPException(status_code=400, detail=f"Tipo de análise não suportado: {analysis_type}")
        
        # Valida resultados
        validation = analytics_engine.validate_results(result)
        
        logger.info(f"Análise concluída: {analysis_type}")
        
        return {
            "message": "Análise concluída com sucesso",
            "analysis_type": analysis_type,
            "result": result,
            "validation": validation,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na análise: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erro na análise: {str(e)}")


@app.post("/generate-pptx")
async def generate_pptx(
    template_path: str = Form(...),
    data: str = Form(...),
    output_filename: str = Form(...)
):
    """
    Endpoint para geração de apresentação PPTX.
    
    Args:
        template_path: Caminho para o template PPTX
        data: Dados para substituir placeholders (JSON)
        output_filename: Nome do arquivo de saída
        
    Returns:
        Dict: Informações sobre a apresentação gerada
    """
    try:
        logger.info(f"Gerando PPTX: {output_filename}")
        
        # Valida template
        if not os.path.exists(template_path):
            raise HTTPException(status_code=404, detail="Template não encontrado")
        
        # Parse dos dados
        try:
            placeholder_data = json.loads(data)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Dados JSON inválidos")
        
        # Carrega template
        if not pptx_generator.load_template(template_path):
            raise HTTPException(status_code=500, detail="Erro ao carregar template")
        
        # Obtém lista de placeholders
        placeholders = pptx_generator.get_placeholders_list()
        
        # Substitui placeholders
        replaced_count = pptx_generator.replace_placeholders(placeholder_data)
        
        # Salva apresentação
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        if not pptx_generator.save_presentation(output_path):
            raise HTTPException(status_code=500, detail="Erro ao salvar apresentação")
        
        logger.info(f"PPTX gerado com sucesso: {output_filename}")
        
        return {
            "message": "Apresentação gerada com sucesso",
            "output_filename": output_filename,
            "output_path": output_path,
            "placeholders_found": placeholders,
            "placeholders_replaced": replaced_count,
            "download_url": f"/download/{output_filename}",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na geração de PPTX: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erro na geração de PPTX: {str(e)}")


@app.post("/analyze-and-generate")
async def analyze_and_generate(
    file_path: str = Form(...),
    analysis_type: str = Form(...),
    analysis_parameters: str = Form(...),
    template_path: str = Form(...),
    output_filename: str = Form(...)
):
    """
    Endpoint combinado para análise de dados e geração de PPTX.
    
    Args:
        file_path: Caminho para o arquivo de dados
        analysis_type: Tipo de análise
        analysis_parameters: Parâmetros da análise (JSON)
        template_path: Caminho para o template PPTX
        output_filename: Nome do arquivo de saída
        
    Returns:
        Dict: Resultado da análise e informações da apresentação gerada
    """
    try:
        logger.info(f"Executando análise e geração combinada: {analysis_type} -> {output_filename}")
        
        # Executa análise
        analysis_response = await analyze_data(file_path, analysis_type, analysis_parameters)
        analysis_result = analysis_response["result"]
        
        # Prepara dados para PPTX baseado no tipo de análise
        pptx_data = {}
        
        if analysis_type == "compare_periods":
            pptx_data = {
                "total_periodo1": analysis_result["period1"]["metrics"].get("total", 0),
                "total_periodo2": analysis_result["period2"]["metrics"].get("total", 0),
                "media_periodo1": analysis_result["period1"]["metrics"].get("media", 0),
                "media_periodo2": analysis_result["period2"]["metrics"].get("media", 0),
                "crescimento_total": analysis_result["comparison"].get("total_crescimento", 0),
                "crescimento_media": analysis_result["comparison"].get("media_crescimento", 0),
                "periodo1_nome": analysis_result["period1"]["name"],
                "periodo2_nome": analysis_result["period2"]["name"],
                "data_analise": datetime.now().strftime("%d/%m/%Y")
            }
            
        elif analysis_type == "segment_groups":
            # Pega o maior segmento
            segments = analysis_result["segments"]
            if segments:
                largest_segment = max(segments.items(), key=lambda x: x[1]["records"])
                pptx_data = {
                    "total_segmentos": analysis_result["summary"]["total_segments"],
                    "total_registros": analysis_result["summary"]["total_records"],
                    "maior_segmento_nome": largest_segment[0],
                    "maior_segmento_registros": largest_segment[1]["records"],
                    "maior_segmento_percentual": largest_segment[1]["percentage_of_total"],
                    "data_analise": datetime.now().strftime("%d/%m/%Y")
                }
        
        elif analysis_type == "count_reasons":
            most_common = analysis_result["summary"]["most_common_reason"]
            pptx_data = {
                "total_registros": analysis_result["summary"]["total_records"],
                "motivos_unicos": analysis_result["summary"]["unique_reasons"],
                "motivo_mais_comum": most_common["name"],
                "motivo_mais_comum_count": most_common["count"],
                "motivo_mais_comum_percentual": most_common["percentage"],
                "data_analise": datetime.now().strftime("%d/%m/%Y")
            }
        
        # Gera PPTX
        pptx_response = await generate_pptx(
            template_path, 
            json.dumps(pptx_data), 
            output_filename
        )
        
        logger.info(f"Análise e geração combinada concluída: {output_filename}")
        
        return {
            "message": "Análise e geração de PPTX concluídas com sucesso",
            "analysis": analysis_response,
            "pptx": pptx_response,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na análise e geração combinada: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erro na análise e geração combinada: {str(e)}")


@app.get("/download/{filename}")
async def download_file(filename: str):
    """
    Endpoint para download de arquivos gerados.
    
    Args:
        filename: Nome do arquivo para download
        
    Returns:
        FileResponse: Arquivo para download
    """
    try:
        file_path = os.path.join(OUTPUT_DIR, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        
        logger.info(f"Download solicitado: {filename}")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no download: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro no download: {str(e)}")


@app.get("/list-files")
async def list_files():
    """
    Endpoint para listar arquivos disponíveis.
    
    Returns:
        Dict: Lista de arquivos por diretório
    """
    try:
        files = {
            "uploads": [],
            "templates": [],
            "outputs": [],
            "data": []
        }
        
        # Lista arquivos em cada diretório
        directories = {
            "uploads": UPLOAD_DIR,
            "templates": TEMPLATE_DIR,
            "outputs": OUTPUT_DIR,
            "data": DATA_DIR
        }
        
        for key, directory in directories.items():
            if os.path.exists(directory):
                for filename in os.listdir(directory):
                    file_path = os.path.join(directory, filename)
                    if os.path.isfile(file_path):
                        file_info = {
                            "name": filename,
                            "path": file_path,
                            "size": os.path.getsize(file_path),
                            "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                        }
                        files[key].append(file_info)
        
        return {
            "message": "Lista de arquivos",
            "files": files,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar arquivos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao listar arquivos: {str(e)}")


@app.get("/templates/placeholders/{template_name}")
async def get_template_placeholders(template_name: str):
    """
    Endpoint para obter placeholders de um template.
    
    Args:
        template_name: Nome do template
        
    Returns:
        Dict: Lista de placeholders do template
    """
    try:
        template_path = os.path.join(TEMPLATE_DIR, template_name)
        
        if not os.path.exists(template_path):
            raise HTTPException(status_code=404, detail="Template não encontrado")
        
        # Carrega template e obtém placeholders
        temp_generator = PPTXGenerator()
        if not temp_generator.load_template(template_path):
            raise HTTPException(status_code=500, detail="Erro ao carregar template")
        
        placeholders = temp_generator.get_placeholders_list()
        
        return {
            "message": "Placeholders do template",
            "template_name": template_name,
            "placeholders": placeholders,
            "count": len(placeholders),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter placeholders: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter placeholders: {str(e)}")


# Endpoint para integração com Microsoft Copilot M365
@app.post("/copilot/analyze")
async def copilot_analyze(request: Dict[str, Any]):
    """
    Endpoint especial para integração com Microsoft Copilot M365.
    
    Args:
        request: Requisição do Copilot com parâmetros de análise
        
    Returns:
        Dict: Resultado formatado para o Copilot
    """
    try:
        logger.info("Requisição recebida do Microsoft Copilot M365")
        
        # Extrai parâmetros da requisição do Copilot
        query = request.get("query", "")
        data_source = request.get("data_source", "")
        analysis_params = request.get("parameters", {})
        
        # Processa requisição baseada na query
        # EDITE AQUI para adicionar mais tipos de query do Copilot
        if "comparar períodos" in query.lower() or "compare periods" in query.lower():
            # Análise de comparação de períodos
            result = await analyze_data(
                data_source,
                "compare_periods",
                json.dumps(analysis_params)
            )
            
        elif "segmentar" in query.lower() or "segment" in query.lower():
            # Análise de segmentação
            result = await analyze_data(
                data_source,
                "segment_groups",
                json.dumps(analysis_params)
            )
            
        else:
            # Análise genérica
            result = await analyze_data(
                data_source,
                analysis_params.get("type", "compare_periods"),
                json.dumps(analysis_params)
            )
        
        # Formata resposta para o Copilot
        copilot_response = {
            "status": "success",
            "query": query,
            "summary": "Análise concluída com sucesso",
            "data": result["result"],
            "insights": [],  # Adicione insights automáticos aqui
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info("Resposta enviada para Microsoft Copilot M365")
        
        return copilot_response
        
    except Exception as e:
        logger.error(f"Erro na integração com Copilot: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    # Configuração do servidor - EDITE AQUI conforme necessário
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # Permite acesso externo
        port=8000,       # Porta do servidor
        reload=True,     # Recarrega automaticamente em desenvolvimento
        log_level="info"
    )

