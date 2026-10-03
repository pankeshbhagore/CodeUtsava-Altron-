from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sqlglot
import sqlglot.expressions as exp
import hashlib


class QueryMetadata(BaseModel):
    tables: List[str]
    columns: List[str]
    join_count: int
    filter_columns: List[str]
    group_by_columns: List[str]
    order_by_columns: List[str]
    aggregation_functions: List[str]
    subquery_count: int
    estimated_rows: Optional[int] = None
    query_frequency: Optional[float] = None
    execution_time_ms: Optional[float] = None
    plan_hash: Optional[str] = None


class MetadataExtractor:
    """Extract structural metadata from SQL queries.
    
    All identifiers (table names, column names) are anonymized using
    consistent hashing to prevent raw schema names from leaking into
    the AI layer.
    """

    def __init__(self):
        self._table_map: Dict[str, str] = {}
        self._column_map: Dict[str, str] = {}
        self._table_counter = 0
        self._column_counter = 0

    def _anon_table(self, name: str) -> str:
        if name not in self._table_map:
            self._table_counter += 1
            self._table_map[name] = f"TABLE_{self._table_counter}"
        return self._table_map[name]

    def _anon_column(self, name: str) -> str:
        if name not in self._column_map:
            self._column_counter += 1
            self._column_map[name] = f"COL_{self._column_counter}"
        return self._column_map[name]

    def extract_metadata(self, sql: str, execution_stats: dict = None) -> QueryMetadata:
        # Reset mappings per extraction to keep them consistent within a query
        self._table_map = {}
        self._column_map = {}
        self._table_counter = 0
        self._column_counter = 0

        tables = []
        columns = []
        filter_columns = []
        group_by_columns = []
        order_by_columns = []
        aggregation_functions = []
        join_count = 0
        subquery_count = 0

        try:
            parsed = sqlglot.parse_one(sql)

            seen_tables = set()
            for node in parsed.find_all(exp.Table):
                if node.name and node.name not in seen_tables:
                    seen_tables.add(node.name)
                    tables.append(self._anon_table(node.name))

            seen_columns = set()
            for node in parsed.find_all(exp.Column):
                if node.name and node.name not in seen_columns:
                    seen_columns.add(node.name)
                    columns.append(self._anon_column(node.name))

            for node in parsed.find_all(exp.Join):
                join_count += 1

            seen_filters = set()
            for node in parsed.find_all(exp.Where):
                for col in node.find_all(exp.Column):
                    if col.name and col.name not in seen_filters:
                        seen_filters.add(col.name)
                        filter_columns.append(self._anon_column(col.name))

            seen_groups = set()
            for node in parsed.find_all(exp.Group):
                for col in node.find_all(exp.Column):
                    if col.name and col.name not in seen_groups:
                        seen_groups.add(col.name)
                        group_by_columns.append(self._anon_column(col.name))

            seen_orders = set()
            for node in parsed.find_all(exp.Order):
                for col in node.find_all(exp.Column):
                    if col.name and col.name not in seen_orders:
                        seen_orders.add(col.name)
                        order_by_columns.append(self._anon_column(col.name))

            for node in parsed.find_all(exp.AggFunc):
                aggregation_functions.append(node.key.upper())

            subquery_count = max(0, len(list(parsed.find_all(exp.Select))) - 1)

        except Exception:
            pass

        stats = execution_stats or {}
        return QueryMetadata(
            tables=tables,
            columns=columns,
            join_count=join_count,
            filter_columns=filter_columns,
            group_by_columns=group_by_columns,
            order_by_columns=order_by_columns,
            aggregation_functions=aggregation_functions,
            subquery_count=subquery_count,
            estimated_rows=stats.get('estimated_rows'),
            query_frequency=stats.get('query_frequency'),
            execution_time_ms=stats.get('execution_time_ms'),
            plan_hash=stats.get('plan_hash')
        )
