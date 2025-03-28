"""
Module defining the TLS configuration model for QUIC encryption and decryption.

This model uses Pydantic to ensure that the AES-GCM key is exactly 32 bytes and the IV
is exactly 12 bytes.
"""

from pydantic import BaseModel, Field, field_validator

class TLSConfig(BaseModel):
    """
    TLSConfig model that validates and stores the symmetric key and IV for AES-GCM.
    
    Attributes:
        key (bytes): 32-byte (256-bit) symmetric key.
        iv (bytes): 12-byte static IV for nonce derivation.
    """
    key: bytes = Field(
        ...,
        min_length=32,
        max_length=32,
        description="32-byte (256-bit) symmetric key for AES-GCM."
    )
    iv: bytes = Field(
        ...,
        min_length=12,
        max_length=12,
        description="12-byte static IV for nonce derivation."
    )

    @field_validator("key")
    @classmethod
    def validate_key(cls, v: bytes) -> bytes:
        """Validate that the key is exactly 32 bytes."""
        if len(v) != 32:
            raise ValueError("Key must be exactly 32 bytes (256 bits).")
        return v

    @field_validator("iv")
    @classmethod
    def validate_iv(cls, v: bytes) -> bytes:
        """Validate that the IV is exactly 12 bytes."""
        if len(v) != 12:
            raise ValueError("IV must be exactly 12 bytes.")
        return v
