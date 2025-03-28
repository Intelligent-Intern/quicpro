"""
Module implementing the QUICReceiver.
This module defines the QUICReceiver class that reassembles incoming QUIC packets
and delegates the HTTP/3 stream frame to an HTTP3Receiver.
"""

import logging
from typing import Any

from quicpro.exceptions import QUICFrameReassemblyError
from quicpro.utils.quic.packet.decoder import decode_quic_packet

logger = logging.getLogger(__name__)


class QUICReceiver:
    """
    Receiver for reassembling QUIC packets and delegating processing to an HTTP3Receiver.
    """
    def __init__(self, http3_receiver: Any) -> None:
        """Initialize with an HTTP3Receiver instance."""
        self.http3_receiver = http3_receiver

    def receive(self, quic_packet: bytes) -> None:
        """
        Decode an incoming QUIC packet and forward the extracted stream frame.
        Raises:
          QUICFrameReassemblyError: if decoding or processing fails.
        """
        try:
            stream_frame = decode_quic_packet(quic_packet)
            self.http3_receiver.receive(stream_frame)
        except Exception as e:
            logger.exception("QUICReceiver failed to process packet: %s", e)
            raise QUICFrameReassemblyError(
                f"Error reassembling QUIC packet: {e}"
            ) from e
