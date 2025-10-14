#!/usr/bin/env python3
"""
Script de Verificação de Pré-requisitos para Integração CÓRTEX BI com Copilot Studio
Versão: 1.0
Autor: Manus AI
"""

import requests
import json
import sys
import time
import socket
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class CortexIntegrationChecker:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.results = []
        
    def log_result(self, test_name: str, status: str, message: str, details: Optional[str] = None):
        """Registra resultado de um teste"""
        result = {
            "test": test_name,
            "status": status,  # SUCCESS, WARNING, ERROR
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        
        # Exibir resultado imediatamente
        status_icon = "✅" if status == "SUCCESS" else "⚠️" if status == "WARNING" else "❌"
        print(f"{status_icon} {test_name}: {message}")
        if details:
            print(f"   Detalhes: {details}")
    
    def check_server_connectivity(self) -> bool:
        """Verifica se o servidor CÓRTEX BI está acessível"""
        try:
            # Extrair host e porta da URL
            url_parts = self.base_url.replace('http://', '').replace('https://', '')
            if ':' in url_parts:
                host, port = url_parts.split(':')
                port = int(port)
            else:
                host = url_parts
                port = 80 if 'http://' in self.base_url else 443
            
            # Teste de conectividade TCP
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                self.log_result(
                    "Conectividade TCP",
                    "SUCCESS",
                    f"Servidor acessível em {host}:{port}"
                )
                return True
            else:
                self.log_result(
                    "Conectividade TCP",
                    "ERROR",
                    f"Não foi possível conectar ao servidor {host}:{port}",
                    "Verifique se o servidor está rodando e se não há firewall bloqueando"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Conectividade TCP",
                "ERROR",
                "Erro ao testar conectividade",
                str(e)
            )
            return False
    
    def check_health_endpoint(self) -> bool:
        """Verifica se o endpoint de health está funcionando"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                
                # Verificar se todos os serviços estão ativos
                services = health_data.get('services', {})
                inactive_services = [name for name, status in services.items() if status != 'active']
                
                if not inactive_services:
                    self.log_result(
                        "Health Check",
                        "SUCCESS",
                        "Todos os módulos estão ativos",
                        f"Serviços: {', '.join(services.keys())}"
                    )
                    return True
                else:
                    self.log_result(
                        "Health Check",
                        "WARNING",
                        f"Alguns módulos estão inativos: {', '.join(inactive_services)}",
                        "Verifique os logs do servidor para mais detalhes"
                    )
                    return False
            else:
                self.log_result(
                    "Health Check",
                    "ERROR",
                    f"Endpoint retornou status {response.status_code}",
                    response.text[:200]
                )
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Health Check",
                "ERROR",
                "Erro ao acessar endpoint de health",
                str(e)
            )
            return False
    
    def check_api_endpoints(self) -> Dict[str, bool]:
        """Verifica se os principais endpoints estão respondendo"""
        endpoints = {
            "/": "Endpoint raiz",
            "/health": "Health check",
            "/list-files": "Listagem de arquivos",
            "/docs": "Documentação da API"
        }
        
        results = {}
        
        for endpoint, description in endpoints.items():
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                
                if response.status_code in [200, 404]:  # 404 é aceitável para alguns endpoints
                    self.log_result(
                        f"Endpoint {endpoint}",
                        "SUCCESS",
                        f"{description} acessível"
                    )
                    results[endpoint] = True
                else:
                    self.log_result(
                        f"Endpoint {endpoint}",
                        "WARNING",
                        f"{description} retornou status {response.status_code}"
                    )
                    results[endpoint] = False
                    
            except requests.exceptions.RequestException as e:
                self.log_result(
                    f"Endpoint {endpoint}",
                    "ERROR",
                    f"Erro ao acessar {description}",
                    str(e)
                )
                results[endpoint] = False
        
        return results
    
    def check_cors_configuration(self) -> bool:
        """Verifica se CORS está configurado adequadamente"""
        try:
            # Fazer uma requisição OPTIONS para verificar CORS
            response = requests.options(f"{self.base_url}/health", timeout=5)
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            
            if cors_headers['Access-Control-Allow-Origin']:
                self.log_result(
                    "Configuração CORS",
                    "SUCCESS",
                    "CORS configurado",
                    f"Origin: {cors_headers['Access-Control-Allow-Origin']}"
                )
                return True
            else:
                self.log_result(
                    "Configuração CORS",
                    "WARNING",
                    "CORS pode não estar configurado adequadamente",
                    "Verifique se o Copilot Studio conseguirá acessar a API"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Configuração CORS",
                "WARNING",
                "Não foi possível verificar CORS",
                str(e)
            )
            return False
    
    def check_ssl_certificate(self) -> bool:
        """Verifica se SSL está configurado (se usando HTTPS)"""
        if not self.base_url.startswith('https://'):
            self.log_result(
                "Certificado SSL",
                "WARNING",
                "Servidor não está usando HTTPS",
                "Recomenda-se usar HTTPS para produção"
            )
            return False
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5, verify=True)
            self.log_result(
                "Certificado SSL",
                "SUCCESS",
                "Certificado SSL válido"
            )
            return True
            
        except requests.exceptions.SSLError as e:
            self.log_result(
                "Certificado SSL",
                "ERROR",
                "Problema com certificado SSL",
                str(e)
            )
            return False
        except Exception as e:
            self.log_result(
                "Certificado SSL",
                "WARNING",
                "Não foi possível verificar SSL",
                str(e)
            )
            return False
    
    def test_api_functionality(self) -> bool:
        """Testa funcionalidades básicas da API"""
        try:
            # Teste de listagem de arquivos
            response = requests.get(f"{self.base_url}/list-files", timeout=10)
            
            if response.status_code == 200:
                files = response.json()
                self.log_result(
                    "Funcionalidade API",
                    "SUCCESS",
                    f"API funcionando - {len(files)} arquivos encontrados"
                )
                return True
            else:
                self.log_result(
                    "Funcionalidade API",
                    "WARNING",
                    f"API retornou status {response.status_code}",
                    "Algumas funcionalidades podem não estar disponíveis"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Funcionalidade API",
                "ERROR",
                "Erro ao testar funcionalidade da API",
                str(e)
            )
            return False
    
    def generate_integration_config(self) -> Dict:
        """Gera configuração sugerida para integração"""
        config = {
            "cortex_bi_url": self.base_url,
            "recommended_actions": [
                {
                    "name": "CORTEX_HealthCheck",
                    "method": "GET",
                    "endpoint": "/health",
                    "description": "Verificar status do sistema"
                },
                {
                    "name": "CORTEX_Analyze",
                    "method": "POST",
                    "endpoint": "/analyze",
                    "description": "Executar análises de dados"
                },
                {
                    "name": "CORTEX_GeneratePPTX",
                    "method": "POST",
                    "endpoint": "/generate-pptx",
                    "description": "Gerar apresentações"
                },
                {
                    "name": "CORTEX_NLPQuery",
                    "method": "POST",
                    "endpoint": "/nlp/query",
                    "description": "Processar consultas em linguagem natural"
                }
            ],
            "authentication": {
                "type": "api_key",
                "header": "X-API-Key",
                "note": "Configure uma API key segura no CÓRTEX BI"
            },
            "timeout_settings": {
                "connection_timeout": 10,
                "read_timeout": 30,
                "retry_attempts": 3
            }
        }
        
        return config
    
    def run_all_checks(self) -> Dict:
        """Executa todos os testes de verificação"""
        print("🔍 Iniciando verificação de pré-requisitos para integração CÓRTEX BI + Copilot Studio")
        print("=" * 80)
        
        # Executar todos os testes
        connectivity_ok = self.check_server_connectivity()
        
        if connectivity_ok:
            health_ok = self.check_health_endpoint()
            endpoints_ok = self.check_api_endpoints()
            cors_ok = self.check_cors_configuration()
            ssl_ok = self.check_ssl_certificate()
            api_ok = self.test_api_functionality()
        else:
            health_ok = endpoints_ok = cors_ok = ssl_ok = api_ok = False
        
        # Resumo dos resultados
        print("\n" + "=" * 80)
        print("📊 RESUMO DOS RESULTADOS")
        print("=" * 80)
        
        success_count = len([r for r in self.results if r['status'] == 'SUCCESS'])
        warning_count = len([r for r in self.results if r['status'] == 'WARNING'])
        error_count = len([r for r in self.results if r['status'] == 'ERROR'])
        
        print(f"✅ Sucessos: {success_count}")
        print(f"⚠️  Avisos: {warning_count}")
        print(f"❌ Erros: {error_count}")
        
        # Determinar status geral
        if error_count == 0 and warning_count <= 2:
            overall_status = "READY"
            print(f"\n🎉 STATUS GERAL: PRONTO PARA INTEGRAÇÃO")
        elif error_count <= 1:
            overall_status = "NEEDS_ATTENTION"
            print(f"\n⚠️  STATUS GERAL: REQUER ATENÇÃO")
        else:
            overall_status = "NOT_READY"
            print(f"\n❌ STATUS GERAL: NÃO PRONTO PARA INTEGRAÇÃO")
        
        # Gerar configuração sugerida
        config = self.generate_integration_config()
        
        return {
            "overall_status": overall_status,
            "test_results": self.results,
            "summary": {
                "success": success_count,
                "warnings": warning_count,
                "errors": error_count
            },
            "suggested_config": config
        }

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Verificar pré-requisitos para integração CÓRTEX BI + Copilot Studio')
    parser.add_argument('--url', default='http://localhost:8000', help='URL base do CÓRTEX BI')
    parser.add_argument('--output', help='Arquivo para salvar relatório JSON')
    
    args = parser.parse_args()
    
    # Executar verificações
    checker = CortexIntegrationChecker(args.url)
    results = checker.run_all_checks()
    
    # Salvar relatório se solicitado
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n📄 Relatório salvo em: {args.output}")
    
    # Retornar código de saída apropriado
    if results['overall_status'] == 'READY':
        sys.exit(0)
    elif results['overall_status'] == 'NEEDS_ATTENTION':
        sys.exit(1)
    else:
        sys.exit(2)

if __name__ == "__main__":
    main()

