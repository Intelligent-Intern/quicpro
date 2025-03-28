"""
retransmission.py - Handles scheduling and managing retransmission of lost QUIC packets.

This module defines a RetransmissionManager class that maintains a mapping of
packet IDs to (packet, retry_count) tuples, and provides methods to add packets,
mark them as acknowledged, and retrieve packets for retransmission.
"""


class RetransmissionManager:
    """
    Manages retransmission for lost QUIC packets.
    """

    def __init__(self) -> None:
        """Initialize an empty retransmission queue."""
        self.pending_packets = {
        }  # Mapping: packet_id -> (packet, retry_count)

    def add_packet(self, packet_id: int, packet: bytes) -> None:
        """
        Add a packet to the retransmission queue.

        Args:
            packet_id (int): Unique identifier for the packet.
            packet (bytes): The QUIC packet data.
        """
        self.pending_packets[packet_id] = (packet, 0)

    def mark_packet_acked(self, packet_id: int) -> None:
        """
        Remove a packet from the retransmission queue upon acknowledgment.

        Args:
            packet_id (int): Unique identifier for the packet.
        """
        if packet_id in self.pending_packets:
            del self.pending_packets[packet_id]

    def get_packets_for_retransmission(self, max_retries: int = 3) -> list:
        """
        Retrieve packets that need retransmission.

        Args:
            max_retries (int): Maximum number of retry attempts before giving up.

        Returns:
            list: List of packets (bytes) to retransmit.
        """
        to_retransmit = []
        for packet_id, (packet, retry_count) in list(self.pending_packets.items()):
            if retry_count < max_retries:
                self.pending_packets[packet_id] = (packet, retry_count + 1)
                to_retransmit.append(packet)
            else:
                del self.pending_packets[packet_id]
        return to_retransmit
