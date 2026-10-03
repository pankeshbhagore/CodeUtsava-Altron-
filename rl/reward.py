import numpy as np
from typing import Dict, Any, Optional
from pydantic import BaseModel
from .environment import QueryContext

class RewardConfig(BaseModel):
    weight_performance: float = 1.0
    weight_storage: float = 0.5
    weight_write_latency: float = 0.8
    weight_complexity: float = 0.3
    weight_regression: float = 1.0

class RewardCalculator:
    def __init__(self, config: Optional[RewardConfig] = None):
        self.config = config or RewardConfig()

    def estimate_performance_gain(self, action: int, context: QueryContext) -> float:
        base_gain = 0.0
        if action in [0, 1]:  
            base_gain = context.execution_time_ms * 0.4
        elif action in [2, 3]: 
            if context.estimated_rows > 1000000:
                base_gain = context.execution_time_ms * 0.6
        elif action == 4: 
            base_gain = context.execution_time_ms * 0.7
        elif action == 5: 
            base_gain = context.execution_time_ms * 0.3
            
        return base_gain * context.query_frequency / 1000.0

    def estimate_storage_cost(self, action: int, context: QueryContext) -> float:
        if action == 0:
            return 100.0 
        elif action == 1:
            return 50.0  
        elif action in [2, 3]:
            return 10.0  
        elif action == 4:
            return 500.0 
        return 0.0

    def calculate(self, state_before: np.ndarray, state_after: np.ndarray, action: int, context: QueryContext) -> float:
        performance_gain = self.estimate_performance_gain(action, context)
        storage_penalty = self.estimate_storage_cost(action, context)
        
        write_latency_penalty = 0.0
        if action in [0, 1]:
            write_latency_penalty = float(context.metadata.get('write_frequency', 0.0)) * 10.0
            
        complexity_penalty = 0.0
        if action in [2, 3, 4]:
            complexity_penalty = 50.0
            
        regression_penalty = 0.0
        if action == 5:
            regression_penalty = 20.0
            
        reward = (self.config.weight_performance * performance_gain) - \
                 (self.config.weight_storage * storage_penalty) - \
                 (self.config.weight_write_latency * write_latency_penalty) - \
                 (self.config.weight_complexity * complexity_penalty) - \
                 (self.config.weight_regression * regression_penalty)
                 
        return float(reward)
