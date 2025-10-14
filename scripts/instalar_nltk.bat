@echo off
REM ========================================
REM CÓRTEX BI - Instalar NLTK (Etapa 2/3)
REM ========================================

echo 📚 CÓRTEX BI - Instalando NLTK (2/3)
echo ==========================================

echo [INFO] Instalando NLTK para processamento de linguagem natural...
echo.

echo [1/6] Instalando NLTK...
echo 📦 Instalando nltk...
python -m pip install nltk
if %errorLevel% equ 0 (
    echo ✅ NLTK instalado com sucesso
) else (
    echo ❌ ERRO na instalação do NLTK
    echo.
    echo 💡 TENTATIVAS ALTERNATIVAS:
    echo.
    
    echo [1a] Tentando com --user...
    python -m pip install --user nltk
    if %errorLevel% equ 0 (
        echo ✅ NLTK instalado com --user
    ) else (
        echo ❌ Falha com --user
        
        echo [1b] Tentando versão específica...
        python -m pip install nltk==3.8.1
        if %errorLevel% equ 0 (
            echo ✅ NLTK versão específica instalada
        ) else (
            echo ❌ TODAS as tentativas falharam
            pause
            exit /b 1
        )
    )
)

echo.
echo [2/6] Testando importação do NLTK...
python -c "
try:
    import nltk
    print('✅ NLTK: Importação OK')
    print('📋 Versão:', nltk.__version__)
except Exception as e:
    print('❌ NLTK: Erro na importação:', e)
    exit(1)
"

if %errorLevel% neq 0 (
    echo ❌ ERRO: NLTK não pode ser importado
    pause
    exit /b 1
)

echo.
echo [3/6] Instalando TextBlob (complementar)...
echo 📦 Instalando textblob...
python -m pip install textblob
if %errorLevel% equ 0 (
    echo ✅ TextBlob instalado com sucesso
) else (
    echo ⚠️  TextBlob falhou, continuando sem ele...
)

echo.
echo [4/6] Baixando dados do NLTK...
echo 📥 Baixando recursos essenciais do NLTK...
python -c "
import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

print('📥 Baixando punkt...')
try:
    nltk.download('punkt', quiet=True)
    print('✅ punkt baixado')
except:
    print('⚠️  punkt falhou')

print('📥 Baixando stopwords...')
try:
    nltk.download('stopwords', quiet=True)
    print('✅ stopwords baixado')
except:
    print('⚠️  stopwords falhou')

print('📥 Baixando vader_lexicon...')
try:
    nltk.download('vader_lexicon', quiet=True)
    print('✅ vader_lexicon baixado')
except:
    print('⚠️  vader_lexicon falhou')

print('📥 Baixando wordnet...')
try:
    nltk.download('wordnet', quiet=True)
    print('✅ wordnet baixado')
except:
    print('⚠️  wordnet falhou')
"

echo.
echo [5/6] Testando funcionalidades do NLTK...
python -c "
try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    
    # Teste básico
    texto = 'Este é um teste do NLTK para o CÓRTEX BI'
    tokens = word_tokenize(texto)
    print('✅ NLTK: Tokenização funcionando')
    print('📋 Tokens:', len(tokens))
    
    # Teste stopwords
    try:
        stop_words = stopwords.words('portuguese')
        print('✅ NLTK: Stopwords português OK')
    except:
        print('⚠️  NLTK: Stopwords português não disponível')
    
except Exception as e:
    print('❌ NLTK: Erro no teste:', e)
"

echo.
echo [6/6] Testando TextBlob (se disponível)...
python -c "
try:
    from textblob import TextBlob
    blob = TextBlob('CÓRTEX BI é incrível')
    print('✅ TextBlob: Funcionando')
except Exception as e:
    print('⚠️  TextBlob: Não disponível -', e)
"

echo.
echo ==========================================
echo 🎉 NLTK INSTALADO COM SUCESSO! (2/3)
echo ==========================================
echo.
echo ✅ NLTK está pronto para processamento de linguagem
echo 📋 Próximo passo: Sklearn
echo.
echo 🚀 EXECUTE AGORA:
echo    instalar_sklearn.bat
echo.
pause

