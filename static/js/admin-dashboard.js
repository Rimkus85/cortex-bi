// CÓRTEX BI - Admin Dashboard JavaScript

// Configuração da API
const API_BASE_URL = window.location.origin;
const API_KEY = localStorage.getItem('cortex_api_key') || 'demo-key';

// Função para fazer requisições à API
async function apiRequest(endpoint, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY
        }
    };
    
    const mergedOptions = { ...defaultOptions, ...options };
    if (options.headers) {
        mergedOptions.headers = { ...defaultOptions.headers, ...options.headers };
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, mergedOptions);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API Request Error:', error);
        showNotification('Erro ao comunicar com a API', 'danger');
        throw error;
    }
}

// Navegação entre seções
function showSection(sectionName) {
    // Esconder todas as seções
    document.querySelectorAll('.section-content').forEach(section => {
        section.style.display = 'none';
    });
    
    // Mostrar seção selecionada
    const targetSection = document.getElementById(`section-${sectionName}`);
    if (targetSection) {
        targetSection.style.display = 'block';
    }
    
    // Atualizar menu ativo
    document.querySelectorAll('.sidebar-menu a').forEach(link => {
        link.classList.remove('active');
    });
    event.target.closest('a').classList.add('active');
    
    // Atualizar título da página
    const titles = {
        'overview': 'Dashboard Administrativo',
        'anomalies': 'Detecção de Anomalias',
        'analytics': 'Analytics',
        'ml-models': 'Modelos de Machine Learning',
        'data-sources': 'Fontes de Dados',
        'templates': 'Templates PPTX',
        'users': 'Gerenciamento de Usuários',
        'api-keys': 'API Keys',
        'alerts': 'Configuração de Alertas',
        'logs': 'Logs do Sistema',
        'settings': 'Configurações'
    };
    document.getElementById('page-title').textContent = titles[sectionName] || 'Dashboard';
    
    // Carregar dados da seção
    loadSectionData(sectionName);
}

// Carregar dados da seção
async function loadSectionData(sectionName) {
    switch(sectionName) {
        case 'overview':
            await loadOverviewData();
            break;
        case 'anomalies':
            await loadAnomaliesData();
            break;
        case 'ml-models':
            await loadMLModelsData();
            break;
        case 'data-sources':
            await loadDataSourcesData();
            break;
    }
}

// Carregar dados da visão geral
async function loadOverviewData() {
    try {
        // Carregar estatísticas
        const stats = await apiRequest('/admin/stats');
        document.getElementById('stat-analyses').textContent = stats.total_analyses || 0;
        document.getElementById('stat-users').textContent = stats.active_users || 0;
        document.getElementById('stat-anomalies').textContent = stats.anomalies_detected || 0;
        
        // Carregar status dos agentes
        const health = await apiRequest('/health');
        displayAgentsStatus(health.services);
        
        // Carregar atividade recente
        const activity = await apiRequest('/admin/activity/recent');
        displayRecentActivity(activity);
        
        // Criar gráfico de análises
        createAnalysesChart();
        
    } catch (error) {
        console.error('Error loading overview data:', error);
    }
}

// Exibir status dos agentes
function displayAgentsStatus(services) {
    const container = document.getElementById('agents-status');
    
    if (!services) {
        container.innerHTML = '<p class="text-muted">Não foi possível carregar o status dos agentes.</p>';
        return;
    }
    
    const agentNames = {
        'data_loader': 'Data Loader',
        'analytics_engine': 'Analytics Engine',
        'pptx_generator': 'PPTX Generator',
        'nlp_engine': 'NLP Engine',
        'ml_engine': 'ML Engine',
        'recommendation_engine': 'Recommendation Engine',
        'feedback_system': 'Feedback System',
        'admin_system': 'Admin System'
    };
    
    let html = '<div class="list-group">';
    
    for (const [key, status] of Object.entries(services)) {
        const isActive = status === 'active';
        const badgeClass = isActive ? 'badge-success' : 'badge-danger';
        const icon = isActive ? 'check-circle' : 'times-circle';
        
        html += `
            <div class="list-group-item d-flex justify-content-between align-items-center">
                <span><i class="fas fa-${icon} me-2"></i> ${agentNames[key] || key}</span>
                <span class="badge-custom ${badgeClass}">${status}</span>
            </div>
        `;
    }
    
    html += '</div>';
    container.innerHTML = html;
}

