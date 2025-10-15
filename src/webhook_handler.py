"""
Webhook Handler para Auto-Deploy do CÓRTEX BI
Atualiza automaticamente quando há push no GitHub

Uso:
    python src/webhook_handler.py

Configuração no GitHub:
    1. Vá em Settings > Webhooks > Add webhook
    2. Payload URL: http://seu-servidor:5001/webhook/github
    3. Content type: application/json
    4. Secret: Mesmo valor de GITHUB_WEBHOOK_SECRET no .env
    5. Events: Just the push event
"""

from flask import Flask, request, jsonify
import subprocess
import hmac
import hashlib
import os
import sys
from threading import Thread
from datetime import datetime

app = Flask(__name__)

# Configurações
WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET', 'change-me-in-production')
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(PROJECT_DIR, 'logs', 'webhook.log')

def log(message):
    """Escreve log com timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    
    # Garantir que diretório de logs existe
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    with open(LOG_FILE, 'a') as f:
        f.write(log_message + '\n')

def verify_signature(payload, signature):
    """Verifica assinatura do webhook do GitHub"""
    if not signature:
        log("⚠️  Assinatura não fornecida")
        return False
    
    try:
        sha_name, signature_hash = signature.split('=')
        if sha_name != 'sha256':
            log(f"⚠️  Algoritmo inválido: {sha_name}")
            return False
        
        mac = hmac.new(
            WEBHOOK_SECRET.encode(),
            msg=payload,
            digestmod=hashlib.sha256
        )
        
        is_valid = hmac.compare_digest(mac.hexdigest(), signature_hash)
        
        if not is_valid:
            log("❌ Assinatura inválida!")
        
        return is_valid
        
    except Exception as e:
        log(f"❌ Erro ao verificar assinatura: {e}")
        return False

def run_command(command, shell=False):
    """Executa comando e retorna resultado"""
    try:
        result = subprocess.run(
            command if shell else command.split(),
            capture_output=True,
            text=True,
            cwd=PROJECT_DIR,
            shell=shell
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def update_and_restart():
    """Atualiza código e reinicia servidor"""
    try:
        log("🔄 Iniciando processo de atualização...")
        
        # Ir para diretório do projeto
        os.chdir(PROJECT_DIR)
        log(f"📁 Diretório: {PROJECT_DIR}")
        
        # Verificar branch atual
        success, branch, _ = run_command("git branch --show-current")
        if success:
            log(f"🌿 Branch atual: {branch.strip()}")
        
        # Fazer backup das configurações
        log("💾 Fazendo backup das configurações...")
        if os.path.exists('.env'):
            run_command("cp .env .env.backup", shell=True)
        if os.path.exists('config'):
            run_command("cp -r config config.backup", shell=True)
        
        # Puxar atualizações
        log("⬇️  Baixando atualizações do GitHub...")
        success, stdout, stderr = run_command("git pull origin master")
        
        if success:
            log(f"✅ Git pull concluído:\n{stdout}")
        else:
            log(f"❌ Erro no git pull:\n{stderr}")
            return False
        
        # Restaurar configurações
        log("♻️  Restaurando configurações...")
        if os.path.exists('.env.backup'):
            run_command("cp .env.backup .env", shell=True)
        
        # Verificar se requirements.txt mudou
        log("📦 Verificando dependências...")
        success, diff, _ = run_command("git diff HEAD@{1} HEAD -- requirements.txt")
        
        if diff.strip():
            log("📦 requirements.txt modificado. Atualizando dependências...")
            success, stdout, stderr = run_command(
                f"{sys.executable} -m pip install -r requirements.txt --upgrade"
            )
            if success:
                log("✅ Dependências atualizadas")
            else:
                log(f"⚠️  Aviso ao atualizar dependências:\n{stderr}")
        else:
            log("✅ Dependências já estão atualizadas")
        
        # Reiniciar servidor
        log("🔄 Reiniciando servidor CÓRTEX BI...")
        
        # Parar servidor (tentar múltiplos métodos)
        log("⏸️  Parando servidor...")
        
        # Método 1: Script de parada
        if os.path.exists('scripts/stop_ai.sh'):
            run_command("bash scripts/stop_ai.sh", shell=True)
        elif os.path.exists('scripts/stop_ai.bat'):
            run_command("scripts\\stop_ai.bat", shell=True)
        
        # Método 2: pkill
        run_command("pkill -f main_ai.py", shell=True)
        
        # Aguardar processo parar
        import time
        time.sleep(2)
        
        # Iniciar servidor
        log("🚀 Iniciando servidor...")
        if os.path.exists('scripts/start_ai.sh'):
            subprocess.Popen(['bash', 'scripts/start_ai.sh'], cwd=PROJECT_DIR)
        elif os.path.exists('scripts/start_ai.bat'):
            subprocess.Popen(['scripts\\start_ai.bat'], cwd=PROJECT_DIR, shell=True)
        else:
            # Iniciar diretamente
            subprocess.Popen([sys.executable, 'src/main_ai.py'], cwd=PROJECT_DIR)
        
        log("✅ Atualização concluída com sucesso!")
        return True
        
    except Exception as e:
        log(f"❌ Erro crítico na atualização: {e}")
        import traceback
        log(traceback.format_exc())
        return False

@app.route('/webhook/github', methods=['POST'])
def github_webhook():
    """Endpoint para receber webhooks do GitHub"""
    
    # Verificar assinatura
    signature = request.headers.get('X-Hub-Signature-256')
    
    if WEBHOOK_SECRET != 'change-me-in-production':
        if not verify_signature(request.data, signature):
            log("❌ Webhook rejeitado: assinatura inválida")
            return jsonify({'error': 'Invalid signature'}), 401
    else:
        log("⚠️  AVISO: Webhook secret não configurado! Configure GITHUB_WEBHOOK_SECRET no .env")
    
    # Processar evento
    event = request.headers.get('X-GitHub-Event')
    payload = request.json
    
    log(f"📥 Webhook recebido: {event}")
    
    if event == 'ping':
        log("🏓 Ping recebido do GitHub")
        return jsonify({'message': 'Pong! Webhook configurado com sucesso ✅'}), 200
    
    if event == 'push':
        ref = payload.get('ref', '')
        branch = ref.split('/')[-1] if '/' in ref else ref
        
        log(f"📌 Push na branch: {branch}")
        
        # Verificar se é push na branch master
        if ref == 'refs/heads/master':
            commit_message = payload.get('head_commit', {}).get('message', 'N/A')
            commit_id = payload.get('head_commit', {}).get('id', 'N/A')[:7]
            pusher = payload.get('pusher', {}).get('name', 'N/A')
            
            log(f"👤 Pusher: {pusher}")
            log(f"💬 Commit: {commit_id} - {commit_message}")
            
            # Executar atualização em thread separada
            log("🚀 Iniciando atualização em background...")
            thread = Thread(target=update_and_restart)
            thread.daemon = True
            thread.start()
            
            return jsonify({
                'status': 'success',
                'message': 'Atualização iniciada',
                'commit': commit_id,
                'pusher': pusher
            }), 200
        else:
            log(f"ℹ️  Push ignorado (branch: {branch})")
            return jsonify({
                'status': 'ignored',
                'message': f'Push na branch {branch} foi ignorado. Apenas master dispara deploy.'
            }), 200
    
    log(f"ℹ️  Evento {event} ignorado")
    return jsonify({'status': 'ignored', 'message': f'Event {event} not handled'}), 200

@app.route('/webhook/status', methods=['GET'])
def webhook_status():
    """Verificar status do webhook e sistema"""
    try:
        # Informações do Git
        success, branch, _ = run_command("git branch --show-current")
        current_branch = branch.strip() if success else "unknown"
        
        success, commit, _ = run_command("git rev-parse --short HEAD")
        current_commit = commit.strip() if success else "unknown"
        
        success, remote, _ = run_command("git config --get remote.origin.url")
        remote_url = remote.strip() if success else "unknown"
        
        # Verificar se há atualizações disponíveis
        run_command("git fetch origin master")
        success, behind, _ = run_command("git rev-list HEAD..origin/master --count")
        commits_behind = int(behind.strip()) if success and behind.strip().isdigit() else 0
        
        return jsonify({
            'status': 'active',
            'webhook_secret_configured': WEBHOOK_SECRET != 'change-me-in-production',
            'project_dir': PROJECT_DIR,
            'git': {
                'branch': current_branch,
                'commit': current_commit,
                'remote': remote_url,
                'commits_behind': commits_behind,
                'update_available': commits_behind > 0
            },
            'log_file': LOG_FILE
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/webhook/logs', methods=['GET'])
def webhook_logs():
    """Ver últimas linhas do log"""
    try:
        lines = int(request.args.get('lines', 50))
        
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                all_lines = f.readlines()
                last_lines = all_lines[-lines:]
                
            return jsonify({
                'log_file': LOG_FILE,
                'total_lines': len(all_lines),
                'showing_lines': len(last_lines),
                'logs': ''.join(last_lines)
            }), 200
        else:
            return jsonify({
                'error': 'Log file not found',
                'log_file': LOG_FILE
            }), 404
            
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/webhook/update', methods=['POST'])
def manual_update():
    """Disparar atualização manual (sem webhook)"""
    log("🔧 Atualização manual solicitada")
    
    thread = Thread(target=update_and_restart)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'status': 'success',
        'message': 'Atualização manual iniciada'
    }), 200

@app.route('/')
def index():
    """Página inicial do webhook handler"""
    return """
    <html>
    <head>
        <title>CÓRTEX BI - Webhook Handler</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            h1 { color: #1e40af; }
            .endpoint { background: #f3f4f6; padding: 10px; margin: 10px 0; border-radius: 5px; }
            .status { color: #10b981; font-weight: bold; }
            code { background: #1f2937; color: #10b981; padding: 2px 6px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <h1>🧠 CÓRTEX BI - Webhook Handler</h1>
        <p class="status">✅ Webhook ativo e funcionando!</p>
        
        <h2>📡 Endpoints Disponíveis:</h2>
        
        <div class="endpoint">
            <strong>POST /webhook/github</strong><br>
            Recebe webhooks do GitHub para auto-deploy
        </div>
        
        <div class="endpoint">
            <strong>GET /webhook/status</strong><br>
            Verifica status do sistema e Git<br>
            <a href="/webhook/status">Ver status</a>
        </div>
        
        <div class="endpoint">
            <strong>GET /webhook/logs?lines=50</strong><br>
            Visualiza últimas linhas do log<br>
            <a href="/webhook/logs?lines=100">Ver logs</a>
        </div>
        
        <div class="endpoint">
            <strong>POST /webhook/update</strong><br>
            Dispara atualização manual (sem webhook)
        </div>
        
        <h2>🔧 Configuração no GitHub:</h2>
        <ol>
            <li>Vá em <code>Settings > Webhooks > Add webhook</code></li>
            <li>Payload URL: <code>http://seu-servidor:5001/webhook/github</code></li>
            <li>Content type: <code>application/json</code></li>
            <li>Secret: Configure <code>GITHUB_WEBHOOK_SECRET</code> no .env</li>
            <li>Events: <code>Just the push event</code></li>
        </ol>
        
        <p><small>CÓRTEX BI v2.0 - Desenvolvido em parceria com Manus AI</small></p>
    </body>
    </html>
    """

if __name__ == '__main__':
    log("=" * 60)
    log("🚀 Iniciando Webhook Handler do CÓRTEX BI")
    log(f"📁 Diretório do projeto: {PROJECT_DIR}")
    log(f"📝 Log file: {LOG_FILE}")
    log(f"🔐 Webhook secret configurado: {WEBHOOK_SECRET != 'change-me-in-production'}")
    log("=" * 60)
    
    # Rodar em porta separada (não conflitar com CÓRTEX BI)
    app.run(host='0.0.0.0', port=5001, debug=False)

