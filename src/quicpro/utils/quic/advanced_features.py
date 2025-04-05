"""
Advanced Features Module for QUIC

This module defines a production-ready configuration model for advanced QUIC features,
including support for different versions, extensions, transport parameters, connection IDs,
stream IDs, stream priorities, stream types, stream states, stream events, stream handlers,
stream listeners, stream filters, stream encoders, stream decoders, stream serializers,
stream deserializers, stream compressors, stream decompressors, stream encryptors,
stream decryptors, stream signers, stream verifiers, and stream authenticators.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict

class QUICAdvancedFeatures(BaseModel):
    quic_version: Optional[str] = Field(None, description="Supported QUIC version")
    quic_extensions: Optional[List[str]] = Field(None, description="List of supported QUIC extensions")
    transport_parameters: Optional[Dict[str, str]] = Field(None, description="QUIC transport parameters")
    connection_id_format: Optional[str] = Field(None, description="Format for QUIC connection IDs")
    stream_id_format: Optional[str] = Field(None, description="Format for QUIC stream IDs")
    stream_priorities: Optional[List[int]] = Field(None, description="Supported QUIC stream priority weights")
    stream_types: Optional[List[str]] = Field(None, description="Supported QUIC stream types")
    stream_states: Optional[List[str]] = Field(None, description="Supported QUIC stream states")
    stream_events: Optional[List[str]] = Field(None, description="Supported QUIC stream events")
    stream_handlers: Optional[List[str]] = Field(None, description="Custom QUIC stream handler identifiers")
    stream_listeners: Optional[List[str]] = Field(None, description="QUIC stream event listeners")
    stream_filters: Optional[List[str]] = Field(None, description="QUIC stream filters")
    stream_encoders: Optional[List[str]] = Field(None, description="Supported QUIC stream encoder algorithms")
    stream_decoders: Optional[List[str]] = Field(None, description="Supported QUIC stream decoder algorithms")
    stream_serializers: Optional[List[str]] = Field(None, description="Supported QUIC stream serializer methods")
    stream_deserializers: Optional[List[str]] = Field(None, description="Supported QUIC stream deserializer methods")
    stream_compressors: Optional[List[str]] = Field(None, description="Supported QUIC stream compression algorithms")
    stream_decompressors: Optional[List[str]] = Field(None, description="Supported QUIC stream decompression algorithms")
    stream_encryptors: Optional[List[str]] = Field(None, description="Supported QUIC stream encryption algorithms")
    stream_decryptors: Optional[List[str]] = Field(None, description="Supported QUIC stream decryption algorithms")
    stream_signers: Optional[List[str]] = Field(None, description="Supported QUIC stream signing algorithms")
    stream_verifiers: Optional[List[str]] = Field(None, description="Supported QUIC stream signature verification methods")
    stream_authenticators: Optional[List[str]] = Field(None, description="Supported QUIC stream authentication methods")

    @validator('quic_version')
    def validate_quic_version(cls, v: Optional[str]) -> Optional[str]:
        allowed = {"v1", "v2", "v3"}
        if v is not None and v not in allowed:
            raise ValueError(f"QUIC version '{v}' is not supported; choose from {allowed}.")
        return v

advanced_features_config: Optional[QUICAdvancedFeatures] = None

def apply_advanced_features(config: dict) -> QUICAdvancedFeatures:
    global advanced_features_config
    advanced_features_config = QUICAdvancedFeatures(**config)
    return advanced_features_config
