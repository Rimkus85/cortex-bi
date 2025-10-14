"""
Analytics Agent - Servidor FastAPI Principal com IA
Sistema completo de analytics com capacidades de aprendizado contínuo
"""

import os
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

from agents.data_loader import DataLoader
from agents.analytics_engine import AnalyticsEngine
from agents.pptx_generator import PPTXGenerator
from agents.feedback_system import feedback_system
from agents.nlp_engine import nlp_engine
from agents.recommendation_engine import recommendation_engine
from agents.ml_engine import ml_engine
from agents.admin_system import admin_system

from loguru import logger

# Configurar logging
logger.add("logs/analytics_agent.log", rotation="1 day", retention="30 days")

# Inicializar FastAPI
app = FastAPI(
    title="Analytics Agent com IA",
    description="Sistema de analytics com aprendizado contínuo e processamento de linguagem natural",
    version="2.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instâncias dos agentes
data_loader = DataLoader()
analytics_engine = AnalyticsEngine()
pptx_generator = PPTXGenerator()

# Modelos Pydantic para IA
class NLPQuery(BaseModel):
    query: str
    user_id: str = "default"
    context: Optional[Dict] = None

class FeedbackData(BaseModel):
    interaction_id: str
    rating: int  # 1-5
    feedback_type: str = "general"
    comment: Optional[str] = None
    useful: Optional[bool] = None
    suggestions: Optional[str] = None

class RecommendationRequest(BaseModel):
    user_id: str
    analysis_type: Optional[str] = None
    context: Optional[Dict] = None

class MLTrainingRequest(BaseModel):
    model_type: str
    retrain: bool = False

class AdminRequest(BaseModel):
    user_id: str
    action: str
    parameters: Optional[Dict] = None

class TemplateUpdateRequest(BaseModel):
    user_id: str
    template_name: str
    new_placeholders: Dict[str, str]

class SharePointConfigRequest(BaseModel):
    user_id: str
    config: Dict[str, str]

# Middleware para logging de interações
@app.middleware("http")
async def log_interactions(request: Request, call_next):
    start_time = time.time()
    
    # Gerar ID da sessão se não existir
    session_id = request.headers.get("X-Session-ID", str(uuid.uuid4()))
    user_id = request.headers.get("X-User-ID", "anonymous")
    
    response = await call_next(request)
    
    execution_time = time.time() - start_time
    
    # Log da interação (em background para não afetar performance)
    if hasattr(request.state, "interaction_data"):
        interaction_data = request.state.interaction_data
        interaction_data.update({
            "execution_time": execution_time,
            "success": response.status_code < 400,
            "user_id": user_id,
            "session_id": session_id
        })
        
        # Registrar no sistema de feedback
        try:
            feedback_system.log_interaction(**interaction_data)
        except Exception as e:
            logger.warning(f"Erro ao registrar interação: {e}")
    
    return response

# Endpoints originais mantidos
@app.get("/")
async def root():
    """Endpoint raiz com informações do sistema"""
    return {
        "message": "Analytics Agent com IA - Sistema de análise de dados com aprendizado contínuo",
        "version": "2.0.0",
        "features": [
            "Análise de dados avançada",
            "Geração automática de apresentações",
            "Processamento de linguagem natural",
            "Sistema de recomendações",
            "Aprendizado contínuo com ML",
            "Feedback e personalização"
        ],
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "upload": "/upload-file",
            "analyze": "/analyze",
            "generate_pptx": "/generate-pptx",
            "nlp_query": "/nlp/query",
            "recommendations": "/recommendations",
            "feedback": "/feedback",
            "ml_status": "/ml/status"
        }
    }

