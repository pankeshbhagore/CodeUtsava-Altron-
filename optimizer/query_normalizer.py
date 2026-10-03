import hashlib
from typing import List, Optional
from pydantic import BaseModel
import sqlglot
from sqlglot import exp

class NormalizedQuery(BaseModel):
    normalized_sql: str
    query_fingerprint: str
    query_hash: str
    tables: List[str]
    columns: List[str]
    joins: List[str]
    filters: List[str]
    aggregations: List[str]
    sorting: List[str]
    grouping: List[str]
    original_sql: Optional[str] = None

class QueryNormalizer:
    def normalize(self, sql: str) -> NormalizedQuery:
        """
        Normalizes a SQL query by replacing literals with parameters and extracting metadata.
        """
        query_hash = hashlib.sha256(sql.encode('utf-8')).hexdigest()
        try:
            parsed = sqlglot.parse_one(sql)
            
            # Replace literals with '?'
            for node in parsed.find_all(exp.Literal):
                # Ensure we only replace literals that are values (not identifiers)
                if not isinstance(node.parent, (exp.Alias, exp.Column, exp.Table)):
                    node.replace(exp.Var(this='?'))
            
            normalized_sql = parsed.sql()
            query_fingerprint = hashlib.sha256(normalized_sql.encode('utf-8')).hexdigest()
            
            # Extract basic components
            tables = list(set([t.name for t in parsed.find_all(exp.Table) if t.name]))
            columns = list(set([c.name for c in parsed.find_all(exp.Column) if c.name]))
            
            joins = [join.sql() for join in parsed.find_all(exp.Join)]
            
            filters = []
            for where in parsed.find_all(exp.Where):
                filters.append(where.sql())
                
            aggregations = [agg.sql() for agg in parsed.find_all(exp.AggFunc)]
            
            sorting = []
            for order in parsed.find_all(exp.Order):
                sorting.append(order.sql())
                
            grouping = []
            for group in parsed.find_all(exp.Group):
                grouping.append(group.sql())
            
            return NormalizedQuery(
                normalized_sql=normalized_sql,
                query_fingerprint=query_fingerprint,
                query_hash=query_hash,
                tables=tables,
                columns=columns,
                joins=joins,
                filters=filters,
                aggregations=aggregations,
                sorting=sorting,
                grouping=grouping
            )
        except Exception:
            # Fallback
            return NormalizedQuery(
                normalized_sql=sql,
                query_fingerprint=query_hash,
                query_hash=query_hash,
                tables=[],
                columns=[],
                joins=[],
                filters=[],
                aggregations=[],
                sorting=[],
                grouping=[]
            )
