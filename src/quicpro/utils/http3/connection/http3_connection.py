"""
Module: http3_connection.py

This module defines the HTTP3Connection class that wraps an underlying QUIC connection (via QuicManager)
to provide HTTP/3–specific behavior including settings negotiation and control frame handling.
"""

import logging

from quicpro.utils.quic.manager import QuicManager

logger = logging.getLogger(__name__)


class HTTP3Connection:
    """
    A wrapper to provide HTTP/3-specific functionality on top of a QUIC connection.

    This class is responsible for:
      - Negotiating HTTP/3 settings with the server.
      - Managing control frames (e.g. SETTINGS, GOAWAY) and stream behavior.
      - Facilitating the sending and receiving of HTTP/3 requests and responses.
    """

    def __init__(self, quic_manager: QuicManager) -> None:
        """
        Initialize the HTTP3Connection with an existing QuicManager instance.
        
        Args:
            quic_manager (QuicManager): The underlying QUIC manager handling packet transmission.
        """
        self.quic_manager = quic_manager
        self.settings = {}  # Placeholder for HTTP/3 settings

    def negotiate_settings(self, settings: dict) -> None:
        """
        Negotiate HTTP/3 settings with the server.

        In a complete implementation, this method would send a SETTINGS frame over the QUIC connection,
        wait for a SETTINGS acknowledgment from the server, and update the current settings accordingly.

        Args:
            settings (dict): A dictionary representing the desired HTTP/3 settings.
        """
        # For now, we simply store the settings.
        self.settings = settings
        logger.info("Negotiated HTTP/3 settings: %s", settings)

    def send_request(self, request_data: bytes, stream_id: int = 1) -> None:
        """
        Send an HTTP/3 request encapsulated in a QUIC stream.

        This method wraps the raw request data into an HTTP/3 frame and sends it via the quic_manager.

        Args:
            request_data (bytes): The encoded HTTP/3 request (headers + optional payload).
            stream_id (int): The stream identifier to be used.
        """
        logger.info("Sending HTTP/3 request on stream %d: %s", stream_id, request_data)
        # In a full implementation, the request_data is framed and possibly compressed/decorated.
        # Here, we simply pass it along as the stream frame.
        self.quic_manager.send_stream(stream_id=stream_id, stream_frame=request_data)

    def receive_response(self, packet: bytes) -> None:
        """
        Process a received HTTP/3 response packet.

        This method serves as a hook for processing incoming HTTP/3 frames.
        In a full implementation, it would decode the HTTP/3 frame, possibly decompress headers via QPACK,
        and then update the response state.

        Args:
            packet (bytes): The raw QUIC packet containing the HTTP/3 response frame.
        """
        logger.info("Received HTTP/3 response packet: %s", packet)
        # For demonstration, we forward the packet to the quic_manager's processing.
        self.quic_manager.receive_packet(packet)
