"""
NLP Engine para Processamento de Linguagem Natural
Interpreta queries em português e mapeia para análises específicas
"""

import re
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import pandas as pd

# Imports opcionais - não quebram se não estiverem disponíveis
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ openai não disponível - funcionalidades avançadas de NLP desabilitadas")

try:
    from loguru import logger
    LOGURU_AVAILABLE = True
except ImportError:
    LOGURU_AVAILABLE = False
    import logging
    logger = logging.getLogger(__name__)


class NLPEngine:
    """Engine de processamento de linguagem natural para Analytics Agent"""
    
    def __init__(self):
        """Inicializa o NLP Engine"""
        self.intent_patterns = self._load_intent_patterns()
        self.entity_extractors = self._load_entity_extractors()
        self.analysis_mappings = self._load_analysis_mappings()
        
        if LOGURU_AVAILABLE:
            logger.info("NLPEngine inicializado com sucesso")
        else:
            print("✅ NLPEngine inicializado com sucesso")
    
    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """Carrega padrões de intenção para classificação"""
        return {
            "compare_periods": [
                r"compar\w*.*período",
                r"compar\w*.*ano",
                r"compar\w*.*mês",
                r"diferença.*entre",
                r"evolução.*tempo",
                r"crescimento.*período",
                r"variação.*temporal",
                r"antes.*depois",
                r"(\d{4}).*vs.*(\d{4})",
                r"(\d{4}).*contra.*(\d{4})"
            ],
            "segment_groups": [
                r"segment\w*",
                r"grup\w*.*por",
                r"categori\w*",
                r"divid\w*.*grupo",
                r"analis\w*.*categoria",
                r"quebr\w*.*por",
                r"classificar.*por",
                r"agrupar.*por"
            ],
            "count_reasons": [
                r"cont\w*.*motivo",
                r"frequência.*motivo",
                r"quantos.*motivo",
                r"principal.*motivo",
                r"mais.*comum",
                r"ranking.*motivo",
                r"top.*motivo",
                r"motivos.*mais"
            ],
            "custom_kpis": [
                r"kpi",
                r"indicador",
                r"métrica",
                r"performance",
                r"desempenho",
                r"resultado",
                r"média",
                r"total",
                r"soma",
                r"calcul\w*"
            ],
            "trend_analysis": [
                r"tendência",
                r"trend",
                r"padrão.*tempo",
                r"evolução",
                r"comportamento.*tempo",
                r"série.*temporal",
                r"histórico",
                r"ao.*longo.*tempo"
            ],
            "summary": [
                r"resumo",
                r"sumário",
                r"visão.*geral",
                r"overview",
                r"panorama",
                r"síntese",
                r"consolidado"
            ]
        }
    
    def _load_entity_extractors(self) -> Dict[str, str]:
        """Carrega padrões para extração de entidades"""
        return {
            "years": r"(\d{4})",
            "months": r"(janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)",
            "periods": r"(trimestre|semestre|bimestre|quinzena|semana)",
            "metrics": r"(vendas|receita|lucro|prejuízo|faturamento|ticket|valor|quantidade|volume)",
            "columns": r"(grupo|categoria|tipo|perfil|segmento|canal|produto|região)",
            "comparisons": r"(maior|menor|melhor|pior|superior|inferior|acima|abaixo)",
            "aggregations": r"(total|soma|média|mediana|máximo|mínimo|contagem)"
        }
    
    def _load_analysis_mappings(self) -> Dict[str, Dict]:
        """Carrega mapeamentos de análises disponíveis"""
        return {
            "compare_periods": {
                "function": "compare_periods",
                "required_params": ["period1", "period2"],
                "optional_params": ["metrics", "date_column"],
                "description": "Compara métricas entre dois períodos diferentes"
            },
            "segment_groups": {
                "function": "segment_by_groups",
                "required_params": ["group_columns"],
                "optional_params": ["metrics", "aggregation_method"],
                "description": "Segmenta dados por grupos/categorias"
            },
            "count_reasons": {
                "function": "count_contact_reasons",
                "required_params": ["reason_column"],
                "optional_params": ["top_n", "include_percentage"],
                "description": "Conta frequência de motivos/razões"
            },
            "custom_kpis": {
                "function": "calculate_custom_kpis",
                "required_params": ["kpi_definitions"],
                "optional_params": ["group_by"],
                "description": "Calcula KPIs personalizados"
            }
        }
    
    def process_query(self, query: str, context: Dict = None) -> Dict[str, Any]:
        """
        Processa uma query em linguagem natural
        
        Args:
            query: Query em português
            context: Contexto adicional (dados disponíveis, usuário, etc.)
            
        Returns:
            Dicionário com intenção, entidades e parâmetros
        """
        logger.info(f"Processando query: {query}")
        
        # Normalizar query
        normalized_query = self._normalize_query(query)
        
        # Classificar intenção
        intent = self._classify_intent(normalized_query)
        
        # Extrair entidades
        entities = self._extract_entities(normalized_query)
        
        # Gerar parâmetros para análise
        analysis_params = self._generate_analysis_params(intent, entities, context)
        
        # Gerar resposta contextualizada
        response = self._generate_response(intent, entities, analysis_params)
        
        result = {
            "intent": intent,
            "entities": entities,
            "analysis_params": analysis_params,
            "response": response,
            "confidence": self._calculate_confidence(intent, entities),
            "suggestions": self._generate_suggestions(intent, entities, context)
        }
        
        logger.info(f"Query processada - Intent: {intent}, Confidence: {result['confidence']:.2f}")
        return result
    
    def _normalize_query(self, query: str) -> str:
        """Normaliza a query para processamento"""
        # Converter para minúsculas
        normalized = query.lower()
        
        # Remover acentos
        replacements = {
            'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a',
            'é': 'e', 'ê': 'e',
            'í': 'i', 'î': 'i',
            'ó': 'o', 'ô': 'o', 'õ': 'o',
            'ú': 'u', 'û': 'u',
            'ç': 'c'
        }
        
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        
        # Remover pontuação extra
        normalized = re.sub(r'[^\w\s]', ' ', normalized)
        
        # Remover espaços extras
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def _classify_intent(self, query: str) -> str:
        """Classifica a intenção da query"""
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, query, re.IGNORECASE))
                score += matches
            
            if score > 0:
                intent_scores[intent] = score
        
        if not intent_scores:
            return "unknown"
        
        # Retornar intenção com maior score
        return max(intent_scores, key=intent_scores.get)
    
    def _extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extrai entidades da query"""
        entities = {}
        
        for entity_type, pattern in self.entity_extractors.items():
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                entities[entity_type] = matches
        
        return entities
    
    def _generate_analysis_params(self, intent: str, entities: Dict, context: Dict = None) -> Dict[str, Any]:
        """Gera parâmetros para a análise baseado na intenção e entidades"""
        if intent not in self.analysis_mappings:
            return {}
        
        mapping = self.analysis_mappings[intent]
        params = {}
        
        if intent == "compare_periods":
            # Extrair períodos
            years = entities.get("years", [])
            if len(years) >= 2:
                params["period1"] = years[0]
                params["period2"] = years[1]
            else:
                # Usar anos padrão se não especificados
                current_year = datetime.now().year
                params["period1"] = str(current_year - 1)
                params["period2"] = str(current_year)
            
            # Extrair métricas
            metrics = entities.get("metrics", ["total", "media"])
            params["metrics"] = metrics
        
        elif intent == "segment_groups":
            # Extrair colunas de agrupamento
            columns = entities.get("columns", [])
            if not columns and context and "available_columns" in context:
                # Sugerir colunas categóricas disponíveis
                categorical_cols = [col for col in context["available_columns"] 
                                  if col.lower() in ["grupo", "categoria", "tipo", "perfil", "segmento"]]
                columns = categorical_cols[:2]  # Máximo 2 colunas
            
            params["group_columns"] = columns or ["grupo"]
            
            # Extrair métricas
            metrics = entities.get("metrics", ["total", "count"])
            params["metrics"] = metrics
        
        elif intent == "count_reasons":
            # Determinar coluna de motivos
            reason_col = "motivo"
            if context and "available_columns" in context:
                for col in context["available_columns"]:
                    if "motivo" in col.lower() or "razao" in col.lower():
                        reason_col = col
                        break
            
            params["reason_column"] = reason_col
        
        elif intent == "custom_kpis":
            # Gerar KPIs baseados nas métricas mencionadas
            metrics = entities.get("metrics", [])
            aggregations = entities.get("aggregations", [])
            
            kpi_definitions = {}
            for metric in metrics:
                for agg in aggregations:
                    if agg in ["total", "soma"]:
                        kpi_definitions[f"{metric}_{agg}"] = f"{metric}.sum()"
                    elif agg in ["media"]:
                        kpi_definitions[f"{metric}_{agg}"] = f"{metric}.mean()"
                    elif agg in ["maximo"]:
                        kpi_definitions[f"{metric}_{agg}"] = f"{metric}.max()"
                    elif agg in ["minimo"]:
                        kpi_definitions[f"{metric}_{agg}"] = f"{metric}.min()"
            
            if not kpi_definitions:
                # KPIs padrão
                kpi_definitions = {
                    "total_geral": "valor.sum()",
                    "media_geral": "valor.mean()",
                    "contagem": "valor.count()"
                }
            
            params["kpi_definitions"] = kpi_definitions
        
        return params
    
    def _generate_response(self, intent: str, entities: Dict, params: Dict) -> str:
        """Gera resposta contextualizada para o usuário"""
        if intent == "compare_periods":
            period1 = params.get("period1", "período 1")
            period2 = params.get("period2", "período 2")
            return f"Vou comparar os dados entre {period1} e {period2}. Analisarei as métricas solicitadas e mostrarei a evolução entre os períodos."
        
        elif intent == "segment_groups":
            columns = params.get("group_columns", [])
            if columns:
                cols_text = " e ".join(columns)
                return f"Vou segmentar os dados por {cols_text} e mostrar as métricas para cada grupo."
            else:
                return "Vou segmentar os dados por grupos e mostrar as métricas para cada categoria."
        
        elif intent == "count_reasons":
            column = params.get("reason_column", "motivos")
            return f"Vou analisar a frequência dos {column} e mostrar quais são os mais comuns."
        
        elif intent == "custom_kpis":
            kpis = list(params.get("kpi_definitions", {}).keys())
            if kpis:
                kpis_text = ", ".join(kpis)
                return f"Vou calcular os seguintes KPIs: {kpis_text}."
            else:
                return "Vou calcular os KPIs personalizados solicitados."
        
        else:
            return "Vou processar sua solicitação e gerar a análise correspondente."
    
    def _calculate_confidence(self, intent: str, entities: Dict) -> float:
        """Calcula score de confiança da interpretação"""
        base_confidence = 0.5
        
        # Aumentar confiança se intenção foi identificada
        if intent != "unknown":
            base_confidence += 0.3
        
        # Aumentar confiança baseado no número de entidades extraídas
        entity_count = sum(len(values) for values in entities.values())
        entity_bonus = min(entity_count * 0.05, 0.2)
        base_confidence += entity_bonus
        
        return min(base_confidence, 1.0)
    
    def _generate_suggestions(self, intent: str, entities: Dict, context: Dict = None) -> List[str]:
        """Gera sugestões para melhorar a query"""
        suggestions = []
        
        if intent == "unknown":
            suggestions.append("Tente ser mais específico sobre o tipo de análise desejada")
            suggestions.append("Exemplos: 'comparar vendas de 2024 vs 2025', 'segmentar por grupo', 'contar motivos'")
        
        elif intent == "compare_periods":
            if not entities.get("years"):
                suggestions.append("Especifique os períodos a comparar (ex: 2024 vs 2025)")
            if not entities.get("metrics"):
                suggestions.append("Mencione quais métricas analisar (ex: vendas, receita, quantidade)")
        
        elif intent == "segment_groups":
            if not entities.get("columns"):
                suggestions.append("Especifique por quais colunas agrupar (ex: por grupo, por categoria)")
        
        return suggestions
    
    def interpret_with_ai(self, query: str, context: Dict = None) -> Dict[str, Any]:
        """
        Usa IA (OpenAI) para interpretação mais avançada
        
        Args:
            query: Query em linguagem natural
            context: Contexto adicional
            
        Returns:
            Interpretação avançada da query
        """
        try:
            # Preparar contexto para a IA
            available_analyses = list(self.analysis_mappings.keys())
            available_columns = context.get("available_columns", []) if context else []
            
            prompt = f"""
            Você é um assistente especializado em análise de dados. Interprete a seguinte solicitação em português e mapeie para uma análise específica.

            Solicitação: "{query}"

            Análises disponíveis:
            - compare_periods: Compara métricas entre períodos
            - segment_groups: Segmenta dados por grupos/categorias  
            - count_reasons: Conta frequência de motivos
            - custom_kpis: Calcula KPIs personalizados

            Colunas disponíveis: {available_columns}

            Responda em JSON com:
            {{
                "intent": "tipo_de_analise",
                "parameters": {{"parametro": "valor"}},
                "explanation": "explicação da interpretação",
                "confidence": 0.95
            }}
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info(f"Interpretação IA concluída - Intent: {result.get('intent')}")
            return result
            
        except Exception as e:
            logger.warning(f"Erro na interpretação IA: {e}")
            # Fallback para interpretação baseada em regras
            return self.process_query(query, context)
    
    def generate_natural_response(self, analysis_result: Dict, query: str) -> str:
        """
        Gera resposta em linguagem natural baseada no resultado da análise
        
        Args:
            analysis_result: Resultado da análise
            query: Query original do usuário
            
        Returns:
            Resposta em linguagem natural
        """
        try:
            prompt = f"""
            Gere uma resposta em português natural e amigável baseada no resultado da análise de dados.

            Query original: "{query}"
            
            Resultado da análise: {json.dumps(analysis_result, indent=2)}

            A resposta deve:
            - Ser em português brasileiro
            - Destacar os principais insights
            - Ser clara e objetiva
            - Incluir números relevantes
            - Sugerir próximos passos se apropriado

            Resposta:
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            natural_response = response.choices[0].message.content
            logger.info("Resposta natural gerada com sucesso")
            return natural_response
            
        except Exception as e:
            logger.warning(f"Erro na geração de resposta natural: {e}")
            return self._generate_fallback_response(analysis_result)
    
    def _generate_fallback_response(self, analysis_result: Dict) -> str:
        """Gera resposta de fallback quando IA não está disponível"""
        if "period1" in analysis_result and "period2" in analysis_result:
            return f"Análise de comparação concluída. Comparei os dados entre os períodos solicitados."
        elif "segments" in analysis_result:
            segments_count = len(analysis_result.get("segments", {}))
            return f"Segmentação concluída. Encontrei {segments_count} grupos diferentes nos dados."
        elif "reasons" in analysis_result:
            reasons_count = len(analysis_result.get("reasons", {}))
            return f"Análise de motivos concluída. Identifiquei {reasons_count} motivos diferentes."
        else:
            return "Análise concluída com sucesso. Os resultados estão disponíveis."
    
    def extract_data_requirements(self, query: str) -> Dict[str, Any]:
        """
        Extrai requisitos de dados da query
        
        Args:
            query: Query em linguagem natural
            
        Returns:
            Requisitos de dados necessários
        """
        requirements = {
            "required_columns": [],
            "date_columns": [],
            "numeric_columns": [],
            "categorical_columns": [],
            "filters": [],
            "time_range": None
        }
        
        # Extrair colunas mencionadas
        entities = self._extract_entities(query)
        
        if "columns" in entities:
            requirements["categorical_columns"].extend(entities["columns"])
        
        if "metrics" in entities:
            requirements["numeric_columns"].extend(entities["metrics"])
        
        if "years" in entities:
            requirements["time_range"] = {
                "start": min(entities["years"]),
                "end": max(entities["years"])
            }
        
        # Detectar necessidade de coluna de data
        date_keywords = ["período", "tempo", "ano", "mês", "data", "quando"]
        if any(keyword in query.lower() for keyword in date_keywords):
            requirements["date_columns"].append("data")
        
        return requirements


# Instância global do NLP Engine
nlp_engine = NLPEngine()

