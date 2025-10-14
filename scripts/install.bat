@echo off
REM Analytics Agent - Script de Instalação para Windows
REM Este script automatiza a instalação e configuração do Analytics Agent

setlocal enabledelayedexpansion

echo ==========================================
echo Analytics Agent - Instalação Windows
echo ==========================================

REM Verificar se está executando como administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [ERRO] Este script não deve ser executado como administrador
    echo Execute como usuário normal
    pause
    exit /b 1
)

echo [INFO] Iniciando instalação do Analytics Agent...

REM 1. Verificar instalação do Python
echo [INFO] Verificando instalação do Python...

python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERRO] Python não encontrado
    echo Por favor, instale Python 3.8+ de https://python.org/downloads/
    echo Certifique-se de marcar "Add Python to PATH" durante a instalação
    pause
    exit /b 1
)

REM Verificar versão do Python
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [SUCESSO] Python %PYTHON_VERSION% encontrado

REM 2. Verificar instalação do pip
echo [INFO] Verificando instalação do pip...

pip --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERRO] pip não encontrado
    echo Reinstale o Python com pip incluído
    pause
    exit /b 1
)

echo [SUCESSO] pip encontrado

REM 3. Atualizar pip
echo [INFO] Atualizando pip...
python -m pip install --upgrade pip

REM 4. Criar ambiente virtual
echo [INFO] Criando ambiente virtual...

if not exist "venv" (
    python -m venv venv
    echo [SUCESSO] Ambiente virtual criado
) else (
    echo [AVISO] Ambiente virtual já existe
)

REM 5. Ativar ambiente virtual e instalar dependências
echo [INFO] Ativando ambiente virtual e instalando dependências...

call venv\Scripts\activate.bat

REM Instalar dependências do requirements.txt
if exist "requirements.txt" (
    pip install -r requirements.txt
    echo [SUCESSO] Dependências Python instaladas
) else (
    echo [ERRO] Arquivo requirements.txt não encontrado
    pause
    exit /b 1
)

REM 6. Instalar driver ODBC para SQL Server (opcional)
echo [INFO] Verificando driver ODBC para SQL Server...

REM Verificar se o driver já está instalado
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\ODBC\ODBCINST.INI\ODBC Driver 17 for SQL Server" >nul 2>&1
if %errorLevel% neq 0 (
    echo [AVISO] Driver ODBC SQL Server não encontrado
    echo Para conectar ao SQL Server, baixe e instale:
    echo https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
) else (
    echo [SUCESSO] Driver ODBC SQL Server encontrado
)

REM 7. Criar arquivo .env de exemplo
echo [INFO] Criando arquivo de configuração...

if not exist ".env" (
    (
        echo # Configurações do Banco de Dados SQL Server
        echo SQL_SERVER=localhost
        echo SQL_DATABASE=master
        echo SQL_USERNAME=
        echo SQL_PASSWORD=
        echo.
        echo # Configurações do Power BI
        echo POWERBI_CLIENT_ID=
        echo POWERBI_CLIENT_SECRET=
        echo POWERBI_TENANT_ID=
        echo.
        echo # Configurações do Servidor
        echo SERVER_HOST=0.0.0.0
        echo SERVER_PORT=8000
        echo DEBUG=True
        echo.
        echo # Configurações de Log
        echo LOG_LEVEL=INFO
        echo LOG_FILE=logs/analytics_agent.log
    ) > .env
    echo [SUCESSO] Arquivo .env criado
    echo [AVISO] Configure as variáveis de ambiente no arquivo .env conforme necessário
) else (
    echo [AVISO] Arquivo .env já existe
)

REM 8. Criar diretórios necessários
echo [INFO] Criando estrutura de diretórios...

if not exist "logs" mkdir logs
if not exist "uploads" mkdir uploads
if not exist "output" mkdir output

echo [SUCESSO] Diretórios criados

REM 9. Verificar instalação
echo [INFO] Verificando instalação...

python -c "
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

if %errorLevel% neq 0 (
    echo [ERRO] Falha na verificação
    pause
    exit /b 1
)

echo [SUCESSO] Verificação concluída com sucesso

REM 10. Criar script de inicialização
echo [INFO] Criando script de inicialização...

(
    echo @echo off
    echo REM Script para iniciar o Analytics Agent
    echo.
    echo echo Iniciando Analytics Agent...
    echo.
    echo REM Ativar ambiente virtual
    echo call venv\Scripts\activate.bat
    echo.
    echo REM Verificar se o servidor já está rodando
    echo netstat -an ^| find ":8000" ^| find "LISTENING" ^>nul
    echo if %%errorLevel%% equ 0 ^(
    echo     echo Servidor já está rodando na porta 8000
    echo     echo Para parar: taskkill /f /im python.exe
    echo     pause
    echo     exit /b 1
    echo ^)
    echo.
    echo REM Iniciar servidor
    echo echo Iniciando servidor na porta 8000...
    echo echo Acesse: http://localhost:8000/docs
    echo python main.py
    echo.
    echo pause
) > start.bat

echo [SUCESSO] Script de inicialização criado (start.bat)

REM 11. Criar script de parada
(
    echo @echo off
    echo REM Script para parar o Analytics Agent
    echo.
    echo echo Parando Analytics Agent...
    echo.
    echo REM Parar processo do servidor
    echo taskkill /f /im python.exe /fi "WINDOWTITLE eq Analytics Agent*" 2^>nul
    echo.
    echo if %%errorLevel%% equ 0 ^(
    echo     echo Servidor parado com sucesso
    echo ^) else ^(
    echo     echo Nenhum servidor encontrado rodando
    echo ^)
    echo.
    echo pause
) > stop.bat

echo [SUCESSO] Script de parada criado (stop.bat)

REM 12. Criar script para abrir documentação
(
    echo @echo off
    echo REM Script para abrir documentação da API
    echo.
    echo echo Abrindo documentação da API...
    echo start http://localhost:8000/docs
) > docs.bat

echo [SUCESSO] Script de documentação criado (docs.bat)

REM 13. Finalização
echo.
echo ==========================================
echo [SUCESSO] Instalação concluída com sucesso!
echo ==========================================
echo.
echo [INFO] Próximos passos:
echo 1. Configure o arquivo .env com suas credenciais
echo 2. Execute: start.bat para iniciar o servidor
echo 3. Execute: docs.bat para abrir a documentação da API
echo 4. Execute: stop.bat para parar o servidor
echo.
echo [INFO] Arquivos importantes:
echo - .env: Configurações do sistema
echo - data\: Arquivos de dados de exemplo
echo - templates\: Templates PPTX
echo - logs\: Logs do sistema
echo.
echo [INFO] Comandos úteis:
echo - start.bat: Iniciar servidor
echo - stop.bat: Parar servidor
echo - docs.bat: Abrir documentação
echo - venv\Scripts\activate.bat: Ativar ambiente virtual
echo - deactivate: Desativar ambiente virtual
echo.
echo [AVISO] Lembre-se de configurar as credenciais no arquivo .env antes de usar!

REM Desativar ambiente virtual
call deactivate 2>nul

echo.
echo Pressione qualquer tecla para finalizar...
pause >nul

exit /b 0

