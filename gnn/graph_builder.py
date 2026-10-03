import hashlib
from typing import List, Dict, Any, Optional
import numpy as np
import networkx as nx
from pydantic import BaseModel, Field

class GraphNode(BaseModel):
    id: int
    node_type: str
    features: Dict[str, float]
    children: List[int] = Field(default_factory=list)
    cost: float
    actual_time: float
    rows: float
    loops: int
    is_bottleneck: bool = False

class GraphEdge(BaseModel):
    source_id: int
    target_id: int
    edge_type: str
    features: Dict[str, float]

class ExecutionGraph(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    adjacency_matrix: Any  # Will be a numpy array
    node_features_matrix: Any  # Will be a numpy array
    root_node_id: int
    
    class Config:
        arbitrary_types_allowed = True

class ExecutionPlanGraphBuilder:
    def __init__(self):
        self.node_types = [
            "Seq Scan", "Index Scan", "Bitmap Heap Scan", "Bitmap Index Scan",
            "Hash Join", "Nested Loop", "Merge Join", "Sort", "Hash",
            "Aggregate", "Limit", "Materialize", "Result", "Append", "Gather", "Gather Merge"
        ]
        
    def _encode_node_type(self, node_type: str) -> float:
        if node_type in self.node_types:
            return float(self.node_types.index(node_type))
        return float(len(self.node_types))
        
    def _anonymize_relation(self, name: Optional[str]) -> float:
        if not name:
            return 0.0
        return float(int(hashlib.md5(name.encode()).hexdigest()[:8], 16) % 1000)

    def build_graph(self, plan: Dict[str, Any]) -> ExecutionGraph:
        if "Plan" in plan:
            plan_node = plan["Plan"]
        else:
            plan_node = plan
            
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []
        
        self._traverse_and_build(plan_node, nodes, edges, -1)
        
        # Build adjacency matrix
        n = len(nodes)
        adj = np.zeros((n, n), dtype=np.float32)
        for e in edges:
            adj[e.source_id, e.target_id] = 1.0
            
        # Build features matrix
        # Features: [node_type, total_cost, actual_time, plan_rows, actual_rows, loops, width, relation, startup_cost, rows_removed]
        feature_dim = 10
        feat_matrix = np.zeros((n, feature_dim), dtype=np.float32)
        for i, node in enumerate(nodes):
            f = node.features
            feat_matrix[i] = [
                f.get("node_type_enc", 0.0),
                f.get("total_cost", 0.0),
                f.get("actual_time", 0.0),
                f.get("estimated_rows", 0.0),
                f.get("actual_rows", 0.0),
                f.get("loops", 0.0),
                f.get("width", 0.0),
                f.get("relation_enc", 0.0),
                f.get("startup_cost", 0.0),
                f.get("rows_removed", 0.0)
            ]
            
        return ExecutionGraph(
            nodes=nodes,
            edges=edges,
            adjacency_matrix=adj,
            node_features_matrix=feat_matrix,
            root_node_id=0 if nodes else -1
        )
        
    def _traverse_and_build(self, node_data: Dict[str, Any], nodes: List[GraphNode], edges: List[GraphEdge], parent_id: int) -> int:
        current_id = len(nodes)
        node_type = node_data.get("Node Type", "Unknown")
        
        features = {
            "node_type_enc": self._encode_node_type(node_type),
            "total_cost": node_data.get("Total Cost", 0.0),
            "actual_time": node_data.get("Actual Total Time", 0.0),
            "estimated_rows": node_data.get("Plan Rows", 0.0),
            "actual_rows": node_data.get("Actual Rows", 0.0),
            "loops": float(node_data.get("Actual Loops", 0)),
            "width": float(node_data.get("Plan Width", 0)),
            "relation_enc": self._anonymize_relation(node_data.get("Relation Name")),
            "startup_cost": node_data.get("Startup Cost", 0.0),
            "rows_removed": float(node_data.get("Rows Removed by Filter", 0.0) or node_data.get("Rows Removed by Index Recheck", 0.0))
        }
        
        graph_node = GraphNode(
            id=current_id,
            node_type=node_type,
            features=features,
            cost=features["total_cost"],
            actual_time=features["actual_time"],
            rows=features["actual_rows"] if features["actual_rows"] > 0 else features["estimated_rows"],
            loops=int(features["loops"])
        )
        nodes.append(graph_node)
        
        if parent_id >= 0:
            edges.append(GraphEdge(
                source_id=parent_id,
                target_id=current_id,
                edge_type="parent_child",
                features={"parent_child": 1.0, "execution_order": float(current_id)}
            ))
            nodes[parent_id].children.append(current_id)
            
        if "Plans" in node_data:
            for child_data in node_data["Plans"]:
                self._traverse_and_build(child_data, nodes, edges, current_id)
                
        return current_id

    def to_networkx(self, graph: ExecutionGraph) -> nx.DiGraph:
        nx_g = nx.DiGraph()
        for node in graph.nodes:
            nx_g.add_node(node.id, **node.dict())
        for edge in graph.edges:
            nx_g.add_edge(edge.source_id, edge.target_id, **edge.dict())
        return nx_g