@app.get("/health")
async def health_check():
    """Verificação de saúde do sistema"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "data_loader": "active",
            "analytics_engine": "active", 
            "pptx_generator": "active",
            "feedback_system": "active",
            "nlp_engine": "active",
            "recommendation_engine": "active",
            "ml_engine": "active"
        }
    }

@app.get("/list-files")
async def list_files():
    """Lista arquivos disponíveis para análise"""
    data_dir = Path("data")
    if not data_dir.exists():
        return {"files": []}
    
    files = []
    for file_path in data_dir.glob("*"):
        if file_path.is_file() and file_path.suffix in ['.csv', '.xlsx', '.xls']:
            files.append({
                "name": file_path.name,
                "size": file_path.stat().st_size,
                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            })
    
    return {"files": files}

@app.post("/upload-file")
async def upload_file(request: Request, file: UploadFile = File(...)):
    """Upload de arquivo para análise"""
    start_time = time.time()
    
    try:
        # Salvar arquivo
        file_path = f"data/{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Carregar e validar dados
        df = data_loader.load_data(file_path)
        validation = data_loader.validate_data(df)
        
        result = {
            "message": f"Arquivo {file.filename} carregado com sucesso",
            "file_path": file_path,
            "rows": len(df),
            "columns": list(df.columns),
            "validation": validation
        }
        
        # Registrar interação
        request.state.interaction_data = {
            "action_type": "upload",
            "endpoint": "/upload-file",
            "request_data": {"filename": file.filename, "size": len(content)},
            "response_data": result
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Erro no upload: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/analyze")
async def analyze_data(
    request: Request,
    file_path: str,
    analysis_type: str,
    parameters: Optional[Dict] = None,
    user_id: str = Query("default", description="ID do usuário")
):
    """Análise de dados com IA integrada"""
    start_time = time.time()
    
    try:
        # Carregar dados
        df = data_loader.load_data(file_path)
        
        # Preparar contexto para IA
        context = {
            "available_columns": list(df.columns),
            "data_size": len(df),
            "data_type": "tabular",
            "file_path": file_path
        }
        
        # Predizer qualidade esperada (se modelo estiver treinado)
        quality_prediction = ml_engine.predict_quality({
            "request_data": {"analysis_type": analysis_type, "parameters": parameters},
            "execution_time": 0,  # Será atualizado depois
            "success": True
        })
        
        # Executar análise
        if analysis_type == "compare_periods":
            result = analytics_engine.compare_periods(df, parameters or {})
        elif analysis_type == "segment_by_groups":
            result = analytics_engine.segment_by_groups(df, parameters or {})
        elif analysis_type == "count_contact_reasons":
            result = analytics_engine.count_contact_reasons(df, parameters or {})
        elif analysis_type == "calculate_custom_kpis":
            result = analytics_engine.calculate_custom_kpis(df, parameters or {})
        else:
            raise ValueError(f"Tipo de análise não suportado: {analysis_type}")
        
        # Adicionar informações de IA
        result["ai_insights"] = {
            "quality_prediction": quality_prediction,
            "context": context
        }
        
        # Detectar anomalias na interação
        interaction_data = {
            "request_data": {"analysis_type": analysis_type, "parameters": parameters},
            "response_data": result,
            "execution_time": time.time() - start_time,
            "user_id": user_id
        }
        
        anomaly_detection = ml_engine.detect_anomaly(interaction_data)
        if anomaly_detection.get("is_anomaly"):
            result["ai_insights"]["anomaly_detected"] = anomaly_detection
        
        # Gerar recomendações
        recommendations = recommendation_engine.recommend_analyses(user_id, context)
        result["ai_insights"]["recommendations"] = recommendations[:3]
        
        # Registrar interação
        request.state.interaction_data = {
            "action_type": "analyze",
            "endpoint": "/analyze",
            "request_data": {"analysis_type": analysis_type, "parameters": parameters},
            "response_data": result
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Erro na análise: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/generate-pptx")
async def generate_pptx(
    request: Request,
    analysis_result: Dict,
    template_path: str = "templates/template_relatorio.pptx",
    output_filename: Optional[str] = None,
    user_id: str = Query("default", description="ID do usuário")
):
    """Geração de PPTX com recomendações de template"""
    start_time = time.time()
    
    try:
        # Recomendar template baseado no usuário e tipo de análise
        analysis_type = analysis_result.get("analysis_type", "general")
        template_recommendations = recommendation_engine.recommend_templates(user_id, analysis_type)
        
        # Usar template recomendado se disponível
        if template_recommendations:
            recommended_template = template_recommendations[0]["template"]
            template_path = f"templates/{recommended_template}"
            
            # Verificar se template existe
            if not Path(template_path).exists():
                template_path = "templates/template_relatorio.pptx"
        
        # Gerar nome do arquivo se não fornecido
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"relatorio_analytics_{timestamp}.pptx"
        
        output_path = f"output/{output_filename}"
        
        # Gerar apresentação
        pptx_generator.generate_presentation(analysis_result, template_path, output_path)
        
        result = {
            "message": "Apresentação gerada com sucesso",
            "output_path": output_path,
            "template_used": template_path,
            "template_recommendations": template_recommendations
        }
        
        # Registrar interação
        request.state.interaction_data = {
            "action_type": "generate_pptx",
            "endpoint": "/generate-pptx",
            "request_data": {"template_path": template_path, "output_filename": output_filename},
            "response_data": result
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Erro na geração de PPTX: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Novos endpoints de IA

@app.post("/nlp/query")
async def process_nlp_query(request: Request, query_data: NLPQuery):
    """Processa query em linguagem natural"""
    try:
        # Processar query com NLP
        result = nlp_engine.process_query(query_data.query, query_data.context)
        
        # Se confiança for baixa, tentar interpretação com IA
        if result.get("confidence", 0) < 0.7:
            ai_result = nlp_engine.interpret_with_ai(query_data.query, query_data.context)
            if "error" not in ai_result:
                result["ai_interpretation"] = ai_result
        
        # Registrar interação
        request.state.interaction_data = {
            "action_type": "nlp_query",
            "endpoint": "/nlp/query",
            "request_data": {"query": query_data.query, "user_id": query_data.user_id},
            "response_data": result
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Erro no processamento NLP: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/nlp/execute")
async def execute_nlp_analysis(query_data: NLPQuery):
    """Executa análise baseada em query NLP"""
    try:
        # Processar query
        nlp_result = nlp_engine.process_query(query_data.query, query_data.context)
        
        if nlp_result.get("intent") == "unknown":
            return {"error": "Não foi possível interpretar a solicitação", "suggestions": nlp_result.get("suggestions", [])}
        
        # Executar análise baseada na intenção
        analysis_params = nlp_result.get("analysis_params", {})
        
        # Aqui você integraria com os endpoints de análise existentes
        # Por simplicidade, retornamos a interpretação
        
        result = {
            "interpretation": nlp_result,
            "message": nlp_result.get("response", "Análise interpretada com sucesso"),
            "next_steps": "Use os parâmetros interpretados para executar a análise"
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Erro na execução NLP: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/recommendations/{user_id}")
async def get_recommendations(user_id: str, analysis_type: Optional[str] = None):
    """Obtém recomendações personalizadas para o usuário"""
    try:
        # Obter recomendações de análises
        analysis_recs = recommendation_engine.recommend_analyses(user_id)
        
        # Obter recomendações de templates
        template_recs = recommendation_engine.recommend_templates(user_id, analysis_type)
        
        # Obter alertas proativos
        alerts = recommendation_engine.generate_proactive_alerts(user_id)
        
        # Obter configurações de personalização
        personalization = recommendation_engine.get_personalization_settings(user_id)
        
        result = {
            "user_id": user_id,
            "analysis_recommendations": analysis_recs,
            "template_recommendations": template_recs,
            "proactive_alerts": alerts,
            "personalization_settings": personalization
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao obter recomendações: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/feedback")
async def submit_feedback(feedback_data: FeedbackData):
    """Coleta feedback do usuário"""
    try:
        feedback_id = feedback_system.collect_feedback(
            interaction_id=feedback_data.interaction_id,
            rating=feedback_data.rating,
            feedback_type=feedback_data.feedback_type,
            comment=feedback_data.comment,
            useful=feedback_data.useful,
            suggestions=feedback_data.suggestions
        )
        
        return {
            "message": "Feedback coletado com sucesso",
            "feedback_id": feedback_id
        }
        
    except Exception as e:
        logger.error(f"Erro ao coletar feedback: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/feedback/analytics")
async def get_feedback_analytics(days: int = Query(30, description="Número de dias para análise")):
    """Obtém analytics de feedback"""
    try:
        analytics = feedback_system.get_feedback_analytics(days)
        return analytics
        
    except Exception as e:
        logger.error(f"Erro ao obter analytics de feedback: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/ml/status")
async def get_ml_status():
    """Obtém status dos modelos de ML"""
    try:
        status = ml_engine.get_model_status()
        return status
        
    except Exception as e:
        logger.error(f"Erro ao obter status ML: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/ml/train")
async def train_ml_model(training_request: MLTrainingRequest, background_tasks: BackgroundTasks):
    """Treina modelos de ML"""
    try:
        model_type = training_request.model_type
        retrain = training_request.retrain
        
        if model_type == "all":
            # Treinar todos os modelos em background
            background_tasks.add_task(ml_engine.retrain_all_models)
            return {"message": "Treinamento de todos os modelos iniciado em background"}
        
        elif model_type == "analysis_predictor":
            result = ml_engine.train_analysis_predictor(retrain)
        elif model_type == "quality_classifier":
            result = ml_engine.train_quality_classifier(retrain)
        elif model_type == "anomaly_detector":
            result = ml_engine.train_anomaly_detector(retrain)
        elif model_type == "user_clusterer":
            result = ml_engine.train_user_clusterer(retrain)
        else:
            raise ValueError(f"Tipo de modelo não suportado: {model_type}")
        
        return {
            "message": f"Modelo {model_type} treinado com sucesso",
            "metrics": result
        }
        
    except Exception as e:
        logger.error(f"Erro no treinamento ML: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/user/{user_id}/profile")
async def get_user_profile(user_id: str):
    """Obtém perfil do usuário"""
    try:
        profile = recommendation_engine.build_user_profile(user_id)
        return profile
        
    except Exception as e:
        logger.error(f"Erro ao obter perfil do usuário: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/user/{user_id}/patterns")
async def get_user_patterns(user_id: str, limit: int = Query(10, description="Número máximo de padrões")):
    """Obtém padrões de uso do usuário"""
    try:
        patterns = feedback_system.get_user_patterns(user_id, limit)
        return {"user_id": user_id, "patterns": patterns}
        
    except Exception as e:
        logger.error(f"Erro ao obter padrões do usuário: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download de arquivos gerados"""
    file_path = Path("output") / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )

