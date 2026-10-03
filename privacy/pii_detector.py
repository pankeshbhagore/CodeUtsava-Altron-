import re
from typing import List, Dict, Any
from pydantic import BaseModel

class PIIDetectionResult(BaseModel):
    pii_found: bool
    pii_types: List[str]
    pii_count: int
    locations: List[Dict[str, Any]]

class PIIDetector:
    PATTERNS = {
        'EMAIL': r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',
        'PHONE': r'\b(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
        'SSN': r'\b\d{3}-\d{2}-\d{4}\b',
        'CREDIT_CARD': r'\b(?:\d[ -]*?){13,16}\b',
        'IP_ADDRESS': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
        'NAME': r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', # Simple common name pattern
        'ADDRESS': r'\d+ [A-Za-z0-9\s,]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct)\b'
    }
    
    def detect_pii(self, text: str) -> PIIDetectionResult:
        found_types = []
        locations = []
        count = 0
        
        for pii_type, pattern in self.PATTERNS.items():
            for match in re.finditer(pattern, text):
                found_types.append(pii_type)
                locations.append({
                    'type': pii_type,
                    'start': match.start(),
                    'end': match.end(),
                    'value': match.group()
                })
                count += 1
                
        return PIIDetectionResult(
            pii_found=count > 0,
            pii_types=list(set(found_types)),
            pii_count=count,
            locations=locations
        )

    def contains_pii(self, text: str) -> bool:
        result = self.detect_pii(text)
        return result.pii_found

    def mask_pii(self, text: str) -> str:
        masked_text = text
        for pii_type, pattern in self.PATTERNS.items():
            masked_text = re.sub(pattern, f'[MASKED_{pii_type}]', masked_text)
        return masked_text
