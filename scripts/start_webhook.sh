#!/bin/bash

# Script para iniciar Webhook Handler do CÓRTEX BI
# Permite auto-deploy quando há push no GitHub

echo "🚀 Iniciando Webhook Handler do CÓRTEX BI..."

# Diretório do projeto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale Python 3.8+ primeiro."
    exit 1
fi

# Criar diretório de logs se não existir
mkdir -p logs

# Verificar se já está rodando
if [ -f webhook.pid ]; then
    OLD_PID=$(cat webhook.pid)
    if ps -p $OLD_PID > /dev/null 2>&1; then
        echo "⚠️  Webhook já está rodando (PID: $OLD_PID)"
        echo "Para parar: ./scripts/stop_webhook.sh"
        exit 1
    fi
fi

# Iniciar webhook em background
nohup python3 src/webhook_handler.py > logs/webhook.log 2>&1 &
WEBHOOK_PID=$!

# Salvar PID
echo $WEBHOOK_PID > webhook.pid

# Aguardar inicialização
sleep 2

# Verificar se iniciou corretamente
if ps -p $WEBHOOK_PID > /dev/null 2>&1; then
    echo "✅ Webhook Handler iniciado com sucesso!"
    echo "📝 PID: $WEBHOOK_PID"
    echo "📊 Status: http://localhost:5001/webhook/status"
    echo "📋 Logs: tail -f logs/webhook.log"
    echo ""
    echo "Para parar: ./scripts/stop_webhook.sh"
else
    echo "❌ Erro ao iniciar webhook. Verifique os logs:"
    tail -20 logs/webhook.log
    rm -f webhook.pid
    exit 1
fi

