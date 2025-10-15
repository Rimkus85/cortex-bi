# 📊 CÓRTEX BI - Configuração de Fontes de Dados para Detecção de Anomalias

**Versão:** 2.0  
**Data:** Outubro 2025  
**Desenvolvido em parceria com:** Manus AI

---

## 🎯 Visão Geral

A configuração das **fontes de dados** é o coração do sistema de detecção de anomalias. É aqui que você define:

- **ONDE** o sistema deve buscar os dados (SQL Server, arquivos CSV, APIs, etc.)
- **O QUE** monitorar (vendas, custos, métricas de performance, etc.)
- **QUANDO** verificar (intervalos de tempo)
- **COMO** interpretar os dados (thresholds, severidade, etc.)

---

## 📁 Estrutura de Configuração

### Localização dos Arquivos

```
cortex-bi/
├── config/
│   └── anomaly_rules/
│       ├── metrics_config.json          # ⭐ ARQUIVO PRINCIPAL
│       ├── data_sources.json            # Configuração de conexões
│       ├── false_positive_rules.json    # Regras de falsos positivos
│       └── alert_templates.json         # Templates de alertas
│
├── data/
│   ├── raw/                             # Dados brutos (CSV, Excel, etc.)
│   ├── processed/                       # Dados processados
│   └── anomalies/                       # Histórico de anomalias detectadas
│
└── .env                                 # Credenciais e configurações globais
```

---

## ⚙️ Arquivo Principal: metrics_config.json

Este é o arquivo mais importante. Ele define todas as métricas que serão monitoradas.

### Template Completo

Crie o arquivo `config/anomaly_rules/metrics_config.json`:

