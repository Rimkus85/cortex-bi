# 🛠️ CÓRTEX BI - Guia Completo de Instalação, Configuração e Administração

**Versão:** 2.0  
**Data:** Outubro 2025  
**Desenvolvido em parceria com:** Manus AI

---

## 📋 Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Instalação](#instalação)
3. [Configuração Inicial](#configuração-inicial)
4. [Inicialização do Sistema](#inicialização-do-sistema)
5. [Configuração Avançada](#configuração-avançada)
6. [Administração do Sistema](#administração-do-sistema)
7. [Integração Microsoft 365](#integração-microsoft-365)
8. [Monitoramento e Manutenção](#monitoramento-e-manutenção)
9. [Troubleshooting](#troubleshooting)
10. [Segurança e Backup](#segurança-e-backup)

---

## 🔧 Pré-requisitos

### Requisitos de Sistema Operacional

O CÓRTEX BI pode ser instalado nos seguintes sistemas operacionais:

**Linux:**
- Ubuntu 20.04 LTS ou superior
- CentOS 8 ou superior
- Red Hat Enterprise Linux (RHEL) 8 ou superior
- Debian 10 ou superior

**Windows:**
- Windows 10 (versão 1909 ou superior)
- Windows 11
- Windows Server 2019 ou superior

**macOS:**
- macOS 10.15 (Catalina) ou superior
- macOS 11 (Big Sur) ou superior
- macOS 12 (Monterey) ou superior

### Requisitos de Hardware

**Mínimos:**
- Processador: Dual-core 2.0 GHz
- Memória RAM: 4 GB
- Espaço em disco: 10 GB livres
- Conexão de rede: 10 Mbps

**Recomendados:**
- Processador: Quad-core 3.0 GHz ou superior
- Memória RAM: 8 GB ou superior
- Espaço em disco: 20 GB livres (SSD recomendado)
- Conexão de rede: 100 Mbps ou superior

### Software Necessário

**Obrigatório:**
- **Python 3.8 ou superior** (recomendado Python 3.10)
- **pip** (gerenciador de pacotes Python)
- **Git** (para clonar o repositório)

**Opcional (para funcionalidades específicas):**
- **SQL Server** - Para conexão com banco de dados corporativo
- **Power BI Desktop** - Para integração com datasets do Power BI
- **Microsoft 365** - Para integração com Copilot Studio, Teams e SharePoint

### Verificação de Pré-requisitos

Execute os seguintes comandos para verificar se os pré-requisitos estão instalados:

```bash
# Verificar versão do Python
python3 --version
# Deve retornar: Python 3.8.x ou superior

# Verificar pip
pip3 --version

# Verificar Git
git --version

# Verificar espaço em disco (Linux/macOS)
df -h

# Verificar espaço em disco (Windows)
wmic logicaldisk get size,freespace,caption
```

---

## 📥 Instalação

### Método 1: Instalação Automática (Recomendado)

#### Linux / macOS

```bash
# 1. Clonar o repositório
git clone https://github.com/Rimkus85/cortex-bi.git
cd cortex-bi

# 2. Dar permissão de execução ao script
chmod +x scripts/install.sh

# 3. Executar instalação automática
./scripts/install.sh
```

O script automático irá:
- ✅ Verificar versão do Python
- ✅ Criar ambiente virtual Python
- ✅ Instalar todas as dependências
- ✅ Criar diretórios necessários
- ✅ Configurar permissões
- ✅ Validar a instalação

#### Windows

```powershell
# 1. Abrir PowerShell como Administrador

# 2. Clonar o repositório
git clone https://github.com/Rimkus85/cortex-bi.git
cd cortex-bi

# 3. Executar instalação automática
.\scripts\install.bat
```

O script irá:
- ✅ Verificar instalação do Python
- ✅ Criar ambiente virtual
- ✅ Instalar dependências
- ✅ Configurar variáveis de ambiente
- ✅ Criar atalhos para inicialização

### Método 2: Instalação Manual

Se preferir controle total sobre o processo:

```bash
# 1. Clonar o repositório
git clone https://github.com/Rimkus85/cortex-bi.git
cd cortex-bi

# 2. Criar ambiente virtual Python
python3 -m venv venv

# 3. Ativar ambiente virtual
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. Atualizar pip
pip install --upgrade pip

# 5. Instalar dependências
pip install -r requirements.txt

# 6. Criar diretórios necessários
mkdir -p data output logs database templates

# 7. Verificar instalação
python src/main_ai.py --help
```

### Verificação da Instalação

Após a instalação, execute o script de verificação:

```bash
# Linux/macOS
python3 scripts/verificar_integracao_copilot.py --url http://localhost:5000

# Windows
python scripts\verificar_integracao_copilot.py --url http://localhost:5000
```

---

## ⚙️ Configuração Inicial

### Arquivo de Configuração (.env)

O CÓRTEX BI utiliza variáveis de ambiente para configuração. Crie um arquivo `.env` na raiz do projeto:

```bash
# Copiar template de exemplo
cp .env.example .env

# Editar configurações
nano .env  # Linux/macOS
notepad .env  # Windows
```

### Variáveis de Ambiente Principais

```bash
# ===== SERVIDOR =====
HOST=0.0.0.0
PORT=5000
DEBUG=False
WORKERS=4

# ===== SEGURANÇA =====
API_KEY=cHKALRHOHMpDnoFGGuHimNigg3HugUrq
SECRET_KEY=sua-chave-secreta-aqui
CORS_ORIGINS=https://copilotstudio.microsoft.com,https://teams.microsoft.com

# ===== BANCO DE DADOS =====
DB_TYPE=sqlite  # ou 'sqlserver', 'postgresql'
DB_HOST=localhost
DB_PORT=1433
DB_NAME=cortexbi
DB_USER=seu_usuario
DB_PASSWORD=sua_senha

# ===== SQL SERVER (Opcional) =====
SQL_SERVER_HOST=seu-servidor.database.windows.net
SQL_SERVER_DATABASE=seu_banco
SQL_SERVER_USERNAME=seu_usuario
SQL_SERVER_PASSWORD=sua_senha
SQL_SERVER_DRIVER=ODBC Driver 17 for SQL Server

# ===== POWER BI (Opcional) =====
POWERBI_CLIENT_ID=seu-client-id
POWERBI_CLIENT_SECRET=seu-client-secret
POWERBI_TENANT_ID=seu-tenant-id

# ===== SHAREPOINT (Opcional) =====
SHAREPOINT_SITE_URL=https://suaempresa.sharepoint.com/sites/seu-site
SHAREPOINT_CLIENT_ID=seu-client-id
SHAREPOINT_CLIENT_SECRET=seu-client-secret
SHAREPOINT_TENANT_ID=seu-tenant-id
SHAREPOINT_UPLOAD_PATH=/Documentos/CORTEX_BI

# ===== EMAIL (Opcional) =====
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USER=seu-email@empresa.com
SMTP_PASSWORD=sua-senha
SMTP_FROM=cortexbi@empresa.com

# ===== LOGS =====
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=logs/cortexbi.log
LOG_MAX_SIZE=10485760  # 10MB
LOG_BACKUP_COUNT=5

# ===== CACHE =====
CACHE_ENABLED=True
CACHE_TTL=1800  # 30 minutos em segundos
CACHE_MAX_SIZE=1000

# ===== IA E ML =====
ML_MODEL_PATH=models/
NLP_MODEL=pt_core_news_lg
FEEDBACK_THRESHOLD=0.7
RECOMMENDATION_MIN_CONFIDENCE=0.6
```

### Configuração de Diretórios

Crie a estrutura de diretórios necessária:

```bash
# Estrutura de diretórios
mkdir -p data/{raw,processed,archive}
mkdir -p output/{reports,presentations,exports}
mkdir -p logs
mkdir -p database
mkdir -p templates/{pptx,excel,pdf}
mkdir -p models
mkdir -p cache
```

### Permissões (Linux/macOS)

Configure as permissões adequadas:

```bash
# Dar permissão de execução aos scripts
chmod +x scripts/*.sh

# Configurar permissões dos diretórios
chmod 755 data output logs database templates models cache
chmod 644 .env
```

---

## 🚀 Inicialização do Sistema

### Método 1: Scripts Automáticos (Recomendado)

#### Linux / macOS

```bash
# Iniciar o servidor
./scripts/start_ai.sh

# O script irá:
# 1. Ativar ambiente virtual
# 2. Verificar dependências
# 3. Iniciar servidor FastAPI
# 4. Abrir documentação no navegador
```

#### Windows

```powershell
# Iniciar o servidor
.\scripts\start_ai.bat
```

### Método 2: Inicialização Manual

```bash
# 1. Ativar ambiente virtual
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 2. Iniciar servidor
python src/main_ai.py

# 3. Servidor estará disponível em:
# http://localhost:5000
```

### Verificação do Sistema

Após iniciar, verifique se o sistema está funcionando:

```bash
# 1. Health Check
curl http://localhost:5000/health

# Resposta esperada:
{
  "status": "healthy",
  "timestamp": "2025-10-14T18:30:00.000000",
  "services": {
    "data_loader": "active",
    "analytics_engine": "active",
    "pptx_generator": "active",
    "nlp_engine": "active",
    "ml_engine": "active",
    "recommendation_engine": "active",
    "feedback_system": "active",
    "admin_system": "active"
  }
}
```

### Acessar Interfaces

**Documentação Interativa (Swagger UI):**
```
http://localhost:5000/docs
```

**Dashboard Administrativo:**
```
http://localhost:5000/admin/admin_dashboard.html
```

**API Health Check:**
```
http://localhost:5000/health
```

---

## 🔧 Configuração Avançada

### Configuração de Banco de Dados SQL Server

Para conectar o CÓRTEX BI a um banco de dados SQL Server corporativo:

**1. Instalar driver ODBC:**

```bash
# Ubuntu/Debian
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Windows
# Baixar e instalar de: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
```

**2. Configurar conexão no .env:**

```bash
DB_TYPE=sqlserver
SQL_SERVER_HOST=seu-servidor.database.windows.net
SQL_SERVER_DATABASE=seu_banco
SQL_SERVER_USERNAME=seu_usuario
SQL_SERVER_PASSWORD=sua_senha
SQL_SERVER_DRIVER=ODBC Driver 17 for SQL Server
```

**3. Testar conexão:**

```python
python3 -c "
from src.agents.data_loader import DataLoader
loader = DataLoader()
loader.test_sql_connection()
"
```

### Configuração de Templates PPTX

Personalize os templates de apresentação:

**1. Criar template personalizado:**

```bash
# Copiar template base
cp templates/template_relatorio.pptx templates/meu_template.pptx

# Editar no PowerPoint adicionando placeholders:
# {{titulo_principal}}
# {{data_geracao}}
# {{total_vendas}}
# {{crescimento_percentual}}
# {{insights_principais}}
```

**2. Registrar template no sistema:**

```python
# Via API
curl -X POST "http://localhost:5000/admin/template/register" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-api-key" \
  -d '{
    "template_name": "meu_template.pptx",
    "description": "Template personalizado para relatórios executivos",
    "placeholders": [
      "titulo_principal",
      "data_geracao",
      "total_vendas",
      "crescimento_percentual",
      "insights_principais"
    ]
  }'
```

### Configuração de Cache

Otimize o desempenho configurando o cache:

```bash
# No arquivo .env
CACHE_ENABLED=True
CACHE_TTL=1800  # 30 minutos
CACHE_MAX_SIZE=1000  # Máximo de itens no cache
```

### Configuração de Logs

Personalize o sistema de logs:

```bash
# No arquivo .env
LOG_LEVEL=INFO
LOG_FILE=logs/cortexbi.log
LOG_MAX_SIZE=10485760  # 10MB
LOG_BACKUP_COUNT=5

# Logs separados por tipo
LOG_AI_INTERACTIONS=logs/ai_interactions.log
LOG_ERRORS=logs/errors.log
LOG_AUDIT=logs/audit.log
```

---

## 👨‍💼 Administração do Sistema

### Dashboard Administrativo

Acesse o dashboard em: `http://localhost:5000/admin/admin_dashboard.html`

**Funcionalidades disponíveis:**

**1. Métricas em Tempo Real:**
- Número de análises executadas
- Usuários ativos
- Tempo médio de resposta
- Taxa de sucesso das operações
- Uso de recursos (CPU, memória)

**2. Gerenciamento de Templates:**
- Visualizar templates disponíveis
- Upload de novos templates
- Editar placeholders
- Ativar/desativar templates
- Visualizar preview

**3. Gerenciamento de Usuários:**
- Criar/editar usuários
- Definir permissões
- Gerar API Keys
- Visualizar histórico de acesso
- Revogar acessos

**4. Configurações do Sistema:**
- Ajustar parâmetros de performance
- Configurar integrações
- Gerenciar cache
- Configurar logs
- Backup e restore

### Gerenciamento de API Keys

**Criar nova API Key:**

```bash
curl -X POST "http://localhost:5000/admin/api-key/create" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: admin-api-key" \
  -d '{
    "user_id": "usuario@empresa.com",
    "permissions": ["read", "write", "admin"],
    "expiration_days": 90
  }'
```

**Listar API Keys:**

```bash
curl -X GET "http://localhost:5000/admin/api-keys" \
  -H "X-API-Key: admin-api-key"
```

**Revogar API Key:**

```bash
curl -X DELETE "http://localhost:5000/admin/api-key/{key_id}" \
  -H "X-API-Key: admin-api-key"
```

### Gerenciamento de Templates

**Via Dashboard Administrativo:**

1. Acesse `http://localhost:5000/admin/admin_dashboard.html`
2. Navegue até "Gerenciar Templates"
3. Clique em "Upload Novo Template"
4. Selecione arquivo PPTX
5. Configure placeholders
6. Salve e ative

**Via API:**

```bash
# Listar templates
curl -X GET "http://localhost:5000/admin/templates/usuario" \
  -H "X-API-Key: sua-api-key"

# Atualizar placeholders
curl -X POST "http://localhost:5000/admin/template/update" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-api-key" \
  -d '{
    "template_name": "template_relatorio.pptx",
    "new_placeholders": {
      "total_vendas": "receita_total",
      "crescimento": "variacao_percentual"
    }
  }'
```

### Configuração de Integrações

**SharePoint:**

```bash
curl -X POST "http://localhost:5000/admin/sharepoint/config" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-api-key" \
  -d '{
    "base_url": "https://suaempresa.sharepoint.com",
    "site_path": "/sites/seu-site",
    "upload_path": "/Documentos/CORTEX_BI",
    "client_id": "seu-client-id",
    "client_secret": "seu-client-secret",
    "tenant_id": "seu-tenant-id"
  }'
```

**Power BI:**

```bash
curl -X POST "http://localhost:5000/admin/powerbi/config" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-api-key" \
  -d '{
    "client_id": "seu-client-id",
    "client_secret": "seu-client-secret",
    "tenant_id": "seu-tenant-id",
    "workspace_id": "seu-workspace-id"
  }'
```

---

## 🔗 Integração Microsoft 365

### Pré-requisitos para Integração

- Microsoft 365 Business ou superior
- Microsoft Copilot for Microsoft 365 licenciado
- Permissões de administrador no tenant
- CÓRTEX BI rodando em servidor acessível

### Integração com Copilot Studio

**Passo 1: Registrar o CÓRTEX BI como Plugin**

1. Acesse o Microsoft Copilot Studio
2. Navegue até "Plugins" → "Add Plugin"
3. Selecione "API Plugin"
4. Configure:

```json
{
  "schema_version": "v1",
  "name_for_human": "CÓRTEX BI",
  "name_for_model": "cortex_bi",
  "description_for_human": "Agente de análise de dados e business intelligence",
  "description_for_model": "Analisa dados, gera relatórios e apresentações PPTX automaticamente. Responde perguntas em português sobre métricas, vendas, performance e KPIs.",
  "auth": {
    "type": "service_http",
    "authorization_type": "bearer",
    "verification_tokens": {
      "api_key": "sua-api-key"
    }
  },
  "api": {
    "type": "openapi",
    "url": "http://seu-servidor:5000/openapi.json"
  },
  "logo_url": "http://seu-servidor:5000/static/logo.png",
  "contact_email": "admin@empresa.com",
  "legal_info_url": "http://seu-servidor:5000/legal"
}
```

**Passo 2: Criar Flows no Power Automate**

Para cada funcionalidade do CÓRTEX BI, crie um Flow:

**Flow 1: CÓRTEX Health Check**
```
Trigger: When Copilot calls action
Action: HTTP Request
  Method: GET
  URL: http://seu-servidor:5000/health
  Headers: X-API-Key: sua-api-key
Response: Return to Copilot
```

**Flow 2: CÓRTEX Analyze**
```
Trigger: When Copilot calls action with parameters
Action: HTTP Request
  Method: POST
  URL: http://seu-servidor:5000/analyze
  Headers: X-API-Key: sua-api-key
  Body: {
    "file_path": @{triggerBody()['file_path']},
    "analysis_type": @{triggerBody()['analysis_type']}
  }
Response: Format and return to Copilot
```

**Flow 3: CÓRTEX NLP Query**
```
Trigger: When Copilot calls action with query
Action: HTTP Request
  Method: POST
  URL: http://seu-servidor:5000/nlp/query
  Headers: X-API-Key: sua-api-key
  Body: {
    "query": @{triggerBody()['query']},
    "user_id": @{triggerBody()['user_id']}
  }
Response: Return formatted results
```

**Passo 3: Configurar Tópicos no Copilot Studio**

Crie tópicos para ativar o CÓRTEX BI:

**Tópico 1: Análise de Dados**
- Gatilho: "analisar dados", "análise", "métricas"
- Ação: Chamar Flow "CÓRTEX Analyze"

**Tópico 2: Perguntas Naturais**
- Gatilho: "como foram", "mostre", "qual foi"
- Ação: Chamar Flow "CÓRTEX NLP Query"

**Tópico 3: Gerar Relatório**
- Gatilho: "gerar relatório", "criar apresentação"
- Ação: Chamar Flow "CÓRTEX Generate PPTX"

**Passo 4: Testar Integração**

No Microsoft Teams:
```
@Copilot, use CÓRTEX BI para analisar vendas do último trimestre
```

### Script de Configuração Automática

Execute o script automatizado:

```bash
python scripts/configurar_integracao_copilot.py \
  --url http://seu-servidor:5000 \
  --api-key sua-api-key \
  --copilot-url https://copilotstudio.microsoft.com
```

---

## 📊 Monitoramento e Manutenção

### Monitoramento Contínuo

**Script de Monitoramento:**

```bash
# Executar monitoramento contínuo
python scripts/monitorar_integracao_copilot.py \
  --url http://localhost:5000 \
  --interval 60  # Verificar a cada 60 segundos
```

**Métricas Monitoradas:**
- Status de cada agente
- Tempo de resposta
- Taxa de sucesso
- Uso de memória e CPU
- Número de requisições
- Erros e exceções

### Logs do Sistema

**Visualizar logs em tempo real:**

```bash
# Log principal
tail -f logs/cortexbi.log

# Logs de IA
tail -f logs/ai_interactions.log

# Logs de erro
tail -f logs/errors.log

# Logs de auditoria
tail -f logs/audit.log
```

**Analisar logs:**

```bash
# Buscar erros
grep ERROR logs/cortexbi.log

# Contar requisições por hora
grep "POST /analyze" logs/cortexbi.log | cut -d' ' -f1 | cut -d'T' -f2 | cut -d':' -f1 | sort | uniq -c

# Usuários mais ativos
grep "user_id" logs/audit.log | cut -d'"' -f4 | sort | uniq -c | sort -nr | head -10
```

### Backup e Restore

**Backup Automático:**

```bash
#!/bin/bash
# Script de backup diário

BACKUP_DIR="/backup/cortexbi"
DATE=$(date +%Y%m%d)

# Criar diretório de backup
mkdir -p $BACKUP_DIR/$DATE

# Backup do banco de dados
cp -r database/ $BACKUP_DIR/$DATE/

# Backup de templates
cp -r templates/ $BACKUP_DIR/$DATE/

# Backup de configurações
cp .env $BACKUP_DIR/$DATE/

# Backup de logs
cp -r logs/ $BACKUP_DIR/$DATE/

# Compactar
tar -czf $BACKUP_DIR/cortexbi_$DATE.tar.gz $BACKUP_DIR/$DATE/

# Remover backups antigos (manter últimos 30 dias)
find $BACKUP_DIR -name "cortexbi_*.tar.gz" -mtime +30 -delete
```

**Restore:**

```bash
#!/bin/bash
# Restaurar backup

BACKUP_FILE=$1

# Extrair backup
tar -xzf $BACKUP_FILE -C /tmp/

# Parar serviço
./scripts/stop_ai.sh

# Restaurar arquivos
cp -r /tmp/cortexbi_*/database/ .
cp -r /tmp/cortexbi_*/templates/ .
cp /tmp/cortexbi_*/.env .

# Reiniciar serviço
./scripts/start_ai.sh
```

### Atualização do Sistema

```bash
# 1. Fazer backup
./scripts/backup.sh

# 2. Parar serviço
./scripts/stop_ai.sh

# 3. Atualizar código
git pull origin master

# 4. Atualizar dependências
pip install -r requirements.txt --upgrade

# 5. Executar migrações (se houver)
python scripts/migrate.py

# 6. Reiniciar serviço
./scripts/start_ai.sh

# 7. Verificar saúde
curl http://localhost:5000/health
```

---

## 🔍 Troubleshooting

### Problema: Servidor não inicia

**Sintomas:**
- Erro ao executar `python src/main_ai.py`
- Porta já em uso

**Soluções:**

```bash
# Verificar se porta está ocupada
netstat -tlnp | grep :5000  # Linux
netstat -ano | findstr :5000  # Windows

# Matar processo na porta
# Linux:
lsof -ti:5000 | xargs kill -9
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Tentar porta alternativa
PORT=8000 python src/main_ai.py
```

### Problema: Erro de dependências

**Sintomas:**
- `ModuleNotFoundError`
- Erros de importação

**Soluções:**

```bash
# Reinstalar dependências
pip install -r requirements.txt --force-reinstall

# Verificar versão do Python
python3 --version  # Deve ser 3.8+

# Limpar cache do pip
pip cache purge

# Criar novo ambiente virtual
python3 -m venv venv_new
source venv_new/bin/activate
pip install -r requirements.txt
```

### Problema: Erro de conexão SQL Server

**Sintomas:**
- Erro ao conectar com banco de dados
- Timeout de conexão

**Soluções:**

```bash
# Verificar drivers ODBC
odbcinst -q -d  # Linux
# Deve listar: ODBC Driver 17 for SQL Server

# Testar conectividade
telnet seu-servidor.database.windows.net 1433

# Verificar credenciais no .env
cat .env | grep SQL_SERVER

# Testar conexão manualmente
python3 -c "
import pyodbc
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=seu-servidor;'
    'DATABASE=seu-banco;'
    'UID=usuario;'
    'PWD=senha'
)
print('Conexão bem-sucedida!')
"
```

### Problema: Template PPTX não encontrado

**Sintomas:**
- Erro ao gerar apresentação
- Arquivo não encontrado

**Soluções:**

```bash
# Verificar templates disponíveis
ls -la templates/

# Criar template básico se necessário
python3 -c "
from pptx import Presentation
prs = Presentation()
prs.save('templates/template_basico.pptx')
print('Template criado!')
"

# Verificar permissões
chmod 644 templates/*.pptx
```

### Problema: Alto uso de memória

**Sintomas:**
- Sistema lento
- Erros de memória

**Soluções:**

```bash
# Verificar uso de memória
ps aux | grep python

# Limpar cache
curl -X POST "http://localhost:5000/admin/cache/clear" \
  -H "X-API-Key: sua-api-key"

# Ajustar configurações no .env
CACHE_MAX_SIZE=500  # Reduzir tamanho do cache
WORKERS=2  # Reduzir número de workers

# Reiniciar serviço
./scripts/stop_ai.sh
./scripts/start_ai.sh
```

### Script de Diagnóstico Automático

```bash
# Executar diagnóstico completo
python scripts/diagnosticar_integracao_copilot.py \
  --url http://localhost:5000 \
  --full-check

# O script verificará:
# - Conectividade
# - Status de agentes
# - Integridade de dados
# - Configurações
# - Logs de erro
# - Performance
```

---

## 🔐 Segurança e Backup

### Configuração de Firewall

**Linux (UFW):**

```bash
# Permitir apenas IPs específicos
sudo ufw allow from 192.168.1.0/24 to any port 5000

# Permitir Copilot Studio
sudo ufw allow from 20.190.0.0/16 to any port 5000
```

**Windows:**

```powershell
# Criar regra de firewall
New-NetFirewallRule -DisplayName "CORTEX BI" `
  -Direction Inbound `
  -LocalPort 5000 `
  -Protocol TCP `
  -Action Allow `
  -RemoteAddress 192.168.1.0/24
```

### Rotação de API Keys

```bash
# Script de rotação automática (executar mensalmente)
#!/bin/bash

# Gerar nova API Key
NEW_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Atualizar no .env
sed -i "s/API_KEY=.*/API_KEY=$NEW_KEY/" .env

# Reiniciar serviço
./scripts/stop_ai.sh
./scripts/start_ai.sh

# Notificar administradores
echo "Nova API Key gerada: $NEW_KEY" | mail -s "CORTEX BI - Nova API Key" admin@empresa.com
```

### Criptografia de Dados Sensíveis

```python
# Configurar criptografia no .env
ENCRYPTION_ENABLED=True
ENCRYPTION_KEY=sua-chave-de-criptografia-32-bytes
```

### Auditoria e Compliance

```bash
# Gerar relatório de auditoria
python scripts/gerar_relatorio_auditoria.py \
  --start-date 2025-10-01 \
  --end-date 2025-10-31 \
  --output relatorio_auditoria_outubro.pdf

# Relatório incluirá:
# - Todos os acessos ao sistema
# - Operações realizadas por usuário
# - Dados acessados
# - Modificações em configurações
# - Tentativas de acesso negadas
```

---

## 📞 Suporte e Recursos Adicionais

### Documentação Completa

- **README Principal**: `/docs/README.md`
- **API Reference**: `http://localhost:5000/docs`
- **Guias de Integração**: `/docs/integracao/`

### Scripts Úteis

Todos os scripts estão disponíveis em `/scripts/`:

- `install.sh/bat` - Instalação automática
- `start_ai.sh/bat` - Iniciar servidor
- `stop_ai.sh/bat` - Parar servidor
- `verificar_integracao_copilot.py` - Verificar pré-requisitos
- `configurar_integracao_copilot.py` - Configurar integração
- `diagnosticar_integracao_copilot.py` - Diagnosticar problemas
- `monitorar_integracao_copilot.py` - Monitoramento contínuo
- `backup.sh` - Backup automático
- `restore.sh` - Restaurar backup

### Contato

- **GitHub Issues**: https://github.com/Rimkus85/cortex-bi/issues
- **Email**: suporte@cortexbi.com
- **Documentação Online**: https://github.com/Rimkus85/cortex-bi

---

**CÓRTEX BI v2.0** - *Cognitive Operations & Real-Time EXpert Business Intelligence*  
Desenvolvido em parceria com **Manus AI** | Outubro 2025

✅ Sistema pronto para produção  
🚀 Transformando dados em decisões inteligentes

