#!/usr/bin/env python3
"""
Script de Configuração Automática para Integração CÓRTEX BI com Copilot Studio
Versão: 1.0
Autor: Manus AI
"""

import json
import os
import secrets
import string
from datetime import datetime
from typing import Dict, List, Optional
import argparse

class CopilotIntegrationConfigurator:
    def __init__(self, cortex_url: str, output_dir: str = "./copilot_integration"):
        self.cortex_url = cortex_url.rstrip('/')
        self.output_dir = output_dir
        self.config = {}
        
        # Criar diretório de saída se não existir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_api_key(self, length: int = 32) -> str:
        """Gera uma API key segura"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def create_actions_config(self) -> Dict:
        """Cria configuração das Actions para Copilot Studio"""
        actions = {
            "actions": [
                {
                    "name": "CORTEX_HealthCheck",
                    "displayName": "Verificar Status do CÓRTEX BI",
                    "description": "Verifica se o sistema CÓRTEX BI está funcionando corretamente",
                    "method": "GET",
                    "url": f"{self.cortex_url}/health",
                    "parameters": [],
                    "response_mapping": {
                        "status_message": "$.status",
                        "services": "$.services",
                        "timestamp": "$.timestamp"
                    },
                    "sample_response": {
                        "status": "healthy",
                        "timestamp": "2025-09-02T16:33:04.511838",
                        "services": {
                            "data_loader": "active",
                            "analytics_engine": "active",
                            "pptx_generator": "active",
                            "feedback_system": "active",
                            "nlp_engine": "active",
                            "recommendation_engine": "active",
                            "ml_engine": "active"
                        }
                    }
                },
                {
                    "name": "CORTEX_Analyze",
                    "displayName": "Executar Análise de Dados",
                    "description": "Executa análises avançadas de dados com IA",
                    "method": "POST",
                    "url": f"{self.cortex_url}/analyze",
                    "parameters": [
                        {
                            "name": "analysis_type",
                            "type": "string",
                            "required": True,
                            "description": "Tipo de análise (vendas, financeiro, operacional)",
                            "enum": ["vendas", "financeiro", "operacional", "geral"]
                        },
                        {
                            "name": "period",
                            "type": "string",
                            "required": False,
                            "description": "Período para análise (ex: 2024-Q1, último_mês)",
                            "default": "último_mês"
                        },
                        {
                            "name": "detail_level",
                            "type": "string",
                            "required": False,
                            "description": "Nível de detalhe da análise",
                            "enum": ["básico", "detalhado", "executivo"],
                            "default": "detalhado"
                        }
                    ],
                    "response_mapping": {
                        "insights": "$.insights",
                        "recommendations": "$.recommendations",
                        "data_summary": "$.data_summary"
                    }
                },
                {
                    "name": "CORTEX_GeneratePPTX",
                    "displayName": "Gerar Apresentação",
                    "description": "Gera apresentação PowerPoint com análises e insights",
                    "method": "POST",
                    "url": f"{self.cortex_url}/generate-pptx",
                    "parameters": [
                        {
                            "name": "presentation_type",
                            "type": "string",
                            "required": True,
                            "description": "Tipo de apresentação",
                            "enum": ["executiva", "técnica", "operacional"]
                        },
                        {
                            "name": "data_source",
                            "type": "string",
                            "required": True,
                            "description": "Fonte de dados para a apresentação"
                        },
                        {
                            "name": "title",
                            "type": "string",
                            "required": False,
                            "description": "Título da apresentação",
                            "default": "Relatório CÓRTEX BI"
                        }
                    ],
                    "response_mapping": {
                        "download_url": "$.download_url",
                        "filename": "$.filename",
                        "slides_count": "$.slides_count"
                    }
                },
                {
                    "name": "CORTEX_NLPQuery",
                    "displayName": "Consulta em Linguagem Natural",
                    "description": "Processa consultas em linguagem natural usando IA",
                    "method": "POST",
                    "url": f"{self.cortex_url}/nlp/query",
                    "parameters": [
                        {
                            "name": "query",
                            "type": "string",
                            "required": True,
                            "description": "Consulta em linguagem natural"
                        },
                        {
                            "name": "context",
                            "type": "string",
                            "required": False,
                            "description": "Contexto adicional para a consulta"
                        }
                    ],
                    "response_mapping": {
                        "intent": "$.intent",
                        "entities": "$.entities",
                        "response": "$.response",
                        "confidence": "$.confidence"
                    }
                },
                {
                    "name": "CORTEX_GetRecommendations",
                    "displayName": "Obter Recomendações",
                    "description": "Obtém recomendações personalizadas baseadas em IA",
                    "method": "GET",
                    "url": f"{self.cortex_url}/recommendations/{{user_id}}",
                    "parameters": [
                        {
                            "name": "user_id",
                            "type": "string",
                            "required": True,
                            "description": "ID do usuário para recomendações personalizadas"
                        }
                    ],
                    "response_mapping": {
                        "recommendations": "$.recommendations",
                        "user_profile": "$.user_profile"
                    }
                }
            ],
            "authentication": {
                "type": "api_key",
                "header": "X-API-Key",
                "description": "Chave de API para autenticação com CÓRTEX BI"
            },
            "base_url": self.cortex_url,
            "timeout": 30,
            "retry_policy": {
                "max_attempts": 3,
                "backoff_factor": 2
            }
        }
        
        return actions
    
    def create_topics_config(self) -> Dict:
        """Cria configuração dos tópicos para Copilot Studio"""
        topics = {
            "topics": [
                {
                    "name": "Saudação",
                    "trigger_phrases": [
                        "olá",
                        "oi",
                        "bom dia",
                        "boa tarde",
                        "boa noite",
                        "help",
                        "ajuda"
                    ],
                    "response": "Olá! Sou o assistente CÓRTEX BI. Posso ajudá-lo com análises de dados, geração de relatórios e insights de negócio. Como posso ajudar hoje?",
                    "follow_up_suggestions": [
                        "Analisar vendas do último mês",
                        "Gerar apresentação executiva",
                        "Verificar status do sistema",
                        "Obter recomendações personalizadas"
                    ]
                },
                {
                    "name": "Análise de Vendas",
                    "trigger_phrases": [
                        "vendas",
                        "faturamento",
                        "receita",
                        "performance de vendas",
                        "relatório de vendas",
                        "como foram as vendas"
                    ],
                    "entities": [
                        {
                            "name": "período",
                            "type": "datetime",
                            "patterns": ["último mês", "Q1", "Q2", "Q3", "Q4", "ano passado", "este ano"]
                        }
                    ],
                    "action": "CORTEX_Analyze",
                    "parameters": {
                        "analysis_type": "vendas",
                        "period": "{período}",
                        "detail_level": "detalhado"
                    }
                },
                {
                    "name": "Análise Financeira",
                    "trigger_phrases": [
                        "financeiro",
                        "custos",
                        "despesas",
                        "lucro",
                        "margem",
                        "análise financeira",
                        "performance financeira"
                    ],
                    "entities": [
                        {
                            "name": "período",
                            "type": "datetime",
                            "patterns": ["último mês", "Q1", "Q2", "Q3", "Q4", "ano passado", "este ano"]
                        }
                    ],
                    "action": "CORTEX_Analyze",
                    "parameters": {
                        "analysis_type": "financeiro",
                        "period": "{período}",
                        "detail_level": "executivo"
                    }
                },
                {
                    "name": "Gerar Apresentação",
                    "trigger_phrases": [
                        "gerar apresentação",
                        "criar slides",
                        "fazer powerpoint",
                        "relatório executivo",
                        "apresentação para diretoria"
                    ],
                    "entities": [
                        {
                            "name": "tipo",
                            "type": "string",
                            "patterns": ["executiva", "técnica", "operacional"]
                        },
                        {
                            "name": "assunto",
                            "type": "string",
                            "patterns": ["vendas", "financeiro", "operacional", "geral"]
                        }
                    ],
                    "action": "CORTEX_GeneratePPTX",
                    "parameters": {
                        "presentation_type": "{tipo}",
                        "data_source": "{assunto}",
                        "title": "Relatório {assunto} - {tipo}"
                    }
                },
                {
                    "name": "Status do Sistema",
                    "trigger_phrases": [
                        "status",
                        "funcionando",
                        "sistema ok",
                        "verificar sistema",
                        "health check",
                        "está online"
                    ],
                    "action": "CORTEX_HealthCheck",
                    "response_template": "Status do CÓRTEX BI: {status_message}. Todos os módulos estão funcionando normalmente."
                },
                {
                    "name": "Consulta Livre",
                    "trigger_phrases": [
                        "pergunta",
                        "consulta",
                        "quero saber",
                        "me diga",
                        "explique"
                    ],
                    "action": "CORTEX_NLPQuery",
                    "parameters": {
                        "query": "{user_input}",
                        "context": "consulta_geral"
                    }
                },
                {
                    "name": "Recomendações",
                    "trigger_phrases": [
                        "recomendações",
                        "sugestões",
                        "o que devo analisar",
                        "insights",
                        "próximos passos"
                    ],
                    "action": "CORTEX_GetRecommendations",
                    "parameters": {
                        "user_id": "{user.id}"
                    }
                }
            ],
            "fallback_responses": [
                "Desculpe, não entendi sua solicitação. Posso ajudar com análises de dados, geração de relatórios ou verificação do sistema.",
                "Não consegui processar essa consulta. Tente perguntar sobre vendas, análises financeiras ou geração de apresentações.",
                "Essa funcionalidade não está disponível. Posso ajudar com análises de dados usando o CÓRTEX BI."
            ],
            "error_handling": {
                "timeout": "A análise está demorando mais que o esperado. Tente novamente em alguns minutos.",
                "server_error": "Houve um problema temporário com o CÓRTEX BI. Tente novamente em alguns instantes.",
                "authentication_error": "Problema de autenticação com o sistema. Entre em contato com o administrador."
            }
        }
        
        return topics
    
    def create_security_config(self) -> Dict:
        """Cria configuração de segurança"""
        api_key = self.generate_api_key()
        
        security = {
            "api_key": api_key,
            "authentication": {
                "method": "api_key",
                "header": "X-API-Key",
                "value": api_key
            },
            "cors_settings": {
                "allowed_origins": [
                    "https://copilotstudio.microsoft.com",
                    "https://*.copilotstudio.microsoft.com",
                    "https://powerva.microsoft.com",
                    "https://*.powerva.microsoft.com"
                ],
                "allowed_methods": ["GET", "POST", "OPTIONS"],
                "allowed_headers": ["Content-Type", "Authorization", "X-API-Key"]
            },
            "rate_limiting": {
                "requests_per_minute": 100,
                "burst_limit": 20
            },
            "security_headers": {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "X-XSS-Protection": "1; mode=block"
            }
        }
        
        return security
    
    def create_deployment_script(self) -> str:
        """Cria script de deployment"""
        script = f"""#!/bin/bash
