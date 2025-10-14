#!/usr/bin/env python3
"""
Script de Monitoramento Contínuo para Integração CÓRTEX BI com Copilot Studio
Versão: 1.0
Autor: Manus AI
"""

import requests
import json
import time
import smtplib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import argparse
import threading

class IntegrationMonitor:
    def __init__(self, config_file: str):
        self.config = self.load_config(config_file)
        self.setup_logging()
        self.metrics_history = []
        self.alerts_sent = {}
        self.running = False
        
    def load_config(self, config_file: str) -> Dict:
        """Carrega configuração do arquivo JSON"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Configuração padrão se arquivo não existir
            return {
                "cortex_url": "http://localhost:8000",
                "api_key": "",
                "monitoring": {
                    "interval_seconds": 60,
                    "timeout_seconds": 10,
                    "max_response_time": 2.0,
                    "alert_threshold_failures": 3
                },
                "endpoints": [
                    "/health",
                    "/list-files",
                    "/docs"
                ],
                "alerts": {
                    "email": {
                        "enabled": False,
                        "smtp_server": "smtp.gmail.com",
                        "smtp_port": 587,
                        "username": "",
                        "password": "",
                        "to_addresses": []
                    },
                    "webhook": {
                        "enabled": False,
                        "url": "",
                        "headers": {}
                    }
                },
                "logging": {
                    "level": "INFO",
                    "file": "integration_monitor.log",
                    "max_size_mb": 10,
                    "backup_count": 5
                }
            }
    
    def setup_logging(self):
        """Configura sistema de logging"""
        log_config = self.config.get('logging', {})
        
        # Configurar rotação de logs
        from logging.handlers import RotatingFileHandler
        
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        log_file = log_config.get('file', 'integration_monitor.log')
        max_bytes = log_config.get('max_size_mb', 10) * 1024 * 1024
        backup_count = log_config.get('backup_count', 5)
        
        # Configurar logger
        self.logger = logging.getLogger('IntegrationMonitor')
        self.logger.setLevel(log_level)
        
        # Handler para arquivo com rotação
        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count
        )
        file_handler.setLevel(log_level)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        
        # Formato das mensagens
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def check_endpoint(self, endpoint: str) -> Dict:
        """Verifica um endpoint específico"""
        url = f"{self.config['cortex_url']}{endpoint}"
        headers = {}
        
        if self.config.get('api_key'):
            headers['X-API-Key'] = self.config['api_key']
        
        try:
            start_time = time.time()
            response = requests.get(
                url, 
                headers=headers, 
                timeout=self.config['monitoring']['timeout_seconds']
            )
            end_time = time.time()
            
            response_time = end_time - start_time
            
            return {
                'endpoint': endpoint,
                'status': 'OK' if response.status_code < 400 else 'ERROR',
                'status_code': response.status_code,
                'response_time': round(response_time, 3),
                'timestamp': datetime.now().isoformat(),
                'error': None
            }
            
        except requests.exceptions.Timeout:
            return {
                'endpoint': endpoint,
                'status': 'TIMEOUT',
                'status_code': None,
                'response_time': None,
                'timestamp': datetime.now().isoformat(),
                'error': 'Request timeout'
            }
        except requests.exceptions.ConnectionError:
            return {
                'endpoint': endpoint,
                'status': 'CONNECTION_ERROR',
                'status_code': None,
                'response_time': None,
                'timestamp': datetime.now().isoformat(),
                'error': 'Connection failed'
            }
        except Exception as e:
            return {
                'endpoint': endpoint,
                'status': 'ERROR',
                'status_code': None,
                'response_time': None,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def check_health_details(self) -> Dict:
        """Verifica detalhes do health check"""
        try:
            url = f"{self.config['cortex_url']}/health"
            headers = {}
            
            if self.config.get('api_key'):
                headers['X-API-Key'] = self.config['api_key']
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                services = health_data.get('services', {})
                
                # Contar serviços ativos/inativos
                active_services = sum(1 for status in services.values() if status == 'active')
                total_services = len(services)
                
                return {
                    'status': 'OK',
                    'active_services': active_services,
                    'total_services': total_services,
                    'services': services,
                    'health_score': round((active_services / total_services) * 100, 1) if total_services > 0 else 0
                }
            else:
                return {
                    'status': 'ERROR',
                    'error': f'Health endpoint returned {response.status_code}'
                }
                
        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e)
            }
    
    def collect_metrics(self) -> Dict:
        """Coleta métricas completas do sistema"""
        self.logger.info("Coletando métricas do sistema...")
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'endpoints': [],
            'health_details': self.check_health_details(),
            'overall_status': 'OK'
        }
        
        # Verificar cada endpoint
        failed_endpoints = 0
        total_response_time = 0
        successful_checks = 0
        
        for endpoint in self.config['endpoints']:
            result = self.check_endpoint(endpoint)
            metrics['endpoints'].append(result)
            
            if result['status'] != 'OK':
                failed_endpoints += 1
            else:
                if result['response_time']:
                    total_response_time += result['response_time']
                    successful_checks += 1
        
        # Calcular métricas agregadas
        metrics['failed_endpoints'] = failed_endpoints
        metrics['success_rate'] = round(((len(self.config['endpoints']) - failed_endpoints) / len(self.config['endpoints'])) * 100, 1)
        metrics['avg_response_time'] = round(total_response_time / successful_checks, 3) if successful_checks > 0 else None
        
        # Determinar status geral
        if failed_endpoints == 0:
            metrics['overall_status'] = 'HEALTHY'
        elif failed_endpoints <= 1:
            metrics['overall_status'] = 'DEGRADED'
        else:
            metrics['overall_status'] = 'CRITICAL'
        
        # Verificar se response time está alto
        max_response_time = self.config['monitoring']['max_response_time']
        if metrics['avg_response_time'] and metrics['avg_response_time'] > max_response_time:
            metrics['overall_status'] = 'DEGRADED' if metrics['overall_status'] == 'HEALTHY' else metrics['overall_status']
        
        return metrics
    
    def should_send_alert(self, alert_type: str, current_status: str) -> bool:
        """Determina se deve enviar alerta baseado no histórico"""
        now = datetime.now()
        
        # Verificar se já enviou alerta recentemente (evitar spam)
        if alert_type in self.alerts_sent:
            last_sent = self.alerts_sent[alert_type]
            if now - last_sent < timedelta(minutes=15):  # Cooldown de 15 minutos
                return False
        
        # Verificar threshold de falhas consecutivas
        threshold = self.config['monitoring']['alert_threshold_failures']
        
        if len(self.metrics_history) >= threshold:
            recent_metrics = self.metrics_history[-threshold:]
            consecutive_failures = all(m['overall_status'] in ['DEGRADED', 'CRITICAL'] for m in recent_metrics)
            
            if consecutive_failures and current_status in ['DEGRADED', 'CRITICAL']:
                return True
        
        return False
    
    def send_email_alert(self, subject: str, body: str):
        """Envia alerta por email"""
        email_config = self.config['alerts']['email']
        
        if not email_config['enabled']:
            return
        
        try:
            msg = MimeMultipart()
            msg['From'] = email_config['username']
            msg['To'] = ', '.join(email_config['to_addresses'])
            msg['Subject'] = subject
            
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['username'], email_config['password'])
            
            text = msg.as_string()
            server.sendmail(email_config['username'], email_config['to_addresses'], text)
            server.quit()
            
            self.logger.info(f"Alerta enviado por email: {subject}")
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar email: {e}")
    
    def send_webhook_alert(self, payload: Dict):
        """Envia alerta via webhook"""
        webhook_config = self.config['alerts']['webhook']
        
        if not webhook_config['enabled']:
            return
        
        try:
            headers = webhook_config.get('headers', {})
            headers['Content-Type'] = 'application/json'
            
            response = requests.post(
                webhook_config['url'],
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code < 400:
                self.logger.info("Alerta enviado via webhook")
            else:
                self.logger.error(f"Erro no webhook: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Erro ao enviar webhook: {e}")
    
    def process_alerts(self, metrics: Dict):
        """Processa e envia alertas se necessário"""
        status = metrics['overall_status']
        
        if status in ['DEGRADED', 'CRITICAL']:
            alert_type = f"status_{status.lower()}"
            
            if self.should_send_alert(alert_type, status):
                # Preparar conteúdo do alerta
                subject = f"🚨 CÓRTEX BI Integration Alert - {status}"
                
                body = f"""
