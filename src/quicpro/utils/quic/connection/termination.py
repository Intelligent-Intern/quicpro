"""
termination.py - Handles termination of QUIC connections.

Provides procedures for graceful and abrupt termination of a connection.
"""

import logging

logger = logging.getLogger(__name__)

def terminate_connection(connection, reason: str = "Normal Closure") -> None:
    """
    Terminate the given connection.

    Args:
        connection: An instance of Connection.
        reason (str): The reason for termination.
    """
    logger.info("Terminating connection %s: %s",
                connection.connection_id, reason)
    connection.close()
