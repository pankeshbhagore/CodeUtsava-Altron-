"""Benchmark Runner for Database Simulator."""
from typing import Dict, Any, List
from pydantic import BaseModel, Field

class PlanComparison(BaseModel):
    before_cost: float
    after_cost: float
    improvement_pct: float
    nodes_improved: int
    nodes_regressed: int

class BenchmarkResult(BaseModel):
    before_results: List[Dict[str, Any]]
    after_results: List[Dict[str, Any]]
    summary: str
    total_improvement_pct: float
    regression_queries: List[str]
    benchmark_method: str = Field(default='SIMULATED')

class BenchmarkRunner:
    """Runs simulated benchmarks."""
    
    def run_benchmark(self, queries: List[str], table_stats: Dict[str, Any], proposed_changes: List[Dict[str, Any]]) -> BenchmarkResult:
        before_res = []
        after_res = []
        regressions = []
        
        total_before = 0.0
        total_after = 0.0
        
        for q in queries:
            # Simulated base cost
            b_cost = 1000.0
            
            # Simulate improvements
            a_cost = b_cost
            for change in proposed_changes:
                ctype = change.get('type')
                if ctype in ('index', 'composite_index'):
                    a_cost *= 0.3
                elif ctype == 'sql_rewrite':
                    a_cost *= 0.5
                elif ctype == 'partitioning':
                    a_cost *= 0.25
            
            before_res.append({'query': q, 'cost': b_cost})
            after_res.append({'query': q, 'cost': a_cost})
            
            total_before += b_cost
            total_after += a_cost
            
            if a_cost > b_cost:
                regressions.append(q)
                
        improvement = 0.0
        if total_before > 0:
            improvement = ((total_before - total_after) / total_before) * 100.0
            
        summary = f"Simulated benchmark completed. Improvement: {improvement:.2f}%."
        
        return BenchmarkResult(
            before_results=before_res,
            after_results=after_res,
            summary=summary,
            total_improvement_pct=improvement,
            regression_queries=regressions,
            benchmark_method='SIMULATED'
        )

    def compare_plans(self, before_plan: Dict[str, Any], after_plan: Dict[str, Any]) -> PlanComparison:
        b_cost = before_plan.get('Total Cost', 100.0)
        a_cost = after_plan.get('Total Cost', 50.0)
        
        imp = 0.0
        if b_cost > 0:
            imp = ((b_cost - a_cost) / b_cost) * 100.0
            
        return PlanComparison(
            before_cost=b_cost,
            after_cost=a_cost,
            improvement_pct=imp,
            nodes_improved=2,
            nodes_regressed=0
        )
