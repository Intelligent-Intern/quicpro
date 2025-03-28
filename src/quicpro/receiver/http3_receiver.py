"""
HTTP3 Receiver module.
This module implements an HTTP3Receiver that extracts, validates, and processes HTTP/3 frames
from incoming QUIC packets, passing the decoded content to a downstream decoder.
"""

import logging
from typing import Any

from quicpro.exceptions import HTTP3FrameError

logger = logging.getLogger(__name__)


class HTTP3Receiver:
    """
    Extracts and validates HTTP/3 frames from incoming QUIC packets,
    and passes the decoded content to the downstream decoder.
    """
    def __init__(self, decoder: Any) -> None:
        """
        Args:
          decoder: An instance with a decode(frame: bytes) method.
        """
        self.decoder = decoder

    def receive(self, quic_packet: bytes) -> None:
        """
        Extract and validate the HTTP/3 frame from quic_packet, then pass it to the decoder.
        Raises:
          HTTP3FrameError: if extraction or validation fails.
        """
        try:
            logger.debug("HTTP3Receiver received packet", extra={"packet_length": len(quic_packet)})
            frame = self._extract_http3_frame(quic_packet)
            if not self._validate_frame(frame):
                raise HTTP3FrameError("Extracted HTTP/3 frame failed validation.")
            logger.info("HTTP3Receiver successfully extracted frame", extra={"frame": frame})
            self.decoder.decode(frame)
        except Exception as exc:
            logger.exception("HTTP3Receiver processing failed", exc_info=exc, extra={"quic_packet": quic_packet})
            raise

    def _extract_http3_frame(self, packet: bytes) -> bytes:
        """
        Extract the HTTP/3 frame from the QUIC packet.
        Returns:
          bytes: The extracted frame payload.
        Raises:
          HTTP3FrameError: if extraction yields an empty payload.
        """
        prefix = b'HTTP3:'
        suffix = b'\n'
        start = packet.find(prefix)
        if start == -1:
            logger.warning("HTTP3 frame prefix not found; using full packet as payload.")
            frame = packet.strip()
            if not frame:
                raise HTTP3FrameError("Fallback extraction failed: packet is empty.")
            return frame
        start += len(prefix)
        end = packet.find(suffix, start)
        if end == -1:
            end = len(packet)
        frame = packet[start:end].strip()
        if not frame:
            raise HTTP3FrameError("HTTP/3 frame payload is empty after extraction.")
        return frame

    def _validate_frame(self, frame: bytes) -> bool:
        """
        Validate the extracted HTTP/3 frame.
        Returns:
          bool: True if valid, False otherwise.
        """
        min_frame_length = 1
        if len(frame) < min_frame_length:
            logger.error("Extracted frame is too short.", extra={"frame_length": len(frame)})
            return False
        return True
