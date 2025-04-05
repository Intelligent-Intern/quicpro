"""
Cancel Frame Module for HTTP/3

This module implements a production-ready CANCEL frame encoder.
According to our production HTTP/3 frame format, the CANCEL frame is defined with a specific type identifier,
a 2-byte length header, and a payload that contains the stream ID being cancelled.
It is expected that the connection or stream manager will use this frame to perform the actual cancellation.
"""

import struct
import logging

logger = logging.getLogger(__name__)

# Define the CANCEL frame type constant (example value; must conform to production spec)
FRAME_TYPE_CANCEL = 0x07  # Production-defined CANCEL frame type

def handle_cancel_frame(stream_id: int) -> bytes:
    """
    Construct and return a CANCEL frame for the specified stream ID.
    
    The frame format is as follows:
      - 1 byte: Frame type (FRAME_TYPE_CANCEL)
      - 2 bytes: Payload length (big endian)
      - Payload: 4-byte big-endian encoded stream_id
    
    Args:
        stream_id (int): Identifier of the stream to cancel.
    
    Returns:
        bytes: The fully encoded CANCEL frame.
    
    Raises:
        ValueError: If stream_id is not a positive integer.
    """
    if not isinstance(stream_id, int) or stream_id <= 0:
        logger.error("Invalid stream_id provided for CANCEL frame: %s", stream_id)
        raise ValueError("stream_id must be a positive integer.")
    
    # Encode the payload - we use 4 bytes for stream_id
    payload = struct.pack("!I", stream_id)
    payload_length = len(payload)
    
    # Build frame header: 1-byte frame type and 2-byte payload length.
    frame_header = struct.pack("!BH", FRAME_TYPE_CANCEL, payload_length)
    frame = frame_header + payload
    
    logger.info("Constructed CANCEL frame for stream %d: %s", stream_id, frame.hex())
    return frame
