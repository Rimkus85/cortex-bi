#!/bin/bash

# Analytics Agent - Script de Instalação para Linux
# Este script automatiza a instalação e configuração do Analytics Agent

set -e  # Para o script se houver erro

echo "=========================================="
echo "Analytics Agent - Instalação Linux"
echo "=========================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCESSO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

# Verificar se está executando como root
if [[ $EUID -eq 0 ]]; then
   print_error "Este script não deve ser executado como root"
   exit 1
fi

# Verificar sistema operacional
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    print_error "Este script é apenas para sistemas Linux"
    exit 1
fi

print_status "Iniciando instalação do Analytics Agent..."

# 1. Verificar e instalar Python 3.8+
print_status "Verificando instalação do Python..."

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    REQUIRED_VERSION="3.8"
    
    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
        print_success "Python $PYTHON_VERSION encontrado"
    else
        print_error "Python 3.8+ é necessário. Versão encontrada: $PYTHON_VERSION"
        exit 1
    fi
else
    print_error "Python 3 não encontrado. Por favor, instale Python 3.8+ primeiro."
    print_status "Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip"
    print_status "CentOS/RHEL: sudo yum install python3 python3-pip"
    exit 1
fi

# 2. Verificar e instalar pip
print_status "Verificando instalação do pip..."

if command -v pip3 &> /dev/null; then
    print_success "pip3 encontrado"
else
    print_error "pip3 não encontrado. Instalando..."
    
    # Detectar distribuição Linux
    if [ -f /etc/debian_version ]; then
        sudo apt update
        sudo apt install -y python3-pip
    elif [ -f /etc/redhat-release ]; then
        sudo yum install -y python3-pip
    else
        print_error "Distribuição Linux não suportada automaticamente"
        print_status "Por favor, instale pip3 manualmente"
        exit 1
    fi
fi

# 3. Instalar dependências do sistema
print_status "Instalando dependências do sistema..."

if [ -f /etc/debian_version ]; then
    # Ubuntu/Debian
    sudo apt update
    sudo apt install -y \
        python3-dev \
        python3-venv \
        build-essential \
        libssl-dev \
        libffi-dev \
        unixodbc-dev \
        curl \
        wget
elif [ -f /etc/redhat-release ]; then
    # CentOS/RHEL
    sudo yum groupinstall -y "Development Tools"
    sudo yum install -y \
        python3-devel \
        openssl-devel \
        libffi-devel \
        unixODBC-devel \
        curl \
        wget
fi

# 4. Criar ambiente virtual
print_status "Criando ambiente virtual..."

if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Ambiente virtual criado"
else
    print_warning "Ambiente virtual já existe"
fi

# 5. Ativar ambiente virtual e instalar dependências Python
print_status "Ativando ambiente virtual e instalando dependências..."

source venv/bin/activate

# Atualizar pip
pip install --upgrade pip

# Instalar dependências do requirements.txt
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Dependências Python instaladas"
else
    print_error "Arquivo requirements.txt não encontrado"
    exit 1
fi

# 6. Instalar driver ODBC para SQL Server (opcional)
print_status "Configurando driver ODBC para SQL Server..."

if [ -f /etc/debian_version ]; then
    # Ubuntu/Debian
    if ! curl -s https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add - 2>/dev/null; then
        print_warning "Não foi possível adicionar chave Microsoft"
    fi
    
    if ! curl -s https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | sudo tee /etc/apt/sources.list.d/msprod.list 2>/dev/null; then
        print_warning "Não foi possível adicionar repositório Microsoft"
    fi
    
    sudo apt update 2>/dev/null || true
    
    # Aceitar EULA automaticamente
    echo 'msodbcsql17 msodbcsql/ACCEPT_EULA boolean true' | sudo debconf-set-selections
    
    if sudo apt install -y msodbcsql17 2>/dev/null; then
        print_success "Driver ODBC SQL Server instalado"
    else
        print_warning "Não foi possível instalar driver ODBC SQL Server"
        print_status "Você pode instalá-lo manualmente mais tarde se precisar"
    fi
