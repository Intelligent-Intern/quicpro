"""
This package implements QPACK/HPACK Huffman encoding and decoding.
It exports the encoder and decoder functions.
"""

from .encoder import encode as huffman_encode
from .decoder import decode as huffman_decode