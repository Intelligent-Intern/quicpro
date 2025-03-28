"""
negotiation.py - Implements QUIC version negotiation.

This module defines a function to negotiate a common protocol version between
a local endpoint and a peer.
"""


def negotiate_version(local_version: str, peer_versions: list) -> str:
    """
    Negotiate the protocol version based on local and peer supported versions.

    Args:
        local_version (str): Local supported version.
        peer_versions (list): Versions supported by the peer.

    Returns:
        str: The agreed version.

    Raises:
        ValueError: If no common version is found.
    """
    if local_version in peer_versions:
        return local_version
    common = set(peer_versions)
    if common:
        return sorted(common)[0]
    raise ValueError("No common QUIC version found.")
