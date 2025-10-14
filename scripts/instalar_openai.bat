@echo off
REM ========================================
REM CÓRTEX BI - Instalar OpenAI (Etapa 1/3)
REM ========================================

echo 🤖 CÓRTEX BI - Instalando OpenAI (1/3)
echo ==========================================

echo [INFO] Instalando OpenAI para funcionalidades de NLP avançado...
echo.

echo [1/5] Verificando pip...
python -m pip --version
if %errorLevel% neq 0 (
    echo ❌ ERRO: pip não encontrado
    pause
    exit /b 1
)
echo ✅ pip funcionando

echo.
echo [2/5] Atualizando pip...
python -m pip install --upgrade pip
if %errorLevel% neq 0 (
    echo ⚠️  Falha ao atualizar pip, continuando...
)

echo.
echo [3/5] Instalando OpenAI...
echo 📦 Instalando openai...
python -m pip install openai
if %errorLevel% equ 0 (
    echo ✅ OpenAI instalado com sucesso
) else (
    echo ❌ ERRO na instalação do OpenAI
    echo.
    echo 💡 TENTATIVAS ALTERNATIVAS:
    echo.
    
    echo [3a] Tentando com --user...
    python -m pip install --user openai
    if %errorLevel% equ 0 (
        echo ✅ OpenAI instalado com --user
    ) else (
        echo ❌ Falha com --user
        
        echo [3b] Tentando com --no-cache-dir...
        python -m pip install --no-cache-dir openai
        if %errorLevel% equ 0 (
            echo ✅ OpenAI instalado sem cache
        ) else (
            echo ❌ Falha sem cache
            
            echo [3c] Tentando versão específica...
            python -m pip install openai==1.3.0
            if %errorLevel% equ 0 (
                echo ✅ OpenAI versão específica instalada
            ) else (
                echo ❌ TODAS as tentativas falharam
                echo.
                echo 🚨 PROBLEMA CRÍTICO:
                echo • Verifique conexão com internet
                echo • Execute como administrador
                echo • Verifique proxy corporativo
                echo.
                pause
                exit /b 1
            )
        )
    )
)

echo.
echo [4/5] Testando importação do OpenAI...
python -c "
try:
    import openai
    print('✅ OpenAI: Importação OK')
    print('📋 Versão:', openai.__version__)
except Exception as e:
    print('❌ OpenAI: Erro na importação:', e)
    exit(1)
"

if %errorLevel% neq 0 (
    echo ❌ ERRO: OpenAI não pode ser importado
    pause
    exit /b 1
)

echo.
echo [5/5] Testando funcionalidades básicas...
python -c "
try:
    import openai
    # Teste básico de configuração
    client = openai.OpenAI(api_key='test-key')
    print('✅ OpenAI: Cliente criado com sucesso')
except Exception as e:
    print('⚠️  OpenAI: Aviso na criação do cliente:', e)
    print('ℹ️  Isso é normal sem API key válida')
"

echo.
echo ==========================================
echo 🎉 OPENAI INSTALADO COM SUCESSO! (1/3)
echo ==========================================
echo.
echo ✅ OpenAI está pronto para uso
echo 📋 Próximo passo: NLTK
echo.
echo 🚀 EXECUTE AGORA:
echo    instalar_nltk.bat
echo.
pause