# Script de Deployment para Integração CÓRTEX BI + Copilot Studio
# Gerado automaticamente em {datetime.now().isoformat()}

echo "🚀 Iniciando configuração da integração CÓRTEX BI + Copilot Studio"

# Verificar se o CÓRTEX BI está rodando
echo "📡 Verificando conectividade com CÓRTEX BI..."
curl -f {self.cortex_url}/health > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ CÓRTEX BI está acessível"
else
    echo "❌ CÓRTEX BI não está acessível em {self.cortex_url}"
    echo "   Verifique se o servidor está rodando e acessível"
    exit 1
fi

# Configurar API Key no CÓRTEX BI
echo "🔐 Configurando autenticação..."
# Adicione aqui comandos específicos para configurar a API key no seu sistema

# Verificar configuração CORS
echo "🌐 Verificando configuração CORS..."
curl -H "Origin: https://copilotstudio.microsoft.com" \\
     -H "Access-Control-Request-Method: POST" \\
     -H "Access-Control-Request-Headers: X-API-Key" \\
     -X OPTIONS {self.cortex_url}/health

# Testar endpoints principais
echo "🧪 Testando endpoints principais..."
endpoints=("/health" "/list-files" "/docs")
for endpoint in "${{endpoints[@]}}"; do
    echo "  Testando $endpoint..."
    curl -f {self.cortex_url}$endpoint > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "    ✅ $endpoint OK"
    else
        echo "    ⚠️  $endpoint com problemas"
    fi
