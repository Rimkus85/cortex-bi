#!/usr/bin/env python3
"""
Script de Diagnóstico para Integração CÓRTEX BI com Copilot Studio
Versão: 1.0
Autor: Manus AI
"""

import requests
import json
import socket
import ssl
import time
import subprocess
import platform
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import argparse

class IntegrationDiagnostic:
    def __init__(self, cortex_url: str, api_key: Optional[str] = None):
        self.cortex_url = cortex_url.rstrip('/')
        self.api_key = api_key
        self.issues = []
        self.recommendations = []
        
    def log_issue(self, severity: str, component: str, description: str, solution: str):
        """Registra um problema encontrado"""
        issue = {
            "severity": severity,  # CRITICAL, HIGH, MEDIUM, LOW
            "component": component,
            "description": description,
            "solution": solution,
            "timestamp": datetime.now().isoformat()
        }
        self.issues.append(issue)
        
        # Exibir imediatamente
        severity_icon = {
            "CRITICAL": "🔴",
            "HIGH": "🟠", 
            "MEDIUM": "🟡",
            "LOW": "🔵"
        }
        print(f"{severity_icon.get(severity, '⚪')} [{severity}] {component}: {description}")
    
    def add_recommendation(self, category: str, recommendation: str):
        """Adiciona uma recomendação"""
        self.recommendations.append({
            "category": category,
            "recommendation": recommendation,
            "timestamp": datetime.now().isoformat()
        })
    
    def check_network_connectivity(self) -> Dict:
        """Verifica conectividade de rede básica"""
        print("\n🌐 Verificando conectividade de rede...")
        
        results = {}
        
        # Extrair host e porta
        url_parts = self.cortex_url.replace('http://', '').replace('https://', '')
        if ':' in url_parts:
            host, port = url_parts.split(':')
            port = int(port)
        else:
            host = url_parts
            port = 443 if 'https://' in self.cortex_url else 80
        
        # Teste de resolução DNS
        try:
            import socket
            ip = socket.gethostbyname(host)
            results['dns_resolution'] = {'status': 'OK', 'ip': ip}
            print(f"✅ DNS: {host} → {ip}")
        except Exception as e:
            results['dns_resolution'] = {'status': 'FAILED', 'error': str(e)}
            self.log_issue('CRITICAL', 'DNS', f'Falha na resolução DNS para {host}', 
                          'Verifique se o domínio está correto e acessível')
        
        # Teste de conectividade TCP
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                results['tcp_connectivity'] = {'status': 'OK', 'port': port}
                print(f"✅ TCP: Conectividade OK na porta {port}")
            else:
                results['tcp_connectivity'] = {'status': 'FAILED', 'port': port}
                self.log_issue('CRITICAL', 'TCP', f'Não foi possível conectar na porta {port}',
                              'Verifique firewall e se o serviço está rodando')
        except Exception as e:
            results['tcp_connectivity'] = {'status': 'ERROR', 'error': str(e)}
            self.log_issue('CRITICAL', 'TCP', f'Erro na conectividade TCP: {e}',
                          'Verifique configurações de rede')
        
        # Teste de latência
        try:
            start_time = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((host, port))
            sock.close()
            latency = (time.time() - start_time) * 1000
            
            results['latency'] = {'status': 'OK', 'ms': round(latency, 2)}
            print(f"✅ Latência: {latency:.2f}ms")
            
            if latency > 1000:
                self.log_issue('MEDIUM', 'Latência', f'Latência alta: {latency:.2f}ms',
                              'Considere otimizar rede ou usar CDN')
        except Exception as e:
            results['latency'] = {'status': 'FAILED', 'error': str(e)}
        
        return results
    
    def check_ssl_certificate(self) -> Dict:
        """Verifica certificado SSL se usando HTTPS"""
        if not self.cortex_url.startswith('https://'):
            return {'status': 'NOT_APPLICABLE', 'reason': 'HTTP em uso'}
        
        print("\n🔒 Verificando certificado SSL...")
        
        try:
            # Extrair hostname
            hostname = self.cortex_url.replace('https://', '').split(':')[0]
            
            # Verificar certificado
            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Verificar validade
                    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_until_expiry = (not_after - datetime.now()).days
                    
                    result = {
                        'status': 'VALID',
                        'subject': dict(x[0] for x in cert['subject']),
                        'issuer': dict(x[0] for x in cert['issuer']),
                        'expires': cert['notAfter'],
                        'days_until_expiry': days_until_expiry
                    }
                    
                    print(f"✅ SSL: Certificado válido (expira em {days_until_expiry} dias)")
                    
                    if days_until_expiry < 30:
                        self.log_issue('HIGH', 'SSL', f'Certificado expira em {days_until_expiry} dias',
                                      'Renove o certificado SSL antes da expiração')
                    
                    return result
                    
        except ssl.SSLError as e:
            self.log_issue('CRITICAL', 'SSL', f'Erro no certificado SSL: {e}',
                          'Verifique se o certificado está válido e configurado corretamente')
            return {'status': 'SSL_ERROR', 'error': str(e)}
        except Exception as e:
            self.log_issue('HIGH', 'SSL', f'Erro ao verificar SSL: {e}',
                          'Verifique configuração HTTPS')
            return {'status': 'ERROR', 'error': str(e)}
    
    def check_api_endpoints(self) -> Dict:
        """Verifica se os endpoints da API estão funcionando"""
        print("\n🔌 Verificando endpoints da API...")
        
        headers = {}
        if self.api_key:
            headers['X-API-Key'] = self.api_key
        
        endpoints = {
            '/health': 'GET',
            '/list-files': 'GET',
            '/docs': 'GET',
            '/analyze': 'POST',
            '/nlp/query': 'POST'
        }
        
        results = {}
        
        for endpoint, method in endpoints.items():
            try:
                url = f"{self.cortex_url}{endpoint}"
                
                if method == 'GET':
                    response = requests.get(url, headers=headers, timeout=10)
                else:
                    # Para POST, enviar dados de teste mínimos
                    test_data = {}
                    if endpoint == '/analyze':
                        test_data = {'analysis_type': 'test'}
                    elif endpoint == '/nlp/query':
                        test_data = {'query': 'test'}
                    
                    response = requests.post(url, json=test_data, headers=headers, timeout=10)
                
                results[endpoint] = {
                    'status_code': response.status_code,
                    'response_time': response.elapsed.total_seconds(),
                    'content_type': response.headers.get('content-type', ''),
                    'status': 'OK' if response.status_code < 400 else 'ERROR'
                }
                
                if response.status_code < 400:
                    print(f"✅ {endpoint}: {response.status_code} ({response.elapsed.total_seconds():.2f}s)")
                else:
                    print(f"❌ {endpoint}: {response.status_code}")
                    self.log_issue('HIGH', 'API', f'Endpoint {endpoint} retornou {response.status_code}',
                                  'Verifique logs do servidor e configuração da API')
                
            except requests.exceptions.Timeout:
                results[endpoint] = {'status': 'TIMEOUT'}
                self.log_issue('HIGH', 'API', f'Timeout no endpoint {endpoint}',
                              'Verifique performance do servidor ou aumente timeout')
            except requests.exceptions.ConnectionError:
                results[endpoint] = {'status': 'CONNECTION_ERROR'}
                self.log_issue('CRITICAL', 'API', f'Erro de conexão no endpoint {endpoint}',
                              'Verifique se o servidor está rodando e acessível')
            except Exception as e:
                results[endpoint] = {'status': 'ERROR', 'error': str(e)}
                self.log_issue('HIGH', 'API', f'Erro no endpoint {endpoint}: {e}',
                              'Verifique configuração e logs do servidor')
        
        return results
    
    def check_cors_configuration(self) -> Dict:
        """Verifica configuração CORS"""
        print("\n🌍 Verificando configuração CORS...")
        
        try:
            # Simular requisição do Copilot Studio
            headers = {
                'Origin': 'https://copilotstudio.microsoft.com',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type, X-API-Key'
            }
            
            response = requests.options(f"{self.cortex_url}/health", headers=headers, timeout=10)
            
            cors_headers = {
                'access-control-allow-origin': response.headers.get('access-control-allow-origin'),
                'access-control-allow-methods': response.headers.get('access-control-allow-methods'),
                'access-control-allow-headers': response.headers.get('access-control-allow-headers'),
                'access-control-allow-credentials': response.headers.get('access-control-allow-credentials')
            }
            
            result = {
                'status_code': response.status_code,
                'cors_headers': cors_headers
            }
            
            # Verificar se CORS está configurado adequadamente
            if cors_headers['access-control-allow-origin'] in ['*', 'https://copilotstudio.microsoft.com']:
                print("✅ CORS: Configurado adequadamente")
                result['status'] = 'OK'
            else:
                print("⚠️ CORS: Pode não estar configurado para Copilot Studio")
                self.log_issue('MEDIUM', 'CORS', 'CORS pode não permitir acesso do Copilot Studio',
                              'Configure CORS para permitir origem https://copilotstudio.microsoft.com')
                result['status'] = 'WARNING'
            
            return result
            
        except Exception as e:
            self.log_issue('MEDIUM', 'CORS', f'Erro ao verificar CORS: {e}',
                          'Verifique configuração CORS no servidor')
            return {'status': 'ERROR', 'error': str(e)}
    
    def check_authentication(self) -> Dict:
        """Verifica autenticação"""
        print("\n🔐 Verificando autenticação...")
        
        if not self.api_key:
            self.log_issue('HIGH', 'Auth', 'API Key não fornecida',
                          'Configure uma API Key para autenticação')
            return {'status': 'NO_API_KEY'}
        
        try:
            # Testar com API key
            headers = {'X-API-Key': self.api_key}
            response = requests.get(f"{self.cortex_url}/health", headers=headers, timeout=10)
            
            if response.status_code == 200:
                print("✅ Autenticação: API Key válida")
                return {'status': 'OK', 'api_key_valid': True}
            elif response.status_code == 401:
                self.log_issue('CRITICAL', 'Auth', 'API Key inválida ou expirada',
                              'Verifique se a API Key está correta e ativa')
                return {'status': 'INVALID_KEY'}
            elif response.status_code == 403:
                self.log_issue('HIGH', 'Auth', 'API Key sem permissões adequadas',
                              'Verifique permissões da API Key')
                return {'status': 'INSUFFICIENT_PERMISSIONS'}
            else:
                self.log_issue('MEDIUM', 'Auth', f'Resposta inesperada na autenticação: {response.status_code}',
                              'Verifique configuração de autenticação')
                return {'status': 'UNEXPECTED_RESPONSE', 'status_code': response.status_code}
                
        except Exception as e:
            self.log_issue('HIGH', 'Auth', f'Erro ao testar autenticação: {e}',
                          'Verifique configuração de autenticação')
            return {'status': 'ERROR', 'error': str(e)}
    
    def check_server_performance(self) -> Dict:
        """Verifica performance do servidor"""
        print("\n⚡ Verificando performance do servidor...")
        
        try:
            # Fazer múltiplas requisições para medir performance
            times = []
            for i in range(5):
                start = time.time()
                response = requests.get(f"{self.cortex_url}/health", timeout=10)
                end = time.time()
                
                if response.status_code == 200:
                    times.append(end - start)
                time.sleep(0.5)
            
            if times:
                avg_time = sum(times) / len(times)
                min_time = min(times)
                max_time = max(times)
                
                result = {
                    'status': 'OK',
                    'avg_response_time': round(avg_time, 3),
                    'min_response_time': round(min_time, 3),
                    'max_response_time': round(max_time, 3),
                    'samples': len(times)
                }
                
                print(f"✅ Performance: Tempo médio {avg_time:.3f}s (min: {min_time:.3f}s, max: {max_time:.3f}s)")
                
                if avg_time > 2.0:
                    self.log_issue('MEDIUM', 'Performance', f'Tempo de resposta alto: {avg_time:.3f}s',
                                  'Considere otimizar servidor ou aumentar recursos')
                
                return result
            else:
                self.log_issue('HIGH', 'Performance', 'Não foi possível medir performance',
                              'Verifique se o servidor está respondendo')
                return {'status': 'NO_DATA'}
                
        except Exception as e:
            self.log_issue('MEDIUM', 'Performance', f'Erro ao medir performance: {e}',
                          'Verifique conectividade e status do servidor')
            return {'status': 'ERROR', 'error': str(e)}
    
    def check_system_resources(self) -> Dict:
        """Verifica recursos do sistema (se local)"""
        print("\n💻 Verificando recursos do sistema...")
        
        try:
            # Verificar se é sistema local
            if 'localhost' in self.cortex_url or '127.0.0.1' in self.cortex_url:
                import psutil
                
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                result = {
                    'status': 'OK',
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_available_gb': round(memory.available / (1024**3), 2),
                    'disk_percent': disk.percent,
                    'disk_free_gb': round(disk.free / (1024**3), 2)
                }
                
                print(f"✅ CPU: {cpu_percent}%")
                print(f"✅ Memória: {memory.percent}% ({result['memory_available_gb']}GB disponível)")
                print(f"✅ Disco: {disk.percent}% ({result['disk_free_gb']}GB livre)")
                
                # Verificar se recursos estão críticos
                if cpu_percent > 90:
                    self.log_issue('HIGH', 'Sistema', f'CPU alta: {cpu_percent}%',
                                  'Considere otimizar processos ou aumentar recursos')
                
                if memory.percent > 90:
                    self.log_issue('HIGH', 'Sistema', f'Memória alta: {memory.percent}%',
                                  'Considere aumentar RAM ou otimizar uso de memória')
                
                if disk.percent > 90:
                    self.log_issue('MEDIUM', 'Sistema', f'Disco cheio: {disk.percent}%',
                                  'Libere espaço em disco')
                
                return result
            else:
                return {'status': 'REMOTE_SERVER', 'message': 'Servidor remoto - recursos não verificáveis'}
                
        except ImportError:
            return {'status': 'PSUTIL_NOT_AVAILABLE', 'message': 'psutil não instalado'}
        except Exception as e:
            self.log_issue('LOW', 'Sistema', f'Erro ao verificar recursos: {e}',
                          'Instale psutil para monitoramento de recursos')
            return {'status': 'ERROR', 'error': str(e)}
    
    def generate_recommendations(self):
        """Gera recomendações baseadas nos problemas encontrados"""
        print("\n💡 Gerando recomendações...")
        
        # Recomendações baseadas em problemas críticos
        critical_issues = [i for i in self.issues if i['severity'] == 'CRITICAL']
        if critical_issues:
            self.add_recommendation('Urgente', 'Resolva problemas críticos antes de usar em produção')
        
        # Recomendações de segurança
        if not self.cortex_url.startswith('https://'):
            self.add_recommendation('Segurança', 'Use HTTPS em produção para maior segurança')
        
        if not self.api_key:
            self.add_recommendation('Segurança', 'Configure autenticação por API Key')
        
        # Recomendações de performance
        high_perf_issues = [i for i in self.issues if i['component'] == 'Performance']
        if high_perf_issues:
            self.add_recommendation('Performance', 'Otimize performance do servidor para melhor experiência')
        
        # Recomendações de monitoramento
        self.add_recommendation('Monitoramento', 'Configure monitoramento contínuo da integração')
        self.add_recommendation('Backup', 'Implemente backup regular das configurações')
        
        # Exibir recomendações
        if self.recommendations:
            for rec in self.recommendations:
                print(f"💡 {rec['category']}: {rec['recommendation']}")
    
    def run_full_diagnostic(self) -> Dict:
        """Executa diagnóstico completo"""
        print("🔍 Iniciando diagnóstico completo da integração CÓRTEX BI + Copilot Studio")
        print("=" * 80)
        
        start_time = time.time()
        
        # Executar todos os testes
        results = {
            'network': self.check_network_connectivity(),
            'ssl': self.check_ssl_certificate(),
            'api_endpoints': self.check_api_endpoints(),
            'cors': self.check_cors_configuration(),
            'authentication': self.check_authentication(),
            'performance': self.check_server_performance(),
            'system_resources': self.check_system_resources()
        }
        
        # Gerar recomendações
        self.generate_recommendations()
        
        # Resumo final
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 80)
        print("📊 RESUMO DO DIAGNÓSTICO")
        print("=" * 80)
        
        # Contar problemas por severidade
        severity_counts = {}
        for issue in self.issues:
            severity = issue['severity']
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        print(f"🔴 Críticos: {severity_counts.get('CRITICAL', 0)}")
        print(f"🟠 Altos: {severity_counts.get('HIGH', 0)}")
        print(f"🟡 Médios: {severity_counts.get('MEDIUM', 0)}")
        print(f"🔵 Baixos: {severity_counts.get('LOW', 0)}")
        
        # Status geral
        if severity_counts.get('CRITICAL', 0) == 0 and severity_counts.get('HIGH', 0) <= 1:
            overall_status = "HEALTHY"
            print(f"\n✅ STATUS GERAL: SAUDÁVEL")
        elif severity_counts.get('CRITICAL', 0) <= 1:
            overall_status = "NEEDS_ATTENTION"
            print(f"\n⚠️ STATUS GERAL: REQUER ATENÇÃO")
        else:
            overall_status = "CRITICAL"
            print(f"\n🔴 STATUS GERAL: CRÍTICO")
        
        print(f"⏱️ Diagnóstico concluído em {duration:.2f} segundos")
        
        return {
            'overall_status': overall_status,
            'duration': duration,
            'issues': self.issues,
            'recommendations': self.recommendations,
            'test_results': results,
            'summary': severity_counts
        }

def main():
    parser = argparse.ArgumentParser(description='Diagnóstico de integração CÓRTEX BI + Copilot Studio')
    parser.add_argument('--url', required=True, help='URL base do CÓRTEX BI')
    parser.add_argument('--api-key', help='API Key para autenticação')
    parser.add_argument('--output', help='Arquivo para salvar relatório JSON')
    parser.add_argument('--verbose', action='store_true', help='Saída detalhada')
    
    args = parser.parse_args()
    
    # Executar diagnóstico
    diagnostic = IntegrationDiagnostic(args.url, args.api_key)
    results = diagnostic.run_full_diagnostic()
    
    # Salvar relatório se solicitado
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n📄 Relatório detalhado salvo em: {args.output}")
    
    # Código de saída baseado no status
    if results['overall_status'] == 'HEALTHY':
        exit(0)
    elif results['overall_status'] == 'NEEDS_ATTENTION':
        exit(1)
    else:
        exit(2)

if __name__ == "__main__":
    main()

