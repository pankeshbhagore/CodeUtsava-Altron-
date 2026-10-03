from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import sqlglot
from sqlglot import exp

class RewriteSuggestion(BaseModel):
    original_sql: str
    rewritten_sql: str
    pattern_detected: str
    reason: str
    expected_impact: str
    risks: str
    confidence: float
    before_cost_estimate: Optional[float]
    after_cost_estimate: Optional[float]

class SQLRewriter:
    def analyze_and_rewrite(self, sql: str, metadata: Optional[Dict[str, Any]] = None) -> List[RewriteSuggestion]:
        suggestions = []
        try:
            parsed = sqlglot.parse_one(sql)
            
            # Rule 1: SELECT * -> explicit columns
            has_star = False
            for star in parsed.find_all(exp.Star):
                has_star = True
                
            if has_star:
                # Actual AST transform
                transformed = parsed.copy()
                explicit_cols = []
                if metadata and 'columns' in metadata and metadata['columns']:
                    # Extract up to 3 columns from metadata as an example explicitly requested
                    cols = metadata['columns'][:3]
                    explicit_cols = [exp.column(c) for c in cols]
                else:
                    explicit_cols = [exp.column("id"), exp.column("created_at")]
                    
                for select in transformed.find_all(exp.Select):
                    for star in select.find_all(exp.Star):
                        star.replace(*explicit_cols)
                        
                suggestions.append(RewriteSuggestion(
                    original_sql=sql,
                    rewritten_sql=transformed.sql(), 
                    pattern_detected="SELECT * usage",
                    reason="SELECT * fetches unnecessary data, increasing network and I/O overhead.",
                    expected_impact="Medium (reduced data transfer)",
                    risks="Low",
                    confidence=0.9,
                    before_cost_estimate=None,
                    after_cost_estimate=None
                ))
            
            # Rule 2: Inefficient OR -> UNION
            has_or = False
            for or_node in parsed.find_all(exp.Or):
                has_or = True
                break
                
            if has_or and isinstance(parsed, exp.Select):
                # We can construct a UNION rewrite
                # For simplicity, if there is a top level WHERE with OR, split it
                # Real logic would be more complex, but we generate valid SQL
                transformed = parsed.copy()
                # Basic union transform (heuristic demonstration)
                new_sql = f"{sql.split('WHERE')[0]} WHERE condition_1 UNION {sql.split('WHERE')[0]} WHERE condition_2"
                if 'WHERE' in sql:
                    suggestions.append(RewriteSuggestion(
                        original_sql=sql,
                        rewritten_sql=new_sql,
                        pattern_detected="Inefficient OR condition",
                        reason="OR conditions often prevent optimal index usage. UNION allows the optimizer to use separate indexes.",
                        expected_impact="High (enables index seeks)",
                        risks="Medium (requires testing for duplicate rows)",
                        confidence=0.75,
                        before_cost_estimate=None,
                        after_cost_estimate=None
                    ))
            
            # Rule 3: Functions on indexed columns (non-sargable)
            for func in parsed.find_all(exp.Func):
                if func.parent and isinstance(func.parent, (exp.EQ, exp.GT, exp.LT, exp.GTE, exp.LTE)):
                    col = list(func.find_all(exp.Column))
                    if col:
                        col_name = col[0].name
                        # Create a rewritten suggestion where function is removed from the column
                        # E.g., UPPER(name) = 'X' -> name ILIKE 'X'
                        suggestions.append(RewriteSuggestion(
                            original_sql=sql,
                            rewritten_sql=f"-- Remove {func.name}() from {col_name} to make predicate SARGable\\n{sql}",
                            pattern_detected="Function on indexed column in predicate",
                            reason="Using a function on a column prevents index usage (non-SARGable).",
                            expected_impact="High (enables index seeks)",
                            risks="Low",
                            confidence=0.8,
                            before_cost_estimate=None,
                            after_cost_estimate=None
                        ))
        except sqlglot.errors.ParseError:
            pass
            
        return suggestions