Alerta de Monitoramento - Integração CÓRTEX BI + Copilot Studio

Status: {status}
Timestamp: {metrics['timestamp']}
Taxa de Sucesso: {metrics['success_rate']}%
Tempo de Resposta Médio: {metrics['avg_response_time']}s

Detalhes dos Endpoints:
"""
                
                for endpoint_result in metrics['endpoints']:
                    body += f"- {endpoint_result['endpoint']}: {endpoint_result['status']}"
                    if endpoint_result['response_time']:
                        body += f" ({endpoint_result['response_time']}s)"
                    body += "\n"
                
                if metrics['health_details']['status'] == 'OK':
                    body += f"\nServiços Ativos: {metrics['health_details']['active_services']}/{metrics['health_details']['total_services']}"
                    body += f"\nHealth Score: {metrics['health_details']['health_score']}%"
                
                body += f"\n\nURL do Sistema: {self.config['cortex_url']}"
                body += "\n\nVerifique o sistema e tome as ações necessárias."
                
                # Enviar alertas
                self.send_email_alert(subject, body)
                
                webhook_payload = {
                    'alert_type': alert_type,
                    'status': status,
                    'metrics': metrics,
                    'timestamp': metrics['timestamp']
                }
                self.send_webhook_alert(webhook_payload)
                
                # Registrar que alerta foi enviado
                self.alerts_sent[alert_type] = datetime.now()
    
    def generate_status_report(self) -> str:
        """Gera relatório de status atual"""
        if not self.metrics_history:
            return "Nenhuma métrica coletada ainda."
        
        latest = self.metrics_history[-1]
        
        report = f"""
