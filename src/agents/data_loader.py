"""
Data Loader - Módulo de Carregamento de Dados

Este módulo é responsável por carregar dados de múltiplas fontes:
- Arquivos CSV e Excel
- Banco de dados SQL Server via pyodbc
- Power BI via API REST

Instruções para personalização:
1. Configure as credenciais de banco de dados no arquivo .env
2. Configure as credenciais do Power BI no arquivo .env
3. Ajuste os métodos de validação conforme necessário
4. Adicione novos tipos de fonte de dados conforme necessário
"""

import pandas as pd
import os
from typing import Dict, List, Optional, Union
from pathlib import Path
import json
from datetime import datetime

# Imports opcionais - não quebram se não estiverem disponíveis
try:
    import pyodbc
    PYODBC_AVAILABLE = True
except ImportError:
    PYODBC_AVAILABLE = False
    print("⚠️ pyodbc não disponível - funcionalidades SQL Server desabilitadas")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️ requests não disponível - funcionalidades Power BI desabilitadas")

try:
    from loguru import logger
    LOGURU_AVAILABLE = True
except ImportError:
    LOGURU_AVAILABLE = False
    # Logger básico se loguru não estiver disponível
    import logging
    logger = logging.getLogger(__name__)

try:
    import msal
    MSAL_AVAILABLE = True
except ImportError:
    MSAL_AVAILABLE = False
    print("⚠️ msal não disponível - autenticação Power BI desabilitada")


