from typing import List, Dict, Any
from pydantic import BaseModel

class WorkloadDrift(BaseModel):
    drift_score: float
    new_tables: List[str]
    new_filters: List[str]
    new_joins: List[str]
    frequency_changes: Dict[str, float]
    confidence_impact: float
    summary: str

class WorkloadStats(BaseModel):
    total_queries: int
    unique_patterns: int
    avg_execution_time: float
    p95_execution_time: float
    top_tables: List[str]
    top_filters: List[str]
    query_distribution: Dict[str, int]

class WorkloadAnalyzer:
    def analyze_drift(self, historical_queries: List[Dict[str, Any]], recent_queries: List[Dict[str, Any]]) -> WorkloadDrift:
        hist_tables = set()
        hist_filters = set()
        for q in historical_queries:
            hist_tables.update(q.get("tables", []))
            hist_filters.update(q.get("filters", []))
            
        recent_tables = set()
        recent_filters = set()
        freq_changes = {}
        for q in recent_queries:
            recent_tables.update(q.get("tables", []))
            recent_filters.update(q.get("filters", []))
            pattern = q.get("pattern", "unknown")
            freq_changes[pattern] = freq_changes.get(pattern, 0.0) + 1.0
            
        new_tables = list(recent_tables - hist_tables)
        new_filters = list(recent_filters - hist_filters)
        
        drift_score = len(new_tables) * 0.3 + len(new_filters) * 0.15
        if len(historical_queries) > 0 and len(recent_queries) > 0:
            drift_score += 0.05
            
        drift_score = min(drift_score, 1.0)
        
        return WorkloadDrift(
            drift_score=drift_score,
            new_tables=new_tables,
            new_filters=new_filters, 
            new_joins=[],   
            frequency_changes=freq_changes,
            confidence_impact=-(drift_score * 0.5),
            summary=f"Workload drift detected with score {drift_score:.2f}."
        )

    def get_workload_stats(self, queries: List[Dict[str, Any]]) -> WorkloadStats:
        if not queries:
            return WorkloadStats(
                total_queries=0,
                unique_patterns=0,
                avg_execution_time=0.0,
                p95_execution_time=0.0,
                top_tables=[],
                top_filters=[],
                query_distribution={}
            )
            
        exec_times = [q.get("execution_time_ms", 0.0) for q in queries]
        avg_exec = sum(exec_times) / len(exec_times)
        
        sorted_times = sorted(exec_times)
        p95_idx = int(len(sorted_times) * 0.95)
        p95_exec = sorted_times[p95_idx] if p95_idx < len(sorted_times) else avg_exec
        
        distribution = {}
        for q in queries:
            pattern = q.get("pattern", "unknown")
            distribution[pattern] = distribution.get(pattern, 0) + 1
            
        return WorkloadStats(
            total_queries=len(queries),
            unique_patterns=len(distribution),
            avg_execution_time=avg_exec,
            p95_execution_time=p95_exec,
            top_tables=[], 
            top_filters=[], 
            query_distribution=distribution
        )

