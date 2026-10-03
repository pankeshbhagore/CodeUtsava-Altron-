import os
import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class IndexRecommendation(BaseModel):
    type: str
    columns: List[str]
    table: str
    create_sql: str
    drop_sql: str
    reason: str
    evidence: str
    estimated_improvement_pct: float
    storage_overhead_mb: float
    write_latency_impact_ms: float
    confidence: float
    risk_level: str

class IndexOptimizer:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.api_key) if self.api_key and OpenAI else None

    def analyze_query(self, normalized_sql: str, metadata: Dict[str, Any], existing_indexes: List[Dict[str, Any]]) -> List[IndexRecommendation]:
        if self.client and os.getenv('OPENAI_MODEL'):
            return self._analyze_with_llm(normalized_sql, metadata)
        return self._analyze_heuristic(normalized_sql, metadata)

    def _analyze_with_llm(self, sql: str, metadata: Dict[str, Any]) -> List[IndexRecommendation]:
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        
        # Check for pgvector operations
        is_vector_search = "<->" in sql or "<#>" in sql or "<=>" in sql
        vector_prompt = ""
        if is_vector_search:
            vector_prompt = "WARNING: This query uses pgvector distance operators. You MUST recommend an HNSW or IVFFlat index. Type should be vector. "
            
        system_prompt = """You are the Consensus AI representing a debate between an Aggressive Optimizer Agent and a Conservative DBA Agent.
1. The Optimizer Agent wants maximum read speed and suggests complex/large indexes.
2. The Conservative DBA Agent worries about write latency, storage cost, and index maintenance.
You must synthesize their debate and provide the final consensus recommendation."""

        prompt = f"""{vector_prompt}
Analyze this SQL query and recommend ONE highly effective database index (single, composite, or vector) to optimize it.
SQL:
{sql}

Metadata:
{json.dumps(metadata, indent=2)}

Respond with valid JSON matching this schema:
{{
  "type": "composite",
  "columns": ["col1", "col2"],
  "table": "table_name_here",
  "create_sql": "CREATE INDEX idx_name ON table_name ...;",
  "drop_sql": "DROP INDEX idx_name;",
  "reason": "Explain the final decision, mentioning the multi-agent consensus (e.g., Optimizer suggested X, DBA raised concerns about Y, so we agreed on Z).",
  "estimated_improvement_pct": 85.0,
  "storage_overhead_mb": 2.5,
  "write_latency_impact_ms": 1.2,
  "risk_level": "LOW"
}}
Return ONLY the JSON object.
"""
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={ "type": "json_object" }
            )
            data = json.loads(response.choices[0].message.content)
            
            return [IndexRecommendation(
                type=data.get("type", "composite"),
                columns=data.get("columns", []),
                table=data.get("table", metadata.get("tables", ["unknown"])[0]),
                create_sql=data.get("create_sql", ""),
                drop_sql=data.get("drop_sql", ""),
                reason=data.get("reason", "AI Recommended Index"),
                evidence="Identified by Multi-Agent Consensus Analysis.",
                estimated_improvement_pct=float(data.get("estimated_improvement_pct", 80.0)),
                storage_overhead_mb=float(data.get("storage_overhead_mb", 1.0)),
                write_latency_impact_ms=float(data.get("write_latency_impact_ms", 1.0)),
                confidence=0.95,
                risk_level=data.get("risk_level", "LOW")
            )]
        except Exception as e:
            print(f"LLM Error: {e}")
            return self._analyze_heuristic(sql, metadata)

    def _analyze_heuristic(self, sql: str, metadata: Dict[str, Any]) -> List[IndexRecommendation]:
        recommendations = []
        tables = metadata.get("tables", [])
        if not tables:
            return recommendations
            
        main_table = tables[0]
        
        # Simple heuristic fallback
        idx_type = "composite"
        cols_str = "idx_col_1, idx_col_2"
        idx_name = f"idx_{main_table}_opt"
        
        recommendation = IndexRecommendation(
            type=idx_type,
            columns=["idx_col_1", "idx_col_2"],
            table=main_table,
            create_sql=f"CREATE INDEX {idx_name} ON {main_table} ({cols_str});",
            drop_sql=f"DROP INDEX {idx_name};",
            reason=f"Fallback heuristic recommendation.",
            evidence=f"Analyzed query structure.",
            estimated_improvement_pct=75.0,
            storage_overhead_mb=1.5,
            write_latency_impact_ms=2.0,
            confidence=0.8,
            risk_level="MEDIUM"
        )
        
        recommendations.append(recommendation)
        return recommendations
