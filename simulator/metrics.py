"""Metrics Calculator for Optimizer Simulation."""
import math
from typing import Dict, Any, List
from pydantic import BaseModel
import numpy as np

class IndexImpact(BaseModel):
    read_improvement_pct: float
    write_overhead_pct: float
    storage_bytes: int
    maintenance_cost_score: float
    net_benefit: float

class PartitionImpact(BaseModel):
    pruning_benefit_pct: float
    avg_partition_size_mb: float
    max_partition_size_mb: float
    min_partition_size_mb: float
    cross_partition_pct: float
    migration_time_estimate_min: float
    net_benefit: float

class RewriteImpact(BaseModel):
    cost_reduction_pct: float
    rows_reduction_pct: float
    cpu_reduction_pct: float
    io_reduction_pct: float

class MetricsCalculator:
    """Calculates impact metrics for various database changes."""
    
    # Cost model assumptions
    SEQ_PAGE_COST = 1.0
    RANDOM_PAGE_COST = 4.0
    CPU_TUPLE_COST = 0.01
    CPU_INDEX_TUPLE_COST = 0.005
    CPU_OPERATOR_COST = 0.0025
    EFFECTIVE_CACHE_SIZE_BYTES = 4 * 1024 * 1024 * 1024 # 4GB
    PAGE_SIZE_BYTES = 8192

    @classmethod
    def calculate_index_impact(cls, index_config: Dict[str, Any], table_stats: Dict[str, Any], query_patterns: List[Dict[str, Any]]) -> IndexImpact:
        row_count = table_stats.get('row_count', 1000)
        avg_row_size = table_stats.get('avg_row_size', 100)
        num_cols = len(index_config.get('columns', ['id']))
        
        storage_bytes = cls.estimate_index_size(row_count, avg_row_size, num_cols)
        
        # Simulated improvements
        selectivity = index_config.get('estimated_selectivity', 0.1)
        read_improvement = 100.0 * (1.0 - selectivity) if selectivity < 1.0 else 0.0
        write_overhead = num_cols * 1.5 
        maintenance_score = (storage_bytes / (1024 * 1024)) * 0.1
        
        net = read_improvement - write_overhead - maintenance_score
        
        return IndexImpact(
            read_improvement_pct=read_improvement,
            write_overhead_pct=write_overhead,
            storage_bytes=storage_bytes,
            maintenance_cost_score=maintenance_score,
            net_benefit=net
        )

    @classmethod
    def calculate_partition_impact(cls, partition_config: Dict[str, Any], table_stats: Dict[str, Any], query_patterns: List[Dict[str, Any]]) -> PartitionImpact:
        table_size_mb = table_stats.get('size_bytes', 1000000) / (1024 * 1024)
        num_partitions = partition_config.get('num_partitions', 4)
        
        avg_part_size = table_size_mb / max(1, num_partitions)
        
        return PartitionImpact(
            pruning_benefit_pct=75.0, # Simulated
            avg_partition_size_mb=avg_part_size,
            max_partition_size_mb=avg_part_size * 1.2,
            min_partition_size_mb=avg_part_size * 0.8,
            cross_partition_pct=15.0,
            migration_time_estimate_min=table_size_mb * 0.01,
            net_benefit=60.0
        )

    @classmethod
    def calculate_rewrite_impact(cls, original_cost: float, rewritten_cost: float) -> RewriteImpact:
        red_pct = max(0.0, ((original_cost - rewritten_cost) / max(1.0, original_cost)) * 100.0)
        return RewriteImpact(
            cost_reduction_pct=red_pct,
            rows_reduction_pct=red_pct * 0.9,
            cpu_reduction_pct=red_pct * 0.8,
            io_reduction_pct=red_pct * 0.95
        )

    @classmethod
    def estimate_index_size(cls, row_count: int, avg_row_size: int, num_columns: int) -> int:
        overhead_per_tuple = 24
        key_size = num_columns * 8
        total_tuple_size = overhead_per_tuple + key_size
        tuples_per_page = max(1, math.floor(cls.PAGE_SIZE_BYTES / total_tuple_size))
        pages = math.ceil(row_count / tuples_per_page)
        fill_factor = 0.9
        return int((pages * cls.PAGE_SIZE_BYTES) / fill_factor)

    @classmethod
    def estimate_btree_lookup_cost(cls, row_count: int) -> float:
        if row_count <= 0:
            return 0.0
        # O(log N) operations
        ops = math.log2(row_count)
        return ops * cls.CPU_INDEX_TUPLE_COST * 1000.0 # ms

    @classmethod
    def estimate_seq_scan_cost(cls, row_count: int, avg_row_size: int) -> float:
        total_size = row_count * avg_row_size
        pages = math.ceil(total_size / cls.PAGE_SIZE_BYTES)
        # Combine IO and CPU costs
        cost = (pages * cls.SEQ_PAGE_COST) + (row_count * cls.CPU_TUPLE_COST)
        return cost * 1.0 # arbitrary conversion to ms for sim