📊 RELATÓRIO DE STATUS - CÓRTEX BI + Copilot Studio
{'='*60}

🕐 Última Verificação: {latest['timestamp']}
📈 Status Geral: {latest['overall_status']}
✅ Taxa de Sucesso: {latest['success_rate']}%
⚡ Tempo Médio de Resposta: {latest['avg_response_time']}s

🔗 Endpoints Monitorados:
"""
        
        for endpoint in latest['endpoints']:
            status_icon = "✅" if endpoint['status'] == 'OK' else "❌"
            report += f"{status_icon} {endpoint['endpoint']}: {endpoint['status']}"
            if endpoint['response_time']:
                report += f" ({endpoint['response_time']}s)"
            report += "\n"
        
        if latest['health_details']['status'] == 'OK':
            report += f"\n🏥 Health Check:"
            report += f"\n   Serviços Ativos: {latest['health_details']['active_services']}/{latest['health_details']['total_services']}"
            report += f"\n   Health Score: {latest['health_details']['health_score']}%"
        
        # Estatísticas históricas (últimas 24h)
        if len(self.metrics_history) > 1:
            recent_metrics = [m for m in self.metrics_history if 
                            datetime.fromisoformat(m['timestamp']) > datetime.now() - timedelta(hours=24)]
            
            if recent_metrics:
                avg_success = sum(m['success_rate'] for m in recent_metrics) / len(recent_metrics)
                avg_response = sum(m['avg_response_time'] for m in recent_metrics if m['avg_response_time']) / len([m for m in recent_metrics if m['avg_response_time']])
                
                report += f"\n\n📈 Estatísticas (24h):"
                report += f"\n   Taxa de Sucesso Média: {avg_success:.1f}%"
                report += f"\n   Tempo de Resposta Médio: {avg_response:.3f}s"
                report += f"\n   Verificações Realizadas: {len(recent_metrics)}"
        
        return report
    
    def run_monitoring_cycle(self):
        """Executa um ciclo de monitoramento"""
        try:
            # Coletar métricas
            metrics = self.collect_metrics()
            
            # Adicionar ao histórico
            self.metrics_history.append(metrics)
            
            # Manter apenas últimas 1000 métricas para evitar uso excessivo de memória
            if len(self.metrics_history) > 1000:
                self.metrics_history = self.metrics_history[-1000:]
            
            # Processar alertas
            self.process_alerts(metrics)
            
            # Log do status
            self.logger.info(f"Status: {metrics['overall_status']}, Success Rate: {metrics['success_rate']}%, Avg Response: {metrics['avg_response_time']}s")
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Erro no ciclo de monitoramento: {e}")
            return None
    
    def start_monitoring(self):
        """Inicia monitoramento contínuo"""
        self.running = True
        interval = self.config['monitoring']['interval_seconds']
        
        self.logger.info(f"Iniciando monitoramento contínuo (intervalo: {interval}s)")
        print(f"🔍 Monitoramento iniciado - Intervalo: {interval}s")
        print("Pressione Ctrl+C para parar")
        
        try:
            while self.running:
                self.run_monitoring_cycle()
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.logger.info("Monitoramento interrompido pelo usuário")
            print("\n⏹️ Monitoramento parado")
        except Exception as e:
            self.logger.error(f"Erro no monitoramento: {e}")
            print(f"\n❌ Erro no monitoramento: {e}")
        finally:
            self.running = False
    
    def stop_monitoring(self):
        """Para o monitoramento"""
        self.running = False

def create_default_config(filename: str):
    """Cria arquivo de configuração padrão"""
    default_config = {
        "cortex_url": "http://localhost:8000",
        "api_key": "",
        "monitoring": {
            "interval_seconds": 60,
            "timeout_seconds": 10,
            "max_response_time": 2.0,
            "alert_threshold_failures": 3
        },
        "endpoints": [
            "/health",
            "/list-files",
            "/docs"
        ],
        "alerts": {
            "email": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "seu-email@gmail.com",
                "password": "sua-senha-app",
                "to_addresses": ["admin@empresa.com"]
            },
            "webhook": {
                "enabled": False,
                "url": "https://hooks.slack.com/services/...",
                "headers": {
                    "Authorization": "Bearer token"
                }
            }
        },
        "logging": {
            "level": "INFO",
            "file": "integration_monitor.log",
            "max_size_mb": 10,
            "backup_count": 5
        }
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(default_config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Arquivo de configuração criado: {filename}")
    print("📝 Edite o arquivo para configurar URL, API key e alertas")

def main():
    parser = argparse.ArgumentParser(description='Monitor de integração CÓRTEX BI + Copilot Studio')
    parser.add_argument('--config', default='monitor_config.json', help='Arquivo de configuração')
    parser.add_argument('--create-config', action='store_true', help='Criar arquivo de configuração padrão')
    parser.add_argument('--status', action='store_true', help='Mostrar status atual e sair')
    parser.add_argument('--test', action='store_true', help='Executar teste único e sair')
    
    args = parser.parse_args()
    
    if args.create_config:
        create_default_config(args.config)
        return
    
    # Inicializar monitor
    try:
        monitor = IntegrationMonitor(args.config)
    except Exception as e:
        print(f"❌ Erro ao carregar configuração: {e}")
        print(f"💡 Use --create-config para criar arquivo de configuração padrão")
        return
    
    if args.test:
        print("🧪 Executando teste único...")
        metrics = monitor.run_monitoring_cycle()
        if metrics:
            print(monitor.generate_status_report())
    elif args.status:
        print("📊 Status atual do sistema...")
        metrics = monitor.run_monitoring_cycle()
        if metrics:
            print(monitor.generate_status_report())
    else:
        # Monitoramento contínuo
        monitor.start_monitoring()

if __name__ == "__main__":
    main()

