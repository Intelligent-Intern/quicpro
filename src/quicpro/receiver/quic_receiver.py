"""
QUIC Receiver Module

This module defines the QUICReceiver class that reassembles incoming QUIC packets,
extracts the encapsulated HTTP/3 frame, and routes it to an HTTP3Receiver for further
processing. It integrates seamlessly with the HTTP/3 pipeline including QPACK-based
header decoding and stream demultiplexing.
"""

import logging
from typing import Any

from quicpro.exceptions.quic_frame_reassembly_error import QUICFrameReassemblyError
from quicpro.utils.quic.packet.decoder import decode_quic_packet

logger = logging.getLogger(__name__)


class QUICReceiver:
    """
    Receives and reassembles QUIC packets, delegating the extracted HTTP/3 frame
    to an HTTP3Receiver instance.
    """

    def __init__(self, http3_receiver: Any) -> None:
        """
        Initialize the QUICReceiver.

        Args:
            http3_receiver (Any): An instance of HTTP3Receiver that processes
                                  the HTTP/3 stream frame.
        """
        self.http3_receiver = http3_receiver

    def receive(self, quic_packet: bytes) -> None:
        """
        Decode an incoming QUIC packet and forward the extracted HTTP/3 frame.

        The packet is decoded using a standard format (header marker, length,
        checksum, and payload). If decoding fails or the frame is invalid,
        a QUICFrameReassemblyError is raised.

        Args:
            quic_packet (bytes): The raw QUIC packet to process.

        Raises:
            QUICFrameReassemblyError: If the packet cannot be reassembled.
        """
        try:
            stream_frame = decode_quic_packet(quic_packet)
            logger.info(
                "QUICReceiver extracted stream frame of length %d",
                len(stream_frame)
            )
            self.http3_receiver.receive(stream_frame)
        except Exception as e:
            logger.exception("QUICReceiver failed to process packet: %s", e)
            raise QUICFrameReassemblyError(
                f"Error reassembling QUIC packet: {e}"
            ) from e

    def close(self) -> None:
        """
        Clean up resources when the QUICReceiver is no longer needed.
        """
        logger.info("QUICReceiver has been closed.")