```json
{
  "version": "2.0",
  "description": "Configuração de métricas para detecção de anomalias",
  
  "metrics": [
    {
      "id": "vendas_totais_diarias",
      "name": "Vendas Totais Diárias",
      "description": "Soma de todas as vendas do dia",
      "enabled": true,
      
      "data_source": {
        "type": "sql_server",
        "connection_id": "sql_principal",
        "query": "SELECT SUM(valor_venda) as valor, COUNT(*) as quantidade FROM vendas WHERE CAST(data_venda AS DATE) = CAST(GETDATE() AS DATE)",
        "value_column": "valor",
        "timestamp_column": null
      },
      
      "historical_data": {
        "query": "SELECT CAST(data_venda AS DATE) as data, SUM(valor_venda) as valor FROM vendas WHERE data_venda >= DATEADD(day, -30, GETDATE()) GROUP BY CAST(data_venda AS DATE) ORDER BY data",
        "min_samples": 30,
        "max_samples": 90
      },
      
      "anomaly_detection": {
        "method": "isolation_forest",
        "contamination": 0.1,
        "threshold": -0.5,
        "features": ["valor", "dia_semana", "hora"]
      },
      
      "alert_config": {
        "severity": "high",
        "threshold_type": "percentage",
        "threshold_value": 15,
        "cooldown_minutes": 60,
        "channels": ["email", "teams"],
        "recipients": ["gerente.vendas@empresa.com", "diretor@empresa.com"]
      },
      
      "monitoring": {
        "check_interval": 3600,
        "active_hours": "00:00-23:59",
        "active_days": [1, 2, 3, 4, 5, 6, 7]
      }
    },
    
    {
      "id": "custos_operacionais",
      "name": "Custos Operacionais",
      "description": "Custos operacionais diários",
      "enabled": true,
      
      "data_source": {
        "type": "csv",
        "file_path": "data/raw/custos_diarios.csv",
        "value_column": "custo_total",
        "timestamp_column": "data",
        "delimiter": ",",
        "encoding": "utf-8"
      },
      
      "historical_data": {
        "source": "same_file",
        "min_samples": 30,
        "max_samples": 90
      },
      
      "anomaly_detection": {
        "method": "isolation_forest",
        "contamination": 0.1,
        "threshold": -0.5,
        "features": ["custo_total", "dia_semana"]
      },
      
      "alert_config": {
        "severity": "medium",
        "threshold_type": "absolute",
        "threshold_value": 50000,
        "cooldown_minutes": 120,
        "channels": ["email"],
        "recipients": ["controller@empresa.com"]
      },
      
      "monitoring": {
        "check_interval": 7200,
        "active_hours": "08:00-18:00",
        "active_days": [1, 2, 3, 4, 5]
      }
    },
    
    {
      "id": "taxa_conversao_site",
      "name": "Taxa de Conversão do Site",
      "description": "Percentual de visitantes que convertem",
      "enabled": true,
      
      "data_source": {
        "type": "api",
        "url": "https://api.analytics.empresa.com/conversao/hoje",
        "method": "GET",
        "headers": {
          "Authorization": "Bearer ${API_ANALYTICS_TOKEN}",
          "Content-Type": "application/json"
        },
        "response_path": "data.taxa_conversao",
        "timeout": 30
      },
      
      "historical_data": {
        "api_url": "https://api.analytics.empresa.com/conversao/historico",
        "api_params": {
          "dias": 30
        },
        "response_path": "data.historico",
        "min_samples": 30
      },
      
      "anomaly_detection": {
        "method": "isolation_forest",
        "contamination": 0.1,
        "threshold": -0.5,
        "features": ["taxa_conversao", "hora", "dia_semana"]
      },
      
      "alert_config": {
        "severity": "high",
        "threshold_type": "percentage",
        "threshold_value": 10,
        "cooldown_minutes": 30,
        "channels": ["email", "teams", "webhook"],
        "recipients": ["marketing@empresa.com"]
      },
      
      "monitoring": {
        "check_interval": 1800,
        "active_hours": "00:00-23:59",
        "active_days": [1, 2, 3, 4, 5, 6, 7]
      }
    },
    
    {
      "id": "tempo_resposta_api",
      "name": "Tempo de Resposta da API",
      "description": "Tempo médio de resposta das requisições",
      "enabled": true,
      
      "data_source": {
        "type": "internal",
        "metric_key": "avg_response_time",
        "aggregation": "avg",
        "window_minutes": 5
      },
      
      "historical_data": {
        "source": "internal_logs",
        "log_file": "logs/cortexbi.log",
        "pattern": "execution_time: (\\d+)",
        "min_samples": 100
      },
      
      "anomaly_detection": {
        "method": "isolation_forest",
        "contamination": 0.05,
        "threshold": -0.3,
        "features": ["response_time", "hora"]
      },
      
      "alert_config": {
        "severity": "critical",
        "threshold_type": "absolute",
        "threshold_value": 5000,
        "cooldown_minutes": 15,
        "channels": ["teams", "webhook"],
        "recipients": ["ti@empresa.com", "devops@empresa.com"]
      },
      
      "monitoring": {
        "check_interval": 60,
        "active_hours": "00:00-23:59",
        "active_days": [1, 2, 3, 4, 5, 6, 7]
      }
    },
    
    {
      "id": "estoque_produto_critico",
      "name": "Estoque de Produto Crítico",
      "description": "Nível de estoque do produto mais vendido",
      "enabled": true,
      
      "data_source": {
        "type": "excel",
        "file_path": "data/raw/estoque.xlsx",
        "sheet_name": "Estoque_Atual",
        "value_column": "quantidade",
        "filter": {
          "column": "produto_id",
          "value": "PROD-001"
        }
      },
      
      "historical_data": {
        "file_path": "data/raw/historico_estoque.xlsx",
        "sheet_name": "Historico",
        "min_samples": 30
      },
      
      "anomaly_detection": {
        "method": "isolation_forest",
        "contamination": 0.1,
        "threshold": -0.5,
        "features": ["quantidade", "dia_semana"]
      },
      
      "alert_config": {
        "severity": "high",
        "threshold_type": "absolute",
        "threshold_value": 100,
        "direction": "below",
        "cooldown_minutes": 240,
        "channels": ["email"],
        "recipients": ["logistica@empresa.com"]
      },
      
      "monitoring": {
        "check_interval": 14400,
        "active_hours": "08:00-18:00",
        "active_days": [1, 2, 3, 4, 5]
      }
    },
    
    {
      "id": "nps_diario",
      "name": "NPS Diário",
      "description": "Net Promoter Score calculado diariamente",
      "enabled": true,
      
      "data_source": {
        "type": "power_bi",
        "workspace_id": "seu-workspace-id",
        "dataset_id": "seu-dataset-id",
        "table": "NPS_Diario",
        "measure": "NPS_Score",
        "filter": "Data = TODAY()"
      },
      
      "historical_data": {
        "source": "power_bi",
        "filter": "Data >= TODAY() - 30",
        "min_samples": 30
      },
      
      "anomaly_detection": {
        "method": "isolation_forest",
        "contamination": 0.1,
        "threshold": -0.5,
        "features": ["nps_score", "dia_semana"]
      },
      
      "alert_config": {
        "severity": "medium",
        "threshold_type": "percentage",
        "threshold_value": 20,
        "cooldown_minutes": 1440,
        "channels": ["email", "teams"],
        "recipients": ["atendimento@empresa.com", "qualidade@empresa.com"]
      },
      
      "monitoring": {
        "check_interval": 86400,
        "active_hours": "09:00-09:30",
        "active_days": [1, 2, 3, 4, 5]
      }
    }
  ],
  
  "global_settings": {
    "timezone": "America/Sao_Paulo",
    "min_historical_days": 30,
    "max_historical_days": 90,
    "confidence_threshold": 0.8,
    "default_cooldown_minutes": 60,
    "retry_on_error": true,
    "max_retries": 3,
    "retry_delay_seconds": 60
  }
}
```

