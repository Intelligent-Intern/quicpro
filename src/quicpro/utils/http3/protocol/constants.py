"""
Module: constants.py

Defines HTTP/3 protocol constants including frame types and settings identifiers.
"""

# Frame type constants
FRAME_TYPE_DATA             = 0x00
FRAME_TYPE_HEADERS          = 0x01
FRAME_TYPE_PRIORITY         = 0x02
FRAME_TYPE_PUSH_PROMISE     = 0x03
FRAME_TYPE_SETTINGS         = 0x04
FRAME_TYPE_PUSH             = 0x05
FRAME_TYPE_DUPLICATE_PUSH   = 0x06

# HTTP/3 SETTINGS identifiers (example values)
SETTINGS_QPACK_MAX_TABLE_CAPACITY = 0x01
SETTINGS_MAX_HEADER_LIST_SIZE     = 0x06

# Other protocol-specific constants can be defined here.
