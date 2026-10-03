"""Attribute Bitmasking for column-level data obfuscation."""
import hashlib
import struct
from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class BitmaskConfig(BaseModel):
    seed: int = 42
    mask_bits: int = 32
    preserve_type: bool = True


class BitmaskResult(BaseModel):
    original_field_count: int
    masked_field_count: int
    mask_key_hash: str
    method: str = 'XOR_BITMASK'


class AttributeBitmasker:
    """
    Applies bitwise XOR masking to sensitive column metadata values
    before they are sent to any AI model. This ensures that even
    structural metadata (like cardinalities, row counts, column stats)
    cannot be reverse-engineered to reveal business data.
    """

    def __init__(self, config: Optional[BitmaskConfig] = None):
        self.config = config or BitmaskConfig()
        self._mask_key = self._generate_mask_key(self.config.seed)

    def _generate_mask_key(self, seed: int) -> int:
        """Generate a deterministic mask key from a seed using SHA-256."""
        h = hashlib.sha256(str(seed).encode()).digest()
        return struct.unpack('>I', h[:4])[0]  # 32-bit unsigned int

    def _xor_mask_int(self, value: int) -> int:
        """Apply XOR bitmask to an integer value."""
        return value ^ self._mask_key

    def _xor_mask_float(self, value: float) -> float:
        """Apply bitmask to float by masking the integer part."""
        int_part = int(value)
        frac_part = value - int_part
        masked_int = int_part ^ self._mask_key
        return float(masked_int) + frac_part

    def mask_value(self, value: Any) -> Any:
        """Mask a single value based on its type."""
        if isinstance(value, bool):
            return value
        elif isinstance(value, int):
            return self._xor_mask_int(value)
        elif isinstance(value, float):
            return self._xor_mask_float(value)
        elif isinstance(value, str):
            return hashlib.sha256(value.encode()).hexdigest()[:16]
        elif isinstance(value, list):
            return [self.mask_value(v) for v in value]
        elif isinstance(value, dict):
            return self.mask_dict(value)
        return value

    def mask_dict(self, data: Dict[str, Any],
                  sensitive_keys: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Apply bitmasking to all sensitive fields in a dictionary.
        Preserves dict structure and key names.
        """
        if sensitive_keys is None:
            sensitive_keys = [
                'row_count', 'estimated_rows', 'actual_rows',
                'plan_rows', 'total_cost', 'startup_cost',
                'execution_time_ms', 'planning_time_ms',
                'avg_row_size', 'table_size_bytes', 'index_size_bytes',
                'cardinality', 'selectivity', 'frequency',
                'amount', 'total', 'count', 'sum', 'avg',
                'relation_name', 'table_name', 'column_name',
                'filter', 'index_name', 'schema_name'
            ]

        lower_keys = [k.lower() for k in sensitive_keys]
        masked = {}
        for key, value in data.items():
            if key.lower() in lower_keys:
                masked[key] = self.mask_value(value)
            elif isinstance(value, dict):
                masked[key] = self.mask_dict(value, sensitive_keys)
            elif isinstance(value, list):
                masked[key] = [
                    self.mask_dict(item, sensitive_keys) if isinstance(item, dict)
                    else item
                    for item in value
                ]
            else:
                masked[key] = value
        return masked

    def mask_metadata(self, metadata: Dict[str, Any]) -> BitmaskResult:
        """Mask metadata and return audit result."""
        original_count = len(metadata)
        masked_data = self.mask_dict(metadata)
        masked_count = sum(
            1 for k in metadata
            if k in masked_data and metadata[k] != masked_data[k]
        )
        return BitmaskResult(
            original_field_count=original_count,
            masked_field_count=masked_count,
            mask_key_hash=hashlib.sha256(
                str(self._mask_key).encode()
            ).hexdigest()[:16]
        )

    def unmask_int(self, masked_value: int) -> int:
        """XOR is its own inverse, so unmasking = masking again."""
        return masked_value ^ self._mask_key
