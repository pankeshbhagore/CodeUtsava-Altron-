import hashlib
import uuid
from pydantic import BaseModel
from typing import Optional, Any
from .anonymizer import SQLAnonymizer
from .pii_detector import PIIDetector, PIIDetectionResult
from .metadata_extractor import MetadataExtractor
from .audit import PrivacyAuditor, AuditEntry
from .bitmasker import AttributeBitmasker

class PrivacyProcessedResult(BaseModel):
    anonymized_sql: str
    metadata: Any
    pii_scan_result: PIIDetectionResult
    audit_entry: AuditEntry
    is_safe: bool

class PrivacyGateway:
    def __init__(self):
        self.anonymizer = SQLAnonymizer()
        self.pii_detector = PIIDetector()
        self.metadata_extractor = MetadataExtractor()
        self.auditor = PrivacyAuditor()
        self.bitmasker = AttributeBitmasker()


    def process(self, raw_sql: str, execution_stats: dict = None) -> PrivacyProcessedResult:
        request_id = str(uuid.uuid4())

        pii_result = self.pii_detector.detect_pii(raw_sql)

                # Always anonymize - PII scan is informational
        anonymized = self.anonymizer.anonymize(raw_sql)
        anonymization_status = anonymized.anonymization_status
        raw_metadata = self.metadata_extractor.extract_metadata(raw_sql, execution_stats)
        
        # Apply strict attribute bitmasking to metadata before returning
        masked_dict = self.bitmasker.mask_dict(raw_metadata.model_dump() if hasattr(raw_metadata, 'model_dump') else raw_metadata)
        
        # Restore to QueryMetadata object if it was one
        if hasattr(raw_metadata, 'model_validate'):
            metadata = type(raw_metadata).model_validate(masked_dict)
        else:
            metadata = masked_dict

        payload_hash = hashlib.sha256(
            anonymized.anonymized_sql.encode()
        ).hexdigest()

        fields_masked = anonymized.literal_count + len(anonymized.table_mapping) + len(anonymized.column_mapping)

        # Override anonymization status if PII is detected (we blocked it)
        is_safe = ("SUCCESS" in anonymization_status or anonymization_status == "PASSED") and not pii_result.pii_found
        if pii_result.pii_found:
            anonymization_status = "BLOCKED_PII_DETECTED"

        audit = self.auditor.log_request(
            request_id=request_id,
            source_type="SQL_QUERY",
            raw_fields_detected=pii_result.pii_count + anonymized.literal_count,
            fields_masked=fields_masked,
            fields_hashed=len(anonymized.table_mapping) + len(anonymized.column_mapping),
            anonymization_status="PASSED" if "SUCCESS" in anonymization_status or anonymization_status == "PASSED" else anonymization_status,
            ai_payload_hash=payload_hash,
            result_hash=""
        )

        is_safe = ("SUCCESS" in anonymization_status or anonymization_status == "PASSED") and not pii_result.pii_found
        
        # Override anonymization status if PII is detected (we blocked it)
        if pii_result.pii_found:
            anonymization_status = "BLOCKED_PII_DETECTED"

        return PrivacyProcessedResult(
            anonymized_sql=anonymized.anonymized_sql,
            anonymization_detail=anonymized,
            metadata=metadata,
            pii_scan_result=pii_result,
            audit_entry=audit,
            is_safe=is_safe
        )

    def validate_ai_payload(self, payload: dict) -> bool:
        payload_str = json.dumps(payload)
        return not self.pii_detector.contains_pii(payload_str)



