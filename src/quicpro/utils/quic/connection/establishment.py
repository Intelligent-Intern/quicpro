"""
Connection establishment module.
Implements a basic handshake procedure for QUIC.
"""

import logging

logger = logging.getLogger(__name__)


def perform_handshake(connection, _client_initial_data: bytes) -> bool:
    """
    Perform handshake to establish a QUIC connection.
    """
    logger.info("Performing handshake for connection %s", connection.connection_id)
    connection.open()
    return True
