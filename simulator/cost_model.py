"""PostgreSQL Cost Model Simulator."""
import math

class PostgresCostModel:
    """Simplified PostgreSQL cost estimation based on standard constants."""
    
    # Standard PostgreSQL cost constants
    SEQ_PAGE_COST = 1.0
    RANDOM_PAGE_COST = 4.0
    CPU_TUPLE_COST = 0.01
    CPU_INDEX_TUPLE_COST = 0.005
    CPU_OPERATOR_COST = 0.0025
    PAGE_SIZE_BYTES = 8192
    
    @classmethod
    def estimate_seq_scan(cls, pages: int, tuples: int) -> float:
        """Estimate cost of sequential scan."""
        run_cost = (pages * cls.SEQ_PAGE_COST) + (tuples * cls.CPU_TUPLE_COST)
        return run_cost

    @classmethod
    def estimate_index_scan(cls, pages: int, tuples: int, selectivity: float) -> float:
        """Estimate cost of index scan."""
        index_pages = max(1, int(pages * selectivity))
        index_tuples = max(1, int(tuples * selectivity))
        run_cost = (index_pages * cls.RANDOM_PAGE_COST) + (index_tuples * cls.CPU_INDEX_TUPLE_COST) + (index_tuples * cls.CPU_TUPLE_COST)
        return run_cost

    @classmethod
    def estimate_nested_loop(cls, outer_rows: int, inner_cost: float) -> float:
        """Estimate cost of nested loop join."""
        run_cost = cls.CPU_TUPLE_COST * outer_rows + outer_rows * inner_cost
        return run_cost

    @classmethod
    def estimate_hash_join(cls, outer_rows: int, inner_rows: int, hash_cost: float) -> float:
        """Estimate cost of hash join."""
        run_cost = hash_cost + (outer_rows * cls.CPU_TUPLE_COST) + (inner_rows * cls.CPU_TUPLE_COST)
        return run_cost

    @classmethod
    def estimate_sort(cls, rows: int, width: int) -> float:
        """Estimate cost of sorting rows."""
        if rows <= 0:
            return 0.0
        # O(N log N) cost for sort
        run_cost = rows * math.log2(rows) * cls.CPU_OPERATOR_COST
        return run_cost

    @classmethod
    def estimate_aggregate(cls, rows: int) -> float:
        """Estimate cost of aggregation."""
        run_cost = rows * cls.CPU_OPERATOR_COST
        return run_cost