done

echo "✅ Configuração concluída!"
echo ""
echo "📋 Próximos passos:"
echo "1. Configure as Actions no Copilot Studio usando os arquivos gerados"
echo "2. Importe os tópicos de conversação"
echo "3. Configure a autenticação com a API key gerada"
echo "4. Teste a integração com consultas simples"
echo ""
echo "📁 Arquivos de configuração gerados em: {self.output_dir}"
"""
        return script
    
    def create_test_script(self) -> str:
        """Cria script de testes"""
        script = f"""#!/usr/bin/env python3
# Script de Testes para Integração CÓRTEX BI + Copilot Studio
# Gerado automaticamente em {datetime.now().isoformat()}

import requests
import json
import time

BASE_URL = "{self.cortex_url}"
API_KEY = "SUA_API_KEY_AQUI"  # Substitua pela API key gerada

def test_health_check():
    \"\"\"Testa endpoint de health check\"\"\"
    print("🔍 Testando health check...")
    response = requests.get(f"{{BASE_URL}}/health")
    if response.status_code == 200:
        print("✅ Health check OK")
        return True
    else:
        print(f"❌ Health check falhou: {{response.status_code}}")
        return False

def test_analyze_endpoint():
    \"\"\"Testa endpoint de análise\"\"\"
    print("🔍 Testando endpoint de análise...")
    data = {{
        "analysis_type": "vendas",
        "period": "último_mês",
        "detail_level": "básico"
    }}
    headers = {{"X-API-Key": API_KEY, "Content-Type": "application/json"}}
    
    response = requests.post(f"{{BASE_URL}}/analyze", json=data, headers=headers)
    if response.status_code == 200:
        print("✅ Análise OK")
        return True
    else:
        print(f"❌ Análise falhou: {{response.status_code}}")
        return False