---

## 🔌 Tipos de Fontes de Dados Suportadas

### 1. SQL Server

**Configuração básica:**

```json
{
  "data_source": {
    "type": "sql_server",
    "connection_id": "sql_principal",
    "query": "SELECT SUM(valor) as total FROM vendas WHERE data = CAST(GETDATE() AS DATE)",
    "value_column": "total"
  }
}
```

**Configuração da conexão** (em `config/anomaly_rules/data_sources.json`):

```json
{
  "connections": {
    "sql_principal": {
      "type": "sql_server",
      "host": "servidor.database.windows.net",
      "port": 1433,
      "database": "vendas_db",
      "username": "${SQL_SERVER_USERNAME}",
      "password": "${SQL_SERVER_PASSWORD}",
      "driver": "ODBC Driver 17 for SQL Server",
      "connection_timeout": 30,
      "query_timeout": 60
    }
  }
}
```

**Variáveis no `.env`:**

```bash
SQL_SERVER_USERNAME=seu_usuario
SQL_SERVER_PASSWORD=sua_senha
```

### 2. Arquivo CSV

**Configuração:**

```json
{
  "data_source": {
    "type": "csv",
    "file_path": "data/raw/vendas_diarias.csv",
    "value_column": "valor_total",
    "timestamp_column": "data",
    "delimiter": ",",
    "encoding": "utf-8",
    "skip_rows": 0,
    "date_format": "%Y-%m-%d"
  }
}
```

**Exemplo de arquivo CSV** (`data/raw/vendas_diarias.csv`):

```csv
data,valor_total,quantidade,regiao
2025-10-01,125000.50,450,Sul
2025-10-02,132000.75,480,Sul
2025-10-03,118000.00,420,Sul
2025-10-04,145000.25,510,Sul
```

### 3. Arquivo Excel

**Configuração:**

```json
{
  "data_source": {
    "type": "excel",
    "file_path": "data/raw/relatorio_mensal.xlsx",
    "sheet_name": "Vendas",
    "value_column": "Total",
    "timestamp_column": "Data",
    "header_row": 0,
    "filter": {
      "column": "Regiao",
      "value": "Sul"
    }
  }
}
```

### 4. API REST

**Configuração:**

```json
{
  "data_source": {
    "type": "api",
    "url": "https://api.empresa.com/metrics/vendas",
    "method": "GET",
    "headers": {
      "Authorization": "Bearer ${API_TOKEN}",
      "Content-Type": "application/json"
    },
    "params": {
      "data": "hoje",
      "formato": "json"
    },
    "response_path": "data.vendas.total",
    "timeout": 30
  }
}
```

