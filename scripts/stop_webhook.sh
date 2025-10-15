#!/bin/bash

# Script para parar Webhook Handler do CÓRTEX BI

echo "⏸️  Parando Webhook Handler..."

# Diretório do projeto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# Verificar se PID file existe
if [ ! -f webhook.pid ]; then
    echo "⚠️  Arquivo webhook.pid não encontrado"
    echo "Tentando parar processo pelo nome..."
    pkill -f webhook_handler.py
    if [ $? -eq 0 ]; then
        echo "✅ Processo parado"
    else
        echo "❌ Nenhum processo encontrado"
    fi
    exit 0
fi

# Ler PID
WEBHOOK_PID=$(cat webhook.pid)

# Verificar se processo está rodando
if ps -p $WEBHOOK_PID > /dev/null 2>&1; then
    # Parar processo
    kill $WEBHOOK_PID
    
    # Aguardar processo parar
    sleep 2
    
    # Verificar se parou
    if ps -p $WEBHOOK_PID > /dev/null 2>&1; then
        echo "⚠️  Processo não parou. Forçando..."
        kill -9 $WEBHOOK_PID
        sleep 1
    fi
    
    echo "✅ Webhook Handler parado (PID: $WEBHOOK_PID)"
else
    echo "⚠️  Processo não está rodando (PID: $WEBHOOK_PID)"
fi

# Remover PID file
rm -f webhook.pid

echo "✅ Concluído"

