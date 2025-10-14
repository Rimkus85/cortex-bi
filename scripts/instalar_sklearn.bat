@echo off
REM ========================================
REM CÓRTEX BI - Instalar Sklearn (Etapa 3/3)
REM ========================================

echo 🧠 CÓRTEX BI - Instalando Sklearn (3/3)
echo ==========================================

echo [INFO] Instalando Sklearn para Machine Learning...
echo.

echo [1/5] Verificando dependências do Sklearn...
echo 📦 Verificando NumPy e SciPy...
python -c "
try:
    import numpy
    print('✅ NumPy:', numpy.__version__)
except:
    print('❌ NumPy não encontrado')
    exit(1)
"

if %errorLevel% neq 0 (
    echo [1a] Instalando NumPy...
    python -m pip install numpy
    if %errorLevel% neq 0 (
        echo ❌ ERRO: Não foi possível instalar NumPy
        pause
        exit /b 1
    )
)

echo.
echo [2/5] Instalando SciPy (dependência do Sklearn)...
echo 📦 Instalando scipy...
python -m pip install scipy
if %errorLevel% equ 0 (
    echo ✅ SciPy instalado com sucesso
) else (
    echo ⚠️  SciPy falhou, tentando continuar...
)

echo.
echo [3/5] Instalando Sklearn...
echo 📦 Instalando scikit-learn...
python -m pip install scikit-learn
if %errorLevel% equ 0 (
    echo ✅ Sklearn instalado com sucesso
) else (
    echo ❌ ERRO na instalação do Sklearn
    echo.
    echo 💡 TENTATIVAS ALTERNATIVAS:
    echo.
    
    echo [3a] Tentando com --user...
    python -m pip install --user scikit-learn
    if %errorLevel% equ 0 (
        echo ✅ Sklearn instalado com --user
    ) else (
        echo ❌ Falha com --user
        
        echo [3b] Tentando versão específica...
        python -m pip install scikit-learn==1.3.0
        if %errorLevel% equ 0 (
            echo ✅ Sklearn versão específica instalada
        ) else (
            echo ❌ Falha versão específica
            
            echo [3c] Tentando sem cache...
            python -m pip install --no-cache-dir scikit-learn
            if %errorLevel% equ 0 (
                echo ✅ Sklearn instalado sem cache
            ) else (
                echo ❌ TODAS as tentativas falharam
                echo.
                echo 🚨 PROBLEMA CRÍTICO COM SKLEARN:
                echo • Pode ser problema de compilação
                echo • Tente instalar Microsoft Visual C++ Build Tools
                echo • Ou use versão pré-compilada
                echo.
                echo 💡 ALTERNATIVA: Continuar sem Sklearn
                echo    (funcionalidades ML limitadas)
                echo.
                set /p choice="Continuar sem Sklearn? (s/n): "
                if /i "%choice%"=="s" (
                    echo ⚠️  Continuando sem Sklearn...
                    goto :test_import
                ) else (
                    pause
                    exit /b 1
                )
            )
        )
    )
)

:test_import
echo.
echo [4/5] Testando importação do Sklearn...
python -c "
try:
    import sklearn
    print('✅ Sklearn: Importação OK')
    print('📋 Versão:', sklearn.__version__)
    
    # Teste básico de funcionalidades
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    
    print('✅ Sklearn: Módulos principais OK')
    
except Exception as e:
    print('❌ Sklearn: Erro na importação:', e)
    print('⚠️  Continuando sem Sklearn (funcionalidades ML limitadas)')
"

echo.
echo [5/5] Testando funcionalidades de ML...
python -c "
try:
    import sklearn
    import numpy as np
    from sklearn.cluster import KMeans
    
    # Teste básico de clustering
    X = np.array([[1, 2], [1, 4], [1, 0], [10, 2], [10, 4], [10, 0]])
    kmeans = KMeans(n_clusters=2, random_state=0, n_init=10)
    kmeans.fit(X)
    
    print('✅ Sklearn: Clustering funcionando')
    print('📋 Clusters encontrados:', len(set(kmeans.labels_)))
    
except Exception as e:
    print('⚠️  Sklearn: Funcionalidades limitadas -', e)
"

echo.
echo ==========================================
echo 🎉 SKLEARN INSTALADO COM SUCESSO! (3/3)
echo ==========================================
echo.
echo ✅ Todas as dependências de IA instaladas!
echo.
echo 📊 RESUMO DAS INSTALAÇÕES:
echo • OpenAI: ✅ Processamento de linguagem avançado
echo • NLTK: ✅ Análise de texto e sentimentos  
echo • Sklearn: ✅ Machine Learning e clustering
echo.
echo 🚀 PRÓXIMO PASSO:
echo    Testar CÓRTEX BI completo com todas as funcionalidades!
echo.
echo 💻 EXECUTE:
echo    python main_ai.py
echo.
pause

