@echo off
REM ========================================
REM CÓRTEX BI - ETAPA 3: Dependências IA (Opcionais)
REM ========================================

echo 🧠 CÓRTEX BI - ETAPA 3: Dependências IA (Opcionais)
echo ==========================================

echo ⚠️  NOTA: Esta etapa instala dependências de IA
echo Se houver erro, você pode pular e usar funcionalidades básicas
echo.

REM 1. Tentar instalar scikit-learn (versão compatível)
echo [1/4] Instalando Scikit-Learn...
pip install scikit-learn
if %errorLevel% neq 0 (
    echo ⚠️  AVISO: Erro ao instalar Scikit-Learn
    echo 💡 Funcionalidades de ML podem não funcionar
) else (
    echo ✅ Scikit-Learn instalado
)

REM 2. Tentar instalar NLTK
echo [2/4] Instalando NLTK...
pip install nltk
if %errorLevel% neq 0 (
    echo ⚠️  AVISO: Erro ao instalar NLTK
    echo 💡 Processamento de linguagem natural pode não funcionar
) else (
    echo ✅ NLTK instalado
)

REM 3. Tentar instalar TextBlob
echo [3/4] Instalando TextBlob...
pip install textblob
if %errorLevel% neq 0 (
    echo ⚠️  AVISO: Erro ao instalar TextBlob
    echo 💡 Análise de sentimento pode não funcionar
) else (
    echo ✅ TextBlob instalado
)

REM 4. Tentar instalar OpenAI (opcional)
echo [4/4] Instalando OpenAI (opcional)...
pip install openai
if %errorLevel% neq 0 (
    echo ⚠️  AVISO: Erro ao instalar OpenAI
    echo 💡 Funcionalidades avançadas de IA podem não funcionar
) else (
    echo ✅ OpenAI instalado
)

echo.
echo 🎉 ETAPA 3 CONCLUÍDA!
echo.
echo 📋 Próximo passo: Execute install_step4.bat
echo.
pause

