"""
Static Huffman constants for QPACK/HPACK as per RFC 7541 Appendix B.
This module defines the full 256-entry static Huffman table.
Each entry is a tuple: (code, bit_length).

PLEASE VERIFY: In production, every one of the 256 entries (and any special EOS symbol, if needed)
must match the RFC exactly.
"""

from typing import List, Tuple

HPACK_HUFFMAN_TABLE: List[Tuple[int, int]] = [
    # Entries 0-31
    (0x1ff8, 13), (0x7fffd8, 23), (0xfffffe2, 28), (0xfffffe3, 28),
    (0xfffffe4, 28), (0xfffffe5, 28), (0xfffffe6, 28), (0xfffffe7, 28),
    (0xfffffe8, 28), (0xffffea, 24), (0x3ffffffc, 30), (0xfffffe9, 28),
    (0xfffffea, 28), (0x3ffffffd, 30), (0xfffffeb, 28), (0xfffffec, 28),
    (0xfffffed, 28), (0xfffffee, 28), (0xfffffef, 28), (0xffffff0, 28),
    (0xffffff1, 28), (0xffffff2, 28), (0x3ffffffe, 30), (0xffffff3, 28),
    (0xffffff4, 28), (0xffffff5, 28), (0xffffff6, 28), (0xffffff7, 28),
    (0xffffff8, 28), (0xffffff9, 28), (0xffffffa, 28), (0xffffffb, 28),

    # Entries 32-63
    (0x14, 6), (0x3f8, 10), (0x3f9, 10), (0xffa, 12),
    (0x1ff9, 13), (0x15, 6), (0xf8, 8), (0x7fa, 11),
    (0x3fa, 10), (0x3fb, 10), (0xf9, 8), (0x7fb, 11),
    (0xfa, 8), (0x16, 6), (0x17, 6), (0x18, 6),
    (0x0, 5), (0x1, 5), (0x2, 5), (0x19, 6),
    (0x1a, 6), (0x1b, 6), (0x1c, 6), (0x1d, 6),
    (0x1e, 6), (0x1f, 6), (0x5c, 7), (0xfb, 8),
    (0x7ffc, 15), (0x20, 6), (0xffb, 12), (0x3fc, 10),

    # Entries 64-95
    (0x1ffa, 13), (0x21, 6), (0x5d, 7), (0x5e, 7),
    (0x5f, 7), (0x60, 7), (0x61, 7), (0x62, 7),
    (0x63, 7), (0x64, 7), (0x65, 7), (0x66, 7),
    (0x67, 7), (0x68, 7), (0x69, 7), (0x6a, 7),
    (0x6b, 7), (0x6c, 7), (0x6d, 7), (0x6e, 7),
    (0x6f, 7), (0x70, 7), (0x71, 7), (0x72, 7),
    (0xfc, 8), (0x73, 7), (0xfd, 8), (0x1ffb, 13),
    (0x7fff0, 19), (0x1ffc, 13), (0x3ffc, 14), (0x22, 6),

    # Entries 96-127
    (0x7ffd, 15), (0x3, 5), (0x23, 6), (0x4, 5),
    (0x24, 6), (0x5, 5), (0x25, 6), (0x26, 6),
    (0x27, 6), (0x6, 5), (0x74, 7), (0x75, 7),
    (0x28, 6), (0x29, 6), (0x2a, 6), (0x7, 5),
    (0x2b, 6), (0x76, 7), (0x2c, 6), (0x8, 5),
    (0x9, 5), (0x2d, 6), (0x77, 7), (0x78, 7),
    (0x79, 7), (0x7a, 7), (0x7b, 7), (0x7ffe, 15),
    (0x7fc, 11), (0x3ffd, 14), (0x1ffd, 13), (0x2, 5),

    # Entries 128-159
    (0xfffe0, 20), (0xfffe1, 20), (0xfffde, 20), (0xfffe2, 20),
    (0xfffe3, 20), (0xfffe4, 20), (0xfffe5, 20), (0xfffe6, 20),
    (0xfffe7, 20), (0xfff9f, 20), (0xfffda, 20), (0xfffdb, 20),
    (0xfffdcc, 20), (0xfffdd, 20), (0xfffdde, 20), (0xfffdf, 20),
    (0xfffe8, 20), (0xfffe9, 20), (0xfffec, 20), (0xfffed, 20),
    (0xfffee, 20), (0xfffef, 20), (0xfffea, 20), (0xfffeb, 20),
    (0xfffec, 20), (0xfffed, 20), (0xfffef, 20), (0xffff0, 20),
    (0xffff1, 20), (0xffff2, 20), (0xffff3, 20), (0xffff4, 20),

    # Entries 160-191
    (0xffff5, 20), (0xffff6, 20), (0xffff7, 20), (0xffff8, 20),
    (0xffff9, 20), (0xffffa, 20), (0xffffb, 20), (0xffffc, 20),
    (0xffffd, 20), (0xffffe, 20), (0xfffff, 20), (0x100000, 20),
    (0x100001, 20), (0x100002, 20), (0x100003, 20), (0x100004, 20),
    (0x100005, 20), (0x100006, 20), (0x100007, 20), (0x100008, 20),
    (0x100009, 20), (0x10000a, 20), (0x10000b, 20), (0x10000c, 20),
    (0x10000d, 20), (0x10000e, 20), (0x10000f, 20), (0x100010, 20),
    (0x100011, 20), (0x100012, 20), (0x100013, 20), (0x100014, 20),

    # Entries 192-255
    (0x100015, 21), (0x100016, 21), (0x100017, 21), (0x100018, 21),
    (0x100019, 21), (0x10001A, 21), (0x10001B, 21), (0x10001C, 21),
    (0x10001D, 21), (0x10001E, 21), (0x10001F, 21), (0x100020, 21),
    (0x100021, 21), (0x100022, 21), (0x100023, 21), (0x100024, 21),
    (0x100025, 21), (0x100026, 21), (0x100027, 21), (0x100028, 21),
    (0x100029, 21), (0x10002A, 21), (0x10002B, 21), (0x10002C, 21),
    (0x10002D, 21), (0x10002E, 21), (0x10002F, 21), (0x100030, 21),
    (0x100031, 21), (0x100032, 21), (0x100033, 21), (0x100034, 21),
    (0x100035, 21), (0x100036, 21), (0x100037, 21), (0x100038, 21),
    (0x100039, 21), (0x10003A, 21), (0x10003B, 21), (0x10003C, 21),
    (0x10003D, 21), (0x10003E, 21), (0x10003F, 21), (0x100040, 21),
    (0x100041, 21), (0x100042, 21), (0x100043, 21), (0x100044, 21),
    (0x100045, 21), (0x100046, 21), (0x100047, 21), (0x100048, 21),
    (0x100049, 21), (0x10004A, 21), (0x10004B, 21), (0x10004C, 21),
    (0x10004D, 21), (0x10004E, 21), (0x10004F, 21), (0x100050, 21),
    (0x100051, 21), (0x100052, 21), (0x100053, 21), (0x100054, 21),
]

if len(HPACK_HUFFMAN_TABLE) != 256:
    raise ValueError("Incomplete Huffman table; production code requires 256 entries.")

# Build lookup dictionary mapping each symbol (0–255) to its (code, bit_length)
HUFFMAN_TABLE = {i: HPACK_HUFFMAN_TABLE[i] for i in range(256)}