**Variáveis no `.env`:**

```bash
API_TOKEN=seu-token-de-api
```

**Exemplo de resposta da API:**

```json
{
  "status": "success",
  "data": {
    "vendas": {
      "total": 125000.50,
      "quantidade": 450,
      "data": "2025-10-14"
    }
  }
}
```

### 5. Power BI

**Configuração:**

```json
{
  "data_source": {
    "type": "power_bi",
    "workspace_id": "12345678-1234-1234-1234-123456789abc",
    "dataset_id": "87654321-4321-4321-4321-cba987654321",
    "table": "Vendas",
    "measure": "Total_Vendas",
    "filter": "Data = TODAY()"
  }
}
```

**Configuração de autenticação** (em `data_sources.json`):

```json
{
  "power_bi": {
    "tenant_id": "${POWERBI_TENANT_ID}",
    "client_id": "${POWERBI_CLIENT_ID}",
    "client_secret": "${POWERBI_CLIENT_SECRET}"
  }
}
```

**Variáveis no `.env`:**

```bash
POWERBI_TENANT_ID=seu-tenant-id
POWERBI_CLIENT_ID=seu-client-id
POWERBI_CLIENT_SECRET=seu-client-secret
```

### 6. Métricas Internas do Sistema

**Configuração:**

```json
{
  "data_source": {
    "type": "internal",
    "metric_key": "avg_response_time",
    "aggregation": "avg",
    "window_minutes": 5
  }
}
```

**Métricas internas disponíveis:**

- `avg_response_time` - Tempo médio de resposta
- `request_count` - Número de requisições
- `error_rate` - Taxa de erro
- `active_users` - Usuários ativos
- `memory_usage` - Uso de memória
- `cpu_usage` - Uso de CPU

### 7. Logs do Sistema

**Configuração:**

```json
{
  "data_source": {
    "type": "log_file",
    "file_path": "logs/cortexbi.log",
    "pattern": "execution_time: (\\d+)",
    "aggregation": "avg",
    "window_minutes": 5
  }
}
```

---

## 📝 Arquivo: data_sources.json

Este arquivo centraliza as configurações de conexão para evitar repetição.

**Criar** `config/anomaly_rules/data_sources.json`:

```json
{
  "version": "2.0",
  "description": "Configurações de conexão para fontes de dados",
  
  "connections": {
    "sql_principal": {
      "type": "sql_server",
      "host": "servidor.database.windows.net",
      "port": 1433,
      "database": "vendas_db",
      "username": "${SQL_SERVER_USERNAME}",
      "password": "${SQL_SERVER_PASSWORD}",
      "driver": "ODBC Driver 17 for SQL Server",
      "connection_timeout": 30,
      "query_timeout": 60,
      "pool_size": 5
    },
    
    "sql_secundario": {
      "type": "sql_server",
      "host": "servidor-backup.database.windows.net",
      "port": 1433,
      "database": "vendas_db_backup",
      "username": "${SQL_SERVER_USERNAME}",
      "password": "${SQL_SERVER_PASSWORD}",
      "driver": "ODBC Driver 17 for SQL Server"
    },
    
    "api_analytics": {
      "type": "api",
      "base_url": "https://api.analytics.empresa.com",
      "auth_type": "bearer",
      "token": "${API_ANALYTICS_TOKEN}",
      "timeout": 30,
      "retry_count": 3
    },
    
    "api_erp": {
      "type": "api",
      "base_url": "https://erp.empresa.com/api/v2",
      "auth_type": "basic",
      "username": "${ERP_API_USER}",
      "password": "${ERP_API_PASSWORD}",
      "timeout": 60
    }
  },
  
  "power_bi": {
    "tenant_id": "${POWERBI_TENANT_ID}",
    "client_id": "${POWERBI_CLIENT_ID}",
    "client_secret": "${POWERBI_CLIENT_SECRET}",
    "authority": "https://login.microsoftonline.com",
    "scope": ["https://analysis.windows.net/powerbi/api/.default"]
  },
  
  "sharepoint": {
    "site_url": "${SHAREPOINT_SITE_URL}",
    "client_id": "${SHAREPOINT_CLIENT_ID}",
    "client_secret": "${SHAREPOINT_CLIENT_SECRET}",
    "tenant_id": "${SHAREPOINT_TENANT_ID}"
  },
  
  "file_paths": {
    "data_root": "data/raw",
    "backup_root": "data/backup",
    "archive_root": "data/archive"
  }
}
```

