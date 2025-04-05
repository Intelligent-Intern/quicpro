"""
TLS Configuration Model

This module defines the TLSManagerConfig model using Pydantic for dynamic,
runtime configuration of TLS parameters.
"""

from pydantic import BaseModel, Field
from typing import Optional

class TLSManagerConfig(BaseModel):
    version: str = Field(default="TLSv1.3", description="TLS version to use (TLSv1.3 or TLSv1.2)")
    certfile: str = Field(..., description="Path to the certificate file (PEM format)")
    keyfile: str = Field(..., description="Path to the private key file (PEM format)")
    cafile: Optional[str] = Field(None, description="Path to the CA bundle file for certificate validation")
    rotation_interval: float = Field(default=3600.0, description="Interval in seconds between key rotations")
    handshake_timeout: float = Field(default=5.0, description="Timeout in seconds for TLS handshake operations")
    aes_key: bytes = Field(..., description="32-byte AES-GCM symmetric key for data encryption")
    iv: bytes = Field(..., description="12-byte initialization vector for AES-GCM encryption")

    class Config:
        json_encoders = {bytes: lambda v: v.hex()}