def test_nlp_endpoint():
    \"\"\"Testa endpoint de NLP\"\"\"
    print("🔍 Testando endpoint de NLP...")
    data = {{
        "query": "Como foram as vendas do último mês?",
        "context": "teste_integracao"
    }}
    headers = {{"X-API-Key": API_KEY, "Content-Type": "application/json"}}
    
    response = requests.post(f"{{BASE_URL}}/nlp/query", json=data, headers=headers)
    if response.status_code == 200:
        print("✅ NLP OK")
        return True
    else:
        print(f"❌ NLP falhou: {{response.status_code}}")
        return False

def main():
    print("🧪 Iniciando testes de integração CÓRTEX BI + Copilot Studio")
    print("=" * 60)
    
    tests = [test_health_check, test_analyze_endpoint, test_nlp_endpoint]
    passed = 0
    
    for test in tests:
        if test():
            passed += 1
        time.sleep(1)
    
    print("=" * 60)
    print(f"📊 Resultados: {{passed}}/{{len(tests)}} testes passaram")
    
    if passed == len(tests):
        print("🎉 Todos os testes passaram! Integração pronta.")
    else:
        print("⚠️  Alguns testes falharam. Verifique a configuração.")

if __name__ == "__main__":
    main()
"""
        return script
    
    def generate_all_configs(self):
        """Gera todos os arquivos de configuração"""
        print(f"🔧 Gerando configurações para integração CÓRTEX BI + Copilot Studio")
        print(f"📁 Diretório de saída: {self.output_dir}")
        
        # Gerar configurações
        actions_config = self.create_actions_config()
        topics_config = self.create_topics_config()
        security_config = self.create_security_config()
        
        # Salvar arquivos JSON
        configs = {
            "actions_config.json": actions_config,
            "topics_config.json": topics_config,
            "security_config.json": security_config
        }
        
        for filename, config in configs.items():
            filepath = os.path.join(self.output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print(f"✅ {filename} criado")
        
        # Salvar scripts
        scripts = {
            "deploy.sh": self.create_deployment_script(),
            "test_integration.py": self.create_test_script()
        }
        
        for filename, script in scripts.items():
            filepath = os.path.join(self.output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(script)
            
            # Tornar scripts executáveis
            if filename.endswith('.sh'):
                os.chmod(filepath, 0o755)
            
            print(f"✅ {filename} criado")
        
        # Criar arquivo README
        readme_content = self.create_readme()
        readme_path = os.path.join(self.output_dir, "README.md")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"✅ README.md criado")
        
        print(f"\n🎉 Configuração completa! API Key gerada: {security_config['api_key']}")
        print(f"📋 Consulte o arquivo README.md para instruções de uso")
    
    def create_readme(self) -> str:
        """Cria arquivo README com instruções"""
        return f"""# Configuração de Integração CÓRTEX BI + Copilot Studio

Arquivos de configuração gerados automaticamente em {datetime.now().strftime('%d/%m/%Y às %H:%M')}.

## 📁 Arquivos Gerados

- `actions_config.json` - Configuração das Actions para Copilot Studio
- `topics_config.json` - Configuração dos tópicos de conversação
- `security_config.json` - Configuração de segurança e autenticação
- `deploy.sh` - Script de deployment automatizado
- `test_integration.py` - Script de testes da integração

## 🚀 Como Usar

### 1. Configurar CÓRTEX BI
```bash
# Executar script de deployment
./deploy.sh
```

### 2. Configurar Copilot Studio

1. Acesse https://copilotstudio.microsoft.com
2. Crie um novo Copilot ou edite um existente
3. Vá para "Actions" e importe as configurações de `actions_config.json`
4. Configure os tópicos usando `topics_config.json` como referência
5. Configure autenticação usando a API key de `security_config.json`

### 3. Testar Integração
```bash
# Executar testes automatizados
python3 test_integration.py
```

## 🔐 Segurança

- **API Key:** Configure a chave gerada no arquivo `security_config.json`
- **CORS:** Já configurado para domínios do Copilot Studio
- **Rate Limiting:** 100 requisições por minuto por padrão

## 📞 Suporte

Consulte o guia completo de integração para instruções detalhadas e troubleshooting.

---
*Gerado automaticamente pelo Configurador de Integração CÓRTEX BI*
"""

def main():
    parser = argparse.ArgumentParser(description='Configurar integração CÓRTEX BI + Copilot Studio')
    parser.add_argument('--url', required=True, help='URL base do CÓRTEX BI')
    parser.add_argument('--output', default='./copilot_integration', help='Diretório de saída')
    
    args = parser.parse_args()
    
    configurator = CopilotIntegrationConfigurator(args.url, args.output)
    configurator.generate_all_configs()

if __name__ == "__main__":
    main()

