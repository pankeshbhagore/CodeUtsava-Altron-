import numpy as np
from typing import Dict, Any, Tuple, Optional
from pydantic import BaseModel
from .environment import QueryContext, DatabaseOptimizationEnv

class RLRecommendation(BaseModel):
    action: int
    action_name: str
    confidence: float
    q_values: Optional[np.ndarray] = None
    reward_estimate: float
    model_type: str
    reasoning: str
    
    class Config:
        arbitrary_types_allowed = True

class QLearningPolicy:
    def __init__(self, state_dim: int = 10, num_actions: int = 7, bins: int = 5):
        self.num_actions = num_actions
        self.bins = bins
        self.q_table = {} 
        self.alpha = 0.1
        self.gamma = 0.9

    def _discretize(self, state: np.ndarray) -> tuple:
        discretized = np.floor(state * self.bins)
        return tuple(discretized.astype(int))

    def get_q_values(self, state: np.ndarray) -> np.ndarray:
        state_key = self._discretize(state)
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.num_actions)
        return self.q_table[state_key]

    def select_action(self, state: np.ndarray, epsilon: float = 0.1) -> int:
        if np.random.rand() < epsilon:
            return int(np.random.randint(self.num_actions))
        q_values = self.get_q_values(state)
        return int(np.argmax(q_values))

    def update(self, state: np.ndarray, action: int, reward: float, next_state: np.ndarray) -> None:
        state_key = self._discretize(state)
        next_state_key = self._discretize(next_state)
        
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.num_actions)
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = np.zeros(self.num_actions)
            
        best_next_q = np.max(self.q_table[next_state_key])
        current_q = self.q_table[state_key][action]
        
        self.q_table[state_key][action] = current_q + self.alpha * (reward + self.gamma * best_next_q - current_q)


class ContextualBanditPolicy:
    def __init__(self, num_actions: int = 7, context_dim: int = 10):
        self.num_actions = num_actions
        self.context_dim = context_dim
        self.weights = np.zeros((num_actions, context_dim))

    def select_action(self, context: np.ndarray) -> int:
        scores = np.dot(self.weights, context)
        return int(np.argmax(scores))

    def update(self, context: np.ndarray, action: int, reward: float, learning_rate: float = 0.01) -> None:
        prediction = np.dot(self.weights[action], context)
        error = reward - prediction
        self.weights[action] += learning_rate * error * context


class HeuristicPolicy:
    def select_action(self, state: np.ndarray, context: QueryContext) -> Tuple[int, float, str]:
        sql = context.normalized_sql.lower()
        
        if "select *" in sql or "exists (" in sql:
            return DatabaseOptimizationEnv.ACTION_REWRITE_SQL, 0.8, "Correlated subquery or SELECT * detected."
            
        if context.estimated_rows > 10_000_000 and "where" in sql and context.query_frequency > 10:
            return DatabaseOptimizationEnv.ACTION_PARTITION_TABLE, 0.9, "Large table with frequent filtered queries."
            
        where_count = sql.count(" and ") + 1 if "where" in sql else 0
        if where_count > 1 and context.query_frequency > 50:
            return DatabaseOptimizationEnv.ACTION_ADD_COMPOSITE_INDEX, 0.85, "Multiple columns in WHERE clause."
            
        if context.query_frequency > 100 and "seq scan" in str(context.metadata).lower():
             return DatabaseOptimizationEnv.ACTION_ADD_SINGLE_INDEX, 0.75, "Frequent sequential scan detected."
             
        if context.estimated_rows > 100_000_000:
            return DatabaseOptimizationEnv.ACTION_RECOMMEND_SHARDING, 0.6, "Very large data volume."
            
        return DatabaseOptimizationEnv.ACTION_DO_NOTHING, 0.9, "No significant optimization pattern matched."

class RLOptimizer:
    def __init__(self):
        self.env = DatabaseOptimizationEnv()
        self.heuristic = HeuristicPolicy()
        self.q_learning = QLearningPolicy()
        
        self.action_names = {
            0: "Add composite index",
            1: "Add single-column index",
            2: "Partition table",
            3: "Change partition key",
            4: "Recommend sharding",
            5: "Rewrite SQL",
            6: "Do nothing"
        }

    def recommend(self, query_context: QueryContext, demo_mode: bool = True) -> RLRecommendation:
        state = self.env.reset(query_context)
        
        if demo_mode:
            action_heur, conf_heur, reasoning = self.heuristic.select_action(state, query_context)
            q_vals = self.q_learning.get_q_values(state)
            
            return RLRecommendation(
                action=action_heur,
                action_name=self.action_names.get(action_heur, "Unknown"),
                confidence=conf_heur,
                q_values=q_vals,
                reward_estimate=float(q_vals[action_heur]) if action_heur < len(q_vals) else 0.0,
                model_type="HEURISTIC",
                reasoning=reasoning
            )
        else:
            action_ql = self.q_learning.select_action(state, epsilon=0.05)
            q_vals = self.q_learning.get_q_values(state)
            return RLRecommendation(
                action=action_ql,
                action_name=self.action_names.get(action_ql, "Unknown"),
                confidence=0.7,
                q_values=q_vals,
                reward_estimate=float(q_vals[action_ql]) if action_ql < len(q_vals) else 0.0,
                model_type="Q_LEARNING",
                reasoning="Q-learning policy selected highest Q-value."
            )
