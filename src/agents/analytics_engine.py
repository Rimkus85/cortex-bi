"""
Analytics Engine - Motor de Análise de Dados

Este módulo é responsável por realizar análises complexas nos dados carregados:
- Comparação de períodos (ex: 2024 vs 2025)
- Segmentação por grupos, ilhas, perfis
- Contabilização de motivos de contato
- Cálculo de KPIs customizáveis
- Validação de resultados

Instruções para personalização:
1. Ajuste as funções de análise conforme suas necessidades específicas
2. Adicione novos KPIs na função calculate_custom_kpis()
3. Modifique as regras de segmentação conforme necessário
4. Customize as validações de resultado
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime, timedelta
from loguru import logger
import json
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')


class AnalyticsEngine:
    """
    Motor de análise de dados com funcionalidades avançadas para:
    - Análise temporal e comparação de períodos
    - Segmentação e agrupamento de dados
    - Cálculo de KPIs e métricas customizáveis
    - Validação e qualidade dos resultados
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa o AnalyticsEngine com configurações opcionais.
        
        Args:
            config (Dict, optional): Configurações personalizadas
        """
        self.config = config or {}
        
        # Configurações padrão - EDITE AQUI conforme necessário
        self.default_config = {
            'date_column': 'data',  # Nome padrão da coluna de data
            'value_column': 'valor',  # Nome padrão da coluna de valor
            'group_column': 'grupo',  # Nome padrão da coluna de grupo
            'profile_column': 'perfil',  # Nome padrão da coluna de perfil
            'reason_column': 'motivo',  # Nome padrão da coluna de motivo
            'year_column': 'ano',  # Nome padrão da coluna de ano
            'decimal_places': 2,  # Casas decimais para resultados
            'confidence_threshold': 0.95  # Limite de confiança para validações
        }
        
        # Mescla configurações
        self.settings = {**self.default_config, **self.config}
        
        logger.info("AnalyticsEngine inicializado com sucesso")
    
    def compare_periods(self, df: pd.DataFrame, period1: Union[int, str], period2: Union[int, str], 
                       metrics: Optional[List[str]] = None) -> Dict:
        """
        Compara métricas entre dois períodos.
        
        Args:
            df (pd.DataFrame): DataFrame com os dados
            period1 (int|str): Primeiro período (ex: 2024)
            period2 (int|str): Segundo período (ex: 2025)
            metrics (List[str], optional): Lista de métricas para calcular
            
        Returns:
            Dict: Resultado da comparação entre períodos
            
        Exemplo de uso:
            result = engine.compare_periods(df, 2024, 2025, ['total', 'media', 'crescimento'])
        """
        try:
            logger.info(f"Comparando períodos: {period1} vs {period2}")
            
            # Identifica coluna de período (ano, data, etc.)
            period_col = self._identify_period_column(df)
            value_col = self._identify_value_column(df)
            
            # Filtra dados por período
            df_period1 = self._filter_by_period(df, period_col, period1)
            df_period2 = self._filter_by_period(df, period_col, period2)
            
            # Métricas padrão se não especificadas
            if metrics is None:
                metrics = ['total', 'media', 'mediana', 'crescimento', 'variacao_percentual']
            
            # Calcula métricas para cada período
            metrics_p1 = self._calculate_period_metrics(df_period1, value_col, metrics)
            metrics_p2 = self._calculate_period_metrics(df_period2, value_col, metrics)
            
            # Calcula comparações
            comparison = self._calculate_comparison_metrics(metrics_p1, metrics_p2)
            
            result = {
                'period1': {
                    'name': str(period1),
                    'records': len(df_period1),
                    'metrics': metrics_p1
                },
                'period2': {
                    'name': str(period2),
                    'records': len(df_period2),
                    'metrics': metrics_p2
                },
                'comparison': comparison,
                'analysis_date': datetime.now().isoformat(),
                'data_quality': self._assess_data_quality(df_period1, df_period2)
            }
            
            logger.info(f"Comparação concluída: {len(df_period1)} vs {len(df_period2)} registros")
            return result
            
        except Exception as e:
            logger.error(f"Erro na comparação de períodos: {str(e)}")
            raise
    
    def segment_by_groups(self, df: pd.DataFrame, group_columns: List[str], 
                         metrics: Optional[List[str]] = None) -> Dict:
        """
        Segmenta dados por grupos e calcula métricas para cada segmento.
        
        Args:
            df (pd.DataFrame): DataFrame com os dados
            group_columns (List[str]): Colunas para agrupamento
            metrics (List[str], optional): Métricas para calcular
            
        Returns:
            Dict: Resultado da segmentação por grupos
            
        Exemplo de uso:
            result = engine.segment_by_groups(df, ['grupo', 'perfil'], ['total', 'media'])
        """
        try:
            logger.info(f"Segmentando por grupos: {group_columns}")
            
            # Valida se as colunas existem
            missing_cols = [col for col in group_columns if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Colunas não encontradas: {missing_cols}")
            
            value_col = self._identify_value_column(df)
            
            # Métricas padrão se não especificadas
            if metrics is None:
                metrics = ['total', 'media', 'mediana', 'count', 'desvio_padrao']
            
            # Agrupa dados
            grouped = df.groupby(group_columns)
            
            segments = {}
            for group_key, group_data in grouped:
                # Converte chave do grupo para string se necessário
                if isinstance(group_key, tuple):
                    segment_name = ' | '.join(str(k) for k in group_key)
                else:
                    segment_name = str(group_key)
                
                # Calcula métricas para o segmento
                segment_metrics = self._calculate_period_metrics(group_data, value_col, metrics)
                
                segments[segment_name] = {
                    'records': len(group_data),
                    'metrics': segment_metrics,
                    'percentage_of_total': round((len(group_data) / len(df)) * 100, 2)
                }
            
            # Calcula estatísticas gerais
            total_segments = len(segments)
            largest_segment = max(segments.items(), key=lambda x: x[1]['records'])
            smallest_segment = min(segments.items(), key=lambda x: x[1]['records'])
            
            result = {
                'segments': segments,
                'summary': {
                    'total_segments': total_segments,
                    'total_records': len(df),
                    'largest_segment': {
                        'name': largest_segment[0],
                        'records': largest_segment[1]['records']
                    },
                    'smallest_segment': {
                        'name': smallest_segment[0],
                        'records': smallest_segment[1]['records']
                    }
                },
                'group_columns': group_columns,
                'analysis_date': datetime.now().isoformat()
            }
            
            logger.info(f"Segmentação concluída: {total_segments} segmentos")
            return result
            
        except Exception as e:
            logger.error(f"Erro na segmentação por grupos: {str(e)}")
            raise
    
    def count_contact_reasons(self, df: pd.DataFrame, reason_column: Optional[str] = None) -> Dict:
        """
        Contabiliza motivos de contato e calcula estatísticas.
        
        Args:
            df (pd.DataFrame): DataFrame com os dados
            reason_column (str, optional): Nome da coluna de motivos
            
        Returns:
            Dict: Contabilização de motivos de contato
            
        Exemplo de uso:
            result = engine.count_contact_reasons(df, 'motivo_contato')
        """
        try:
            logger.info("Contabilizando motivos de contato")
            
            # Identifica coluna de motivos
            if reason_column is None:
                reason_column = self.settings['reason_column']
            
            if reason_column not in df.columns:
                raise ValueError(f"Coluna de motivos '{reason_column}' não encontrada")
            
            # Remove valores nulos
            df_clean = df[df[reason_column].notna()].copy()
            
            # Contabiliza motivos
            reason_counts = df_clean[reason_column].value_counts()
            reason_percentages = df_clean[reason_column].value_counts(normalize=True) * 100
            
            # Prepara resultado detalhado
            reasons_detail = {}
            for reason, count in reason_counts.items():
                reasons_detail[str(reason)] = {
                    'count': int(count),
                    'percentage': round(reason_percentages[reason], 2),
                    'rank': int(reason_counts.rank(method='dense', ascending=False)[reason])
                }
            
            # Estatísticas gerais
            total_records = len(df_clean)
            unique_reasons = len(reason_counts)
            most_common = reason_counts.index[0] if len(reason_counts) > 0 else None
            least_common = reason_counts.index[-1] if len(reason_counts) > 0 else None
            
            result = {
                'reasons': reasons_detail,
                'summary': {
                    'total_records': total_records,
                    'unique_reasons': unique_reasons,
                    'most_common_reason': {
                        'name': str(most_common) if most_common else None,
                        'count': int(reason_counts.iloc[0]) if len(reason_counts) > 0 else 0,
                        'percentage': round(reason_percentages.iloc[0], 2) if len(reason_counts) > 0 else 0
                    },
                    'least_common_reason': {
                        'name': str(least_common) if least_common else None,
                        'count': int(reason_counts.iloc[-1]) if len(reason_counts) > 0 else 0,
                        'percentage': round(reason_percentages.iloc[-1], 2) if len(reason_counts) > 0 else 0
                    }
                },
                'reason_column': reason_column,
                'analysis_date': datetime.now().isoformat()
            }
            
            logger.info(f"Contabilização concluída: {unique_reasons} motivos únicos")
            return result
            
        except Exception as e:
            logger.error(f"Erro na contabilização de motivos: {str(e)}")
            raise
    
    def calculate_custom_kpis(self, df: pd.DataFrame, kpi_definitions: Dict) -> Dict:
        """
        Calcula KPIs customizáveis conforme definições fornecidas.
        
        Args:
            df (pd.DataFrame): DataFrame com os dados
            kpi_definitions (Dict): Definições dos KPIs a calcular
            
        Returns:
            Dict: Resultado dos KPIs calculados
            
        Exemplo de uso:
            kpis = {
                'taxa_conversao': {'numerator': 'vendas', 'denominator': 'leads', 'format': 'percentage'},
                'ticket_medio': {'column': 'valor', 'operation': 'mean', 'format': 'currency'}
            }
            result = engine.calculate_custom_kpis(df, kpis)
            
        EDITE AQUI para adicionar novos tipos de KPI:
        - Adicione novas operações na função _calculate_kpi_value()
        - Adicione novos formatos na função _format_kpi_value()
        """
        try:
            logger.info(f"Calculando {len(kpi_definitions)} KPIs customizados")
            
            kpi_results = {}
            
            for kpi_name, kpi_config in kpi_definitions.items():
                try:
                    # Calcula valor do KPI
                    kpi_value = self._calculate_kpi_value(df, kpi_config)
                    
                    # Formata valor conforme especificado
                    formatted_value = self._format_kpi_value(kpi_value, kpi_config.get('format', 'number'))
                    
                    # Calcula tendência se especificado
                    trend = None
                    if 'trend_column' in kpi_config:
                        trend = self._calculate_trend(df, kpi_config)
                    
                    kpi_results[kpi_name] = {
                        'value': kpi_value,
                        'formatted_value': formatted_value,
                        'trend': trend,
                        'calculation_method': kpi_config.get('operation', 'custom'),
                        'data_points': len(df),
                        'confidence': self._calculate_kpi_confidence(df, kpi_config)
                    }
                    
                except Exception as e:
                    logger.warning(f"Erro ao calcular KPI '{kpi_name}': {str(e)}")
                    kpi_results[kpi_name] = {
                        'value': None,
                        'formatted_value': 'Erro no cálculo',
                        'error': str(e)
                    }
            
            result = {
                'kpis': kpi_results,
                'summary': {
                    'total_kpis': len(kpi_definitions),
                    'successful_calculations': len([k for k in kpi_results.values() if k.get('value') is not None]),
                    'failed_calculations': len([k for k in kpi_results.values() if k.get('value') is None])
                },
                'analysis_date': datetime.now().isoformat()
            }
            
            logger.info(f"KPIs calculados: {result['summary']['successful_calculations']}/{result['summary']['total_kpis']}")
            return result
            
        except Exception as e:
            logger.error(f"Erro no cálculo de KPIs: {str(e)}")
            raise
    
    def validate_results(self, results: Dict, validation_rules: Optional[Dict] = None) -> Dict:
        """
        Valida resultados de análise conforme regras especificadas.
        
        Args:
            results (Dict): Resultados da análise para validar
            validation_rules (Dict, optional): Regras de validação personalizadas
            
        Returns:
            Dict: Resultado da validação
            
        EDITE AQUI para adicionar suas próprias regras de validação:
        - Verificação de valores dentro de intervalos esperados
        - Validação de consistência entre métricas
        - Verificação de qualidade dos dados
        """
        try:
            logger.info("Validando resultados da análise")
            
            validation_result = {
                'is_valid': True,
                'errors': [],
                'warnings': [],
                'quality_score': 0,
                'recommendations': []
            }
            
            # Regras padrão de validação
            default_rules = {
                'min_data_points': 10,
                'max_null_percentage': 20,
                'min_confidence': 0.8,
                'check_outliers': True
            }
            
            # Mescla regras padrão com personalizadas
            rules = {**default_rules, **(validation_rules or {})}
            
            # Validações específicas por tipo de resultado
            if 'period1' in results and 'period2' in results:
                self._validate_period_comparison(results, rules, validation_result)
            
            if 'segments' in results:
                self._validate_segmentation(results, rules, validation_result)
            
            if 'kpis' in results:
                self._validate_kpis(results, rules, validation_result)
            
            # Calcula score de qualidade
            validation_result['quality_score'] = self._calculate_quality_score(validation_result)
            
            # Gera recomendações
            validation_result['recommendations'] = self._generate_recommendations(validation_result)
            
            logger.info(f"Validação concluída: {'✓ Válido' if validation_result['is_valid'] else '✗ Inválido'}")
            return validation_result
            
        except Exception as e:
            logger.error(f"Erro na validação: {str(e)}")
            return {'is_valid': False, 'errors': [str(e)], 'warnings': [], 'quality_score': 0}
    
    # Métodos auxiliares privados
    
    def _identify_period_column(self, df: pd.DataFrame) -> str:
        """Identifica automaticamente a coluna de período."""
        possible_names = [self.settings['year_column'], self.settings['date_column'], 'ano', 'data', 'year', 'date', 'periodo']
        
        for col_name in possible_names:
            if col_name in df.columns:
                return col_name
        
        # Se não encontrar, usa a primeira coluna que parece ser de data/ano
        for col in df.columns:
            if df[col].dtype in ['int64', 'datetime64[ns]'] or 'ano' in col.lower() or 'year' in col.lower():
                return col
        
        raise ValueError("Não foi possível identificar a coluna de período")
    
    def _identify_value_column(self, df: pd.DataFrame) -> str:
        """Identifica automaticamente a coluna de valores."""
        possible_names = [self.settings['value_column'], 'valor', 'value', 'amount', 'quantidade', 'total']
        
        for col_name in possible_names:
            if col_name in df.columns:
                return col_name
        
        # Se não encontrar, usa a primeira coluna numérica
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            return numeric_cols[0]
        
        raise ValueError("Não foi possível identificar a coluna de valores")
    
    def _filter_by_period(self, df: pd.DataFrame, period_col: str, period: Union[int, str]) -> pd.DataFrame:
        """Filtra DataFrame por período específico."""
        if df[period_col].dtype == 'datetime64[ns]':
            # Se for datetime, extrai o ano
            return df[df[period_col].dt.year == int(period)]
        else:
            # Se for numérico ou string, compara diretamente
            return df[df[period_col] == period]
    
    def _calculate_period_metrics(self, df: pd.DataFrame, value_col: str, metrics: List[str]) -> Dict:
        """Calcula métricas para um período específico."""
        if df.empty or value_col not in df.columns:
            return {metric: 0 for metric in metrics}
        
        values = df[value_col].dropna()
        
        result = {}
        for metric in metrics:
            if metric == 'total':
                result[metric] = round(values.sum(), self.settings['decimal_places'])
            elif metric == 'media':
                result[metric] = round(values.mean(), self.settings['decimal_places'])
            elif metric == 'mediana':
                result[metric] = round(values.median(), self.settings['decimal_places'])
            elif metric == 'count':
                result[metric] = len(values)
            elif metric == 'desvio_padrao':
                result[metric] = round(values.std(), self.settings['decimal_places'])
            elif metric == 'minimo':
                result[metric] = round(values.min(), self.settings['decimal_places'])
            elif metric == 'maximo':
                result[metric] = round(values.max(), self.settings['decimal_places'])
            else:
                result[metric] = 0
        
        return result
    
    def _calculate_comparison_metrics(self, metrics_p1: Dict, metrics_p2: Dict) -> Dict:
        """Calcula métricas de comparação entre períodos."""
        comparison = {}
        
        for metric in metrics_p1.keys():
            if metric in metrics_p2:
                val1 = metrics_p1[metric]
                val2 = metrics_p2[metric]
                
                if val1 != 0:
                    growth = ((val2 - val1) / val1) * 100
                    comparison[f'{metric}_crescimento'] = round(growth, 2)
                
                comparison[f'{metric}_diferenca'] = round(val2 - val1, self.settings['decimal_places'])
        
        return comparison
    
    def _calculate_kpi_value(self, df: pd.DataFrame, kpi_config: Dict) -> float:
        """Calcula valor de um KPI específico."""
        operation = kpi_config.get('operation', 'sum')
        
        if 'numerator' in kpi_config and 'denominator' in kpi_config:
            # KPI de razão
            num_col = kpi_config['numerator']
            den_col = kpi_config['denominator']
            
            if num_col not in df.columns or den_col not in df.columns:
                raise ValueError(f"Colunas não encontradas: {num_col}, {den_col}")
            
            numerator = df[num_col].sum()
            denominator = df[den_col].sum()
            
            if denominator == 0:
                return 0
            
            return numerator / denominator
        
        elif 'column' in kpi_config:
            # KPI de coluna única
            col = kpi_config['column']
            
            if col not in df.columns:
                raise ValueError(f"Coluna não encontrada: {col}")
            
            values = df[col].dropna()
            
            if operation == 'sum':
                return values.sum()
            elif operation == 'mean':
                return values.mean()
            elif operation == 'median':
                return values.median()
            elif operation == 'count':
                return len(values)
            elif operation == 'std':
                return values.std()
            else:
                raise ValueError(f"Operação não suportada: {operation}")
        
        else:
            raise ValueError("Configuração de KPI inválida")
    
    def _format_kpi_value(self, value: float, format_type: str) -> str:
        """Formata valor do KPI conforme tipo especificado."""
        if value is None or np.isnan(value):
            return "N/A"
        
        if format_type == 'percentage':
            return f"{value * 100:.2f}%"
        elif format_type == 'currency':
            return f"R$ {value:,.2f}"
        elif format_type == 'integer':
            return f"{int(value):,}"
        else:  # 'number'
            return f"{value:.2f}"
    
    def _calculate_trend(self, df: pd.DataFrame, kpi_config: Dict) -> str:
        """Calcula tendência do KPI ao longo do tempo."""
        # Implementação simplificada - pode ser expandida
        trend_col = kpi_config.get('trend_column')
        value_col = kpi_config.get('column')
        
        if not trend_col or not value_col or trend_col not in df.columns or value_col not in df.columns:
            return "unknown"
        
        # Ordena por coluna de tendência e calcula correlação
        df_sorted = df.sort_values(trend_col)
        correlation = df_sorted[trend_col].corr(df_sorted[value_col])
        
        if correlation > 0.1:
            return "increasing"
        elif correlation < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_kpi_confidence(self, df: pd.DataFrame, kpi_config: Dict) -> float:
        """Calcula nível de confiança do KPI."""
        # Implementação simplificada baseada no tamanho da amostra
        sample_size = len(df)
        
        if sample_size >= 1000:
            return 0.95
        elif sample_size >= 100:
            return 0.85
        elif sample_size >= 30:
            return 0.75
        else:
            return 0.60
    
    def _assess_data_quality(self, df1: pd.DataFrame, df2: pd.DataFrame) -> Dict:
        """Avalia qualidade dos dados para comparação."""
        return {
            'period1_completeness': round((1 - df1.isnull().sum().sum() / (len(df1) * len(df1.columns))) * 100, 2),
            'period2_completeness': round((1 - df2.isnull().sum().sum() / (len(df2) * len(df2.columns))) * 100, 2),
            'sample_size_adequate': len(df1) >= 30 and len(df2) >= 30,
            'data_balance': abs(len(df1) - len(df2)) / max(len(df1), len(df2)) < 0.5
        }
    
    def _validate_period_comparison(self, results: Dict, rules: Dict, validation_result: Dict):
        """Valida resultados de comparação de períodos."""
        p1_records = results['period1']['records']
        p2_records = results['period2']['records']
        
        if p1_records < rules['min_data_points']:
            validation_result['warnings'].append(f"Período 1 tem poucos dados: {p1_records}")
        
        if p2_records < rules['min_data_points']:
            validation_result['warnings'].append(f"Período 2 tem poucos dados: {p2_records}")
    
    def _validate_segmentation(self, results: Dict, rules: Dict, validation_result: Dict):
        """Valida resultados de segmentação."""
        total_segments = results['summary']['total_segments']
        
        if total_segments < 2:
            validation_result['warnings'].append("Poucos segmentos identificados")
    
    def _validate_kpis(self, results: Dict, rules: Dict, validation_result: Dict):
        """Valida resultados de KPIs."""
        failed_kpis = results['summary']['failed_calculations']
        
        if failed_kpis > 0:
            validation_result['warnings'].append(f"{failed_kpis} KPIs falharam no cálculo")
    
    def _calculate_quality_score(self, validation_result: Dict) -> float:
        """Calcula score de qualidade geral."""
        base_score = 100
        
        # Reduz score por erros e warnings
        base_score -= len(validation_result['errors']) * 20
        base_score -= len(validation_result['warnings']) * 5
        
        return max(0, min(100, base_score))
    
    def _generate_recommendations(self, validation_result: Dict) -> List[str]:
        """Gera recomendações baseadas na validação."""
        recommendations = []
        
        if len(validation_result['warnings']) > 0:
            recommendations.append("Revisar warnings identificados na validação")
        
        if validation_result['quality_score'] < 80:
            recommendations.append("Melhorar qualidade dos dados de entrada")
        
        return recommendations


# Exemplo de uso e testes
if __name__ == "__main__":
    # Inicializa o AnalyticsEngine
    engine = AnalyticsEngine()
    
    # Exemplo de dados para teste
    sample_data = pd.DataFrame({
        'ano': [2024, 2024, 2025, 2025, 2024, 2025],
        'valor': [100, 150, 200, 180, 120, 220],
        'grupo': ['A', 'B', 'A', 'B', 'A', 'B'],
        'motivo': ['Suporte', 'Vendas', 'Suporte', 'Suporte', 'Vendas', 'Vendas']
    })
    
    try:
        # Teste de comparação de períodos
        comparison = engine.compare_periods(sample_data, 2024, 2025)
        print("Comparação de períodos realizada com sucesso!")
        
        # Teste de segmentação
        segmentation = engine.segment_by_groups(sample_data, ['grupo'])
        print("Segmentação realizada com sucesso!")
        
        # Teste de contagem de motivos
        reasons = engine.count_contact_reasons(sample_data, 'motivo')
        print("Contagem de motivos realizada com sucesso!")
        
    except Exception as e:
        print(f"Erro nos testes: {e}")
    
    print("AnalyticsEngine implementado com sucesso!")


    def _motivos_analysis(self, df: pd.DataFrame) -> Dict:
        """
        Análise específica de motivos de contato.
        
        Args:
            df (pd.DataFrame): DataFrame com dados
            
        Returns:
            Dict: Análise de motivos
        """
        try:
            motivos_analysis = {}
            
            # Procurar coluna de motivos
            motivo_col = None
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['motivo', 'reason', 'causa', 'tipo']):
                    motivo_col = col
                    break
            
            if motivo_col and motivo_col in df.columns:
                # Contagem por motivo
                motivos_count = df[motivo_col].value_counts()
                
                # Percentuais
                motivos_percent = (motivos_count / len(df) * 100).round(2)
                
                # Top motivos
                top_motivos = motivos_count.head(10)
                
                motivos_analysis = {
                    "motivos_contagem": motivos_count.to_dict(),
                    "motivos_percentual": motivos_percent.to_dict(),
                    "top_motivos": top_motivos.to_dict(),
                    "total_motivos_unicos": len(motivos_count),
                    "motivo_mais_frequente": motivos_count.index[0] if len(motivos_count) > 0 else None
                }
                
                # Análise por valor se disponível
                value_col = self._identify_value_column(df)
                if value_col:
                    motivos_valor = df.groupby(motivo_col)[value_col].agg(['sum', 'mean', 'count']).round(2)
                    motivos_analysis["motivos_por_valor"] = motivos_valor.to_dict()
            
            return {"analise_motivos": motivos_analysis}
            
        except Exception as e:
            logger.error(f"Erro na análise de motivos: {e}")
            return {"analise_motivos": {}}
    
    def _validate_results(self, results: Dict, original_df: pd.DataFrame) -> Dict:
        """
        Valida os resultados da análise.
        
        Args:
            results (Dict): Resultados da análise
            original_df (pd.DataFrame): DataFrame original
            
        Returns:
            Dict: Resultado da validação
        """
        try:
            validation_issues = []
            is_valid = True
            
            # Validar integridade dos dados
            if "basic_stats" in results:
                basic_stats = results["basic_stats"]
                
                # Verificar se totais fazem sentido
                if "total_records" in basic_stats:
                    if basic_stats["total_records"] != len(original_df):
                        validation_issues.append("Total de registros não confere")
                        is_valid = False
                
                # Verificar valores nulos excessivos
                if "null_percentage" in basic_stats:
                    if basic_stats["null_percentage"] > 50:
                        validation_issues.append("Muitos valores nulos nos dados (>50%)")
                
                # Verificar consistência de valores
                if "value_stats" in basic_stats:
                    value_stats = basic_stats["value_stats"]
                    if value_stats.get("min", 0) < 0 and "valor" in original_df.columns:
                        validation_issues.append("Valores negativos encontrados")
            
            # Validar comparações temporais
            if "period_comparison" in results:
                comparison = results["period_comparison"]
                if "comparison" in comparison:
                    comp_metrics = comparison["comparison"]
                    # Verificar crescimentos extremos (>1000%)
                    if comp_metrics.get("crescimento_percentual", 0) > 1000:
                        validation_issues.append("Crescimento extremo detectado (>1000%)")
            
            # Validar segmentações
            if "segmentation" in results:
                segmentation = results["segmentation"]
                total_segments = sum(seg.get("count", 0) for seg in segmentation.get("segments", {}).values())
                if abs(total_segments - len(original_df)) > len(original_df) * 0.01:  # 1% tolerância
                    validation_issues.append("Soma dos segmentos não confere com total")
            
            validation_result = {
                "is_valid": is_valid and len(validation_issues) == 0,
                "issues": validation_issues,
                "validation_timestamp": datetime.now().isoformat(),
                "confidence_score": max(0, 100 - len(validation_issues) * 20)  # Reduz 20% por issue
            }
            
            if validation_issues:
                logger.warning(f"Validação encontrou {len(validation_issues)} problemas")
            else:
                logger.info("Validação passou sem problemas")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Erro na validação: {e}")
            return {
                "is_valid": False,
                "issues": [f"Erro na validação: {str(e)}"],
                "validation_timestamp": datetime.now().isoformat(),
                "confidence_score": 0
            }

