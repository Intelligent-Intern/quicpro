"""
migration.py - Supports connection migration for QUIC.

Handles updating connection state when migrating across network paths.
"""

import logging

logger = logging.getLogger(__name__)


def migrate_connection(connection, new_peer_address: tuple) -> None:
    """
    Update the connection with a new peer address.

    Args:
        connection: An instance of Connection.
        new_peer_address (tuple): The new network address.
    """
    logger.info("Migrating connection %s to new address %s",
                connection.connection_id, new_peer_address)
    connection.peer_address = new_peer_address
