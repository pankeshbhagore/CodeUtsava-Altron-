from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import hashlib

class AuditEntry(BaseModel):
    timestamp: datetime
    request_id: str
    source_type: str
    raw_fields_detected: int
    fields_masked: int
    fields_hashed: int
    anonymization_status: str
    ai_payload_hash: str
    result_hash: str

class PrivacyStats(BaseModel):
    total_requests: int
    total_pii_blocked: int
    total_fields_masked: int
    raw_exposure_count: int = 0

class PrivacyAuditor:
    def __init__(self):
        self.logs: List[AuditEntry] = []
        self.stats = PrivacyStats(
            total_requests=0,
            total_pii_blocked=0,
            total_fields_masked=0,
            raw_exposure_count=0
        )

    def log_request(self, request_id: str, source_type: str, raw_fields_detected: int, 
                    fields_masked: int, fields_hashed: int, anonymization_status: str, 
                    ai_payload_hash: str, result_hash: str) -> AuditEntry:
        entry = AuditEntry(
            timestamp=datetime.utcnow(),
            request_id=request_id,
            source_type=source_type,
            raw_fields_detected=raw_fields_detected,
            fields_masked=fields_masked,
            fields_hashed=fields_hashed,
            anonymization_status=anonymization_status,
            ai_payload_hash=ai_payload_hash,
            result_hash=result_hash
        )
        self.logs.append(entry)
        self.stats.total_requests += 1
        if fields_masked > 0:
            self.stats.total_fields_masked += fields_masked
        if raw_fields_detected > 0:
            self.stats.total_pii_blocked += 1
            
        return entry

    def get_audit_trail(self, limit: int = 100) -> List[AuditEntry]:
        return self.logs[-limit:]

    def get_privacy_stats(self) -> PrivacyStats:
        return self.stats
