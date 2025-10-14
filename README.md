# 🧠 CÓRTEX BI - Business Intelligence com Inteligência Artificial

**Cognitive Operations & Real-Time EXpert Business Intelligence**

[![Version](https://img.shields.io/badge/version-2.0-blue.svg)](https://github.com/Rimkus85/cortex-bi)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Sistema avançado de Business Intelligence que combina análise de dados tradicional com inteligência artificial de última geração. Desenvolvido como um agente completo de analytics, oferece processamento de linguagem natural, machine learning e integração nativa com Microsoft Copilot Studio.

---

## 🚀 Visão Geral

O **CÓRTEX BI** democratiza o acesso a insights de negócio através de **analytics conversacional**. Faça perguntas em português natural e receba análises completas, visualizações e apresentações profissionais instantaneamente.

### Principais Características

- 🤖 **8 Agentes Especializados de IA** - Arquitetura modular com agentes dedicados
- 💬 **Processamento de Linguagem Natural** - Perguntas em português, respostas instantâneas
- 📊 **Análises Avançadas** - Comparação de períodos, segmentação, KPIs, anomalias e predições
- 📋 **Geração Automática de Conteúdo** - Apresentações PowerPoint e relatórios executivos
- 🔗 **Integração Microsoft 365** - Copilot Studio, Teams, SharePoint e Power BI
- 🎯 **Aprendizado Contínuo** - Sistema evolui com feedback e uso
- 🔐 **Segurança Empresarial** - Autenticação, CORS, LGPD compliance

---

## 📁 Estrutura do Repositório

```
cortex-bi/
├── docs/                           # Documentação completa
│   ├── README.md                   # Documentação técnica detalhada
│   ├── CORTEX_BI_Manual_Completo.docx
│   └── *.pdf                       # Manuais e guias em PDF
│
├── src/                            # Código-fonte do sistema
│   ├── agents/                     # Agentes de IA
│   │   ├── data_loader.py
│   │   ├── analytics_engine.py
│   │   ├── pptx_generator.py
│   │   ├── nlp_engine.py
│   │   ├── ml_engine.py
│   │   ├── recommendation_engine.py
│   │   ├── feedback_system.py
│   │   └── admin_system.py
│   ├── main.py                     # Servidor FastAPI básico
│   └── main_ai.py                  # Servidor com IA (USAR ESTE)
│
├── scripts/                        # Scripts de instalação e configuração
│   ├── install.sh                  # Instalação Linux/macOS
│   ├── install.bat                 # Instalação Windows
│   ├── start_ai.sh                 # Iniciar servidor (Linux/macOS)
│   ├── start_ai.bat                # Iniciar servidor (Windows)
│   └── *integracao*.py             # Scripts de integração Copilot
│
├── templates/                      # Templates PPTX
│   └── *.pptx                      # Templates de apresentação
│
├── presentations/                  # Apresentações sobre o sistema
│
├── requirements.txt                # Dependências Python
└── README.md                       # Este arquivo
```

---

## 🛠️ Instalação Rápida

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- 4 GB RAM mínimo (8 GB recomendado)
- 10 GB espaço em disco

### Linux/macOS

```bash
# 1. Clonar o repositório
git clone https://github.com/Rimkus85/cortex-bi.git
cd cortex-bi

# 2. Executar instalação automática
chmod +x scripts/install.sh
./scripts/install.sh

# 3. Iniciar o servidor
./scripts/start_ai.sh
```

### Windows

```powershell
# 1. Clonar o repositório
git clone https://github.com/Rimkus85/cortex-bi.git
cd cortex-bi

# 2. Executar instalação (como Administrador)
.\scripts\install.bat

# 3. Iniciar o servidor
.\scripts\start_ai.bat
```

### Instalação Manual

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Iniciar o servidor
python src/main_ai.py
```

---

## 🎯 Como Usar

### Acesso ao Sistema

Após iniciar, o CÓRTEX BI estará disponível em:

- 🏠 **Página Principal**: http://localhost:5000/
- 📚 **Documentação API**: http://localhost:5000/docs
- ❤️ **Health Check**: http://localhost:5000/health

### Exemplos de Uso

#### Via cURL

```bash
# Verificar status do sistema
curl http://localhost:5000/health

# Análise de dados
curl -X POST "http://localhost:5000/analyze" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-api-key" \
  -d '{
    "file_path": "data/vendas.csv",
    "analysis_type": "complete"
  }'

# Processamento de linguagem natural
curl -X POST "http://localhost:5000/nlp/query" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-api-key" \
  -d '{
    "query": "Analise as vendas do último trimestre",
    "user_id": "usuario_teste"
  }'
```

#### Via Python

```python
import requests

BASE_URL = "http://localhost:5000"
API_KEY = "sua-api-key"
headers = {"X-API-Key": API_KEY}

