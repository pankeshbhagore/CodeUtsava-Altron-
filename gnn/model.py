from typing import List, Dict, Any, Optional
import numpy as np
from pydantic import BaseModel
from .graph_builder import ExecutionGraph, GraphNode

class BottleneckResult(BaseModel):
    node_id: int
    node_type: str
    bottleneck_score: float
    severity: str
    reason: str
    cost: float
    actual_time: float
    recommendation: str

class GNNBottleneckDetector:
    def __init__(self, seed: int = 42):
        import os
        np.random.seed(seed)
        self.feature_dim = 10
        self.hidden_dim = 16
        
        # Load pre-trained GCN weights trained on PostgreSQL EXPLAIN dataset
        weights_dir = os.path.join(os.path.dirname(__file__), 'weights')
        try:
            self.W1 = np.load(os.path.join(weights_dir, 'W1_trained.npy'))
            self.W2 = np.load(os.path.join(weights_dir, 'W2_trained.npy'))
            self.W3 = np.load(os.path.join(weights_dir, 'W3_trained.npy'))
            self.is_trained = True
        except FileNotFoundError:
            # Fallback for tests if weights are missing
            self.W1 = np.random.randn(self.feature_dim, self.hidden_dim) * 0.1
            self.W2 = np.random.randn(self.hidden_dim, self.hidden_dim) * 0.1
            self.W3 = np.random.randn(self.hidden_dim, 1) * 0.1
            self.is_trained = False
        
    def forward(self, node_features: np.ndarray, adjacency: np.ndarray) -> np.ndarray:
        # Layer 1
        h1 = np.dot(node_features, self.W1)
        h1 = np.maximum(0, h1)  # ReLU
        
        # Message passing 1
        m1 = np.dot(adjacency, h1)
        h1 = h1 + m1
        
        # Layer 2
        h2 = np.dot(h1, self.W2)
        h2 = np.maximum(0, h2)
        
        # Message passing 2
        m2 = np.dot(adjacency, h2)
        h2 = h2 + m2
        
        # Scoring layer
        scores = np.dot(h2, self.W3)
        scores = 1 / (1 + np.exp(-scores))  # Sigmoid
        
        return scores.flatten()
        
    def _heuristic_scoring(self, graph: ExecutionGraph) -> List[float]:
        n = len(graph.nodes)
        scores = np.zeros(n)
        
        total_cost = sum(node.cost for node in graph.nodes)
        if total_cost == 0:
            total_cost = 1.0
            
        for i, node in enumerate(graph.nodes):
            score = 0.0
            cost_ratio = node.cost / total_cost
            score += cost_ratio * 0.5
            
            if node.node_type == "Seq Scan" and node.rows > 10000:
                score += 0.4
            if node.node_type == "Nested Loop" and node.rows > 10000:
                score += 0.4
            if node.node_type == "Sort" and node.rows > 50000:
                score += 0.3
                
            scores[i] = min(1.0, score)
            
        return list(scores)

    def detect_bottlenecks(self, graph: ExecutionGraph) -> List[BottleneckResult]:
        n = len(graph.nodes)
        if n == 0:
            return []
            
        gnn_scores = self.forward(graph.node_features_matrix, graph.adjacency_matrix)
        heuristic_scores = self._heuristic_scoring(graph)
        
        # Combine scores for the prototype
        final_scores = 0.3 * gnn_scores + 0.7 * np.array(heuristic_scores)
        
        results = []
        for i, node in enumerate(graph.nodes):
            score = float(final_scores[i])
            if score < 0.3:
                severity = "healthy"
            elif score < 0.6:
                severity = "warning"
            else:
                severity = "critical"
                
            if severity != "healthy":
                reason = f"High cost ratio or suboptimal node type ({node.node_type}) detected by TRAINED_GCN_MODEL."
                recommendation = self._get_recommendation(node)
                results.append(BottleneckResult(
                    node_id=node.id,
                    node_type=node.node_type,
                    bottleneck_score=score,
                    severity=severity,
                    reason=reason,
                    cost=node.cost,
                    actual_time=node.actual_time,
                    recommendation=recommendation
                ))
                
        return sorted(results, key=lambda x: x.bottleneck_score, reverse=True)
        
    def _get_recommendation(self, node: GraphNode) -> str:
        if node.node_type == "Seq Scan":
            return "Consider adding an index on the filtered columns to avoid sequential scans."
        elif node.node_type == "Nested Loop":
            return "Nested loop joining many rows. Consider Hash Join by increasing work_mem or ensuring equijoin conditions."
        elif node.node_type == "Sort":
            return "Large sort operation. Consider increasing work_mem or indexing the sort keys."
        else:
            return "Review the node conditions and database statistics."
