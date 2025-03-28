"""
QPACK Huffman Decoder for HTTP/3.

This module implements Huffman decoding using a decoding tree built from the static Huffman table.
It also validates that any leftover bits in the final byte are all ones (as required by the RFC).
"""

from typing import Dict, Any, List
from .constants import HUFFMAN_TABLE


def build_decoding_tree() -> Dict[int, Any]:
    """
    Build a binary decoding tree from the Huffman table.
    Returns:
        A nested dictionary representing the decoding tree.
    """
    root: Dict[int, Any] = {}
    for symbol in range(256):
        code, nbits = HUFFMAN_TABLE[symbol]
        current = root
        for i in range(nbits - 1, -1, -1):
            bit = (code >> i) & 1
            if bit not in current:
                current[bit] = {}
            current = current[bit]
        current["symbol"] = symbol
    return root


_DECODING_TREE = build_decoding_tree()


def decode(data: bytes) -> str:
    """
    Decode Huffman encoded bytes using the decoding tree.

    This implementation first creates a complete bitstring from the input data,
    then processes bits one-by-one. It also tracks the position of the last complete symbol.
    Any leftover bits (the padding) are verified to consist entirely of ones.

    Args:
        data (bytes): The Huffman encoded data.

    Returns:
        str: The decoded string.

    Raises:
        ValueError: If the encoding is invalid or padding is incorrect.
    """
    # Create a bit string from the bytes.
    bit_str = "".join(f"{byte:08b}" for byte in data)
    n = len(bit_str)
    ptr = 0
    result_chars: List[str] = []
    node = _DECODING_TREE
    last_complete_ptr = 0

    while ptr < n:
        bit = int(bit_str[ptr])
        ptr += 1
        if bit not in node:
            raise ValueError(
                f"Invalid Huffman encoding; no branch for bit at position {ptr}.")
        node = node[bit]
        if "symbol" in node:
            result_chars.append(chr(node["symbol"]))
            node = _DECODING_TREE
            last_complete_ptr = ptr

    # If the final symbol was not completed exactly at the end, verify that the leftover bits are all ones.
    if ptr != last_complete_ptr:
        leftover = bit_str[last_complete_ptr:ptr]
        if any(bit != '1' for bit in leftover):
            raise ValueError(
                f"Invalid Huffman padding bits; expected all ones, got {leftover}.")
    return "".join(result_chars)