---

## 🔐 Arquivo: .env (Credenciais)

Todas as credenciais sensíveis devem estar no arquivo `.env`:

```bash
# ===== SQL SERVER =====
SQL_SERVER_USERNAME=usuario_sql
SQL_SERVER_PASSWORD=senha_super_secreta_123

# ===== APIs =====
API_ANALYTICS_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
ERP_API_USER=api_user
ERP_API_PASSWORD=senha_erp_456

# ===== POWER BI =====
POWERBI_TENANT_ID=12345678-1234-1234-1234-123456789abc
POWERBI_CLIENT_ID=87654321-4321-4321-4321-cba987654321
POWERBI_CLIENT_SECRET=cliente_secreto_powerbi

# ===== SHAREPOINT =====
SHAREPOINT_SITE_URL=https://empresa.sharepoint.com/sites/dados
SHAREPOINT_CLIENT_ID=sharepoint-client-id
SHAREPOINT_CLIENT_SECRET=sharepoint-client-secret
SHAREPOINT_TENANT_ID=tenant-id-sharepoint

# ===== ALERTAS =====
ALERT_EMAIL_TO=gerente@empresa.com,diretor@empresa.com
SMTP_USER=cortexbi@empresa.com
SMTP_PASSWORD=senha_email_789
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/seu-webhook
```

---

## 🎯 Exemplos Práticos Completos

### Exemplo 1: Monitorar Vendas do SQL Server

**1. Configurar conexão** (`data_sources.json`):

```json
{
  "connections": {
    "sql_vendas": {
      "type": "sql_server",
      "host": "vendas.database.windows.net",
      "database": "VendasDB",
      "username": "${SQL_VENDAS_USER}",
      "password": "${SQL_VENDAS_PASS}"
    }
  }
}
```

**2. Adicionar credenciais** (`.env`):

```bash
SQL_VENDAS_USER=vendas_user
SQL_VENDAS_PASS=senha123
```

**3. Configurar métrica** (`metrics_config.json`):

```json
{
  "metrics": [
    {
      "id": "vendas_diarias",
      "name": "Vendas Diárias",
      "enabled": true,
      
      "data_source": {
        "type": "sql_server",
        "connection_id": "sql_vendas",
        "query": "SELECT SUM(valor_venda) as total FROM vendas WHERE CAST(data_venda AS DATE) = CAST(GETDATE() AS DATE)",
        "value_column": "total"
      },
      
      "historical_data": {
        "query": "SELECT CAST(data_venda AS DATE) as data, SUM(valor_venda) as total FROM vendas WHERE data_venda >= DATEADD(day, -30, GETDATE()) GROUP BY CAST(data_venda AS DATE)",
        "min_samples": 30
      },
      
      "alert_config": {
        "severity": "high",
        "threshold_type": "percentage",
        "threshold_value": 15,
        "channels": ["email"],
        "recipients": ["gerente@empresa.com"]
      },
      
      "monitoring": {
        "check_interval": 3600
      }
    }
  ]
}
```

### Exemplo 2: Monitorar CSV de Custos

**1. Preparar arquivo CSV** (`data/raw/custos.csv`):

```csv
data,custo_total,categoria
2025-10-01,45000,Operacional
2025-10-02,47000,Operacional
2025-10-03,44500,Operacional
```

**2. Configurar métrica** (`metrics_config.json`):

```json
{
  "metrics": [
    {
      "id": "custos_operacionais",
      "name": "Custos Operacionais",
      "enabled": true,
      
      "data_source": {
        "type": "csv",
        "file_path": "data/raw/custos.csv",
        "value_column": "custo_total",
        "timestamp_column": "data"
      },
      
      "historical_data": {
        "source": "same_file",
        "min_samples": 30
      },
      
      "alert_config": {
        "severity": "medium",
        "threshold_type": "absolute",
        "threshold_value": 50000,
        "channels": ["email"],
        "recipients": ["controller@empresa.com"]
      },
      
      "monitoring": {
        "check_interval": 7200
      }
    }
  ]
}
```

