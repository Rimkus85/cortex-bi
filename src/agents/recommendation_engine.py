"""
Sistema de Recomendações e Personalização
Analisa padrões de uso e gera sugestões personalizadas
"""

import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import json

# Imports opcionais - não quebram se não estiverem disponíveis
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("⚠️ numpy não disponível - algumas funcionalidades de recomendação limitadas")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️ sklearn não disponível - recomendações avançadas desabilitadas")

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


class RecommendationEngine:
    """Engine de recomendações baseado em padrões de uso e feedback"""
    
    def __init__(self):
        """Inicializa o sistema de recomendações"""
        self.user_profiles = {}
        self.analysis_similarity_matrix = None
        self.template_similarity_matrix = None
        
        # Inicializar vectorizer apenas se sklearn estiver disponível
        if SKLEARN_AVAILABLE:
            self.vectorizer = TfidfVectorizer(stop_words=['portuguese'])
        else:
            self.vectorizer = None
            
        if LOGURU_AVAILABLE:
            logger.info("RecommendationEngine inicializado com sucesso")
        else:
            print("✅ RecommendationEngine inicializado com sucesso")
    
    def build_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Constrói perfil do usuário baseado no histórico
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Perfil do usuário com preferências e padrões
        """
        # Obter dados do usuário
        patterns = feedback_system.get_user_patterns(user_id)
        preferences = feedback_system.get_user_preferences(user_id)
        
        # Analisar padrões de uso
        usage_analysis = self._analyze_usage_patterns(patterns)
        
        # Analisar preferências
        preference_analysis = self._analyze_preferences(preferences)
        
        # Calcular scores de interesse
        interest_scores = self._calculate_interest_scores(patterns, preferences)
        
        # Detectar persona do usuário
        persona = self._detect_user_persona(usage_analysis, preference_analysis)
        
        profile = {
            "user_id": user_id,
            "persona": persona,
            "usage_patterns": usage_analysis,
            "preferences": preference_analysis,
            "interest_scores": interest_scores,
            "last_updated": datetime.now().isoformat(),
            "activity_level": self._calculate_activity_level(patterns),
            "expertise_level": self._estimate_expertise_level(patterns, preferences)
        }
        
        self.user_profiles[user_id] = profile
        logger.info(f"Perfil construído para usuário {user_id} - Persona: {persona}")
        return profile
    
    def _analyze_usage_patterns(self, patterns: List[Dict]) -> Dict[str, Any]:
        """Analisa padrões de uso do usuário"""
        if not patterns:
            return {"most_used_analyses": [], "usage_frequency": {}, "time_patterns": {}}
        
        # Contar tipos de análise mais usados
        analysis_counts = Counter()
        total_frequency = 0
        
        for pattern in patterns:
            pattern_data = pattern.get("pattern_data", {})
            analysis_type = pattern_data.get("analysis_type", "unknown")
            frequency = pattern.get("frequency", 1)
            
            analysis_counts[analysis_type] += frequency
            total_frequency += frequency
        
        # Análise temporal (simulada baseada em last_used)
        time_patterns = self._analyze_time_patterns(patterns)
        
        return {
            "most_used_analyses": analysis_counts.most_common(5),
            "usage_frequency": dict(analysis_counts),
            "total_interactions": total_frequency,
            "time_patterns": time_patterns,
            "diversity_score": len(analysis_counts) / max(total_frequency, 1)
        }
    
    def _analyze_preferences(self, preferences: Dict[str, List]) -> Dict[str, Any]:
        """Analisa preferências do usuário"""
        if not preferences:
            return {"preferred_analyses": [], "preferred_templates": [], "confidence_scores": {}}
        
        analysis = {
            "preferred_analyses": [],
            "preferred_templates": [],
            "preferred_metrics": [],
            "confidence_scores": {}
        }
        
        for pref_type, pref_list in preferences.items():
            if pref_list:
                # Ordenar por confiança
                sorted_prefs = sorted(pref_list, key=lambda x: x["confidence"], reverse=True)
                
                if pref_type == "preferred_analysis":
                    analysis["preferred_analyses"] = [(p["value"], p["confidence"]) for p in sorted_prefs[:3]]
                elif pref_type == "preferred_template":
                    analysis["preferred_templates"] = [(p["value"], p["confidence"]) for p in sorted_prefs[:3]]
                elif pref_type == "preferred_metric":
                    analysis["preferred_metrics"] = [(p["value"], p["confidence"]) for p in sorted_prefs[:5]]
                
                # Score médio de confiança por tipo
                avg_confidence = np.mean([p["confidence"] for p in pref_list])
                analysis["confidence_scores"][pref_type] = avg_confidence
        
        return analysis
    
    def _analyze_time_patterns(self, patterns: List[Dict]) -> Dict[str, Any]:
        """Analisa padrões temporais de uso"""
        if not patterns:
            return {}
        
        # Simular análise temporal baseada em last_used
        time_analysis = {
            "most_active_period": "morning",  # Simulado
            "usage_consistency": 0.7,  # Simulado
            "peak_hours": [9, 10, 14, 15],  # Simulado
            "weekly_pattern": "weekdays"  # Simulado
        }
        
        return time_analysis
    
    def _calculate_interest_scores(self, patterns: List[Dict], preferences: Dict) -> Dict[str, float]:
        """Calcula scores de interesse por categoria"""
        scores = defaultdict(float)
        
        # Score baseado em padrões de uso
        for pattern in patterns:
            pattern_data = pattern.get("pattern_data", {})
            analysis_type = pattern_data.get("analysis_type", "unknown")
            frequency = pattern.get("frequency", 1)
            
            # Mapear para categorias
            category = self._map_to_category(analysis_type)
            scores[category] += frequency * 0.1
        
        # Score baseado em preferências
        for pref_type, pref_list in preferences.items():
            for pref in pref_list:
                category = self._map_to_category(pref["value"])
                scores[category] += pref["confidence"] * 0.2
        
        # Normalizar scores
        max_score = max(scores.values()) if scores else 1
        normalized_scores = {k: v / max_score for k, v in scores.items()}
        
        return dict(normalized_scores)
    
    def _map_to_category(self, item: str) -> str:
        """Mapeia item para categoria de interesse"""
        item_lower = item.lower()
        
        if any(word in item_lower for word in ["compare", "periodo", "temporal"]):
            return "temporal_analysis"
        elif any(word in item_lower for word in ["segment", "grupo", "categoria"]):
            return "segmentation"
        elif any(word in item_lower for word in ["motivo", "razao", "count"]):
            return "frequency_analysis"
        elif any(word in item_lower for word in ["kpi", "metric", "performance"]):
            return "performance_metrics"
        elif any(word in item_lower for word in ["vendas", "receita", "financeiro"]):
            return "financial_analysis"
        else:
            return "general_analysis"
    
    def _detect_user_persona(self, usage_analysis: Dict, preference_analysis: Dict) -> str:
        """Detecta persona do usuário baseado nos padrões"""
        total_interactions = usage_analysis.get("total_interactions", 0)
        diversity_score = usage_analysis.get("diversity_score", 0)
        most_used = usage_analysis.get("most_used_analyses", [])
        
        # Analista Explorador: alta diversidade, muitas interações
        if diversity_score > 0.7 and total_interactions > 20:
            return "explorer_analyst"
        
        # Especialista Focado: baixa diversidade, alta frequência em poucos tipos
        elif diversity_score < 0.3 and total_interactions > 10:
            return "focused_specialist"
        
        # Usuário Casual: poucas interações, padrões simples
        elif total_interactions < 10:
            return "casual_user"
        
        # Analista de Performance: foco em KPIs e métricas
        elif most_used and any("kpi" in analysis[0].lower() for analysis in most_used[:2]):
            return "performance_analyst"
        
        # Analista de Tendências: foco em comparações temporais
        elif most_used and any("compare" in analysis[0].lower() for analysis in most_used[:2]):
            return "trend_analyst"
        
        else:
            return "balanced_user"
    
    def _calculate_activity_level(self, patterns: List[Dict]) -> str:
        """Calcula nível de atividade do usuário"""
        total_frequency = sum(pattern.get("frequency", 1) for pattern in patterns)
        
        if total_frequency >= 50:
            return "high"
        elif total_frequency >= 20:
            return "medium"
        elif total_frequency >= 5:
            return "low"
        else:
            return "very_low"
    
    def _estimate_expertise_level(self, patterns: List[Dict], preferences: Dict) -> str:
        """Estima nível de expertise do usuário"""
        # Fatores para expertise
        analysis_diversity = len(set(p.get("pattern_data", {}).get("analysis_type", "") for p in patterns))
        total_interactions = sum(p.get("frequency", 1) for p in patterns)
        avg_confidence = np.mean([
            np.mean([pref["confidence"] for pref in pref_list])
            for pref_list in preferences.values() if pref_list
        ]) if preferences else 0.5
        
        expertise_score = (
            (analysis_diversity / 10) * 0.3 +
            (min(total_interactions / 100, 1)) * 0.4 +
            avg_confidence * 0.3
        )
        
        if expertise_score >= 0.8:
            return "expert"
        elif expertise_score >= 0.6:
            return "advanced"
        elif expertise_score >= 0.4:
            return "intermediate"
        else:
            return "beginner"
    
    def recommend_analyses(self, user_id: str, context: Dict = None) -> List[Dict[str, Any]]:
        """
        Recomenda análises para o usuário
        
        Args:
            user_id: ID do usuário
            context: Contexto atual (dados disponíveis, etc.)
            
        Returns:
            Lista de recomendações de análises
        """
        # Construir/atualizar perfil do usuário
        profile = self.build_user_profile(user_id)
        
        recommendations = []
        
        # Recomendações baseadas na persona
        persona_recs = self._get_persona_recommendations(profile["persona"])
        recommendations.extend(persona_recs)
        
        # Recomendações baseadas em padrões de uso
        pattern_recs = self._get_pattern_based_recommendations(profile)
        recommendations.extend(pattern_recs)
        
        # Recomendações baseadas no contexto
        if context:
            context_recs = self._get_context_based_recommendations(profile, context)
            recommendations.extend(context_recs)
        
        # Recomendações colaborativas (usuários similares)
        collaborative_recs = self._get_collaborative_recommendations(user_id, profile)
        recommendations.extend(collaborative_recs)
        
        # Remover duplicatas e ordenar por relevância
        unique_recs = self._deduplicate_and_rank(recommendations)
        
        logger.info(f"Geradas {len(unique_recs)} recomendações para usuário {user_id}")
        return unique_recs[:10]  # Top 10 recomendações
    
    def _get_persona_recommendations(self, persona: str) -> List[Dict[str, Any]]:
        """Gera recomendações baseadas na persona do usuário"""
        persona_mappings = {
            "explorer_analyst": [
                {"type": "custom_kpis", "reason": "Explore novos KPIs personalizados", "priority": 0.8},
                {"type": "trend_analysis", "reason": "Analise tendências nos seus dados", "priority": 0.7},
                {"type": "correlation_analysis", "reason": "Descubra correlações interessantes", "priority": 0.6}
            ],
            "focused_specialist": [
                {"type": "deep_dive_analysis", "reason": "Análise aprofundada da sua área", "priority": 0.9},
                {"type": "benchmark_analysis", "reason": "Compare com benchmarks do setor", "priority": 0.7}
            ],
            "casual_user": [
                {"type": "summary", "reason": "Visão geral dos seus dados", "priority": 0.9},
                {"type": "compare_periods", "reason": "Compare períodos recentes", "priority": 0.8},
                {"type": "top_insights", "reason": "Principais insights automáticos", "priority": 0.7}
            ],
            "performance_analyst": [
                {"type": "kpi_dashboard", "reason": "Dashboard de KPIs atualizado", "priority": 0.9},
                {"type": "performance_trends", "reason": "Tendências de performance", "priority": 0.8},
                {"type": "goal_tracking", "reason": "Acompanhamento de metas", "priority": 0.7}
            ],
            "trend_analyst": [
                {"type": "time_series_analysis", "reason": "Análise de séries temporais", "priority": 0.9},
                {"type": "seasonal_patterns", "reason": "Padrões sazonais", "priority": 0.8},
                {"type": "forecast", "reason": "Previsões baseadas em tendências", "priority": 0.7}
            ],
            "balanced_user": [
                {"type": "compare_periods", "reason": "Comparação de períodos", "priority": 0.8},
                {"type": "segment_groups", "reason": "Segmentação por grupos", "priority": 0.7},
                {"type": "summary", "reason": "Resumo geral", "priority": 0.6}
            ]
        }
        
        return persona_mappings.get(persona, persona_mappings["balanced_user"])
    
    def _get_pattern_based_recommendations(self, profile: Dict) -> List[Dict[str, Any]]:
        """Gera recomendações baseadas em padrões de uso"""
        recommendations = []
        
        usage_patterns = profile.get("usage_patterns", {})
        most_used = usage_patterns.get("most_used_analyses", [])
        
        # Recomendar variações das análises mais usadas
        for analysis, frequency in most_used[:3]:
            if analysis == "compare_periods":
                recommendations.append({
                    "type": "compare_periods_advanced",
                    "reason": f"Versão avançada da sua análise favorita (usada {frequency}x)",
                    "priority": 0.8
                })
            elif analysis == "segment_groups":
                recommendations.append({
                    "type": "segment_groups_detailed",
                    "reason": f"Segmentação detalhada (baseado no seu uso frequente)",
                    "priority": 0.7
                })
        
        # Recomendar análises complementares
        interest_scores = profile.get("interest_scores", {})
        for category, score in sorted(interest_scores.items(), key=lambda x: x[1], reverse=True)[:2]:
            if category == "temporal_analysis":
                recommendations.append({
                    "type": "trend_analysis",
                    "reason": "Análise de tendências (baseado no seu interesse)",
                    "priority": score * 0.6
                })
            elif category == "segmentation":
                recommendations.append({
                    "type": "advanced_segmentation",
                    "reason": "Segmentação avançada (área de interesse)",
                    "priority": score * 0.6
                })
        
        return recommendations
    
    def _get_context_based_recommendations(self, profile: Dict, context: Dict) -> List[Dict[str, Any]]:
        """Gera recomendações baseadas no contexto atual"""
        recommendations = []
        
        available_columns = context.get("available_columns", [])
        data_size = context.get("data_size", 0)
        data_type = context.get("data_type", "")
        
        # Recomendações baseadas nas colunas disponíveis
        if "data" in available_columns or "timestamp" in available_columns:
            recommendations.append({
                "type": "time_series_analysis",
                "reason": "Dados temporais detectados",
                "priority": 0.8
            })
        
        if any(col in ["grupo", "categoria", "tipo"] for col in available_columns):
            recommendations.append({
                "type": "segment_groups",
                "reason": "Colunas categóricas disponíveis para segmentação",
                "priority": 0.7
            })
        
        if any(col in ["motivo", "razao"] for col in available_columns):
            recommendations.append({
                "type": "count_reasons",
                "reason": "Coluna de motivos detectada",
                "priority": 0.8
            })
        
        # Recomendações baseadas no tamanho dos dados
        if data_size > 10000:
            recommendations.append({
                "type": "sampling_analysis",
                "reason": "Dataset grande - análise com amostragem",
                "priority": 0.6
            })
        elif data_size < 100:
            recommendations.append({
                "type": "detailed_analysis",
                "reason": "Dataset pequeno - análise detalhada possível",
                "priority": 0.7
            })
        
        return recommendations
    
    def _get_collaborative_recommendations(self, user_id: str, profile: Dict) -> List[Dict[str, Any]]:
        """Gera recomendações baseadas em usuários similares"""
        recommendations = []
        
        # Encontrar usuários similares
        similar_users = self._find_similar_users(user_id, profile)
        
        for similar_user_id, similarity_score in similar_users[:3]:
            similar_profile = self.user_profiles.get(similar_user_id)
            if not similar_profile:
                continue
            
            # Recomendar análises populares entre usuários similares
            similar_patterns = similar_profile.get("usage_patterns", {})
            most_used = similar_patterns.get("most_used_analyses", [])
            
            for analysis, frequency in most_used[:2]:
                recommendations.append({
                    "type": analysis,
                    "reason": f"Popular entre usuários similares (similaridade: {similarity_score:.2f})",
                    "priority": similarity_score * 0.5
                })
        
        return recommendations
    
    def _find_similar_users(self, user_id: str, profile: Dict) -> List[Tuple[str, float]]:
        """Encontra usuários similares baseado no perfil"""
        similarities = []
        
        for other_user_id, other_profile in self.user_profiles.items():
            if other_user_id == user_id:
                continue
            
            similarity = self._calculate_profile_similarity(profile, other_profile)
            if similarity > 0.3:  # Threshold mínimo
                similarities.append((other_user_id, similarity))
        
        return sorted(similarities, key=lambda x: x[1], reverse=True)
    
    def _calculate_profile_similarity(self, profile1: Dict, profile2: Dict) -> float:
        """Calcula similaridade entre dois perfis de usuário"""
        # Similaridade de persona
        persona_sim = 1.0 if profile1.get("persona") == profile2.get("persona") else 0.0
        
        # Similaridade de interesse
        interests1 = profile1.get("interest_scores", {})
        interests2 = profile2.get("interest_scores", {})
        
        common_interests = set(interests1.keys()) & set(interests2.keys())
        if common_interests:
            interest_sim = np.mean([
                1 - abs(interests1[interest] - interests2[interest])
                for interest in common_interests
            ])
        else:
            interest_sim = 0.0
        
        # Similaridade de atividade
        activity1 = profile1.get("activity_level", "low")
        activity2 = profile2.get("activity_level", "low")
        activity_sim = 1.0 if activity1 == activity2 else 0.5
        
        # Similaridade de expertise
        expertise1 = profile1.get("expertise_level", "beginner")
        expertise2 = profile2.get("expertise_level", "beginner")
        expertise_sim = 1.0 if expertise1 == expertise2 else 0.5
        
        # Média ponderada
        total_similarity = (
            persona_sim * 0.3 +
            interest_sim * 0.4 +
            activity_sim * 0.15 +
            expertise_sim * 0.15
        )
        
        return total_similarity
    
    def _deduplicate_and_rank(self, recommendations: List[Dict]) -> List[Dict]:
        """Remove duplicatas e ordena recomendações por relevância"""
        # Agrupar por tipo
        grouped = defaultdict(list)
        for rec in recommendations:
            grouped[rec["type"]].append(rec)
        
        # Manter apenas a melhor de cada tipo
        unique_recs = []
        for rec_type, recs in grouped.items():
            best_rec = max(recs, key=lambda x: x["priority"])
            unique_recs.append(best_rec)
        
        # Ordenar por prioridade
        return sorted(unique_recs, key=lambda x: x["priority"], reverse=True)
    
    def recommend_templates(self, user_id: str, analysis_type: str = None) -> List[Dict[str, Any]]:
        """
        Recomenda templates PPTX para o usuário
        
        Args:
            user_id: ID do usuário
            analysis_type: Tipo de análise (opcional)
            
        Returns:
            Lista de templates recomendados
        """
        profile = self.user_profiles.get(user_id)
        if not profile:
            profile = self.build_user_profile(user_id)
        
        recommendations = []
        
        # Templates baseados na persona
        persona = profile.get("persona", "balanced_user")
        persona_templates = {
            "explorer_analyst": ["template_dashboard.pptx", "template_detailed.pptx"],
            "focused_specialist": ["template_executive.pptx", "template_focused.pptx"],
            "casual_user": ["template_simple.pptx", "template_summary.pptx"],
            "performance_analyst": ["template_kpi.pptx", "template_metrics.pptx"],
            "trend_analyst": ["template_trends.pptx", "template_temporal.pptx"],
            "balanced_user": ["template_relatorio.pptx", "template_general.pptx"]
        }
        
        for template in persona_templates.get(persona, ["template_relatorio.pptx"]):
            recommendations.append({
                "template": template,
                "reason": f"Recomendado para {persona}",
                "priority": 0.8
            })
        
        # Templates baseados no tipo de análise
        if analysis_type:
            analysis_templates = {
                "compare_periods": ["template_comparison.pptx", "template_temporal.pptx"],
                "segment_groups": ["template_segmentation.pptx", "template_categories.pptx"],
                "count_reasons": ["template_frequency.pptx", "template_ranking.pptx"],
                "custom_kpis": ["template_kpi.pptx", "template_metrics.pptx"]
            }
            
            for template in analysis_templates.get(analysis_type, []):
                recommendations.append({
                    "template": template,
                    "reason": f"Otimizado para {analysis_type}",
                    "priority": 0.9
                })
        
        # Templates baseados em preferências
        preferences = profile.get("preferences", {})
        preferred_templates = preferences.get("preferred_templates", [])
        
        for template, confidence in preferred_templates[:2]:
            recommendations.append({
                "template": template,
                "reason": f"Baseado no seu histórico (confiança: {confidence:.2f})",
                "priority": confidence
            })
        
        # Remover duplicatas e ordenar
        unique_templates = self._deduplicate_and_rank(recommendations)
        
        return unique_templates[:5]  # Top 5 templates
    
    def generate_proactive_alerts(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Gera alertas proativos para o usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Lista de alertas e sugestões
        """
        profile = self.user_profiles.get(user_id)
        if not profile:
            return []
        
        alerts = []
        
        # Alertas baseados na atividade
        activity_level = profile.get("activity_level", "low")
        if activity_level == "very_low":
            alerts.append({
                "type": "engagement",
                "message": "Que tal explorar uma nova análise hoje?",
                "action": "recommend_analyses",
                "priority": "medium"
            })
        
        # Alertas baseados na expertise
        expertise_level = profile.get("expertise_level", "beginner")
        if expertise_level == "beginner":
            alerts.append({
                "type": "learning",
                "message": "Dica: Experimente a análise de segmentação para insights mais profundos",
                "action": "tutorial_segmentation",
                "priority": "low"
            })
        elif expertise_level == "expert":
            alerts.append({
                "type": "advanced_feature",
                "message": "Nova funcionalidade: Análise preditiva disponível!",
                "action": "try_prediction",
                "priority": "high"
            })
        
        # Alertas baseados em padrões temporais
        usage_patterns = profile.get("usage_patterns", {})
        time_patterns = usage_patterns.get("time_patterns", {})
        
        if time_patterns.get("usage_consistency", 0) < 0.3:
            alerts.append({
                "type": "consistency",
                "message": "Análises regulares podem revelar tendências importantes",
                "action": "schedule_analysis",
                "priority": "medium"
            })
        
        return sorted(alerts, key=lambda x: {"high": 3, "medium": 2, "low": 1}[x["priority"]], reverse=True)
    
    def get_personalization_settings(self, user_id: str) -> Dict[str, Any]:
        """
        Obtém configurações de personalização para o usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Configurações personalizadas
        """
        profile = self.user_profiles.get(user_id)
        if not profile:
            profile = self.build_user_profile(user_id)
        
        settings = {
            "dashboard_layout": self._get_dashboard_layout(profile),
            "default_analyses": self._get_default_analyses(profile),
            "notification_preferences": self._get_notification_preferences(profile),
            "ui_complexity": self._get_ui_complexity(profile),
            "auto_suggestions": True,
            "proactive_alerts": True
        }
        
        return settings
    
    def _get_dashboard_layout(self, profile: Dict) -> str:
        """Determina layout ideal do dashboard"""
        persona = profile.get("persona", "balanced_user")
        
        layout_mapping = {
            "explorer_analyst": "detailed",
            "focused_specialist": "focused",
            "casual_user": "simple",
            "performance_analyst": "metrics_heavy",
            "trend_analyst": "temporal_focused",
            "balanced_user": "balanced"
        }
        
        return layout_mapping.get(persona, "balanced")
    
    def _get_default_analyses(self, profile: Dict) -> List[str]:
        """Determina análises padrão para o usuário"""
        usage_patterns = profile.get("usage_patterns", {})
        most_used = usage_patterns.get("most_used_analyses", [])
        
        if most_used:
            return [analysis for analysis, _ in most_used[:3]]
        else:
            persona = profile.get("persona", "balanced_user")
            defaults = {
                "explorer_analyst": ["custom_kpis", "trend_analysis", "segment_groups"],
                "focused_specialist": ["compare_periods", "custom_kpis"],
                "casual_user": ["summary", "compare_periods"],
                "performance_analyst": ["custom_kpis", "performance_trends"],
                "trend_analyst": ["compare_periods", "trend_analysis"],
                "balanced_user": ["compare_periods", "segment_groups", "summary"]
            }
            return defaults.get(persona, ["compare_periods", "summary"])
    
    def _get_notification_preferences(self, profile: Dict) -> Dict[str, bool]:
        """Determina preferências de notificação"""
        activity_level = profile.get("activity_level", "low")
        expertise_level = profile.get("expertise_level", "beginner")
        
        if activity_level == "high":
            return {
                "new_features": True,
                "analysis_suggestions": True,
                "performance_alerts": True,
                "weekly_summary": False  # Usuários ativos não precisam de resumo
            }
        elif expertise_level == "beginner":
            return {
                "new_features": True,
                "analysis_suggestions": True,
                "performance_alerts": False,
                "weekly_summary": True,
                "tips_and_tutorials": True
            }
        else:
            return {
                "new_features": True,
                "analysis_suggestions": False,
                "performance_alerts": True,
                "weekly_summary": True
            }
    
    def _get_ui_complexity(self, profile: Dict) -> str:
        """Determina nível de complexidade da UI"""
        expertise_level = profile.get("expertise_level", "beginner")
        
        complexity_mapping = {
            "beginner": "simple",
            "intermediate": "standard",
            "advanced": "detailed",
            "expert": "full"
        }
        
        return complexity_mapping.get(expertise_level, "standard")


# Instância global do sistema de recomendações
recommendation_engine = RecommendationEngine()

