"""
Helper functions for TLS modules.
"""

def compute_nonce(iv: bytes, seq_number: int) -> bytes:
    """
    Compute the nonce for AES-GCM by XORing the IV with the sequence number.
    """
    seq_bytes = seq_number.to_bytes(12, byteorder="big")
    return bytes(iv_byte ^ seq_byte for iv_byte, seq_byte in zip(iv, seq_bytes))