# ENDPOINTS DE ADMINISTRAÇÃO - REDECORP\R337786
@app.get("/admin/dashboard/{user_id}")
async def get_admin_dashboard(user_id: str):
    """Dashboard administrativo para usuários autorizados"""
    try:
        dashboard_data = admin_system.get_admin_dashboard_data(user_id)
        return dashboard_data
        
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Erro no dashboard admin: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/admin/templates/{user_id}")
async def list_admin_templates(user_id: str):
    """Lista templates para administração"""
    try:
        if not admin_system.verify_admin_access(user_id):
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        templates = admin_system.list_templates()
        return {"templates": templates}
        
    except Exception as e:
        logger.error(f"Erro ao listar templates: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/admin/template/update")
async def update_template(request: TemplateUpdateRequest):
    """Atualiza placeholders de template"""
    try:
        result = admin_system.update_template(
            request.user_id,
            request.template_name,
            request.new_placeholders
        )
        return result
        
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao atualizar template: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/admin/template/create")
async def create_template(request: AdminRequest):
    """Cria novo template"""
    try:
        params = request.parameters or {}
        result = admin_system.create_new_template(
            request.user_id,
            params.get("template_name"),
            params.get("base_template")
        )
        return result
        
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao criar template: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/admin/sharepoint/config")
async def configure_sharepoint(request: SharePointConfigRequest):
    """Configura integração SharePoint"""
    try:
        result = admin_system.configure_sharepoint(request.user_id, request.config)
        return result
        
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Erro na configuração SharePoint: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/admin/sharepoint/upload")
async def upload_to_sharepoint(request: AdminRequest):
    """Upload de arquivo para SharePoint"""
    try:
        params = request.parameters or {}
        result = admin_system.upload_to_sharepoint(
            params.get("file_path"),
            request.user_id
        )
        return result
        
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Erro no upload SharePoint: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/cleanup")
async def cleanup_old_data(days: int = Query(90, description="Dias para manter os dados")):
    """Limpeza de dados antigos"""
    try:
        # Limpar dados de feedback
        feedback_system.cleanup_old_data(days)
        
        # Limpar modelos antigos
        ml_engine.cleanup_old_models(days)
        
        return {"message": f"Limpeza concluída - dados anteriores a {days} dias removidos"}
        
    except Exception as e:
        logger.error(f"Erro na limpeza: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint para chat/conversação
@app.post("/chat")
async def chat_with_agent(
    message: str,
    user_id: str = Query("default", description="ID do usuário"),
    context: Optional[Dict] = None
):
    """Chat conversacional com o agente"""
    try:
        # Processar mensagem com NLP
        nlp_result = nlp_engine.process_query(message, context)
        
        # Gerar resposta natural
        if "analysis_result" in (context or {}):
            natural_response = nlp_engine.generate_natural_response(
                context["analysis_result"], 
                message
            )
        else:
            natural_response = nlp_result.get("response", "Como posso ajudá-lo com suas análises?")
        
        # Obter recomendações contextuais
        recommendations = recommendation_engine.recommend_analyses(user_id, context)
        
        result = {
            "response": natural_response,
            "interpretation": nlp_result,
            "suggestions": recommendations[:3],
            "can_execute": nlp_result.get("intent") != "unknown"
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Erro no chat: {e}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    # Criar diretórios necessários
    for directory in ["data", "output", "logs", "data/models"]:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # Inicializar modelos ML em background
    try:
        logger.info("Inicializando modelos ML...")
        ml_engine.train_analysis_predictor()
        ml_engine.train_quality_classifier()
        ml_engine.train_anomaly_detector()
        ml_engine.train_user_clusterer()
        logger.info("Modelos ML inicializados")
    except Exception as e:
        logger.warning(f"Erro na inicialização dos modelos ML: {e}")
    
    # Iniciar servidor
    # CONFIGURAÇÃO PARA SERVIDOR LOCAL DA EMPRESA
    # host="0.0.0.0" permite acesso via localhost E IP específico
    uvicorn.run(
        "main_ai:app",
        host="0.0.0.0",        # Permite acesso via localhost e IP específico
        port=5000,             # Porta do servidor
        reload=False,          # Desabilitado para produção
        log_level="info"
    )

