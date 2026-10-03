import numpy as np
from typing import Tuple, List, Dict, Any
from pydantic import BaseModel

class QueryContext(BaseModel):
    normalized_sql: str
    metadata: Dict[str, Any]
    table_stats: Dict[str, Any]
    existing_indexes: List[str]
    execution_time_ms: float
    query_frequency: float
    estimated_rows: int

class DatabaseOptimizationEnv:
    ACTION_ADD_COMPOSITE_INDEX = 0
    ACTION_ADD_SINGLE_INDEX = 1
    ACTION_PARTITION_TABLE = 2
    ACTION_CHANGE_PARTITION_KEY = 3
    ACTION_RECOMMEND_SHARDING = 4
    ACTION_REWRITE_SQL = 5
    ACTION_DO_NOTHING = 6
    
    def __init__(self):
        self.state_dim = 10
        self.num_actions = 7
        self.current_context = None
        self.state = None
        
    def _encode_state(self, context: QueryContext) -> np.ndarray:
        # State space: normalized query features, execution plan features, table statistics, 
        # index metadata, query frequency, execution time, estimated rows, storage overhead, 
        # write frequency, workload characteristics
        features = np.zeros(self.state_dim, dtype=np.float32)
        
        # 0: query length
        features[0] = len(context.normalized_sql) / 1000.0
        # 1: execution time (normalized)
        features[1] = min(context.execution_time_ms / 10000.0, 1.0)
        # 2: query frequency
        features[2] = min(context.query_frequency / 1000.0, 1.0)
        # 3: estimated rows
        features[3] = min(context.estimated_rows / 1000000.0, 1.0)
        # 4: number of existing indexes
        features[4] = min(len(context.existing_indexes) / 10.0, 1.0)
        # 5: number of tables
        features[5] = min(len(context.table_stats) / 10.0, 1.0)
        # 6: storage overhead 
        features[6] = float(context.metadata.get('storage_overhead', 0.5))
        # 7: write frequency 
        features[7] = float(context.metadata.get('write_frequency', 0.5))
        # 8: execution plan features 
        features[8] = float(context.metadata.get('plan_complexity', 0.5))
        # 9: workload characteristics 
        features[9] = float(context.metadata.get('workload_intensity', 0.5))
        
        return features

    def reset(self, query_context: QueryContext) -> np.ndarray:
        self.current_context = query_context
        self.state = self._encode_state(query_context)
        return self.state

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict[str, Any]]:
        if self.state is None or self.current_context is None:
            raise ValueError("Environment not initialized. Call reset() first.")
            
        next_state = self.state.copy()
        
        # Simulate changes based on action
        latency_reduction = 0.0
        storage_increase = 0.0
        
        if action == self.ACTION_ADD_COMPOSITE_INDEX or action == self.ACTION_ADD_SINGLE_INDEX:
            latency_reduction = next_state[1] * 0.5
            next_state[1] -= latency_reduction
            storage_increase = 0.1
            next_state[6] = min(next_state[6] + storage_increase, 1.0)
        elif action == self.ACTION_PARTITION_TABLE or action == self.ACTION_CHANGE_PARTITION_KEY:
            latency_reduction = next_state[1] * 0.4
            next_state[1] -= latency_reduction
            next_state[8] = min(next_state[8] + 0.2, 1.0)
        elif action == self.ACTION_RECOMMEND_SHARDING:
            latency_reduction = next_state[1] * 0.6
            next_state[1] -= latency_reduction
            next_state[9] = min(next_state[9] + 0.3, 1.0)
        elif action == self.ACTION_REWRITE_SQL:
            latency_reduction = next_state[1] * 0.3
            next_state[1] -= latency_reduction
            next_state[8] *= 0.8
            
        # REAL REWARD COMPUTATION (P0 Fix)
        reward = (latency_reduction * 100.0) - (storage_increase * 20.0)
        if action == self.ACTION_DO_NOTHING:
            if self.state[1] > 0.5: # high latency
                reward = -10.0 # penalty for doing nothing on a slow query
            else:
                reward = 5.0 # reward for avoiding unnecessary changes
                
        done = True  
        info = {"action": action, "context": self.current_context}
        
        self.state = next_state
        return next_state, reward, done, info

    def get_valid_actions(self) -> List[int]:
        return list(range(self.num_actions))
