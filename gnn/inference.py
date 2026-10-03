from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from .plan_parser import PostgresPlanParser
from .graph_builder import ExecutionPlanGraphBuilder
from .model import GNNBottleneckDetector, BottleneckResult

class PlanMetrics(BaseModel):
    total_cost: float
    actual_execution_time: float
    planning_time: float
    total_rows: float
    total_loops: int
    node_count: int
    seq_scan_count: int
    index_scan_count: int
    join_count: int
    sort_count: int
    aggregate_count: int
    row_estimation_errors: List[float]

class PlanAnalysisResult(BaseModel):
    bottlenecks: List[BottleneckResult]
    execution_tree: Dict[str, Any]
    total_cost: float
    actual_total_time: float
    planning_time: float
    bottleneck_count: int
    health_score: float
    model_type: str = 'HEURISTIC_GNN'
    recommendations: List[str]

class GNNInferenceEngine:
    def __init__(self):
        self.parser = PostgresPlanParser()
        self.graph_builder = ExecutionPlanGraphBuilder()
        self.detector = GNNBottleneckDetector()
        
    def analyze_plan(self, plan_json: Dict[str, Any]) -> PlanAnalysisResult:
        parsed_plan = self.parser.parse(plan_json)
        graph = self.graph_builder.build_graph(plan_json)
        bottlenecks = self.detector.detect_bottlenecks(graph)
        
        execution_tree = self.get_execution_tree(plan_json, bottlenecks)
        
        total_cost = parsed_plan.total_cost
        actual_total_time = parsed_plan.execution_time
        planning_time = plan_json.get("Planning Time", 0.0) if isinstance(plan_json, dict) else 0.0
        
        bottleneck_count = len([b for b in bottlenecks if b.severity == "critical"])
        health_score = max(0.0, 100.0 - (len(bottlenecks) * 15.0) - (bottleneck_count * 20.0))
        
        recommendations = [b.recommendation for b in bottlenecks[:3]]
        
        return PlanAnalysisResult(
            bottlenecks=bottlenecks,
            execution_tree=execution_tree,
            total_cost=total_cost,
            actual_total_time=actual_total_time,
            planning_time=planning_time,
            bottleneck_count=bottleneck_count,
            health_score=health_score,
            recommendations=recommendations
        )
        
    def get_execution_tree(self, plan_json: Dict[str, Any], bottlenecks: Optional[List[BottleneckResult]] = None) -> Dict[str, Any]:
        if "Plan" in plan_json:
            plan_node = plan_json["Plan"]
        else:
            plan_node = plan_json
            
        bottleneck_map = {}
        if bottlenecks:
            bottleneck_map = {b.node_id: b.severity for b in bottlenecks}
            
        def _build_tree(node_data: Dict[str, Any], node_id: int) -> Dict[str, Any]:
            node_type = node_data.get("Node Type", "Unknown")
            status = bottleneck_map.get(node_id, "healthy")
            
            tree_node = {
                "node_id": node_id,
                "node_type": node_type,
                "cost": node_data.get("Total Cost", 0.0),
                "time": node_data.get("Actual Total Time", 0.0),
                "rows": node_data.get("Actual Rows", node_data.get("Plan Rows", 0.0)),
                "status": status,
                "children": []
            }
            
            next_id = node_id + 1
            if "Plans" in node_data:
                for child_data in node_data["Plans"]:
                    child_tree, next_id = _build_tree_recursive(child_data, next_id)
                    tree_node["children"].append(child_tree)
                    
            return tree_node
            
        def _build_tree_recursive(node_data: Dict[str, Any], node_id: int) -> tuple:
            node_type = node_data.get("Node Type", "Unknown")
            status = bottleneck_map.get(node_id, "healthy")
            
            tree_node = {
                "node_id": node_id,
                "node_type": node_type,
                "cost": node_data.get("Total Cost", 0.0),
                "time": node_data.get("Actual Total Time", 0.0),
                "rows": node_data.get("Actual Rows", node_data.get("Plan Rows", 0.0)),
                "status": status,
                "children": []
            }
            
            next_id = node_id + 1
            if "Plans" in node_data:
                for child_data in node_data["Plans"]:
                    child_tree, next_id = _build_tree_recursive(child_data, next_id)
                    tree_node["children"].append(child_tree)
                    
            return tree_node, next_id

        tree, _ = _build_tree_recursive(plan_node, 0)
        return tree

    def calculate_plan_metrics(self, plan_json: Dict[str, Any]) -> PlanMetrics:
        parsed_plan = self.parser.parse(plan_json)
        
        seq_scan_count = 0
        index_scan_count = 0
        join_count = 0
        sort_count = 0
        aggregate_count = 0
        total_rows = 0.0
        total_loops = 0
        errors = []
        
        for node in parsed_plan.all_nodes:
            ntype = node.node_type
            if "Seq Scan" in ntype:
                seq_scan_count += 1
            elif "Index Scan" in ntype:
                index_scan_count += 1
            elif "Join" in ntype or "Nested Loop" in ntype:
                join_count += 1
            elif "Sort" in ntype:
                sort_count += 1
            elif "Aggregate" in ntype:
                aggregate_count += 1
                
            total_rows += node.actual_rows if node.actual_rows > 0 else node.plan_rows
            total_loops += node.actual_loops
            errors.append(node.row_estimation_error)
            
        return PlanMetrics(
            total_cost=parsed_plan.total_cost,
            actual_execution_time=parsed_plan.execution_time,
            planning_time=plan_json.get("Planning Time", 0.0) if isinstance(plan_json, dict) else 0.0,
            total_rows=total_rows,
            total_loops=total_loops,
            node_count=len(parsed_plan.all_nodes),
            seq_scan_count=seq_scan_count,
            index_scan_count=index_scan_count,
            join_count=join_count,
            sort_count=sort_count,
            aggregate_count=aggregate_count,
            row_estimation_errors=errors
        )