### Exemplo 3: Monitorar API Externa

**1. Configurar conexão** (`data_sources.json`):

```json
{
  "connections": {
    "api_analytics": {
      "type": "api",
      "base_url": "https://api.analytics.com",
      "auth_type": "bearer",
      "token": "${ANALYTICS_TOKEN}"
    }
  }
}
```

**2. Adicionar token** (`.env`):

```bash
ANALYTICS_TOKEN=seu-token-aqui
```

**3. Configurar métrica** (`metrics_config.json`):

```json
{
  "metrics": [
    {
      "id": "taxa_conversao",
      "name": "Taxa de Conversão",
      "enabled": true,
      
      "data_source": {
        "type": "api",
        "url": "https://api.analytics.com/conversao/hoje",
        "method": "GET",
        "headers": {
          "Authorization": "Bearer ${ANALYTICS_TOKEN}"
        },
        "response_path": "data.taxa"
      },
      
      "historical_data": {
        "api_url": "https://api.analytics.com/conversao/historico",
        "api_params": {"dias": 30},
        "response_path": "data.historico"
      },
      
      "alert_config": {
        "severity": "high",
        "threshold_type": "percentage",
        "threshold_value": 10,
        "channels": ["teams"],
        "recipients": ["marketing@empresa.com"]
      },
      
      "monitoring": {
        "check_interval": 1800
      }
    }
  ]
}
```

---

## ✅ Checklist de Configuração

Use este checklist para garantir que tudo está configurado:

### 1. Estrutura de Diretórios
- [ ] `config/anomaly_rules/` existe
- [ ] `data/raw/` existe
- [ ] `data/anomalies/` existe
- [ ] `logs/anomalies/` existe

### 2. Arquivos de Configuração
- [ ] `metrics_config.json` criado
- [ ] `data_sources.json` criado
- [ ] `.env` configurado com credenciais

### 3. Fontes de Dados
- [ ] Conexões SQL Server testadas
- [ ] Arquivos CSV/Excel no lugar correto
- [ ] APIs acessíveis e autenticadas
- [ ] Power BI configurado (se aplicável)

### 4. Métricas
- [ ] Pelo menos 1 métrica configurada
- [ ] Query SQL validada (se SQL Server)
- [ ] Colunas corretas especificadas
- [ ] Dados históricos disponíveis (mínimo 30 dias)

### 5. Alertas
- [ ] Email configurado (SMTP)
- [ ] Teams webhook configurado (se aplicável)
- [ ] Destinatários definidos
- [ ] Templates de alerta personalizados (opcional)

### 6. Testes
- [ ] Conexão com fonte de dados testada
- [ ] Query retorna dados válidos
- [ ] Modelo de ML treinado
- [ ] Alerta de teste enviado com sucesso

---

## 🧪 Scripts de Teste

### Testar Conexão SQL Server

```python
# test_sql_connection.py

import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

connection_string = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={os.getenv('SQL_SERVER_HOST')};"
    f"DATABASE={os.getenv('SQL_SERVER_DATABASE')};"
    f"UID={os.getenv('SQL_SERVER_USERNAME')};"
    f"PWD={os.getenv('SQL_SERVER_PASSWORD')}"
)

try:
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    
    # Testar query
    query = "SELECT SUM(valor_venda) as total FROM vendas WHERE CAST(data_venda AS DATE) = CAST(GETDATE() AS DATE)"
    cursor.execute(query)
    result = cursor.fetchone()
    
    print(f"✅ Conexão bem-sucedida!")
    print(f"📊 Resultado da query: {result[0]}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Erro na conexão: {e}")
```

### Testar Leitura de CSV

