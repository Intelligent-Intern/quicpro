"""
Variable-Length Integer Encoding/Decoding for QPACK

This module provides functions to encode and decode integers using
the QPACK/HPACK variable-length integer encoding scheme.
"""

def encode_integer(value: int, prefix_bits: int) -> bytes:
    """
    Encode an integer using QPACK's variable-length integer encoding.
    
    Args:
        value (int): The integer to encode.
        prefix_bits (int): The number of bits available in the first byte.
        
    Returns:
        bytes: The encoded integer.
    
    Raises:
        ValueError: If the value is negative.
    """
    if value < 0:
        raise ValueError("Cannot encode a negative integer.")
    prefix_max = (1 << prefix_bits) - 1
    if value < prefix_max:
        return bytes([value])
    result = bytearray([prefix_max])
    value -= prefix_max
    while value >= 128:
        result.append((value % 128) + 128)
        value //= 128
    result.append(value)
    return bytes(result)

def decode_integer(data: bytes, prefix_bits: int) -> (int, int):
    """
    Decode an integer from the given data using QPACK's variable-length integer encoding.
    
    Args:
        data (bytes): The bytes containing the encoded integer.
        prefix_bits (int): The number of bits in the first byte reserved for the integer value.
        
    Returns:
        A tuple (value, bytes_consumed) where:
          - value (int): The decoded integer.
          - bytes_consumed (int): The number of bytes that were consumed during decoding.
        
    Raises:
        ValueError: If the data is insufficient to decode the integer.
    """
    if not data:
        raise ValueError("Insufficient data to decode integer")
    
    prefix_max = (1 << prefix_bits) - 1
    first_byte = data[0]
    value = first_byte & prefix_max
    if value < prefix_max:
        return value, 1

    m = 0
    index = 1
    while True:
        if index >= len(data):
            raise ValueError("Insufficient data while decoding integer")
        byte = data[index]
        index += 1
        value += (byte & 0x7F) << m
        m += 7
        if (byte & 0x80) == 0:
            break

    return value, index
