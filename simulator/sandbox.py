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
    carbon_emissions_grams: float = Field(default=0.0)

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
    
    def simulate_change(self, recommendation: Dict[str, Any], table_stats: Dict[str, Any], workload: Any) -> SimulationResult:
        change_type = recommendation.get('type', 'index').lower()
        create_sql = recommendation.get('create_sql', '')
        
        # Base metrics (Before)
        row_count = table_stats.get('row_count', 1000000)
        avg_row_size = table_stats.get('avg_row_size', 100)
        
        # Handle dict vs list workload bug
        if isinstance(workload, list) and len(workload) > 0:
            before_exec_time = workload[0].get('execution_time_ms', MetricsCalculator.estimate_seq_scan_cost(row_count, avg_row_size))
            sample_query = workload[0].get('query', '')
        elif isinstance(workload, dict):
            before_exec_time = workload.get('execution_time_ms', MetricsCalculator.estimate_seq_scan_cost(row_count, avg_row_size))
            sample_query = workload.get('query', '')
        else:
            before_exec_time = MetricsCalculator.estimate_seq_scan_cost(row_count, avg_row_size)
            sample_query = ''
            
        # Carbon calculation
        co2_per_ms = (200 * 1.2 * 400) / (3600 * 1000 * 1000) * 1_000_000
        
        before_metrics = SimMetrics(
            execution_time_ms=before_exec_time,
            planning_time_ms=1.5,
            write_latency_ms=10.0,
            storage_mb=(row_count * avg_row_size) / (1024 * 1024),
            cpu_cost=row_count * MetricsCalculator.CPU_TUPLE_COST,
            io_cost=(row_count * avg_row_size / MetricsCalculator.PAGE_SIZE_BYTES) * MetricsCalculator.SEQ_PAGE_COST,
            cache_hit_ratio=0.8,
            estimated_rows_scanned=row_count,
            index_size_mb=0.0,
            carbon_emissions_grams=before_exec_time * co2_per_ms
        )

        after_exec_time = before_exec_time
        sim_method = 'HEURISTIC'
        storage_increase_mb = 0.0
        write_penalty_ms = 0.0
        
        # REAL POSTGRESQL SANDBOX EXECUTION (P0 Fix)
        if sample_query and (create_sql or change_type == 'rewrite' or change_type == 'sql_rewrite'):
            try:
                import json
                from database.connection import get_db_connection, release_db_connection
                conn = get_db_connection()
                cur = conn.cursor()
                
                # Start transaction that will NEVER be committed
                cur.execute('BEGIN;')
                
                if change_type in ('index', 'composite', 'single', 'composite_index', 'vector') and create_sql:
                    # Execute before EXPLAIN
                    cur.execute(f"EXPLAIN (FORMAT JSON) {sample_query}")
                    b_plan = cur.fetchone()[0][0]['Plan']
                    b_cost = b_plan.get('Total Cost', before_exec_time)
                    
                    # Apply change in sandbox
                    cur.execute(create_sql)
                    
                    # Execute after EXPLAIN
                    cur.execute(f"EXPLAIN (FORMAT JSON) {sample_query}")
                    a_plan = cur.fetchone()[0][0]['Plan']
                    a_cost = a_plan.get('Total Cost', before_exec_time)
                    
                    speedup = a_cost / max(b_cost, 0.001)
                    after_exec_time = before_exec_time * min(speedup, 1.0)
                    sim_method = 'POSTGRES_EXPLAIN_SANDBOX'
                    storage_increase_mb = (len(recommendation.get('columns', ['x'])) * 50.0) # heuristic size
                    write_penalty_ms = 0.5 * len(recommendation.get('columns', ['x']))
                    
                elif change_type in ('rewrite', 'sql_rewrite') and recommendation.get('rewritten_sql'):
                    rewritten = recommendation['rewritten_sql']
                    cur.execute(f"EXPLAIN (FORMAT JSON) {sample_query}")
                    b_cost = cur.fetchone()[0][0]['Plan']['Total Cost']
                    
                    cur.execute(f"EXPLAIN (FORMAT JSON) {rewritten}")
                    a_cost = cur.fetchone()[0][0]['Plan']['Total Cost']
                    
                    speedup = a_cost / max(b_cost, 0.001)
                    after_exec_time = before_exec_time * min(speedup, 1.0)
                    sim_method = 'POSTGRES_EXPLAIN_SANDBOX'
                    
                # ALways Rollback
                cur.execute('ROLLBACK;')
                cur.close()
                release_db_connection(conn)
            except Exception as e:
                print(f"Sandbox execution failed: {e}")
                # Ensure rollback on fail
                try:
                    cur.execute('ROLLBACK;')
                    cur.close()
                    release_db_connection(conn)
                except:
                    pass

        # Fallback to heuristics if Postgres connection fails or query is invalid
        if sim_method == 'HEURISTIC':
            if change_type in ('index', 'composite', 'single', 'composite_index', 'vector'):
                index_impact = MetricsCalculator.calculate_index_impact(recommendation, table_stats, workload if isinstance(workload, list) else [workload])
                after_exec_time = max(1.0, before_exec_time * (1 - index_impact.read_improvement_pct / 100.0))
                storage_increase_mb = index_impact.storage_bytes / (1024 * 1024)
                write_penalty_ms = before_metrics.write_latency_ms * (index_impact.write_overhead_pct / 100.0)
            elif change_type in ('partitioning', 'partition'):
                after_exec_time = before_exec_time * 0.25 
                storage_increase_mb = 15.0
            elif change_type in ('sql_rewrite', 'rewrite'):
                after_exec_time = before_exec_time * 0.6 
                
        after_metrics = before_metrics.model_copy()
        after_metrics.execution_time_ms = after_exec_time
        after_metrics.write_latency_ms += write_penalty_ms
        after_metrics.index_size_mb = storage_increase_mb
        after_metrics.storage_mb += storage_increase_mb
        after_metrics.carbon_emissions_grams = after_metrics.execution_time_ms * co2_per_ms
        
        improvement = 0.0
        if before_exec_time > 0:
            improvement = ((before_exec_time - after_exec_time) / before_exec_time) * 100.0
            
        net_benefit = max(0.0, improvement - write_penalty_ms)
        risk = "LOW" if change_type in ('index', 'composite', 'single', 'vector') else "MEDIUM"
        if 'partition' in change_type or 'shard' in change_type:
            risk = "HIGH"
            
        return SimulationResult(
            before_metrics=before_metrics,
            after_metrics=after_metrics,
            improvement_pct=round(improvement, 2),
            net_benefit_score=round(net_benefit, 2),
            risk_level=risk,
            simulation_method=sim_method,
            simulation_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat()
        )