fi

# 7. Criar arquivo .env de exemplo
print_status "Criando arquivo de configuração..."

if [ ! -f ".env" ]; then
    cat > .env << EOF
# Configurações do Banco de Dados SQL Server
SQL_SERVER=localhost
SQL_DATABASE=master
SQL_USERNAME=
SQL_PASSWORD=

# Configurações do Power BI
POWERBI_CLIENT_ID=
POWERBI_CLIENT_SECRET=
POWERBI_TENANT_ID=

# Configurações do Servidor
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=True

# Configurações de Log
LOG_LEVEL=INFO
LOG_FILE=logs/analytics_agent.log
EOF
    print_success "Arquivo .env criado"
    print_warning "Configure as variáveis de ambiente no arquivo .env conforme necessário"
else
    print_warning "Arquivo .env já existe"
fi

# 8. Criar diretórios necessários
print_status "Criando estrutura de diretórios..."

mkdir -p logs uploads output
print_success "Diretórios criados"

# 9. Verificar instalação
print_status "Verificando instalação..."

# Testar importações principais
python3 -c "
import sys
try:
    from agents.data_loader import DataLoader
    from agents.analytics_engine import AnalyticsEngine
    from agents.pptx_generator import PPTXGenerator
    print('✓ Módulos do agente importados com sucesso')
except ImportError as e:
    print(f'✗ Erro ao importar módulos: {e}')
    sys.exit(1)

try:
    import fastapi
    import uvicorn
    import pandas
    import numpy
    print('✓ Dependências principais verificadas')
except ImportError as e:
    print(f'✗ Erro nas dependências: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    print_success "Verificação concluída com sucesso"
else
    print_error "Falha na verificação"
    exit 1
fi

# 10. Criar script de inicialização
print_status "Criando script de inicialização..."

cat > start.sh << 'EOF'
#!/bin/bash

# Script para iniciar o Analytics Agent

echo "Iniciando Analytics Agent..."

# Ativar ambiente virtual
source venv/bin/activate

# Verificar se o servidor já está rodando
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "Servidor já está rodando na porta 8000"
    echo "Para parar: pkill -f 'uvicorn main:app'"
    exit 1
fi

# Iniciar servidor
echo "Iniciando servidor na porta 8000..."
python3 main.py

EOF

chmod +x start.sh
print_success "Script de inicialização criado (start.sh)"

# 11. Criar script de parada
cat > stop.sh << 'EOF'
#!/bin/bash

# Script para parar o Analytics Agent

echo "Parando Analytics Agent..."

# Parar processo do servidor
pkill -f 'uvicorn main:app'

if [ $? -eq 0 ]; then
    echo "Servidor parado com sucesso"
else
    echo "Nenhum servidor encontrado rodando"
fi

EOF

chmod +x stop.sh
print_success "Script de parada criado (stop.sh)"

# 12. Finalização
echo ""
echo "=========================================="
print_success "Instalação concluída com sucesso!"
echo "=========================================="
echo ""
print_status "Próximos passos:"
echo "1. Configure o arquivo .env com suas credenciais"
echo "2. Execute: ./start.sh para iniciar o servidor"
echo "3. Acesse: http://localhost:8000/docs para ver a documentação da API"
echo "4. Execute: ./stop.sh para parar o servidor"
echo ""
print_status "Arquivos importantes:"
echo "- .env: Configurações do sistema"
echo "- data/: Arquivos de dados de exemplo"
echo "- templates/: Templates PPTX"
echo "- logs/: Logs do sistema"
echo ""
print_status "Comandos úteis:"
echo "- ./start.sh: Iniciar servidor"
echo "- ./stop.sh: Parar servidor"
echo "- source venv/bin/activate: Ativar ambiente virtual"
echo "- deactivate: Desativar ambiente virtual"
echo ""
print_warning "Lembre-se de configurar as credenciais no arquivo .env antes de usar!"

# Desativar ambiente virtual
deactivate 2>/dev/null || true

exit 0

