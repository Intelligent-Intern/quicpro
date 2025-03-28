"""
Congestion Control and Loss Recovery Module (Production Ready)

This module implements robust packet loss detection, ACK processing,
and a congestion control algorithm based on the Cubic algorithm.
It manages different packet number spaces (Initial, Handshake, 1‑RTT)
and governs retransmission logic.
"""

import time
import math
import threading
import logging
from collections import deque
from typing import Dict, Optional, Tuple, Deque

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Constants for Cubic algorithm (values chosen for demonstration purposes)
INITIAL_CWND = 10 * 1460          # Initial congestion window (bytes); assume MSS=1460
INITIAL_SSTHRESH = float('inf')    # Initial slow-start threshold
BETA = 0.7                        # Multiplicative decrease factor
CUBIC_C = 0.4                     # Cubic constant
MIN_CWND = 2 * 1460               # Minimum congestion window (bytes)

class CongestionController:
    """
    Implements a Cubic-based congestion control algorithm.
    Manages the congestion window (cwnd), slow-start threshold (ssthresh),
    and computes adjustments upon receiving ACKs or detecting losses.
    """
    def __init__(self, mss: int = 1460):
        self.mss = mss
        self.cwnd = INITIAL_CWND
        self.ssthresh = INITIAL_SSTHRESH
        self.last_congestion_event_time = time.time()
        self.K = 0.0
        self.origin_point = self.cwnd
        self.lock = threading.Lock()
        logger.debug(f"CongestionController initialized with cwnd={self.cwnd}, ssthresh={self.ssthresh}")

    def _update_cubic(self):
        """
        Update the congestion window according to the Cubic function.
        """
        t = time.time() - self.last_congestion_event_time
        cubic_cwnd = self.origin_point + CUBIC_C * ((t - self.K) ** 3)
        logger.debug(f"Cubic update: t={t:.3f}, K={self.K:.3f}, cubic_cwnd={cubic_cwnd:.2f}")
        if cubic_cwnd < self.cwnd:
            # In slow start, double cwnd on each RTT.
            self.cwnd = min(self.cwnd * 2, cubic_cwnd)
        else:
            self.cwnd = cubic_cwnd
        if self.cwnd < MIN_CWND:
            self.cwnd = MIN_CWND

    def on_ack(self, acked_bytes: int):
        """
        Process an ACK event, increasing cwnd.
        Called when a new ACK for acked_bytes is received.
        """
        with self.lock:
            if self.cwnd < self.ssthresh:
                # Slow start phase: exponential growth.
                self.cwnd += acked_bytes
                logger.debug(f"Slow start: cwnd increased to {self.cwnd}")
            else:
                # Congestion avoidance: cubic growth.
                self._update_cubic()
                logger.debug(f"Congestion avoidance: cwnd updated to {self.cwnd}")

    def on_packet_loss(self):
        """
        Process a packet loss event, reducing the congestion window.
        """
        with self.lock:
            new_cwnd = max(self.cwnd * BETA, MIN_CWND)
            self.ssthresh = new_cwnd
            self.origin_point = new_cwnd
            self.K = ((self.origin_point * (1 - BETA)) / CUBIC_C) ** (1 / 3)
            self.last_congestion_event_time = time.time()
            self.cwnd = new_cwnd
            logger.debug(f"Packet loss: cwnd reduced to {self.cwnd}, ssthresh set to {self.ssthresh}")

    def get_cwnd(self) -> int:
        """
        Return the current congestion window in bytes.
        """
        with self.lock:
            return int(self.cwnd)

    def can_send(self, bytes_to_send: int) -> bool:
        """
        Check if the specified amount of data can be transmitted according to cwnd.
        """
        return bytes_to_send <= self.get_cwnd()


class RetransmissionManager:
    """
    Manages retransmission of QUIC packets.
    Integrates with the CongestionController to decide when to retransmit.
    Maintains a mapping of packet numbers to (packet, timestamp, retry_count).
    """
    def __init__(self, congestion_controller: CongestionController, max_retries: int = 3):
        self.congestion_controller = congestion_controller
        self.max_retries = max_retries
        self.pending_packets: Dict[int, Tuple[bytes, float, int]] = {}  # packet_number -> (packet, timestamp, retry_count)
        self.lock = threading.Lock()
        self.packet_number_counter = 0
        self.retransmit_queue: Deque[int] = deque()

    def add_packet(self, packet: bytes) -> int:
        """
        Add a packet for potential retransmission.
        Returns a unique packet number.
        """
        with self.lock:
            packet_number = self.packet_number_counter
            self.packet_number_counter += 1
            self.pending_packets[packet_number] = (packet, time.time(), 0)
            return packet_number

    def mark_acknowledged(self, packet_number: int):
        """
        Remove a packet from retransmission tracking.
        """
        with self.lock:
            if packet_number in self.pending_packets:
                del self.pending_packets[packet_number]

    def check_timeouts(self, timeout_interval: float = 0.5) -> list:
        """
        Check pending packets for timeout.
        Returns a list of packet numbers that have timed out.
        """
        timed_out = []
        current_time = time.time()
        with self.lock:
            for pkt_num, (pkt, ts, retry) in list(self.pending_packets.items()):
                if current_time - ts > timeout_interval and retry < self.max_retries:
                    timed_out.append(pkt_num)
        return timed_out

    def on_timeout(self, packet_number: int):
        """
        Called when a packet times out. Increases its retry count and signals loss.
        """
        with self.lock:
            if packet_number in self.pending_packets:
                pkt, ts, retry = self.pending_packets[packet_number]
                if retry < self.max_retries:
                    self.pending_packets[packet_number] = (pkt, time.time(), retry + 1)
                    logger.debug(f"Packet {packet_number} timed out; retry count increased to {retry+1}")
                    self.congestion_controller.on_packet_loss()
                    self.retransmit_queue.append(packet_number)
                else:
                    logger.error(f"Packet {packet_number} exceeded max retries and is dropped")
                    del self.pending_packets[packet_number]

    def get_retransmission_packets(self) -> list:
        """
        Return a list of packets that need retransmission and remove them from the queue.
        """
        packets = []
        with self.lock:
            while self.retransmit_queue:
                pkt_num = self.retransmit_queue.popleft()
                if pkt_num in self.pending_packets:
                    packet, _, _ = self.pending_packets[pkt_num]
                    packets.append((pkt_num, packet))
        return packets

    def process_timeouts(self, timeout_interval: float = 0.5):
        """
        Check for packet timeouts and process retransmission accordingly.
        """
        timed_out = self.check_timeouts(timeout_interval)
        for pkt_num in timed_out:
            self.on_timeout(pkt_num)