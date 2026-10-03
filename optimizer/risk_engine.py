from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel
from .index_optimizer import IndexRecommendation
from .sql_rewriter import RewriteSuggestion
from .partition_optimizer import PartitionRecommendation
from .sharding_optimizer import ShardingRecommendation

class ImpactAnalysis(BaseModel):
    benefits: List[str]
    consequences: List[str]
    risk_level: str  # low, medium, high
    risk_score: float  # 0-1
    rollback_plan: str
    deployment_checklist: List[str]
    warnings: List[str]
    stale_statistics_warning: bool
    confidence_adjustment: float

class RiskEngine:
    def analyze_recommendation(self, recommendation: Union[IndexRecommendation, RewriteSuggestion, PartitionRecommendation, ShardingRecommendation], table_stats: Dict[str, Any], workload_stats: Dict[str, Any]) -> ImpactAnalysis:
        benefits = []
        consequences = []
        warnings = []
        stale_statistics_warning = table_stats.get("last_analyzed_days_ago", 0) > 7
        
        if stale_statistics_warning:
            warnings.append("Statistics are stale, which may affect optimization confidence.")
            
        if isinstance(recommendation, IndexRecommendation):
            risk_level = "MEDIUM" if recommendation.type == "composite" else "LOW"
            risk_score = 0.3 if risk_level == "MEDIUM" else 0.1
            benefits.append(f"Improves read performance by {recommendation.estimated_improvement_pct}%")
            consequences.append(f"Increases storage by {recommendation.storage_overhead_mb}MB")
            consequences.append(f"Adds {recommendation.write_latency_impact_ms}ms to writes")
            
            # Check for index explosion
            if table_stats.get("index_count", 0) > 10:
                warnings.append("Table already has many indexes. Adding more may severely impact writes.")
                risk_score += 0.2
                
            rollback_plan = recommendation.drop_sql
            deployment_checklist = ["Create index concurrently", "Monitor write latency", "Monitor disk space"]
            confidence_adjustment = -0.1 if stale_statistics_warning else 0.0
            
        elif isinstance(recommendation, RewriteSuggestion):
            risk_level = "MEDIUM"
            risk_score = 0.4
            benefits.append("Reduces query resource consumption")
            consequences.append("Requires application code change")
            rollback_plan = "Revert application code to use original SQL"
            deployment_checklist = ["Test thoroughly in staging", "Deploy application update"]
            confidence_adjustment = 0.0
            
        elif isinstance(recommendation, PartitionRecommendation) or isinstance(recommendation, ShardingRecommendation):
            risk_level = "HIGH"
            risk_score = 0.8
            benefits.append("Allows scaling beyond single-node or single-table limits")
            consequences.append("High migration complexity and application downtime potential")
            rollback_plan = "Restore from backup or reverse migration script"
            deployment_checklist = ["Perform full database backup", "Schedule maintenance window", "Test migration in staging"]
            confidence_adjustment = -0.2 if stale_statistics_warning else -0.1
            
        else:
            risk_level = "UNKNOWN"
            risk_score = 1.0
            rollback_plan = "N/A"
            deployment_checklist = []
            confidence_adjustment = 0.0
            
        # Cap risk score
        risk_score = min(1.0, max(0.0, risk_score))
        
        return ImpactAnalysis(
            benefits=benefits,
            consequences=consequences,
            risk_level=risk_level,
            risk_score=risk_score,
            rollback_plan=rollback_plan,
            deployment_checklist=deployment_checklist,
            warnings=warnings,
            stale_statistics_warning=stale_statistics_warning,
            confidence_adjustment=confidence_adjustment
        )
