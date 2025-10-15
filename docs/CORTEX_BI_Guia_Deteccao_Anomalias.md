# 🔍 CÓRTEX BI - Guia Completo de Detecção Proativa de Anomalias

**Versão:** 2.0  
**Data:** Outubro 2025  
**Desenvolvido em parceria com:** Manus AI

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Como Funciona](#como-funciona)
3. [Configuração Inicial](#configuração-inicial)
4. [Treinamento do Modelo](#treinamento-do-modelo)
5. [Ativação da Detecção Proativa](#ativação-da-detecção-proativa)
6. [Configuração de Alertas](#configuração-de-alertas)
7. [Monitoramento Contínuo](#monitoramento-contínuo)
8. [Casos de Uso Práticos](#casos-de-uso-práticos)
9. [Ajuste Fino e Otimização](#ajuste-fino-e-otimização)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

O sistema de **Detecção Proativa de Anomalias** do CÓRTEX BI utiliza algoritmos de Machine Learning (especificamente **Isolation Forest**) para identificar automaticamente padrões anormais em seus dados de negócio.

### O que o sistema detecta:

✅ **Quedas súbitas em métricas** - Ex: vendas caíram 15% sem motivo aparente  
✅ **Picos inesperados** - Ex: aumento anormal de custos  
✅ **Padrões atípicos** - Ex: comportamento de compra incomum  
✅ **Desvios de tendência** - Ex: KPI fora da faixa histórica esperada  
✅ **Outliers em dados** - Ex: valores extremos que fogem do padrão  

### Benefícios:

🚀 **Detecção automática** - Não precisa monitorar manualmente  
⚡ **Alertas em tempo real** - Notificação imediata quando anomalia é detectada  
🎯 **Redução de riscos** - Identifica problemas antes que se tornem críticos  
📊 **Insights acionáveis** - Recomendações de ações corretivas  
🔄 **Aprendizado contínuo** - Sistema melhora com o tempo  

---

## 🔧 Como Funciona

### Arquitetura do Sistema

O sistema de detecção de anomalias é composto por três componentes principais:

```
┌─────────────────────────────────────────────────────────┐
│                    CÓRTEX BI                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐    ┌──────────────┐   ┌───────────┐ │
│  │  ML Engine   │───▶│   Anomaly    │──▶│  Alert    │ │
│  │              │    │   Detector   │   │  System   │ │
│  └──────────────┘    └──────────────┘   └───────────┘ │
│         │                    │                  │      │
│         ▼                    ▼                  ▼      │
│  ┌──────────────┐    ┌──────────────┐   ┌───────────┐ │
│  │  Training    │    │  Real-time   │   │  Notifi-  │ │
│  │  Data        │    │  Monitoring  │   │  cation   │ │
│  └──────────────┘    └──────────────┘   └───────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Algoritmo Isolation Forest

O CÓRTEX BI utiliza o algoritmo **Isolation Forest**, que funciona assim:

1. **Treinamento**: Aprende o comportamento "normal" dos seus dados históricos
2. **Isolamento**: Identifica pontos que são facilmente "isolados" (anômalos)
3. **Score**: Atribui um score de anomalia (-1 = anômalo, 1 = normal)
4. **Threshold**: Define limiar de sensibilidade para alertas

**Vantagens do Isolation Forest:**
- ✅ Não requer dados rotulados (unsupervised learning)
- ✅ Eficiente com grandes volumes de dados
- ✅ Detecta anomalias multidimensionais
- ✅ Baixo custo computacional

---

## ⚙️ Configuração Inicial

### Passo 1: Verificar Pré-requisitos

Certifique-se de que o CÓRTEX BI está instalado e rodando:

```bash
# Verificar status do sistema
curl http://localhost:5000/health

# Resposta esperada deve incluir:
{
  "services": {
    "ml_engine": "active",
    ...
  }
}
```

### Passo 2: Configurar Variáveis de Ambiente

Edite o arquivo `.env` na raiz do projeto:

```bash
# ===== MACHINE LEARNING =====
ML_ENABLED=True
ML_MODEL_PATH=data/models/

# ===== DETECÇÃO DE ANOMALIAS =====
ANOMALY_DETECTION_ENABLED=True
ANOMALY_CONTAMINATION=0.1        # 10% dos dados são considerados potenciais anomalias
ANOMALY_THRESHOLD=-0.5           # Score abaixo deste valor é considerado anomalia
ANOMALY_MIN_SAMPLES=20           # Mínimo de amostras para treinar o modelo
ANOMALY_RETRAIN_INTERVAL=86400   # Retreinar a cada 24 horas (em segundos)

# ===== MONITORAMENTO PROATIVO =====
PROACTIVE_MONITORING_ENABLED=True
MONITORING_INTERVAL=300          # Verificar a cada 5 minutos (em segundos)
MONITORING_METRICS=vendas,custos,receita,lucro  # Métricas para monitorar

# ===== ALERTAS =====
ALERT_ENABLED=True
ALERT_CHANNELS=email,teams,webhook  # Canais de notificação
ALERT_SEVERITY_THRESHOLD=medium     # low, medium, high, critical

# ===== EMAIL (para alertas) =====
ALERT_EMAIL_TO=gerente@empresa.com,diretor@empresa.com
ALERT_EMAIL_FROM=cortexbi-alerts@empresa.com
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USER=cortexbi@empresa.com
SMTP_PASSWORD=sua-senha

# ===== MICROSOFT TEAMS (para alertas) =====
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/seu-webhook-url

# ===== WEBHOOK CUSTOMIZADO =====
CUSTOM_WEBHOOK_URL=https://seu-sistema.com/api/alerts
CUSTOM_WEBHOOK_AUTH_TOKEN=seu-token-de-autenticacao
```

### Passo 3: Criar Estrutura de Diretórios

```bash
# Criar diretórios necessários
mkdir -p data/models
mkdir -p data/anomalies
mkdir -p logs/anomalies
mkdir -p config/anomaly_rules

# Configurar permissões
chmod 755 data/models data/anomalies logs/anomalies config/anomaly_rules
```

### Passo 4: Reiniciar o Sistema

```bash
# Parar o servidor
./scripts/stop_ai.sh  # Linux/macOS
# ou
.\scripts\stop_ai.bat  # Windows

# Iniciar o servidor
./scripts/start_ai.sh  # Linux/macOS
# ou
.\scripts\start_ai.bat  # Windows
```

---

## 🎓 Treinamento do Modelo

### Método 1: Treinamento Automático via API

O método mais simples é usar a API para treinar o modelo:

```bash
# Treinar o detector de anomalias
curl -X POST "http://localhost:5000/ml/train/anomaly_detector" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-api-key" \
  -d '{
    "retrain": true,
    "contamination": 0.1
  }'
```

**Resposta esperada:**

```json
{
  "status": "success",
  "model": "anomaly_detector",
  "metrics": {
    "anomaly_rate": 0.095,
    "training_samples": 1250,
    "features": 5,
    "trained_at": "2025-10-14T18:30:00.000000"
  },
  "message": "Modelo treinado com sucesso"
}
```

### Método 2: Treinamento via Python Script

Crie um script personalizado para treinar o modelo:

```python
# train_anomaly_detector.py

from src.agents.ml_engine import MLEngine
import json

# Inicializar ML Engine
ml_engine = MLEngine(models_dir="data/models")

# Treinar detector de anomalias
print("Iniciando treinamento do detector de anomalias...")
metrics = ml_engine.train_anomaly_detector(retrain=True)

print("\nResultados do treinamento:")
print(json.dumps(metrics, indent=2))

if "error" not in metrics:
    print("\n✅ Modelo treinado com sucesso!")
    print(f"📊 Amostras de treinamento: {metrics['training_samples']}")
    print(f"🎯 Taxa de anomalia: {metrics['anomaly_rate']:.2%}")
else:
    print(f"\n❌ Erro no treinamento: {metrics['error']}")
```

Execute o script:

```bash
python train_anomaly_detector.py
```

### Método 3: Treinamento Agendado (Automático)

Configure o treinamento automático periódico:

**Linux/macOS (usando cron):**

```bash
# Editar crontab
crontab -e

# Adicionar linha para retreinar diariamente às 2h da manhã
0 2 * * * cd /caminho/para/cortex-bi && python train_anomaly_detector.py >> logs/training.log 2>&1
```

**Windows (usando Task Scheduler):**

```powershell
# Criar tarefa agendada
$action = New-ScheduledTaskAction -Execute "python" -Argument "C:\caminho\para\cortex-bi\train_anomaly_detector.py"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "CORTEX_BI_Train_Anomaly" -Description "Retreinar detector de anomalias diariamente"
```

### Verificar Status do Modelo

```bash
# Verificar se o modelo foi treinado
curl -X GET "http://localhost:5000/ml/models/status" \
  -H "X-API-Key: sua-api-key"
```

**Resposta:**

```json
{
  "models": {
    "anomaly_detector": {
      "trained": true,
      "last_training": "2025-10-14T02:00:00.000000",
      "samples": 1250,
      "accuracy": 0.95
    }
  }
}
```

---

## 🚀 Ativação da Detecção Proativa

### Configurar Métricas para Monitoramento

Crie um arquivo de configuração para definir quais métricas monitorar:

```bash
# Criar arquivo de configuração
nano config/anomaly_rules/metrics_config.json
```

**Conteúdo do arquivo:**

```json
{
  "metrics": [
    {
      "name": "vendas_totais",
      "data_source": "sql_server",
      "query": "SELECT SUM(valor_venda) as total FROM vendas WHERE data = CAST(GETDATE() AS DATE)",
      "threshold_type": "percentage",
      "threshold_value": 15,
      "severity": "high",
      "check_interval": 300,
      "enabled": true
    },
    {
      "name": "custos_operacionais",
      "data_source": "csv",
      "file_path": "data/custos_diarios.csv",
      "column": "custo_total",
      "threshold_type": "absolute",
      "threshold_value": 50000,
      "severity": "medium",
      "check_interval": 600,
      "enabled": true
    },
    {
      "name": "taxa_conversao",
      "data_source": "api",
      "api_endpoint": "https://api.empresa.com/metrics/conversao",
      "threshold_type": "percentage",
      "threshold_value": 10,
      "severity": "high",
      "check_interval": 300,
      "enabled": true
    },
    {
      "name": "tempo_resposta_sistema",
      "data_source": "internal",
      "metric_key": "avg_response_time",
      "threshold_type": "absolute",
      "threshold_value": 5000,
      "severity": "critical",
      "check_interval": 60,
      "enabled": true
    }
  ],
  "global_settings": {
    "min_historical_days": 30,
    "confidence_threshold": 0.8,
    "alert_cooldown": 3600
  }
}
```

### Iniciar Monitoramento Proativo

**Método 1: Via API**

```bash
# Iniciar monitoramento
curl -X POST "http://localhost:5000/anomaly/monitoring/start" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-api-key" \
  -d '{
    "config_file": "config/anomaly_rules/metrics_config.json",
    "interval": 300
  }'
```

**Método 2: Via Script Python**

Crie um script de monitoramento contínuo:

```python
# start_proactive_monitoring.py

import time
import requests
import json
from datetime import datetime
from src.agents.ml_engine import MLEngine
from src.agents.analytics_engine import AnalyticsEngine

class ProactiveAnomalyMonitor:
    def __init__(self, config_file: str):
        self.ml_engine = MLEngine()
        self.analytics_engine = AnalyticsEngine()
        
        # Carregar configuração
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        self.metrics = self.config['metrics']
        self.global_settings = self.config['global_settings']
        
        print(f"✅ Monitor inicializado com {len(self.metrics)} métricas")
    
    def check_metric(self, metric_config: dict):
        """Verifica uma métrica específica"""
        try:
            # Obter valor atual da métrica
            current_value = self._get_metric_value(metric_config)
            
            # Obter histórico
            historical_data = self._get_historical_data(metric_config)
            
            # Detectar anomalia usando ML Engine
            result = self.ml_engine.detect_anomaly({
                "metric_name": metric_config['name'],
                "current_value": current_value,
                "historical_data": historical_data,
                "execution_time": 0,
                "request_data": json.dumps(metric_config),
                "response_data": json.dumps({"value": current_value}),
                "user_id": "system"
            })
            
            if result.get("is_anomaly"):
                self._trigger_alert(metric_config, current_value, result)
            
            return result
            
        except Exception as e:
            print(f"❌ Erro ao verificar métrica {metric_config['name']}: {e}")
            return {"error": str(e)}
    
    def _get_metric_value(self, metric_config: dict):
        """Obtém valor atual da métrica"""
        data_source = metric_config['data_source']
        
        if data_source == "sql_server":
            # Executar query SQL
            from src.agents.data_loader import DataLoader
            loader = DataLoader()
            result = loader.query_sql_server(metric_config['query'])
            return result[0]['total'] if result else 0
            
        elif data_source == "csv":
            # Ler arquivo CSV
            import pandas as pd
            df = pd.read_csv(metric_config['file_path'])
            return df[metric_config['column']].iloc[-1]
            
        elif data_source == "api":
            # Chamar API externa
            response = requests.get(metric_config['api_endpoint'])
            return response.json().get('value', 0)
            
        elif data_source == "internal":
            # Métrica interna do sistema
            return self._get_internal_metric(metric_config['metric_key'])
        
        return 0
    
    def _get_historical_data(self, metric_config: dict, days: int = 30):
        """Obtém dados históricos da métrica"""
        # Implementar lógica para obter histórico
        # Por enquanto, retorna lista vazia
        return []
    
    def _get_internal_metric(self, metric_key: str):
        """Obtém métrica interna do sistema"""
        # Implementar lógica para métricas internas
        return 0
    
    def _trigger_alert(self, metric_config: dict, current_value: float, anomaly_result: dict):
        """Dispara alerta de anomalia"""
        alert_data = {
            "timestamp": datetime.now().isoformat(),
            "metric_name": metric_config['name'],
            "current_value": current_value,
            "severity": metric_config['severity'],
            "anomaly_score": anomaly_result.get('anomaly_score'),
            "confidence": anomaly_result.get('confidence'),
            "message": f"Anomalia detectada em {metric_config['name']}: valor atual {current_value}"
        }
        
        print(f"\n🚨 ALERTA DE ANOMALIA:")
        print(json.dumps(alert_data, indent=2))
        
        # Enviar alertas
        self._send_email_alert(alert_data)
        self._send_teams_alert(alert_data)
        self._send_webhook_alert(alert_data)
    
    def _send_email_alert(self, alert_data: dict):
        """Envia alerta por email"""
        # Implementar envio de email
        pass
    
    def _send_teams_alert(self, alert_data: dict):
        """Envia alerta para Microsoft Teams"""
        # Implementar envio para Teams
        pass
    
    def _send_webhook_alert(self, alert_data: dict):
        """Envia alerta para webhook customizado"""
        # Implementar envio para webhook
        pass
    
    def run(self):
        """Executa monitoramento contínuo"""
        print("\n🚀 Iniciando monitoramento proativo de anomalias...")
        print(f"📊 Monitorando {len(self.metrics)} métricas")
        
        while True:
            for metric in self.metrics:
                if not metric.get('enabled', True):
                    continue
                
                print(f"\n🔍 Verificando: {metric['name']}")
                result = self.check_metric(metric)
                
                if result.get("is_anomaly"):
                    print(f"⚠️  Anomalia detectada!")
                else:
                    print(f"✅ Normal")
                
                # Aguardar intervalo específico da métrica
                time.sleep(metric.get('check_interval', 300))

# Executar monitor
if __name__ == "__main__":
    monitor = ProactiveAnomalyMonitor("config/anomaly_rules/metrics_config.json")
    monitor.run()
```

Execute o script:

```bash
# Executar em background
nohup python start_proactive_monitoring.py > logs/anomalies/monitor.log 2>&1 &

# Ver logs em tempo real
tail -f logs/anomalies/monitor.log
```

---

## 📧 Configuração de Alertas

### Alertas por Email

Configure o envio de emails no arquivo `.env`:

```bash
ALERT_EMAIL_ENABLED=True
ALERT_EMAIL_TO=gerente@empresa.com,diretor@empresa.com
ALERT_EMAIL_CC=ti@empresa.com
ALERT_EMAIL_FROM=cortexbi-alerts@empresa.com
ALERT_EMAIL_SUBJECT_PREFIX=[CÓRTEX BI - ALERTA]

SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USE_TLS=True
SMTP_USER=cortexbi@empresa.com
SMTP_PASSWORD=sua-senha
```

**Template de email personalizado:**

Crie um arquivo `config/anomaly_rules/email_template.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; }
        .alert-box { 
            border: 2px solid #dc3545; 
            padding: 20px; 
            margin: 20px 0;
            background-color: #f8d7da;
        }
        .severity-high { border-color: #dc3545; background-color: #f8d7da; }
        .severity-medium { border-color: #ffc107; background-color: #fff3cd; }
        .severity-low { border-color: #17a2b8; background-color: #d1ecf1; }
        .metric-value { font-size: 24px; font-weight: bold; color: #dc3545; }
    </style>
</head>
<body>
    <h2>🚨 Alerta de Anomalia Detectada</h2>
    
    <div class="alert-box severity-{{severity}}">
        <h3>{{metric_name}}</h3>
        <p><strong>Valor Atual:</strong> <span class="metric-value">{{current_value}}</span></p>
        <p><strong>Severidade:</strong> {{severity}}</p>
        <p><strong>Confiança:</strong> {{confidence}}%</p>
        <p><strong>Data/Hora:</strong> {{timestamp}}</p>
    </div>
    
    <h3>📊 Detalhes da Anomalia</h3>
    <ul>
        <li><strong>Score de Anomalia:</strong> {{anomaly_score}}</li>
        <li><strong>Desvio do Padrão:</strong> {{deviation}}%</li>
        <li><strong>Valor Esperado:</strong> {{expected_value}}</li>
    </ul>
    
    <h3>💡 Recomendações</h3>
    <ul>
        {{#each recommendations}}
        <li>{{this}}</li>
        {{/each}}
    </ul>
    
    <hr>
    <p><small>Este é um alerta automático do CÓRTEX BI. Para mais informações, acesse o dashboard administrativo.</small></p>
</body>
</html>
```

### Alertas no Microsoft Teams

Configure o webhook do Teams:

```bash
# No arquivo .env
ALERT_TEAMS_ENABLED=True
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/seu-webhook-url
```

**Criar webhook no Teams:**

1. Abra o canal do Teams onde deseja receber alertas
2. Clique nos três pontos (⋯) → "Connectors"
3. Procure por "Incoming Webhook" e clique em "Configure"
4. Dê um nome (ex: "CÓRTEX BI Alertas") e clique em "Create"
5. Copie a URL do webhook gerada
6. Cole no arquivo `.env`

**Template de mensagem Teams:**

```json
{
  "@type": "MessageCard",
  "@context": "https://schema.org/extensions",
  "summary": "Anomalia Detectada",
  "themeColor": "dc3545",
  "title": "🚨 CÓRTEX BI - Alerta de Anomalia",
  "sections": [
    {
      "activityTitle": "{{metric_name}}",
      "activitySubtitle": "Severidade: {{severity}}",
      "facts": [
        {
          "name": "Valor Atual:",
          "value": "{{current_value}}"
        },
        {
          "name": "Confiança:",
          "value": "{{confidence}}%"
        },
        {
          "name": "Data/Hora:",
          "value": "{{timestamp}}"
        }
      ]
    }
  ],
  "potentialAction": [
    {
      "@type": "OpenUri",
      "name": "Ver Dashboard",
      "targets": [
        {
          "os": "default",
          "uri": "http://localhost:5000/admin/admin_dashboard.html"
        }
      ]
    }
  ]
}
```

### Alertas via Webhook Customizado

Para integrar com sistemas próprios:

```bash
# No arquivo .env
ALERT_WEBHOOK_ENABLED=True
CUSTOM_WEBHOOK_URL=https://seu-sistema.com/api/alerts
CUSTOM_WEBHOOK_METHOD=POST
CUSTOM_WEBHOOK_AUTH_TYPE=bearer  # ou 'basic', 'api_key'
CUSTOM_WEBHOOK_AUTH_TOKEN=seu-token
```

**Payload enviado:**

```json
{
  "source": "cortex_bi",
  "alert_type": "anomaly_detection",
  "timestamp": "2025-10-14T18:30:00.000000",
  "severity": "high",
  "metric": {
    "name": "vendas_totais",
    "current_value": 85000,
    "expected_value": 100000,
    "deviation_percentage": -15
  },
  "anomaly": {
    "score": -0.75,
    "confidence": 0.92,
    "is_anomaly": true
  },
  "recommendations": [
    "Verificar campanhas de marketing ativas",
    "Analisar concorrência",
    "Revisar estratégia de preços"
  ]
}
```

---

## 📊 Monitoramento Contínuo

### Dashboard de Anomalias

Acesse o dashboard específico de anomalias:

```
http://localhost:5000/admin/anomalies_dashboard.html
```

**Funcionalidades do Dashboard:**

- 📈 Gráfico de anomalias detectadas ao longo do tempo
- 🎯 Métricas mais afetadas
- 📊 Distribuição de severidade
- 🔔 Histórico de alertas
- ⚙️ Configuração de regras
- 📥 Exportar relatórios

### API de Monitoramento

**Listar anomalias detectadas:**

```bash
curl -X GET "http://localhost:5000/anomaly/list?days=7" \
  -H "X-API-Key: sua-api-key"
```

**Verificar métrica específica:**

```bash
curl -X POST "http://localhost:5000/anomaly/check" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-api-key" \
  -d '{
    "metric_name": "vendas_totais",
    "current_value": 85000,
    "historical_data": [100000, 98000, 102000, 99000, 101000]
  }'
```

**Status do monitoramento:**

```bash
curl -X GET "http://localhost:5000/anomaly/monitoring/status" \
  -H "X-API-Key: sua-api-key"
```

---

## 💼 Casos de Uso Práticos

### Caso 1: Monitorar Vendas Diárias

**Objetivo:** Detectar quedas inesperadas nas vendas

**Configuração:**

```json
{
  "name": "vendas_diarias",
  "data_source": "sql_server",
  "query": "SELECT SUM(valor_venda) as total FROM vendas WHERE data = CAST(GETDATE() AS DATE)",
  "threshold_type": "percentage",
  "threshold_value": 10,
  "severity": "high",
  "check_interval": 3600,
  "enabled": true,
  "alert_channels": ["email", "teams"],
  "recipients": ["gerente.vendas@empresa.com"]
}
```

**Resultado:**
- Sistema verifica vendas a cada hora
- Se vendas caírem mais de 10%, dispara alerta
- Gerente de vendas recebe email e notificação no Teams

### Caso 2: Monitorar Custos Operacionais

**Objetivo:** Identificar picos anormais de custos

**Configuração:**

```json
{
  "name": "custos_operacionais",
  "data_source": "csv",
  "file_path": "data/custos_diarios.csv",
  "column": "custo_total",
  "threshold_type": "absolute",
  "threshold_value": 50000,
  "severity": "medium",
  "check_interval": 7200,
  "enabled": true,
  "alert_channels": ["email"],
  "recipients": ["controller@empresa.com"]
}
```

**Resultado:**
- Sistema verifica custos a cada 2 horas
- Se custos ultrapassarem R$ 50.000, dispara alerta
- Controller recebe email com detalhes

### Caso 3: Monitorar Performance do Sistema

**Objetivo:** Detectar degradação de performance

**Configuração:**

```json
{
  "name": "tempo_resposta_api",
  "data_source": "internal",
  "metric_key": "avg_response_time",
  "threshold_type": "absolute",
  "threshold_value": 5000,
  "severity": "critical",
  "check_interval": 60,
  "enabled": true,
  "alert_channels": ["teams", "webhook"],
  "recipients": ["ti@empresa.com"]
}
```

**Resultado:**
- Sistema verifica performance a cada minuto
- Se tempo de resposta > 5 segundos, dispara alerta crítico
- TI recebe notificação imediata no Teams

---

## 🎛️ Ajuste Fino e Otimização

### Ajustar Sensibilidade

A sensibilidade do detector pode ser ajustada através do parâmetro `contamination`:

```python
# Mais sensível (detecta mais anomalias)
contamination = 0.05  # 5% dos dados são anomalias

# Sensibilidade padrão
contamination = 0.1   # 10% dos dados são anomalias

# Menos sensível (detecta apenas anomalias muito evidentes)
contamination = 0.2   # 20% dos dados são anomalias
```

**Via API:**

```bash
curl -X POST "http://localhost:5000/ml/train/anomaly_detector" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-api-key" \
  -d '{
    "retrain": true,
    "contamination": 0.05
  }'
```

### Ajustar Threshold de Alerta

```bash
# No arquivo .env
ANOMALY_THRESHOLD=-0.5   # Padrão
ANOMALY_THRESHOLD=-0.3   # Mais sensível (mais alertas)
ANOMALY_THRESHOLD=-0.7   # Menos sensível (menos alertas)
```

### Filtrar Falsos Positivos

Crie regras para ignorar falsos positivos conhecidos:

```json
{
  "false_positive_rules": [
    {
      "metric_name": "vendas_totais",
      "condition": "day_of_week == 0",
      "reason": "Domingos sempre têm vendas baixas"
    },
    {
      "metric_name": "acessos_sistema",
      "condition": "hour >= 22 or hour <= 6",
      "reason": "Baixo acesso durante madrugada é normal"
    }
  ]
}
```

### Retreinamento Automático

Configure retreinamento periódico para manter o modelo atualizado:

```bash
# No arquivo .env
ANOMALY_AUTO_RETRAIN=True
ANOMALY_RETRAIN_INTERVAL=86400      # 24 horas
ANOMALY_RETRAIN_MIN_NEW_SAMPLES=100  # Mínimo de novas amostras para retreinar
```

---

## 🔍 Troubleshooting

### Problema: Modelo não detecta anomalias óbvias

**Possíveis causas:**
- Threshold muito alto
- Contamination muito alta
- Dados de treinamento insuficientes

**Soluções:**

```bash
# 1. Ajustar threshold
ANOMALY_THRESHOLD=-0.3  # Mais sensível

# 2. Ajustar contamination
curl -X POST "http://localhost:5000/ml/train/anomaly_detector" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-api-key" \
  -d '{"retrain": true, "contamination": 0.05}'

# 3. Verificar quantidade de dados de treinamento
curl -X GET "http://localhost:5000/ml/models/status" \
  -H "X-API-Key: sua-api-key"
```

### Problema: Muitos falsos positivos

**Possíveis causas:**
- Threshold muito baixo
- Contamination muito baixa
- Dados de treinamento não representativos

**Soluções:**

```bash
# 1. Ajustar threshold
ANOMALY_THRESHOLD=-0.7  # Menos sensível

# 2. Ajustar contamination
curl -X POST "http://localhost:5000/ml/train/anomaly_detector" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-api-key" \
  -d '{"retrain": true, "contamination": 0.15}'

# 3. Adicionar regras de falsos positivos
# Editar config/anomaly_rules/false_positive_rules.json
```

### Problema: Alertas não estão sendo enviados

**Verificações:**

```bash
# 1. Verificar se alertas estão habilitados
grep ALERT_ENABLED .env

# 2. Verificar logs de alertas
tail -f logs/anomalies/alerts.log

# 3. Testar envio de email
curl -X POST "http://localhost:5000/admin/test/email" \
  -H "X-API-Key: sua-api-key"

# 4. Testar webhook do Teams
curl -X POST "http://localhost:5000/admin/test/teams" \
  -H "X-API-Key: sua-api-key"
```

### Problema: Alto uso de CPU/memória

**Soluções:**

```bash
# 1. Aumentar intervalo de verificação
MONITORING_INTERVAL=600  # 10 minutos em vez de 5

# 2. Reduzir número de métricas monitoradas
# Editar config/anomaly_rules/metrics_config.json
# Desabilitar métricas menos críticas

# 3. Limitar histórico de dados
ANOMALY_HISTORICAL_DAYS=30  # Em vez de 90
```

---

## 📞 Suporte e Recursos

### Documentação Adicional

- **README Principal**: `/docs/README.md`
- **API Reference**: `http://localhost:5000/docs`
- **Guia de Instalação**: `/docs/guia_instalacao.md`

### Scripts Úteis

- `train_anomaly_detector.py` - Treinar modelo
- `start_proactive_monitoring.py` - Iniciar monitoramento
- `test_anomaly_detection.py` - Testar detecção
- `export_anomalies_report.py` - Exportar relatório

### Contato

- **GitHub Issues**: https://github.com/Rimkus85/cortex-bi/issues
- **Email**: suporte@cortexbi.com

---

**CÓRTEX BI v2.0** - *Cognitive Operations & Real-Time EXpert Business Intelligence*  
Desenvolvido em parceria com **Manus AI** | Outubro 2025

🚨 **Detecção Proativa de Anomalias**  
Identifique problemas antes que se tornem críticos!

