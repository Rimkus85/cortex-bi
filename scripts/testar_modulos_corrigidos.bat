@echo off
REM ========================================
REM CÓRTEX BI - Testar Módulos Corrigidos
REM ========================================

echo 🧪 CÓRTEX BI - Testando Módulos Corrigidos
echo ==========================================

echo [INFO] Testando importações dos módulos corrigidos...
echo.

echo [1/6] Testando data_loader...
python -c "
try:
    from agents.data_loader import DataLoader
    loader = DataLoader()
    print('✅ DataLoader: OK')
except Exception as e:
    print('❌ DataLoader:', e)
"

echo.
echo [2/6] Testando analytics_engine...
python -c "
try:
    from agents.analytics_engine import AnalyticsEngine
    engine = AnalyticsEngine()
    print('✅ AnalyticsEngine: OK')
except Exception as e:
    print('❌ AnalyticsEngine:', e)
"

echo.
echo [3/6] Testando pptx_generator...
python -c "
try:
    from agents.pptx_generator import PPTXGenerator
    generator = PPTXGenerator()
    print('✅ PPTXGenerator: OK')
except Exception as e:
    print('❌ PPTXGenerator:', e)
"

echo.
echo [4/6] Testando nlp_engine...
python -c "
try:
    from agents.nlp_engine import NLPEngine
    nlp = NLPEngine()
    print('✅ NLPEngine: OK')
except Exception as e:
    print('❌ NLPEngine:', e)
"

echo.
echo [5/6] Testando recommendation_engine...
python -c "
try:
    from agents.recommendation_engine import RecommendationEngine
    rec = RecommendationEngine()
    print('✅ RecommendationEngine: OK')
except Exception as e:
    print('❌ RecommendationEngine:', e)
"

echo.
echo [6/6] Testando ml_engine...
python -c "
try:
    from agents.ml_engine import MLEngine
    ml = MLEngine()
    print('✅ MLEngine: OK')
except Exception as e:
    print('❌ MLEngine:', e)
"

echo.
echo ==========================================
echo 📊 TESTE COMPLETO DOS MÓDULOS
echo ==========================================

echo [TESTE FINAL] Iniciando servidor completo...
echo.
echo 📍 Se todos os módulos estão OK, o servidor deve iniciar sem erros
echo 🌐 Aguarde a mensagem: "Uvicorn running on http://0.0.0.0:5000"
echo.

python main_ai.py

echo.
echo 🎯 SE O SERVIDOR INICIOU:
echo ==========================================
echo • Abra: http://localhost:5000/docs
echo • Teste: http://localhost:5000/health
echo • Admin: http://localhost:5000/admin/admin_dashboard.html
echo.
pause

