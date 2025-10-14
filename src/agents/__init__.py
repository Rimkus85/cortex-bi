"""
Agente de Analytics - Módulos de Análise de Dados

Este pacote contém os módulos principais para:
- Carregamento de dados de múltiplas fontes
- Engine de análise e cálculo de KPIs
- Geração automática de apresentações PPTX

Módulos:
- data_loader: Carregamento de dados (CSV, Excel, SQL, Power BI)
- analytics_engine: Engine de análise e cálculos
- pptx_generator: Geração de apresentações PPTX
"""

__version__ = "1.0.0"
__author__ = "Analytics Agent"

from .data_loader import DataLoader
from .analytics_engine import AnalyticsEngine
from .pptx_generator import PPTXGenerator

__all__ = ["DataLoader", "AnalyticsEngine", "PPTXGenerator"]