// Exibir atividade recente
function displayRecentActivity(activities) {
    const container = document.getElementById('recent-activity');
    
    if (!activities || activities.length === 0) {
        container.innerHTML = '<p class="text-muted">Nenhuma atividade recente.</p>';
        return;
    }
    
    let html = '<table class="custom-table"><thead><tr><th>Hora</th><th>Usuário</th><th>Ação</th><th>Status</th></tr></thead><tbody>';
    
    activities.forEach(activity => {
        const statusBadge = activity.success ? 
            '<span class="badge-custom badge-success">Sucesso</span>' :
            '<span class="badge-custom badge-danger">Erro</span>';
        
        html += `
            <tr>
                <td>${formatDateTime(activity.timestamp)}</td>
                <td>${activity.user_id || 'Sistema'}</td>
                <td>${activity.action_type}</td>
                <td>${statusBadge}</td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

// Criar gráfico de análises
function createAnalysesChart() {
    const ctx = document.getElementById('analysesChart');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'],
            datasets: [{
                label: 'Análises',
                data: [65, 78, 90, 81, 95, 72, 68],
                borderColor: '#1e40af',
                backgroundColor: 'rgba(30, 64, 175, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#f3f4f6'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Carregar dados de anomalias
async function loadAnomaliesData() {
    try {
        // Carregar métricas configuradas
        const metrics = await apiRequest('/anomaly/metrics/list');
        displayMetricsList(metrics);
        
        // Carregar anomalias detectadas
        const anomalies = await apiRequest('/anomaly/list?days=7');
        displayAnomaliesList(anomalies);
        
    } catch (error) {
        console.error('Error loading anomalies data:', error);
    }
}

// Exibir lista de métricas
function displayMetricsList(metrics) {
    const container = document.getElementById('metrics-list');
    
    if (!metrics || metrics.length === 0) {
        container.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle"></i> Nenhuma métrica configurada. 
                Clique em "Nova Métrica" para adicionar.
            </div>
        `;
        return;
    }
    
    let html = '<table class="custom-table"><thead><tr><th>Métrica</th><th>Fonte de Dados</th><th>Intervalo</th><th>Severidade</th><th>Status</th><th>Ações</th></tr></thead><tbody>';
    
    metrics.forEach(metric => {
        const statusBadge = metric.enabled ? 
            '<span class="badge-custom badge-success">Ativa</span>' :
            '<span class="badge-custom badge-warning">Inativa</span>';
        
        const severityBadge = getSeverityBadge(metric.alert_config?.severity || 'medium');
        
        html += `
            <tr>
                <td><strong>${metric.name}</strong><br><small class="text-muted">${metric.description || ''}</small></td>
                <td>${metric.data_source?.type || 'N/A'}</td>
                <td>${formatInterval(metric.monitoring?.check_interval || 3600)}</td>
                <td>${severityBadge}</td>
                <td>${statusBadge}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="editMetric('${metric.id}')">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteMetric('${metric.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

// Exibir lista de anomalias
function displayAnomaliesList(anomalies) {
    const container = document.getElementById('anomalies-list');
    
    if (!anomalies || anomalies.length === 0) {
        container.innerHTML = '<p class="text-muted">Nenhuma anomalia detectada nos últimos 7 dias.</p>';
        return;
    }
    
    let html = '<table class="custom-table"><thead><tr><th>Data/Hora</th><th>Métrica</th><th>Valor</th><th>Severidade</th><th>Score</th><th>Ações</th></tr></thead><tbody>';
    
    anomalies.forEach(anomaly => {
        const severityBadge = getSeverityBadge(anomaly.severity);
        
        html += `
            <tr>
                <td>${formatDateTime(anomaly.timestamp)}</td>
                <td>${anomaly.metric_name}</td>
                <td>${formatNumber(anomaly.current_value)}</td>
                <td>${severityBadge}</td>
                <td>${anomaly.anomaly_score?.toFixed(2) || 'N/A'}</td>
                <td>
                    <button class="btn btn-sm btn-outline-info" onclick="viewAnomalyDetails('${anomaly.id}')">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

// Carregar dados de modelos ML
async function loadMLModelsData() {
    try {
        const models = await apiRequest('/ml/models/status');
        displayMLModelsList(models);
    } catch (error) {
        console.error('Error loading ML models data:', error);
    }
}

// Exibir lista de modelos ML
function displayMLModelsList(models) {
    const container = document.getElementById('ml-models-list');
    
    if (!models) {
        container.innerHTML = '<p class="text-muted">Não foi possível carregar os modelos.</p>';
        return;
    }
    
    const modelNames = {
        'analysis_predictor': 'Preditor de Análises',
        'quality_classifier': 'Classificador de Qualidade',
        'anomaly_detector': 'Detector de Anomalias',
        'user_clusterer': 'Clusterizador de Usuários',
        'performance_predictor': 'Preditor de Performance'
    };
    
    let html = '<div class="row">';
    
    for (const [key, data] of Object.entries(models.models || {})) {
        const isTrained = data.trained;
        const statusBadge = isTrained ? 
            '<span class="badge-custom badge-success">Treinado</span>' :
            '<span class="badge-custom badge-warning">Não Treinado</span>';
        
        html += `
            <div class="col-md-6 mb-3">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">${modelNames[key] || key}</h5>
                        <p class="card-text">
                            Status: ${statusBadge}<br>
                            ${isTrained ? `
                                Último treinamento: ${formatDateTime(data.last_training)}<br>
                                Amostras: ${data.samples || 0}<br>
                                Acurácia: ${(data.accuracy * 100).toFixed(1)}%
                            ` : 'Modelo ainda não foi treinado'}
                        </p>
                        <button class="btn btn-sm btn-primary-custom" onclick="trainModel('${key}')">
                            <i class="fas fa-play"></i> ${isTrained ? 'Retreinar' : 'Treinar'}
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    html += '</div>';
    container.innerHTML = html;
}

// Carregar dados de fontes de dados
async function loadDataSourcesData() {
    try {
        const sources = await apiRequest('/admin/data-sources/list');
        displayDataSourcesList(sources);
    } catch (error) {
        console.error('Error loading data sources:', error);
    }
}

// Exibir lista de fontes de dados
function displayDataSourcesList(sources) {
    const container = document.getElementById('data-sources-list');
    
    if (!sources || sources.length === 0) {
        container.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle"></i> Nenhuma fonte de dados configurada.
            </div>
        `;
        return;
    }
    
    let html = '<table class="custom-table"><thead><tr><th>Nome</th><th>Tipo</th><th>Status</th><th>Última Conexão</th><th>Ações</th></tr></thead><tbody>';
    
    sources.forEach(source => {
        const statusBadge = source.connected ? 
            '<span class="badge-custom badge-success">Conectado</span>' :
            '<span class="badge-custom badge-danger">Desconectado</span>';
        
        html += `
            <tr>
                <td><strong>${source.name}</strong></td>
                <td>${source.type}</td>
                <td>${statusBadge}</td>
                <td>${formatDateTime(source.last_connection)}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="testDataSource('${source.id}')">
                        <i class="fas fa-plug"></i> Testar
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" onclick="editDataSource('${source.id}')">
                        <i class="fas fa-edit"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

// Funções auxiliares
function getSeverityBadge(severity) {
    const badges = {
        'critical': '<span class="badge-custom badge-danger">Crítica</span>',
        'high': '<span class="badge-custom badge-danger">Alta</span>',
        'medium': '<span class="badge-custom badge-warning">Média</span>',
        'low': '<span class="badge-custom badge-info">Baixa</span>'
    };
    return badges[severity] || badges['medium'];
}

function formatInterval(seconds) {
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}min`;
    return `${Math.floor(seconds / 3600)}h`;
}

function formatDateTime(timestamp) {
    if (!timestamp) return 'N/A';
    const date = new Date(timestamp);
    return date.toLocaleString('pt-BR');
}

function formatNumber(value) {
    if (value === null || value === undefined) return 'N/A';
    return new Intl.NumberFormat('pt-BR').format(value);
}

function showNotification(message, type = 'info') {
    // Implementar sistema de notificações toast
    console.log(`[${type.toUpperCase()}] ${message}`);
}

// Funções de ação
function showAddMetricModal() {
    alert('Modal de adicionar métrica será implementado');
}

function editMetric(metricId) {
    alert(`Editar métrica: ${metricId}`);
}

function deleteMetric(metricId) {
    if (confirm('Tem certeza que deseja excluir esta métrica?')) {
        apiRequest(`/anomaly/metrics/${metricId}`, { method: 'DELETE' })
            .then(() => {
                showNotification('Métrica excluída com sucesso', 'success');
                loadAnomaliesData();
            });
    }
}

function viewAnomalyDetails(anomalyId) {
    alert(`Ver detalhes da anomalia: ${anomalyId}`);
}

function trainModel(modelName) {
    showNotification(`Iniciando treinamento do modelo ${modelName}...`, 'info');
    
    apiRequest(`/ml/train/${modelName}`, { 
        method: 'POST',
        body: JSON.stringify({ retrain: true })
    })
    .then(result => {
        showNotification(`Modelo ${modelName} treinado com sucesso!`, 'success');
        loadMLModelsData();
    })
    .catch(error => {
        showNotification(`Erro ao treinar modelo: ${error.message}`, 'danger');
    });
}

function trainAllModels() {
    if (confirm('Tem certeza que deseja treinar todos os modelos? Isso pode levar alguns minutos.')) {
        showNotification('Iniciando treinamento de todos os modelos...', 'info');
        // Implementar lógica de treinamento em lote
    }
}

function showAddDataSourceModal() {
    alert('Modal de adicionar fonte de dados será implementado');
}

function testDataSource(sourceId) {
    showNotification(`Testando conexão com fonte de dados ${sourceId}...`, 'info');
    
    apiRequest(`/admin/data-sources/${sourceId}/test`, { method: 'POST' })
        .then(result => {
            if (result.success) {
                showNotification('Conexão bem-sucedida!', 'success');
            } else {
                showNotification('Falha na conexão', 'danger');
            }
        });
}

function editDataSource(sourceId) {
    alert(`Editar fonte de dados: ${sourceId}`);
}

function refreshActivity() {
    loadOverviewData();
}

function filterAnomalies(severity) {
    // Implementar filtro de anomalias
    console.log(`Filtrar por: ${severity}`);
}

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    // Carregar dados iniciais
    loadOverviewData();
});

