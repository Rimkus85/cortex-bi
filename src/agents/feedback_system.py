"""
Sistema de Feedback e Logging Avançado
Coleta feedback do usuário, armazena interações e aprende com o uso
"""

import sqlite3
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import pandas as pd
from loguru import logger


class FeedbackSystem:
    """Sistema de feedback e logging avançado para aprendizado contínuo"""
    
    def __init__(self, db_path: str = "data/feedback.db"):
        """
        Inicializa o sistema de feedback
        
        Args:
            db_path: Caminho para o banco de dados SQLite
        """
        self.db_path = db_path
        self.setup_database()
        logger.info("FeedbackSystem inicializado com sucesso")
    
    def setup_database(self):
        """Cria as tabelas necessárias no banco de dados"""
        # Criar diretório se não existir
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de interações do usuário
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_interactions (
                id TEXT PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT,
                session_id TEXT,
                action_type TEXT,
                endpoint TEXT,
                request_data TEXT,
                response_data TEXT,
                execution_time REAL,
                success BOOLEAN,
                error_message TEXT
            )
        """)
        
        # Tabela de feedback do usuário
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_feedback (
                id TEXT PRIMARY KEY,
                interaction_id TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                rating INTEGER,
                feedback_type TEXT,
                comment TEXT,
                useful BOOLEAN,
                suggestions TEXT,
                FOREIGN KEY (interaction_id) REFERENCES user_interactions (id)
            )
        """)
        
        # Tabela de padrões de uso
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usage_patterns (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                pattern_type TEXT,
                pattern_data TEXT,
                frequency INTEGER DEFAULT 1,
                last_used DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de preferências do usuário
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                preference_type TEXT,
                preference_value TEXT,
                confidence_score REAL DEFAULT 0.5,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de métricas de performance
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id TEXT PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metric_type TEXT,
                metric_value REAL,
                context_data TEXT
            )
        """)
        
        # Criar índices para performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_interactions_timestamp ON user_interactions(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_interactions_user ON user_interactions(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_interaction ON user_feedback(interaction_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_patterns_user ON usage_patterns(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_preferences_user ON user_preferences(user_id)")
        
        conn.commit()
        conn.close()
        
        logger.info("Banco de dados de feedback configurado com sucesso")
    
    def log_interaction(self, 
                       user_id: str,
                       session_id: str,
                       action_type: str,
                       endpoint: str,
                       request_data: Dict,
                       response_data: Dict,
                       execution_time: float,
                       success: bool = True,
                       error_message: str = None) -> str:
        """
        Registra uma interação do usuário
        
        Args:
            user_id: ID do usuário
            session_id: ID da sessão
            action_type: Tipo de ação (upload, analyze, generate_pptx, etc.)
            endpoint: Endpoint da API chamado
            request_data: Dados da requisição
            response_data: Dados da resposta
            execution_time: Tempo de execução em segundos
            success: Se a operação foi bem-sucedida
            error_message: Mensagem de erro se houver
            
        Returns:
            ID da interação registrada
        """
        interaction_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO user_interactions 
            (id, user_id, session_id, action_type, endpoint, request_data, 
             response_data, execution_time, success, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            interaction_id, user_id, session_id, action_type, endpoint,
            json.dumps(request_data), json.dumps(response_data),
            execution_time, success, error_message
        ))
        
        conn.commit()
        conn.close()
        
        # Atualizar padrões de uso
        self._update_usage_patterns(user_id, action_type, request_data)
        
        logger.info(f"Interação registrada: {interaction_id} - {action_type}")
        return interaction_id
    
    def collect_feedback(self,
                        interaction_id: str,
                        rating: int,
                        feedback_type: str,
                        comment: str = None,
                        useful: bool = None,
                        suggestions: str = None) -> str:
        """
        Coleta feedback do usuário sobre uma interação
        
        Args:
            interaction_id: ID da interação
            rating: Avaliação de 1 a 5
            feedback_type: Tipo de feedback (quality, speed, accuracy, etc.)
            comment: Comentário do usuário
            useful: Se o resultado foi útil
            suggestions: Sugestões de melhoria
            
        Returns:
            ID do feedback registrado
        """
        feedback_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO user_feedback 
            (id, interaction_id, rating, feedback_type, comment, useful, suggestions)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (feedback_id, interaction_id, rating, feedback_type, comment, useful, suggestions))
        
        conn.commit()
        conn.close()
        
        # Atualizar preferências baseadas no feedback
        self._update_preferences_from_feedback(interaction_id, rating, feedback_type)
        
        logger.info(f"Feedback coletado: {feedback_id} - Rating: {rating}")
        return feedback_id
    
    def _update_usage_patterns(self, user_id: str, action_type: str, request_data: Dict):
        """Atualiza padrões de uso do usuário"""
        pattern_key = f"{action_type}_{hash(str(sorted(request_data.items())))}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Verificar se padrão já existe
        cursor.execute("""
            SELECT id, frequency FROM usage_patterns 
            WHERE user_id = ? AND pattern_type = ?
        """, (user_id, pattern_key))
        
        result = cursor.fetchone()
        
        if result:
            # Atualizar frequência
            cursor.execute("""
                UPDATE usage_patterns 
                SET frequency = frequency + 1, last_used = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (result[0],))
        else:
            # Criar novo padrão
            pattern_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO usage_patterns 
                (id, user_id, pattern_type, pattern_data, frequency)
                VALUES (?, ?, ?, ?, 1)
            """, (pattern_id, user_id, pattern_key, json.dumps(request_data)))
        
        conn.commit()
        conn.close()
    
    def _update_preferences_from_feedback(self, interaction_id: str, rating: int, feedback_type: str):
        """Atualiza preferências do usuário baseado no feedback"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Buscar dados da interação
        cursor.execute("""
            SELECT user_id, action_type, request_data FROM user_interactions 
            WHERE id = ?
        """, (interaction_id,))
        
        result = cursor.fetchone()
        if not result:
            conn.close()
            return
        
        user_id, action_type, request_data = result
        request_dict = json.loads(request_data)
        
        # Calcular score de confiança baseado no rating
        confidence_score = rating / 5.0
        
        # Atualizar preferências específicas
        if action_type == "analyze" and "analysis_type" in request_dict:
            self._update_preference(user_id, "preferred_analysis", 
                                  request_dict["analysis_type"], confidence_score)
        
        if "template_path" in request_dict:
            self._update_preference(user_id, "preferred_template", 
                                  request_dict["template_path"], confidence_score)
        
        conn.close()
    
    def _update_preference(self, user_id: str, preference_type: str, 
                          preference_value: str, confidence_score: float):
        """Atualiza uma preferência específica do usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Verificar se preferência já existe
        cursor.execute("""
            SELECT id, confidence_score FROM user_preferences 
            WHERE user_id = ? AND preference_type = ? AND preference_value = ?
        """, (user_id, preference_type, preference_value))
        
        result = cursor.fetchone()
        
        if result:
            # Atualizar score de confiança (média ponderada)
            old_score = result[1]
            new_score = (old_score + confidence_score) / 2
            
            cursor.execute("""
                UPDATE user_preferences 
                SET confidence_score = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (new_score, result[0]))
        else:
            # Criar nova preferência
            pref_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO user_preferences 
                (id, user_id, preference_type, preference_value, confidence_score)
                VALUES (?, ?, ?, ?, ?)
            """, (pref_id, user_id, preference_type, preference_value, confidence_score))
        
        conn.commit()
        conn.close()
    
    def get_user_patterns(self, user_id: str, limit: int = 10) -> List[Dict]:
        """
        Obtém padrões de uso mais frequentes do usuário
        
        Args:
            user_id: ID do usuário
            limit: Número máximo de padrões
            
        Returns:
            Lista de padrões de uso
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT pattern_type, pattern_data, frequency, last_used
            FROM usage_patterns 
            WHERE user_id = ?
            ORDER BY frequency DESC, last_used DESC
            LIMIT ?
        """, (user_id, limit))
        
        patterns = []
        for row in cursor.fetchall():
            patterns.append({
                "pattern_type": row[0],
                "pattern_data": json.loads(row[1]),
                "frequency": row[2],
                "last_used": row[3]
            })
        
        conn.close()
        return patterns
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Obtém preferências do usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Dicionário com preferências
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT preference_type, preference_value, confidence_score
            FROM user_preferences 
            WHERE user_id = ?
            ORDER BY confidence_score DESC
        """, (user_id,))
        
        preferences = {}
        for row in cursor.fetchall():
            pref_type = row[0]
            if pref_type not in preferences:
                preferences[pref_type] = []
            
            preferences[pref_type].append({
                "value": row[1],
                "confidence": row[2]
            })
        
        conn.close()
        return preferences
    
    def get_feedback_analytics(self, days: int = 30) -> Dict[str, Any]:
        """
        Obtém analytics de feedback dos últimos dias
        
        Args:
            days: Número de dias para análise
            
        Returns:
            Dicionário com métricas de feedback
        """
        conn = sqlite3.connect(self.db_path)
        
        # Feedback geral
        df_feedback = pd.read_sql_query("""
            SELECT f.rating, f.feedback_type, f.useful, i.action_type, i.endpoint
            FROM user_feedback f
            JOIN user_interactions i ON f.interaction_id = i.id
            WHERE f.timestamp >= datetime('now', '-{} days')
        """.format(days), conn)
        
        # Interações
        df_interactions = pd.read_sql_query("""
            SELECT action_type, endpoint, success, execution_time
            FROM user_interactions
            WHERE timestamp >= datetime('now', '-{} days')
        """.format(days), conn)
        
        conn.close()
        
        analytics = {
            "total_interactions": len(df_interactions),
            "total_feedback": len(df_feedback),
            "average_rating": df_feedback["rating"].mean() if not df_feedback.empty else 0,
            "success_rate": df_interactions["success"].mean() if not df_interactions.empty else 0,
            "average_execution_time": df_interactions["execution_time"].mean() if not df_interactions.empty else 0,
            "feedback_by_type": df_feedback.groupby("feedback_type")["rating"].mean().to_dict() if not df_feedback.empty else {},
            "most_used_actions": df_interactions["action_type"].value_counts().head(5).to_dict() if not df_interactions.empty else {},
            "useful_percentage": df_feedback["useful"].mean() * 100 if not df_feedback.empty else 0
        }
        
        return analytics
    
    def log_performance_metric(self, metric_type: str, metric_value: float, context: Dict = None):
        """
        Registra uma métrica de performance
        
        Args:
            metric_type: Tipo da métrica (response_time, memory_usage, etc.)
            metric_value: Valor da métrica
            context: Contexto adicional
        """
        metric_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO performance_metrics 
            (id, metric_type, metric_value, context_data)
            VALUES (?, ?, ?, ?)
        """, (metric_id, metric_type, metric_value, json.dumps(context or {})))
        
        conn.commit()
        conn.close()
        
        logger.debug(f"Métrica registrada: {metric_type} = {metric_value}")
    
    def cleanup_old_data(self, days: int = 90):
        """
        Remove dados antigos para manter o banco otimizado
        
        Args:
            days: Número de dias para manter os dados
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Remover interações antigas
        cursor.execute("""
            DELETE FROM user_interactions 
            WHERE timestamp < datetime('now', '-{} days')
        """.format(days))
        
        # Remover feedback órfão
        cursor.execute("""
            DELETE FROM user_feedback 
            WHERE interaction_id NOT IN (SELECT id FROM user_interactions)
        """)
        
        # Remover métricas antigas
        cursor.execute("""
            DELETE FROM performance_metrics 
            WHERE timestamp < datetime('now', '-{} days')
        """.format(days))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Dados antigos removidos (>{days} dias)")
    
    def export_data(self, user_id: str = None) -> Dict[str, Any]:
        """
        Exporta dados para análise externa
        
        Args:
            user_id: ID do usuário específico (opcional)
            
        Returns:
            Dicionário com todos os dados
        """
        conn = sqlite3.connect(self.db_path)
        
        where_clause = f"WHERE user_id = '{user_id}'" if user_id else ""
        
        data = {
            "interactions": pd.read_sql_query(f"SELECT * FROM user_interactions {where_clause}", conn).to_dict('records'),
            "feedback": pd.read_sql_query(f"""
                SELECT f.* FROM user_feedback f
                JOIN user_interactions i ON f.interaction_id = i.id
                {where_clause}
            """, conn).to_dict('records'),
            "patterns": pd.read_sql_query(f"SELECT * FROM usage_patterns {where_clause}", conn).to_dict('records'),
            "preferences": pd.read_sql_query(f"SELECT * FROM user_preferences {where_clause}", conn).to_dict('records'),
            "metrics": pd.read_sql_query("SELECT * FROM performance_metrics", conn).to_dict('records')
        }
        
        conn.close()
        return data


# Instância global do sistema de feedback
feedback_system = FeedbackSystem()

