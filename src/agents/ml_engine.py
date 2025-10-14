"""
Machine Learning Engine para Aprendizado Contínuo
Implementa modelos de ML que evoluem com o uso do sistema
"""

import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json
import pickle
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Imports opcionais - não quebram se não estiverem disponíveis
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("⚠️ numpy não disponível - funcionalidades ML limitadas")

try:
    from sklearn.ensemble import RandomForestClassifier, IsolationForest
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, silhouette_score
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import PCA
    from sklearn.linear_model import LinearRegression
    from sklearn.tree import DecisionTreeRegressor
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️ sklearn não disponível - ML Engine desabilitado")

try:
    from loguru import logger
    LOGURU_AVAILABLE = True
except ImportError:
    LOGURU_AVAILABLE = False
    import logging
    logger = logging.getLogger(__name__)

try:
    from .feedback_system import feedback_system
    FEEDBACK_SYSTEM_AVAILABLE = True
except ImportError:
    FEEDBACK_SYSTEM_AVAILABLE = False
    print("⚠️ feedback_system não disponível - usando dados simulados")


class MLEngine:
    """Engine de Machine Learning para aprendizado contínuo"""
    
    def __init__(self, models_dir: str = "data/models"):
        """
        Inicializa o ML Engine
        
        Args:
            models_dir: Diretório para salvar modelos treinados
        """
        if not SKLEARN_AVAILABLE:
            if LOGURU_AVAILABLE:
                logger.warning("MLEngine inicializado em modo limitado - sklearn não disponível")
            else:
                print("⚠️ MLEngine inicializado em modo limitado - sklearn não disponível")
            self.enabled = False
            return
            
        self.enabled = True
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Modelos ativos
        self.models = {
            "analysis_predictor": None,
            "quality_classifier": None,
            "anomaly_detector": None,
            "user_clusterer": None,
            "performance_predictor": None
        }
        
        # Scalers e encoders
        self.scalers = {}
        self.encoders = {}
        
        # Métricas de performance dos modelos
        self.model_metrics = {}
        
        # Carregar modelos existentes
        self._load_existing_models()
        
        logger.info("MLEngine inicializado com sucesso")
    
    def _load_existing_models(self):
        """Carrega modelos previamente treinados"""
        for model_name in self.models.keys():
            model_path = self.models_dir / f"{model_name}.pkl"
            if model_path.exists():
                try:
                    with open(model_path, 'rb') as f:
                        self.models[model_name] = pickle.load(f)
                    logger.info(f"Modelo {model_name} carregado com sucesso")
                except Exception as e:
                    logger.warning(f"Erro ao carregar modelo {model_name}: {e}")
    
    def _save_model(self, model_name: str, model: Any):
        """Salva modelo treinado"""
        model_path = self.models_dir / f"{model_name}.pkl"
        try:
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            logger.info(f"Modelo {model_name} salvo com sucesso")
        except Exception as e:
            logger.error(f"Erro ao salvar modelo {model_name}: {e}")
    
    def train_analysis_predictor(self, retrain: bool = False) -> Dict[str, Any]:
        """
        Treina modelo para predizer tipo de análise baseado no contexto
        
        Args:
            retrain: Se deve retreinar mesmo com modelo existente
            
        Returns:
            Métricas do modelo treinado
        """
        if self.models["analysis_predictor"] is not None and not retrain:
            return self.model_metrics.get("analysis_predictor", {})
        
        # Obter dados de treinamento
        training_data = self._get_analysis_training_data()
        
        if len(training_data) < 10:
            logger.warning("Dados insuficientes para treinar analysis_predictor")
            return {"error": "Dados insuficientes"}
        
        # Preparar features
        X, y = self._prepare_analysis_features(training_data)
        
        if len(X) == 0:
            logger.warning("Nenhuma feature válida para analysis_predictor")
            return {"error": "Features inválidas"}
        
        # Dividir dados
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Treinar modelo
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Avaliar modelo
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Salvar modelo
        self.models["analysis_predictor"] = model
        self._save_model("analysis_predictor", model)
        
        # Salvar métricas
        metrics = {
            "accuracy": accuracy,
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "features": X.shape[1],
            "classes": len(np.unique(y)),
            "trained_at": datetime.now().isoformat()
        }
        
        self.model_metrics["analysis_predictor"] = metrics
        
        logger.info(f"Analysis predictor treinado - Accuracy: {accuracy:.3f}")
        return metrics
    
    def _get_analysis_training_data(self) -> List[Dict]:
        """Obtém dados de treinamento para predição de análises"""
        # Exportar dados do sistema de feedback
        data = feedback_system.export_data()
        interactions = data.get("interactions", [])
        
        # Filtrar interações de análise com feedback positivo
        training_data = []
        for interaction in interactions:
            if (interaction.get("action_type") == "analyze" and 
                interaction.get("success") and
                interaction.get("request_data")):
                
                try:
                    request_data = json.loads(interaction["request_data"])
                    if "analysis_type" in request_data:
                        training_data.append({
                            "interaction_id": interaction["id"],
                            "analysis_type": request_data["analysis_type"],
                            "parameters": request_data.get("parameters", {}),
                            "execution_time": interaction.get("execution_time", 0),
                            "user_id": interaction.get("user_id"),
                            "timestamp": interaction.get("timestamp")
                        })
                except:
                    continue
        
        return training_data
    
    def _prepare_analysis_features(self, training_data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepara features para predição de análises"""
        features = []
        labels = []
        
        for item in training_data:
            try:
                # Features baseadas nos parâmetros
                params = item.get("parameters", {})
                
                # Features numéricas
                feature_vector = [
                    len(str(params)),  # Complexidade dos parâmetros
                    item.get("execution_time", 0),  # Tempo de execução
                    len(params.keys()) if isinstance(params, dict) else 0,  # Número de parâmetros
                ]
                
                # Features categóricas (one-hot encoding simples)
                has_period = 1 if any(key in str(params).lower() for key in ["period", "ano", "year"]) else 0
                has_group = 1 if any(key in str(params).lower() for key in ["group", "grupo", "categoria"]) else 0
                has_metric = 1 if any(key in str(params).lower() for key in ["metric", "kpi", "valor"]) else 0
                
                feature_vector.extend([has_period, has_group, has_metric])
                
                # Features temporais
                timestamp = item.get("timestamp", "")
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        hour = dt.hour
                        day_of_week = dt.weekday()
                        feature_vector.extend([hour, day_of_week])
                    except:
                        feature_vector.extend([12, 1])  # Valores padrão
                else:
                    feature_vector.extend([12, 1])
                
                features.append(feature_vector)
                labels.append(item["analysis_type"])
                
            except Exception as e:
                logger.debug(f"Erro ao processar item de treinamento: {e}")
                continue
        
        if not features:
            return np.array([]), np.array([])
        
        # Converter para arrays numpy
        X = np.array(features)
        
        # Encoder para labels
        if "analysis_predictor" not in self.encoders:
            self.encoders["analysis_predictor"] = LabelEncoder()
            y = self.encoders["analysis_predictor"].fit_transform(labels)
        else:
            y = self.encoders["analysis_predictor"].transform(labels)
        
        # Scaler para features
        if "analysis_predictor" not in self.scalers:
            self.scalers["analysis_predictor"] = StandardScaler()
            X = self.scalers["analysis_predictor"].fit_transform(X)
        else:
            X = self.scalers["analysis_predictor"].transform(X)
        
        return X, y
    
    def predict_analysis_type(self, context: Dict) -> Dict[str, Any]:
        """
        Prediz tipo de análise baseado no contexto
        
        Args:
            context: Contexto da requisição
            
        Returns:
            Predição com probabilidades
        """
        if self.models["analysis_predictor"] is None:
            return {"error": "Modelo não treinado"}
        
        try:
            # Preparar features do contexto
            features = self._extract_context_features(context)
            
            if "analysis_predictor" in self.scalers:
                features = self.scalers["analysis_predictor"].transform([features])
            else:
                features = np.array([features])
            
            # Fazer predição
            prediction = self.models["analysis_predictor"].predict(features)[0]
            probabilities = self.models["analysis_predictor"].predict_proba(features)[0]
            
            # Decodificar predição
            if "analysis_predictor" in self.encoders:
                predicted_type = self.encoders["analysis_predictor"].inverse_transform([prediction])[0]
                classes = self.encoders["analysis_predictor"].classes_
            else:
                predicted_type = str(prediction)
                classes = [predicted_type]
            
            # Criar resultado com probabilidades
            result = {
                "predicted_type": predicted_type,
                "confidence": float(max(probabilities)),
                "probabilities": {
                    classes[i]: float(prob) for i, prob in enumerate(probabilities)
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Erro na predição de análise: {e}")
            return {"error": str(e)}
    
    def _extract_context_features(self, context: Dict) -> List[float]:
        """Extrai features do contexto para predição"""
        features = []
        
        # Features dos dados
        data_size = context.get("data_size", 0)
        num_columns = len(context.get("available_columns", []))
        
        features.extend([
            np.log1p(data_size),  # Log do tamanho dos dados
            num_columns,  # Número de colunas
            len(str(context))  # Complexidade do contexto
        ])
        
        # Features categóricas baseadas nas colunas disponíveis
        columns = [col.lower() for col in context.get("available_columns", [])]
        
        has_date = 1 if any(col in ["data", "date", "timestamp", "ano", "year"] for col in columns) else 0
        has_category = 1 if any(col in ["grupo", "categoria", "tipo", "perfil"] for col in columns) else 0
        has_value = 1 if any(col in ["valor", "value", "amount", "vendas", "receita"] for col in columns) else 0
        
        features.extend([has_date, has_category, has_value])
        
        # Features temporais (hora atual)
        now = datetime.now()
        features.extend([now.hour, now.weekday()])
        
        return features
    
    def train_quality_classifier(self, retrain: bool = False) -> Dict[str, Any]:
        """
        Treina modelo para classificar qualidade das análises
        
        Args:
            retrain: Se deve retreinar mesmo com modelo existente
            
        Returns:
            Métricas do modelo treinado
        """
        if self.models["quality_classifier"] is not None and not retrain:
            return self.model_metrics.get("quality_classifier", {})
        
        # Obter dados de feedback
        training_data = self._get_quality_training_data()
        
        if len(training_data) < 10:
            logger.warning("Dados insuficientes para treinar quality_classifier")
            return {"error": "Dados insuficientes"}
        
        # Preparar features
        X, y = self._prepare_quality_features(training_data)
        
        if len(X) == 0:
            return {"error": "Features inválidas"}
        
        # Dividir dados
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Treinar modelo
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Avaliar modelo
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Salvar modelo
        self.models["quality_classifier"] = model
        self._save_model("quality_classifier", model)
        
        # Salvar métricas
        metrics = {
            "accuracy": accuracy,
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "features": X.shape[1],
            "trained_at": datetime.now().isoformat()
        }
        
        self.model_metrics["quality_classifier"] = metrics
        
        logger.info(f"Quality classifier treinado - Accuracy: {accuracy:.3f}")
        return metrics
    
    def _get_quality_training_data(self) -> List[Dict]:
        """Obtém dados de treinamento para classificação de qualidade"""
        data = feedback_system.export_data()
        feedback_data = data.get("feedback", [])
        interactions = {item["id"]: item for item in data.get("interactions", [])}
        
        training_data = []
        for feedback in feedback_data:
            interaction_id = feedback.get("interaction_id")
            if interaction_id in interactions:
                interaction = interactions[interaction_id]
                
                # Classificar qualidade baseada no rating
                rating = feedback.get("rating", 3)
                quality_class = "high" if rating >= 4 else "medium" if rating >= 3 else "low"
                
                training_data.append({
                    "interaction": interaction,
                    "feedback": feedback,
                    "quality_class": quality_class,
                    "rating": rating
                })
        
        return training_data
    
    def _prepare_quality_features(self, training_data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepara features para classificação de qualidade"""
        features = []
        labels = []
        
        for item in training_data:
            try:
                interaction = item["interaction"]
                feedback = item["feedback"]
                
                # Features da interação
                execution_time = interaction.get("execution_time", 0)
                success = 1 if interaction.get("success") else 0
                
                # Features do resultado
                response_data = json.loads(interaction.get("response_data", "{}"))
                result_size = len(str(response_data))
                has_validation = 1 if "validation" in response_data else 0
                
                # Features do feedback
                useful = 1 if feedback.get("useful") else 0
                has_comment = 1 if feedback.get("comment") else 0
                
                feature_vector = [
                    execution_time,
                    success,
                    result_size,
                    has_validation,
                    useful,
                    has_comment
                ]
                
                features.append(feature_vector)
                labels.append(item["quality_class"])
                
            except Exception as e:
                logger.debug(f"Erro ao processar item de qualidade: {e}")
                continue
        
        if not features:
            return np.array([]), np.array([])
        
        X = np.array(features)
        
        # Encoder para labels
        if "quality_classifier" not in self.encoders:
            self.encoders["quality_classifier"] = LabelEncoder()
            y = self.encoders["quality_classifier"].fit_transform(labels)
        else:
            y = self.encoders["quality_classifier"].transform(labels)
        
        # Scaler para features
        if "quality_classifier" not in self.scalers:
            self.scalers["quality_classifier"] = StandardScaler()
            X = self.scalers["quality_classifier"].fit_transform(X)
        else:
            X = self.scalers["quality_classifier"].transform(X)
        
        return X, y
    
    def predict_quality(self, interaction_data: Dict) -> Dict[str, Any]:
        """
        Prediz qualidade de uma análise
        
        Args:
            interaction_data: Dados da interação
            
        Returns:
            Predição de qualidade
        """
        if self.models["quality_classifier"] is None:
            return {"error": "Modelo não treinado"}
        
        try:
            # Extrair features
            features = self._extract_quality_features(interaction_data)
            
            if "quality_classifier" in self.scalers:
                features = self.scalers["quality_classifier"].transform([features])
            else:
                features = np.array([features])
            
            # Fazer predição
            prediction = self.models["quality_classifier"].predict(features)[0]
            probabilities = self.models["quality_classifier"].predict_proba(features)[0]
            
            # Decodificar predição
            if "quality_classifier" in self.encoders:
                predicted_quality = self.encoders["quality_classifier"].inverse_transform([prediction])[0]
                classes = self.encoders["quality_classifier"].classes_
            else:
                predicted_quality = str(prediction)
                classes = [predicted_quality]
            
            result = {
                "predicted_quality": predicted_quality,
                "confidence": float(max(probabilities)),
                "probabilities": {
                    classes[i]: float(prob) for i, prob in enumerate(probabilities)
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Erro na predição de qualidade: {e}")
            return {"error": str(e)}
    
    def _extract_quality_features(self, interaction_data: Dict) -> List[float]:
        """Extrai features para predição de qualidade"""
        features = []
        
        # Features básicas
        execution_time = interaction_data.get("execution_time", 0)
        success = 1 if interaction_data.get("success") else 0
        
        # Features do resultado
        response_data = interaction_data.get("response_data", {})
        if isinstance(response_data, str):
            try:
                response_data = json.loads(response_data)
            except:
                response_data = {}
        
        result_size = len(str(response_data))
        has_validation = 1 if "validation" in response_data else 0
        
        features = [
            execution_time,
            success,
            result_size,
            has_validation,
            0,  # useful (não conhecido ainda)
            0   # has_comment (não conhecido ainda)
        ]
        
        return features
    
    def train_anomaly_detector(self, retrain: bool = False) -> Dict[str, Any]:
        """
        Treina detector de anomalias para identificar padrões incomuns
        
        Args:
            retrain: Se deve retreinar mesmo com modelo existente
            
        Returns:
            Métricas do modelo treinado
        """
        if self.models["anomaly_detector"] is not None and not retrain:
            return self.model_metrics.get("anomaly_detector", {})
        
        # Obter dados normais (interações bem-sucedidas)
        training_data = self._get_normal_interactions()
        
        if len(training_data) < 20:
            logger.warning("Dados insuficientes para treinar anomaly_detector")
            return {"error": "Dados insuficientes"}
        
        # Preparar features
        X = self._prepare_anomaly_features(training_data)
        
        if len(X) == 0:
            return {"error": "Features inválidas"}
        
        # Treinar modelo
        model = IsolationForest(contamination=0.1, random_state=42)
        model.fit(X)
        
        # Avaliar modelo (usando dados de treinamento)
        predictions = model.predict(X)
        anomaly_rate = (predictions == -1).mean()
        
        # Salvar modelo
        self.models["anomaly_detector"] = model
        self._save_model("anomaly_detector", model)
        
        # Salvar métricas
        metrics = {
            "anomaly_rate": anomaly_rate,
            "training_samples": len(X),
            "features": X.shape[1],
            "trained_at": datetime.now().isoformat()
        }
        
        self.model_metrics["anomaly_detector"] = metrics
        
        logger.info(f"Anomaly detector treinado - Taxa de anomalia: {anomaly_rate:.3f}")
        return metrics
    
    def _get_normal_interactions(self) -> List[Dict]:
        """Obtém interações normais para treinar detector de anomalias"""
        data = feedback_system.export_data()
        interactions = data.get("interactions", [])
        
        # Filtrar apenas interações bem-sucedidas
        normal_interactions = [
            interaction for interaction in interactions
            if interaction.get("success") and interaction.get("execution_time", 0) > 0
        ]
        
        return normal_interactions
    
    def _prepare_anomaly_features(self, training_data: List[Dict]) -> np.ndarray:
        """Prepara features para detecção de anomalias"""
        features = []
        
        for interaction in training_data:
            try:
                # Features temporais
                execution_time = interaction.get("execution_time", 0)
                
                # Features do request
                request_data = json.loads(interaction.get("request_data", "{}"))
                request_size = len(str(request_data))
                num_params = len(request_data.keys()) if isinstance(request_data, dict) else 0
                
                # Features do response
                response_data = json.loads(interaction.get("response_data", "{}"))
                response_size = len(str(response_data))
                
                # Features do usuário
                user_id_hash = hash(interaction.get("user_id", "")) % 1000  # Hash simples
                
                feature_vector = [
                    execution_time,
                    request_size,
                    num_params,
                    response_size,
                    user_id_hash
                ]
                
                features.append(feature_vector)
                
            except Exception as e:
                logger.debug(f"Erro ao processar interação para anomalia: {e}")
                continue
        
        if not features:
            return np.array([])
        
        X = np.array(features)
        
        # Scaler para features
        if "anomaly_detector" not in self.scalers:
            self.scalers["anomaly_detector"] = StandardScaler()
            X = self.scalers["anomaly_detector"].fit_transform(X)
        else:
            X = self.scalers["anomaly_detector"].transform(X)
        
        return X
    
    def detect_anomaly(self, interaction_data: Dict) -> Dict[str, Any]:
        """
        Detecta se uma interação é anômala
        
        Args:
            interaction_data: Dados da interação
            
        Returns:
            Resultado da detecção de anomalia
        """
        if self.models["anomaly_detector"] is None:
            return {"error": "Modelo não treinado"}
        
        try:
            # Extrair features
            features = self._extract_anomaly_features(interaction_data)
            
            if "anomaly_detector" in self.scalers:
                features = self.scalers["anomaly_detector"].transform([features])
            else:
                features = np.array([features])
            
            # Detectar anomalia
            prediction = self.models["anomaly_detector"].predict(features)[0]
            anomaly_score = self.models["anomaly_detector"].decision_function(features)[0]
            
            is_anomaly = prediction == -1
            
            result = {
                "is_anomaly": bool(is_anomaly),
                "anomaly_score": float(anomaly_score),
                "confidence": abs(float(anomaly_score))
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Erro na detecção de anomalia: {e}")
            return {"error": str(e)}
    
    def _extract_anomaly_features(self, interaction_data: Dict) -> List[float]:
        """Extrai features para detecção de anomalias"""
        # Features temporais
        execution_time = interaction_data.get("execution_time", 0)
        
        # Features do request
        request_data = interaction_data.get("request_data", {})
        if isinstance(request_data, str):
            try:
                request_data = json.loads(request_data)
            except:
                request_data = {}
        
        request_size = len(str(request_data))
        num_params = len(request_data.keys()) if isinstance(request_data, dict) else 0
        
        # Features do response
        response_data = interaction_data.get("response_data", {})
        if isinstance(response_data, str):
            try:
                response_data = json.loads(response_data)
            except:
                response_data = {}
        
        response_size = len(str(response_data))
        
        # Features do usuário
        user_id_hash = hash(interaction_data.get("user_id", "")) % 1000
        
        features = [
            execution_time,
            request_size,
            num_params,
            response_size,
            user_id_hash
        ]
        
        return features
    
    def train_user_clusterer(self, retrain: bool = False) -> Dict[str, Any]:
        """
        Treina modelo para agrupar usuários similares
        
        Args:
            retrain: Se deve retreinar mesmo com modelo existente
            
        Returns:
            Métricas do modelo treinado
        """
        if self.models["user_clusterer"] is not None and not retrain:
            return self.model_metrics.get("user_clusterer", {})
        
        # Obter dados dos usuários
        user_data = self._get_user_clustering_data()
        
        if len(user_data) < 5:
            logger.warning("Dados insuficientes para treinar user_clusterer")
            return {"error": "Dados insuficientes"}
        
        # Preparar features
        X, user_ids = self._prepare_user_features(user_data)
        
        if len(X) == 0:
            return {"error": "Features inválidas"}
        
        # Determinar número ótimo de clusters
        n_clusters = min(max(2, len(X) // 3), 8)
        
        # Treinar modelo
        model = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = model.fit_predict(X)
        
        # Avaliar modelo
        silhouette = silhouette_score(X, clusters) if len(set(clusters)) > 1 else 0
        
        # Salvar modelo
        self.models["user_clusterer"] = model
        self._save_model("user_clusterer", model)
        
        # Salvar métricas
        metrics = {
            "silhouette_score": silhouette,
            "n_clusters": n_clusters,
            "training_samples": len(X),
            "features": X.shape[1],
            "trained_at": datetime.now().isoformat()
        }
        
        self.model_metrics["user_clusterer"] = metrics
        
        logger.info(f"User clusterer treinado - Silhouette: {silhouette:.3f}")
        return metrics
    
    def _get_user_clustering_data(self) -> List[Dict]:
        """Obtém dados para clustering de usuários"""
        data = feedback_system.export_data()
        interactions = data.get("interactions", [])
        
        # Agrupar por usuário
        user_stats = {}
        for interaction in interactions:
            user_id = interaction.get("user_id")
            if not user_id:
                continue
            
            if user_id not in user_stats:
                user_stats[user_id] = {
                    "user_id": user_id,
                    "total_interactions": 0,
                    "successful_interactions": 0,
                    "total_execution_time": 0,
                    "analysis_types": set(),
                    "avg_execution_time": 0
                }
            
            stats = user_stats[user_id]
            stats["total_interactions"] += 1
            
            if interaction.get("success"):
                stats["successful_interactions"] += 1
            
            execution_time = interaction.get("execution_time", 0)
            stats["total_execution_time"] += execution_time
            
            # Extrair tipo de análise
            try:
                request_data = json.loads(interaction.get("request_data", "{}"))
                analysis_type = request_data.get("analysis_type")
                if analysis_type:
                    stats["analysis_types"].add(analysis_type)
            except:
                pass
        
        # Calcular métricas finais
        user_data = []
        for user_id, stats in user_stats.items():
            if stats["total_interactions"] > 0:
                stats["success_rate"] = stats["successful_interactions"] / stats["total_interactions"]
                stats["avg_execution_time"] = stats["total_execution_time"] / stats["total_interactions"]
                stats["analysis_diversity"] = len(stats["analysis_types"])
                user_data.append(stats)
        
        return user_data
    
    def _prepare_user_features(self, user_data: List[Dict]) -> Tuple[np.ndarray, List[str]]:
        """Prepara features para clustering de usuários"""
        features = []
        user_ids = []
        
        for user_stats in user_data:
            try:
                feature_vector = [
                    user_stats["total_interactions"],
                    user_stats["success_rate"],
                    user_stats["avg_execution_time"],
                    user_stats["analysis_diversity"]
                ]
                
                features.append(feature_vector)
                user_ids.append(user_stats["user_id"])
                
            except Exception as e:
                logger.debug(f"Erro ao processar usuário para clustering: {e}")
                continue
        
        if not features:
            return np.array([]), []
        
        X = np.array(features)
        
        # Scaler para features
        if "user_clusterer" not in self.scalers:
            self.scalers["user_clusterer"] = StandardScaler()
            X = self.scalers["user_clusterer"].fit_transform(X)
        else:
            X = self.scalers["user_clusterer"].transform(X)
        
        return X, user_ids
    
    def predict_user_cluster(self, user_id: str) -> Dict[str, Any]:
        """
        Prediz cluster do usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Cluster predito
        """
        if self.models["user_clusterer"] is None:
            return {"error": "Modelo não treinado"}
        
        try:
            # Obter estatísticas do usuário
            user_stats = self._get_user_stats(user_id)
            
            if not user_stats:
                return {"error": "Usuário não encontrado"}
            
            # Extrair features
            features = [
                user_stats["total_interactions"],
                user_stats["success_rate"],
                user_stats["avg_execution_time"],
                user_stats["analysis_diversity"]
            ]
            
            if "user_clusterer" in self.scalers:
                features = self.scalers["user_clusterer"].transform([features])
            else:
                features = np.array([features])
            
            # Predizer cluster
            cluster = self.models["user_clusterer"].predict(features)[0]
            
            result = {
                "cluster": int(cluster),
                "user_stats": user_stats
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Erro na predição de cluster: {e}")
            return {"error": str(e)}
    
    def _get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Obtém estatísticas de um usuário específico"""
        data = feedback_system.export_data()
        interactions = [i for i in data.get("interactions", []) if i.get("user_id") == user_id]
        
        if not interactions:
            return {}
        
        total_interactions = len(interactions)
        successful_interactions = sum(1 for i in interactions if i.get("success"))
        total_execution_time = sum(i.get("execution_time", 0) for i in interactions)
        
        analysis_types = set()
        for interaction in interactions:
            try:
                request_data = json.loads(interaction.get("request_data", "{}"))
                analysis_type = request_data.get("analysis_type")
                if analysis_type:
                    analysis_types.add(analysis_type)
            except:
                pass
        
        return {
            "total_interactions": total_interactions,
            "successful_interactions": successful_interactions,
            "success_rate": successful_interactions / total_interactions,
            "total_execution_time": total_execution_time,
            "avg_execution_time": total_execution_time / total_interactions,
            "analysis_diversity": len(analysis_types),
            "analysis_types": list(analysis_types)
        }
    
    def retrain_all_models(self) -> Dict[str, Any]:
        """
        Retreina todos os modelos com dados atualizados
        
        Returns:
            Resultados do retreinamento
        """
        results = {}
        
        logger.info("Iniciando retreinamento de todos os modelos")
        
        # Retreinar cada modelo
        for model_name in self.models.keys():
            try:
                if model_name == "analysis_predictor":
                    results[model_name] = self.train_analysis_predictor(retrain=True)
                elif model_name == "quality_classifier":
                    results[model_name] = self.train_quality_classifier(retrain=True)
                elif model_name == "anomaly_detector":
                    results[model_name] = self.train_anomaly_detector(retrain=True)
                elif model_name == "user_clusterer":
                    results[model_name] = self.train_user_clusterer(retrain=True)
                
            except Exception as e:
                logger.error(f"Erro ao retreinar {model_name}: {e}")
                results[model_name] = {"error": str(e)}
        
        logger.info("Retreinamento concluído")
        return results
    
    def get_model_status(self) -> Dict[str, Any]:
        """
        Obtém status de todos os modelos
        
        Returns:
            Status dos modelos
        """
        status = {}
        
        for model_name, model in self.models.items():
            status[model_name] = {
                "trained": model is not None,
                "metrics": self.model_metrics.get(model_name, {}),
                "last_trained": self.model_metrics.get(model_name, {}).get("trained_at", "Never")
            }
        
        return status
    
    def cleanup_old_models(self, days: int = 30):
        """
        Remove modelos antigos para economizar espaço
        
        Args:
            days: Número de dias para manter os modelos
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for model_file in self.models_dir.glob("*.pkl"):
            try:
                # Verificar data de modificação
                mod_time = datetime.fromtimestamp(model_file.stat().st_mtime)
                
                if mod_time < cutoff_date:
                    model_file.unlink()
                    logger.info(f"Modelo antigo removido: {model_file.name}")
                    
            except Exception as e:
                logger.warning(f"Erro ao remover modelo {model_file.name}: {e}")


# Instância global do ML Engine
ml_engine = MLEngine()

