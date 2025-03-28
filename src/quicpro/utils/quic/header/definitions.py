"""
Advanced QUIC Header definitions and constants.

This module defines header types and a default header configuration to be used by
the QUIC header implementation.
"""

HEADER_TYPE_INITIAL = 0x0
HEADER_TYPE_0RTT = 0x1
HEADER_TYPE_HANDSHAKE = 0x2
HEADER_TYPE_RETRY = 0x3

DEFAULT_HEADER = {
    "version": "1",
    "type": HEADER_TYPE_INITIAL,
    "connection_id": "00000000",
    "length": 0,
    "packet_number": 0,
}
