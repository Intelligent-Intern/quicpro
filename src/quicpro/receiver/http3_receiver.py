"""
HTTP3 Receiver Module

This module implements an HTTP3Receiver that extracts, decodes, and validates
HTTP/3 frames from incoming QUIC packets. It uses QPACK to decode header blocks
and then passes the fully decoded message (headers and body) to a downstream
decoder.
"""

import logging
from typing import Any, Tuple, Dict

from quicpro.exceptions import HTTP3FrameError
from quicpro.utils.http3.qpack.decoder import QPACKDecoder

logger = logging.getLogger(__name__)


class HTTP3Receiver:
    """
    Extracts, decodes, and validates HTTP/3 frames from incoming QUIC packets.

    This receiver uses a QPACKDecoder to decode the header block present in the
    frame. The resulting headers and the remaining payload (body) are then passed
    to the downstream decoder.
    """
    def __init__(self, decoder: Any) -> None:
        """
        Initialize the HTTP3Receiver.

        Args:
            decoder (Any): An instance providing a decode(headers: Dict[str, str], 
                           body: bytes) method to process the fully decoded HTTP/3 message.
        """
        self.decoder = decoder
        self.qpack_decoder = QPACKDecoder()

    def receive(self, quic_packet: bytes) -> None:
        """
        Extract, decode, and validate an HTTP/3 frame from a QUIC packet, and then
        forward the decoded message to the downstream decoder.

        Args:
            quic_packet (bytes): The raw QUIC packet containing an HTTP/3 frame.

        Raises:
            HTTP3FrameError: If frame extraction, decoding, or validation fails.
        """
        try:
            logger.debug("HTTP3Receiver received packet of length %d", len(quic_packet))
            frame = self._extract_http3_frame(quic_packet)
            if not self._validate_frame(frame):
                raise HTTP3FrameError("Extracted HTTP/3 frame failed validation.")
            headers, body = self._decode_frame(frame)
            logger.info("HTTP3Receiver successfully decoded frame", extra={"headers": headers})
            self.decoder.decode(headers, body)
        except Exception as exc:
            logger.exception(
                "HTTP3Receiver processing failed",
                exc_info=exc,
                extra={"quic_packet": quic_packet}
            )
            raise

    def _extract_http3_frame(self, packet: bytes) -> bytes:
        """
        Extract the HTTP/3 frame from the QUIC packet.

        This method assumes that the entire decrypted packet is the HTTP/3 frame.
        In a production system, further extraction logic might be required.

        Args:
            packet (bytes): The decrypted QUIC packet.

        Returns:
            bytes: The extracted HTTP/3 frame payload.

        Raises:
            HTTP3FrameError: If the packet is empty.
        """
        if not packet:
            raise HTTP3FrameError("Received empty packet.")
        return packet

    def _validate_frame(self, frame: bytes) -> bool:
        """
        Validate the extracted HTTP/3 frame.

        Args:
            frame (bytes): The extracted frame payload.

        Returns:
            bool: True if the frame is valid, False otherwise.
        """
        if len(frame) < 1:
            logger.error("Extracted frame is too short.", extra={"frame_length": len(frame)})
            return False
        return True

    def _decode_frame(self, frame: bytes) -> Tuple[Dict[str, str], bytes]:
        """
        Decode the HTTP/3 frame using QPACK.

        The frame is assumed to start with a 2-byte big-endian integer representing
        the length of the QPACK-encoded header block, followed by the header block
        and then the body.

        Args:
            frame (bytes): The HTTP/3 frame payload.

        Returns:
            Tuple[Dict[str, str], bytes]: A tuple containing the decoded headers and
                                          the body as raw bytes.

        Raises:
            HTTP3FrameError: If the header block length is invalid or the frame is incomplete.
        """
        if len(frame) < 2:
            raise HTTP3FrameError("Frame too short to contain header block length.")
        header_length = int.from_bytes(frame[:2], byteorder="big")
        if len(frame) < 2 + header_length:
            raise HTTP3FrameError("Frame does not contain full header block.")
        header_block = frame[2:2 + header_length]
        body = frame[2 + header_length:]
        headers = self.qpack_decoder.decode(header_block)
        return headers, body
