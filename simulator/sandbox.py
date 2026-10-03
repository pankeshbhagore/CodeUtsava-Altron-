"""Sandbox Simulator for testing proposed database optimizations."""
from typing import Dict, Any, List
import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from .metrics import MetricsCalculator

class SimMetrics(BaseModel):
    execution_time_ms: float
    planning_time_ms: float
    write_latency_ms: float
    storage_mb: float
    cpu_cost: float
    io_cost: float
    cache_hit_ratio: float
    estimated_rows_scanned: int
    index_size_mb: float

class SimulationResult(BaseModel):
    before_metrics: SimMetrics
    after_metrics: SimMetrics
    improvement_pct: float
    net_benefit_score: float
    risk_level: str
    simulation_method: str = Field(default='SIMULATED')
    simulation_id: str
    timestamp: str

class SandboxSimulator:
    """Simulates database optimization impacts."""
    
    def simulate_change(self, recommendation: Dict[str, Any], table_stats: Dict[str, Any], workload: List[Dict[str, Any]]) -> SimulationResult:
        change_type = recommendation.get('type', 'index')
        
        # Base metrics (Before)
        row_count = table_stats.get('row_count', 1000000)
        avg_row_size = table_stats.get('avg_row_size', 100)
        
        before_exec_time = MetricsCalculator.estimate_seq_scan_cost(row_count, avg_row_size)
        before_metrics = SimMetrics(
            execution_time_ms=before_exec_time,
            planning_time_ms=1.5,
            write_latency_ms=10.0,
            storage_mb=(row_count * avg_row_size) / (1024 * 1024),
            cpu_cost=row_count * MetricsCalculator.CPU_TUPLE_COST,
            io_cost=(row_count * avg_row_size / MetricsCalculator.PAGE_SIZE_BYTES) * MetricsCalculator.SEQ_PAGE_COST,
            cache_hit_ratio=0.8,
            estimated_rows_scanned=row_count,
            index_size_mb=0.0
        )
        
        # After metrics
        after_metrics = before_metrics.model_copy()
        improvement = 0.0
        risk = "LOW"
        
        change_type = recommendation.get('type', 'index').lower()
        
        if change_type in ('index', 'composite_index', 'single', 'composite', 'composite index', 'single index'):
            index_impact = MetricsCalculator.calculate_index_impact(recommendation, table_stats, workload)
            after_metrics.execution_time_ms = max(1.0, before_exec_time * (1 - index_impact.read_improvement_pct / 100.0))
            after_metrics.write_latency_ms = before_metrics.write_latency_ms * (1 + index_impact.write_overhead_pct / 100.0)
            after_metrics.index_size_mb = index_impact.storage_bytes / (1024 * 1024)
            after_metrics.storage_mb += after_metrics.index_size_mb
            after_metrics.estimated_rows_scanned = int(row_count * recommendation.get('estimated_selectivity', 0.1))
            improvement = index_impact.read_improvement_pct
            
        elif change_type == 'partitioning':
            part_impact = MetricsCalculator.calculate_partition_impact(recommendation, table_stats, workload)
            after_metrics.execution_time_ms = before_exec_time * (1 - part_impact.pruning_benefit_pct / 100.0)
            after_metrics.estimated_rows_scanned = int(row_count * (1 - part_impact.pruning_benefit_pct / 100.0))
            improvement = part_impact.pruning_benefit_pct
            risk = "HIGH"
            
        elif change_type == 'sql_rewrite':
            after_metrics.execution_time_ms = before_exec_time * 0.6 # 40% improvement
            after_metrics.cpu_cost = before_metrics.cpu_cost * 0.6
            improvement = 40.0
            risk = "MEDIUM"

        net_benefit = max(0.0, improvement - (after_metrics.write_latency_ms - before_metrics.write_latency_ms))
        
        return SimulationResult(
            before_metrics=before_metrics,
            after_metrics=after_metrics,
            improvement_pct=improvement,
            net_benefit_score=net_benefit,
            risk_level=risk,
            simulation_method='SIMULATED',
            simulation_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat()
        )