# Análise completa
response = requests.post(
    f"{BASE_URL}/analyze",
    json={
        "file_path": "data/vendas.csv",
        "analysis_type": "complete"
    },
    headers=headers
)
results = response.json()
print(results)
```

---

## 🤖 Arquitetura do Sistema

### Agentes Especializados

| Agente | Função |
|--------|--------|
| **DataLoader** | Carregamento e validação de dados de múltiplas fontes |
| **AnalyticsEngine** | Motor de análises avançadas (comparações, segmentações, KPIs) |
| **PPTXGenerator** | Geração automática de apresentações PowerPoint |
| **NLPEngine** | Processamento de linguagem natural em português |
| **MLEngine** | Machine learning, predições e detecção de anomalias |
| **RecommendationEngine** | Sistema de recomendações personalizadas |
| **FeedbackSystem** | Coleta e análise de feedback para aprendizado contínuo |
| **AdminSystem** | Dashboard administrativo e gerenciamento |

### Tecnologias Utilizadas

- **Framework**: FastAPI
- **Linguagem**: Python 3.8+
- **Análise de Dados**: Pandas, NumPy
- **Machine Learning**: Scikit-learn
- **NLP**: spaCy
- **Geração PPTX**: python-pptx
- **API**: REST JSON

---

## 🔌 Integração Microsoft 365

O CÓRTEX BI integra nativamente com:

- **Microsoft Copilot Studio** - Ativação via conversação natural
- **Microsoft Teams** - Interação direta via chat
- **Outlook** - Análises por email
- **SharePoint** - Upload automático de relatórios
- **Power BI** - Consumo e atualização de datasets

### Configuração Copilot Studio

Veja o guia completo em [`docs/`](docs/) para instruções detalhadas de integração.

---

## 📊 Funcionalidades

### Analytics Conversacional

Faça perguntas em português natural:

- "Como foram as vendas do último trimestre?"
- "Mostre a performance por região"
- "Gere um relatório executivo do Q4 2024"
- "Quais produtos tiveram queda nas vendas?"

### Análises Disponíveis

- ✅ Comparação de períodos (YoY, MoM, QoQ)
- ✅ Segmentação multidimensional
- ✅ Análise de KPIs customizáveis
- ✅ Detecção de anomalias com ML
- ✅ Predições e forecasting
- ✅ Análise de tendências

### Geração Automática

- 📋 Apresentações PowerPoint profissionais
- 📊 Relatórios executivos formatados
- 📈 Dashboards e visualizações
- 📧 Envio automático por email

---

## 🔐 Segurança

- ✅ Autenticação via API Key
- ✅ CORS configurável
- ✅ Dados permanecem na infraestrutura local
- ✅ Compliance com LGPD
- ✅ Logs completos de auditoria
- ✅ Criptografia para dados sensíveis

---

## 📚 Documentação

A documentação completa está disponível na pasta [`docs/`](docs/):

- **README.md** - Documentação técnica detalhada (100+ páginas)
- **Manual Completo** - Guia em formato Word/PDF
- **Guias de Integração** - Microsoft 365, Copilot Studio
- **API Reference** - Especificação completa de endpoints

---

## 🎓 Casos de Uso

### Análise Executiva Automatizada

Diretor solicita: *"Prepare a apresentação executiva do Q4 2024"*

**Resultado**: Sistema gera apresentação completa com dados, gráficos e insights em < 30 segundos.

### Análise Operacional Diária

Gerente pergunta: *"Como está a performance da equipe este mês?"*

**Resultado**: Análise detalhada com produtividade, top performers e áreas de atenção.

### Detecção Proativa de Anomalias

Sistema detecta automaticamente queda de 15% nas vendas de um produto.

**Resultado**: Notificação proativa com análise, causas possíveis e recomendações.

---

## 🚀 Roadmap

### Versão 2.0 (Atual)
- ✅ Integração completa com Microsoft Copilot Studio
- ✅ Processamento avançado de linguagem natural
- ✅ Sistema de recomendações inteligente
- ✅ Geração automática de apresentações
- ✅ Dashboard administrativo completo

### Próximas Versões
- 🔄 Análise de voz (comandos verbais)
- 🔄 Dashboards interativos em Power BI
- 🔄 Alertas proativos automáticos
- 🔄 Add-in para Excel
- 🔄 Análise de sentimento em textos
- 🔄 Deep learning para predições avançadas

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

---

## 📞 Suporte

- **Issues**: [GitHub Issues](https://github.com/Rimkus85/cortex-bi/issues)
- **Documentação**: Pasta `/docs`
- **Email**: suporte@cortexbi.com

---

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 🎉 Agradecimentos

**CÓRTEX BI v2.0** - Desenvolvido em parceria com **Manus AI**

*Transformando dados em decisões inteligentes* 🚀

---

**Status**: ✅ Produção  
**Versão**: 2.0.0  
**Data**: Outubro 2025