class DataLoader:
    """
    Classe principal para carregamento de dados de múltiplas fontes.
    
    Suporta:
    - CSV e Excel (local e remoto)
    - SQL Server via pyodbc
    - Power BI via API REST
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa o DataLoader com configurações opcionais.
        
        Args:
            config (Dict, optional): Configurações personalizadas
        """
        self.config = config or {}
        self.sql_connection = None
        self.powerbi_token = None
        
        # Configurações padrão - EDITE AQUI conforme necessário
        self.default_config = {
            'sql_driver': '{ODBC Driver 17 for SQL Server}',
            'powerbi_scope': ['https://analysis.windows.net/powerbi/api/.default'],
            'max_retries': 3,
            'timeout': 30
        }
        
        # Carrega variáveis de ambiente
        self._load_env_config()
        
        logger.info("DataLoader inicializado com sucesso")
    
    def _load_env_config(self):
        """
        Carrega configurações do arquivo .env
        
        Variáveis esperadas:
        - SQL_SERVER: servidor SQL
        - SQL_DATABASE: nome do banco
        - SQL_USERNAME: usuário SQL
        - SQL_PASSWORD: senha SQL
        - POWERBI_CLIENT_ID: ID do cliente Power BI
        - POWERBI_CLIENT_SECRET: secret do cliente Power BI
        - POWERBI_TENANT_ID: ID do tenant
        """
        from dotenv import load_dotenv
        load_dotenv()
        
        self.sql_config = {
            'server': os.getenv('SQL_SERVER', 'localhost'),
            'database': os.getenv('SQL_DATABASE', 'master'),
            'username': os.getenv('SQL_USERNAME', ''),
            'password': os.getenv('SQL_PASSWORD', ''),
            'driver': self.default_config['sql_driver']
        }
        
        self.powerbi_config = {
            'client_id': os.getenv('POWERBI_CLIENT_ID', ''),
            'client_secret': os.getenv('POWERBI_CLIENT_SECRET', ''),
            'tenant_id': os.getenv('POWERBI_TENANT_ID', ''),
            'authority': f"https://login.microsoftonline.com/{os.getenv('POWERBI_TENANT_ID', '')}"
        }
    
    def load_csv(self, file_path: str, **kwargs) -> pd.DataFrame:
        """
        Carrega dados de arquivo CSV.
        
        Args:
            file_path (str): Caminho para o arquivo CSV
            **kwargs: Parâmetros adicionais para pd.read_csv
            
        Returns:
            pd.DataFrame: Dados carregados
            
        Exemplo de uso:
            df = loader.load_csv('data/vendas.csv', encoding='utf-8')
        """
        try:
            logger.info(f"Carregando CSV: {file_path}")
            
            # Configurações padrão - EDITE AQUI conforme necessário
            default_params = {
                'encoding': 'utf-8',
                'sep': ',',
                'decimal': '.',
                'thousands': ','
            }
            
            # Mescla parâmetros padrão com os fornecidos
            params = {**default_params, **kwargs}
            
            df = pd.read_csv(file_path, **params)
            
            # Validação básica
            if df.empty:
                raise ValueError("Arquivo CSV está vazio")
            
            logger.info(f"CSV carregado com sucesso: {len(df)} linhas, {len(df.columns)} colunas")
            return self._standardize_dataframe(df)
            
        except Exception as e:
            logger.error(f"Erro ao carregar CSV {file_path}: {str(e)}")
            raise
    
    def load_excel(self, file_path: str, sheet_name: Union[str, int] = 0, **kwargs) -> pd.DataFrame:
        """
        Carrega dados de arquivo Excel.
        
        Args:
            file_path (str): Caminho para o arquivo Excel
            sheet_name (str|int): Nome ou índice da planilha
            **kwargs: Parâmetros adicionais para pd.read_excel
            
        Returns:
            pd.DataFrame: Dados carregados
            
        Exemplo de uso:
            df = loader.load_excel('data/vendas.xlsx', sheet_name='Dados')
        """
        try:
            logger.info(f"Carregando Excel: {file_path}, planilha: {sheet_name}")
            
            df = pd.read_excel(file_path, sheet_name=sheet_name, **kwargs)
            
            # Validação básica
            if df.empty:
                raise ValueError("Planilha Excel está vazia")
            
            logger.info(f"Excel carregado com sucesso: {len(df)} linhas, {len(df.columns)} colunas")
            return self._standardize_dataframe(df)
            
        except Exception as e:
            logger.error(f"Erro ao carregar Excel {file_path}: {str(e)}")
            raise
    
    def load_sql(self, query: str, connection_string: Optional[str] = None) -> pd.DataFrame:
        """
        Carrega dados do SQL Server via pyodbc.
        
        Args:
            query (str): Query SQL para executar
            connection_string (str, optional): String de conexão personalizada
            
        Returns:
            pd.DataFrame: Dados carregados
            
        Exemplo de uso:
            df = loader.load_sql("SELECT * FROM vendas WHERE ano = 2024")
        """
        if not PYODBC_AVAILABLE:
            raise ImportError("pyodbc não está disponível. Instale com: pip install pyodbc")
            
        try:
            if LOGURU_AVAILABLE:
                logger.info("Executando query SQL")
            else:
                print("Executando query SQL")
            
            # Usa connection string personalizada ou padrão
            if connection_string:
                conn_str = connection_string
            else:
                conn_str = self._build_sql_connection_string()
            
            # Conecta ao banco
            with pyodbc.connect(conn_str) as conn:
                df = pd.read_sql(query, conn)
            
            # Validação básica
            if df.empty:
                if LOGURU_AVAILABLE:
                    logger.warning("Query SQL retornou resultado vazio")
                else:
                    print("⚠️ Query SQL retornou resultado vazio")
            
            if LOGURU_AVAILABLE:
                logger.info(f"SQL executado com sucesso: {len(df)} linhas, {len(df.columns)} colunas")
            else:
                print(f"✅ SQL executado com sucesso: {len(df)} linhas, {len(df.columns)} colunas")
                
            return self._standardize_dataframe(df)
            
        except Exception as e:
            if LOGURU_AVAILABLE:
                logger.error(f"Erro ao executar SQL: {str(e)}")
            else:
                print(f"❌ Erro ao executar SQL: {str(e)}")
            raise
    
    def load_powerbi_dataset(self, workspace_id: str, dataset_id: str, table_name: str) -> pd.DataFrame:
        """
        Carrega dados do Power BI via API REST.
        
        Args:
            workspace_id (str): ID do workspace Power BI
            dataset_id (str): ID do dataset
            table_name (str): Nome da tabela
            
        Returns:
            pd.DataFrame: Dados carregados
            
        Exemplo de uso:
            df = loader.load_powerbi_dataset('workspace-id', 'dataset-id', 'vendas')
        """
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests não está disponível. Instale com: pip install requests")
        if not MSAL_AVAILABLE:
            raise ImportError("msal não está disponível. Instale com: pip install msal")
            
        try:
            if LOGURU_AVAILABLE:
                logger.info(f"Carregando dados do Power BI: {table_name}")
            else:
                print(f"Carregando dados do Power BI: {table_name}")
            
            # Obtém token de acesso
            token = self._get_powerbi_token()
            
            # Monta URL da API
            url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/executeQueries"
            
            # Headers da requisição
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # Query DAX para obter dados da tabela
            dax_query = f"EVALUATE {table_name}"
            
            # Payload da requisição
            payload = {
                "queries": [
                    {
                        "query": dax_query
                    }
                ],
                "serializerSettings": {
                    "includeNulls": True
                }
            }
            
            # Executa requisição
            response = requests.post(url, headers=headers, json=payload, timeout=self.default_config['timeout'])
            response.raise_for_status()
            
            # Processa resposta
            data = response.json()
            
            if 'results' not in data or not data['results']:
                raise ValueError("Nenhum resultado retornado do Power BI")
            
            # Converte para DataFrame
            result = data['results'][0]
            if 'tables' not in result or not result['tables']:
                raise ValueError("Nenhuma tabela encontrada no resultado")
            
            table_data = result['tables'][0]
            rows = table_data.get('rows', [])
            
            if not rows:
                logger.warning("Tabela Power BI está vazia")
                return pd.DataFrame()
            
            # Cria DataFrame
            df = pd.DataFrame(rows)
            
            logger.info(f"Power BI carregado com sucesso: {len(df)} linhas, {len(df.columns)} colunas")
            return self._standardize_dataframe(df)
            
        except Exception as e:
            logger.error(f"Erro ao carregar Power BI: {str(e)}")
            raise
    
    def _build_sql_connection_string(self) -> str:
        """
        Constrói string de conexão SQL Server.
        
        Returns:
            str: String de conexão
        """
        return (
            f"DRIVER={self.sql_config['driver']};"
            f"SERVER={self.sql_config['server']};"
            f"DATABASE={self.sql_config['database']};"
            f"UID={self.sql_config['username']};"
            f"PWD={self.sql_config['password']};"
            "TrustServerCertificate=yes;"
        )
    
    def _get_powerbi_token(self) -> str:
        """
        Obtém token de acesso do Power BI via MSAL.
        
        Returns:
            str: Token de acesso
        """
        try:
            # Cria aplicação MSAL
            app = msal.ConfidentialClientApplication(
                client_id=self.powerbi_config['client_id'],
                client_credential=self.powerbi_config['client_secret'],
                authority=self.powerbi_config['authority']
            )
            
            # Obtém token
            result = app.acquire_token_for_client(scopes=self.default_config['powerbi_scope'])
            
            if 'access_token' not in result:
                raise ValueError(f"Erro ao obter token Power BI: {result.get('error_description', 'Erro desconhecido')}")
            
            return result['access_token']
            
        except Exception as e:
            logger.error(f"Erro ao obter token Power BI: {str(e)}")
            raise
    
    def _standardize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Padroniza DataFrame aplicando limpezas e conversões básicas.
        
        Args:
            df (pd.DataFrame): DataFrame original
            
        Returns:
            pd.DataFrame: DataFrame padronizado
            
        EDITE AQUI para adicionar suas próprias regras de padronização:
        - Conversão de tipos de dados
        - Limpeza de valores nulos
        - Padronização de nomes de colunas
        - Formatação de datas
        """
        try:
            # Copia DataFrame para não modificar o original
            df_clean = df.copy()
            
            # Remove espaços em branco dos nomes das colunas
            df_clean.columns = df_clean.columns.str.strip()
            
            # Converte colunas de data automaticamente
            for col in df_clean.columns:
                if df_clean[col].dtype == 'object':
                    # Tenta converter para datetime se parecer com data
                    sample_values = df_clean[col].dropna().head(5)
                    if len(sample_values) > 0:
                        try:
                            pd.to_datetime(sample_values.iloc[0])
                            df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
                            logger.info(f"Coluna '{col}' convertida para datetime")
                        except:
                            pass
            
            # Remove linhas completamente vazias
            df_clean = df_clean.dropna(how='all')
            
            # Adiciona metadados
            df_clean.attrs['loaded_at'] = datetime.now()
            df_clean.attrs['source'] = 'DataLoader'
            
            logger.info(f"DataFrame padronizado: {len(df_clean)} linhas, {len(df_clean.columns)} colunas")
            return df_clean
            
        except Exception as e:
            logger.error(f"Erro ao padronizar DataFrame: {str(e)}")
            return df
    
    def get_data_info(self, df: pd.DataFrame) -> Dict:
        """
        Retorna informações detalhadas sobre o DataFrame.
        
        Args:
            df (pd.DataFrame): DataFrame para analisar
            
        Returns:
            Dict: Informações do DataFrame
        """
        try:
            info = {
                'shape': df.shape,
                'columns': list(df.columns),
                'dtypes': df.dtypes.to_dict(),
                'null_counts': df.isnull().sum().to_dict(),
                'memory_usage': df.memory_usage(deep=True).sum(),
                'loaded_at': df.attrs.get('loaded_at', 'Unknown'),
                'source': df.attrs.get('source', 'Unknown')
            }
            
            # Adiciona estatísticas básicas para colunas numéricas
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                info['numeric_stats'] = df[numeric_cols].describe().to_dict()
            
            return info
            
        except Exception as e:
            logger.error(f"Erro ao obter informações do DataFrame: {str(e)}")
            return {}
    
    def validate_data(self, df: pd.DataFrame, rules: Optional[Dict] = None) -> Dict:
        """
        Valida dados conforme regras especificadas.
        
        Args:
            df (pd.DataFrame): DataFrame para validar
            rules (Dict, optional): Regras de validação personalizadas
            
        Returns:
            Dict: Resultado da validação
            
        EDITE AQUI para adicionar suas próprias regras de validação:
        - Verificação de valores obrigatórios
        - Validação de intervalos de datas
        - Verificação de valores únicos
        - Validação de formatos específicos
        """
        try:
            validation_result = {
                'is_valid': True,
                'errors': [],
                'warnings': [],
                'summary': {}
            }
            
            # Regras padrão de validação
            default_rules = {
                'min_rows': 1,
                'max_null_percentage': 50,
                'required_columns': []
            }
            
            # Mescla regras padrão com personalizadas
            validation_rules = {**default_rules, **(rules or {})}
            
            # Validação: número mínimo de linhas
            if len(df) < validation_rules['min_rows']:
                validation_result['errors'].append(f"DataFrame tem apenas {len(df)} linhas, mínimo requerido: {validation_rules['min_rows']}")
                validation_result['is_valid'] = False
            
            # Validação: colunas obrigatórias
            missing_cols = set(validation_rules['required_columns']) - set(df.columns)
            if missing_cols:
                validation_result['errors'].append(f"Colunas obrigatórias ausentes: {list(missing_cols)}")
                validation_result['is_valid'] = False
            
            # Validação: percentual de valores nulos
            for col in df.columns:
                null_percentage = (df[col].isnull().sum() / len(df)) * 100
                if null_percentage > validation_rules['max_null_percentage']:
                    validation_result['warnings'].append(f"Coluna '{col}' tem {null_percentage:.1f}% de valores nulos")
            
            # Resumo da validação
            validation_result['summary'] = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'null_cells': df.isnull().sum().sum(),
                'duplicate_rows': df.duplicated().sum()
            }
            
            logger.info(f"Validação concluída: {'✓ Válido' if validation_result['is_valid'] else '✗ Inválido'}")
            return validation_result
            
        except Exception as e:
            logger.error(f"Erro na validação: {str(e)}")
            return {'is_valid': False, 'errors': [str(e)], 'warnings': [], 'summary': {}}


# Exemplo de uso e testes
if __name__ == "__main__":
    # Inicializa o DataLoader
    loader = DataLoader()
    
    # Exemplo de carregamento de CSV
    try:
        # df_csv = loader.load_csv('data/exemplo.csv')
        # print("CSV carregado com sucesso!")
        pass
    except Exception as e:
        print(f"Erro ao carregar CSV: {e}")
    
    # Exemplo de carregamento de Excel
    try:
        # df_excel = loader.load_excel('data/exemplo.xlsx', sheet_name='Dados')
        # print("Excel carregado com sucesso!")
        pass
    except Exception as e:
        print(f"Erro ao carregar Excel: {e}")
    
    print("DataLoader implementado com sucesso!")

