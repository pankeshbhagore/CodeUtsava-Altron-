import json
from typing import List, Dict, Any, Union, Optional
from pydantic import BaseModel, Field

class PlanNode(BaseModel):
    node_type: str
    relation_name: Optional[str] = None
    alias: Optional[str] = None
    startup_cost: float = 0.0
    total_cost: float = 0.0
    plan_rows: float = 0.0
    actual_rows: float = 0.0
    actual_time: float = 0.0
    actual_loops: int = 0
    filter: Optional[str] = None
    index_name: Optional[str] = None
    join_type: Optional[str] = None
    sort_key: Optional[List[str]] = None
    hash_cond: Optional[str] = None
    children: List['PlanNode'] = Field(default_factory=list)
    
    @property
    def row_estimation_error(self) -> float:
        if self.actual_rows == 0 and self.plan_rows == 0:
            return 1.0
        if self.actual_rows == 0:
            return self.plan_rows
        return max(self.plan_rows / self.actual_rows, self.actual_rows / self.plan_rows)

class ParsedPlan(BaseModel):
    root_node: PlanNode
    all_nodes: List[PlanNode] = Field(default_factory=list)
    total_cost: float = 0.0
    execution_time: float = 0.0

class PostgresPlanParser:
    def parse(self, plan_text_or_json: Union[str, Dict[str, Any]]) -> ParsedPlan:
        if isinstance(plan_text_or_json, str):
            try:
                plan_data = json.loads(plan_text_or_json)
            except json.JSONDecodeError:
                raise NotImplementedError("Text format EXPLAIN parsing not fully supported, please use JSON")
        else:
            plan_data = plan_text_or_json
            
        if isinstance(plan_data, list):
            plan_data = plan_data[0]
            
        if "Plan" in plan_data:
            plan_dict = plan_data["Plan"]
            execution_time = plan_data.get("Execution Time", plan_data.get("Actual Total Time", 0.0))
        else:
            plan_dict = plan_data
            execution_time = plan_dict.get("Actual Total Time", 0.0)
            
        all_nodes = []
        root_node = self._parse_node(plan_dict, all_nodes)
        
        return ParsedPlan(
            root_node=root_node,
            all_nodes=all_nodes,
            total_cost=root_node.total_cost,
            execution_time=execution_time
        )
        
    def _parse_node(self, node_dict: Dict[str, Any], all_nodes: List[PlanNode]) -> PlanNode:
        node = PlanNode(
            node_type=node_dict.get("Node Type", "Unknown"),
            relation_name=node_dict.get("Relation Name"),
            alias=node_dict.get("Alias"),
            startup_cost=node_dict.get("Startup Cost", 0.0),
            total_cost=node_dict.get("Total Cost", 0.0),
            plan_rows=node_dict.get("Plan Rows", 0.0),
            actual_rows=node_dict.get("Actual Rows", 0.0),
            actual_time=node_dict.get("Actual Total Time", 0.0),
            actual_loops=node_dict.get("Actual Loops", 0),
            filter=node_dict.get("Filter"),
            index_name=node_dict.get("Index Name"),
            join_type=node_dict.get("Join Type"),
            sort_key=node_dict.get("Sort Key"),
            hash_cond=node_dict.get("Hash Cond")
        )
        
        all_nodes.append(node)
        
        if "Plans" in node_dict:
            for child_dict in node_dict["Plans"]:
                child_node = self._parse_node(child_dict, all_nodes)
                node.children.append(child_node)
                
        return node