```python
# test_csv_reading.py

import pandas as pd

try:
    df = pd.read_csv("data/raw/custos.csv")
    
    print(f"✅ Arquivo CSV lido com sucesso!")
    print(f"📊 Linhas: {len(df)}")
    print(f"📊 Colunas: {list(df.columns)}")
    print(f"\nÚltimos 5 registros:")
    print(df.tail())
    
    # Testar coluna de valor
    valor_atual = df['custo_total'].iloc[-1]
    print(f"\n💰 Valor atual: {valor_atual}")
    
except Exception as e:
    print(f"❌ Erro ao ler CSV: {e}")
```

### Testar API

```python
# test_api_connection.py

import requests
import os
from dotenv import load_dotenv

load_dotenv()

url = "https://api.analytics.com/conversao/hoje"
headers = {
    "Authorization": f"Bearer {os.getenv('ANALYTICS_TOKEN')}",
    "Content-Type": "application/json"
}

try:
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    
    data = response.json()
    
    print(f"✅ API acessível!")
    print(f"📊 Status: {response.status_code}")
    print(f"📊 Resposta:")
    print(data)
    
except Exception as e:
    print(f"❌ Erro ao acessar API: {e}")
```

### Testar Configuração Completa

```python
# test_full_config.py

import json
import os
from pathlib import Path

def test_configuration():
    """Testa toda a configuração"""
    
    print("🔍 Verificando configuração...\n")
    
    # 1. Verificar estrutura de diretórios
    print("1️⃣ Verificando diretórios...")
    dirs = [
        "config/anomaly_rules",
        "data/raw",
        "data/anomalies",
        "logs/anomalies"
    ]
    for dir_path in dirs:
        if Path(dir_path).exists():
            print(f"   ✅ {dir_path}")
        else:
            print(f"   ❌ {dir_path} - NÃO EXISTE!")
    
    # 2. Verificar arquivos de configuração
    print("\n2️⃣ Verificando arquivos de configuração...")
    files = [
        "config/anomaly_rules/metrics_config.json",
        "config/anomaly_rules/data_sources.json",
        ".env"
    ]
    for file_path in files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - NÃO EXISTE!")
    
    # 3. Validar metrics_config.json
    print("\n3️⃣ Validando metrics_config.json...")
    try:
        with open("config/anomaly_rules/metrics_config.json", 'r') as f:
            config = json.load(f)
        
        metrics = config.get('metrics', [])
        print(f"   ✅ Arquivo válido")
        print(f"   📊 Métricas configuradas: {len(metrics)}")
        
        for metric in metrics:
            status = "✅ Habilitada" if metric.get('enabled') else "⏸️  Desabilitada"
            print(f"      - {metric.get('name')}: {status}")
        
    except Exception as e:
        print(f"   ❌ Erro ao validar: {e}")
    
    # 4. Verificar variáveis de ambiente
    print("\n4️⃣ Verificando variáveis de ambiente...")
    from dotenv import load_dotenv
    load_dotenv()
    
    env_vars = [
        "SQL_SERVER_USERNAME",
        "ALERT_EMAIL_TO",
        "ANOMALY_DETECTION_ENABLED"
    ]
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var} = {'*' * len(value)}")
        else:
            print(f"   ⚠️  {var} - NÃO DEFINIDA")
    
    print("\n✅ Verificação completa!")

if __name__ == "__main__":
    test_configuration()
```

Execute:

```bash
python test_full_config.py
```

---

## 📞 Resumo

**A configuração da fonte de dados está em:**

1. **`config/anomaly_rules/metrics_config.json`** → Define QUAIS métricas monitorar e ONDE buscar os dados
2. **`config/anomaly_rules/data_sources.json`** → Define conexões reutilizáveis (SQL, APIs, etc.)
3. **`.env`** → Armazena credenciais sensíveis (senhas, tokens, etc.)

**Cada métrica precisa especificar:**
- `data_source` → De onde vem o dado atual
- `historical_data` → De onde vem o histórico para comparação
- `alert_config` → Como alertar quando anomalia for detectada
- `monitoring` → Com que frequência verificar

---

**CÓRTEX BI v2.0** - *Cognitive Operations & Real-Time EXpert Business Intelligence*  
Desenvolvido em parceria com **Manus AI** | Outubro 2025

📊 **Fontes de Dados Configuradas = Anomalias Detectadas**

