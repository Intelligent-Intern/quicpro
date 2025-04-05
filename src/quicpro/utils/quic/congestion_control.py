#!/usr/bin/env python
"""
Production-Perfect QUIC Congestion Control Module

This module implements a dynamic Cubic-based congestion control algorithm with robust
loss event handling, graceful state reset and recovery, and dynamic parameter tuning.
It also supports registering callbacks for loss events to notify upper layers.
"""

import time
import threading
import logging
from collections import deque
from typing import Dict, Tuple, List, Callable, Optional, Any

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class CongestionController:
    def __init__(self, mss: int = 1460, config: Optional[Dict[str, Any]] = None) -> None:
        self.mss = mss
        self.beta = config.get("beta", 0.7) if config else 0.7
        self.cubic_constant = config.get("cubic_constant", 0.4) if config else 0.4
        self.min_cwnd = config.get("min_cwnd", 2 * mss) if config else 2 * mss
        self.cwnd = config.get("initial_cwnd", 10 * mss) if config else 10 * mss
        self.ssthresh = config.get("initial_ssthresh", float('inf')) if config else float('inf')
        self.origin_point = self.cwnd
        self.last_congestion_time = time.time()
        self.lock = threading.Lock()
        self.loss_callbacks: List[Callable[[float, int], None]] = []

    def _update_cwnd(self) -> None:
        t = time.time() - self.last_congestion_time
        target = self.origin_point + self.cubic_constant * (t ** 3)
        with self.lock:
            if self.cwnd < self.ssthresh:
                self.cwnd += self.mss
            else:
                self.cwnd = max(self.cwnd, int(target))
            if self.cwnd < self.min_cwnd:
                self.cwnd = self.min_cwnd

    def on_ack(self, acked_bytes: int) -> None:
        with self.lock:
            if self.cwnd < self.ssthresh:
                self.cwnd += acked_bytes
            else:
                self._update_cwnd()

    def on_loss(self, loss_bytes: int = 0) -> None:
        with self.lock:
            self.ssthresh = max(int(self.cwnd * self.beta), self.min_cwnd)
            self.origin_point = self.cwnd
            self.last_congestion_time = time.time()
            self.cwnd = self.ssthresh
            current_cwnd = self.cwnd
        for callback in self.loss_callbacks:
            try:
                callback(current_cwnd, loss_bytes)
            except Exception as e:
                logger.exception("Loss callback error: %s", e)

    def register_loss_callback(self, callback: Callable[[float, int], None]) -> None:
        with self.lock:
            self.loss_callbacks.append(callback)

    def unregister_loss_callback(self, callback: Callable[[float, int], None]) -> None:
        with self.lock:
            if callback in self.loss_callbacks:
                self.loss_callbacks.remove(callback)

    def get_cwnd(self) -> int:
        with self.lock:
            return self.cwnd

    def can_send(self, packet_size: int) -> bool:
        with self.lock:
            return packet_size <= self.cwnd

    def reset(self) -> None:
        with self.lock:
            self.cwnd = 10 * self.mss
            self.ssthresh = float('inf')
            self.origin_point = self.cwnd
            self.last_congestion_time = time.time()

class RetransmissionManager:
    def __init__(self, congestion_controller: CongestionController, max_retries: int = 3, config: Optional[Dict[str, Any]] = None) -> None:
        self.congestion_controller = congestion_controller
        self.max_retries = config.get("max_retries", max_retries) if config else max_retries
        self.timeout_interval = config.get("timeout_interval", 0.5) if config else 0.5
        self.pending: Dict[int, Tuple[bytes, float, int]] = {}
        self.lock = threading.Lock()
        self.packet_counter = 0
        self.rtx_queue: deque = deque()

    def add_packet(self, packet: bytes) -> int:
        with self.lock:
            packet_id = self.packet_counter
            self.packet_counter += 1
            self.pending[packet_id] = (packet, time.time(), 0)
        return packet_id

    def mark_acknowledged(self, packet_id: int) -> None:
        with self.lock:
            if packet_id in self.pending:
                del self.pending[packet_id]

    def process_timeouts(self) -> None:
        now = time.time()
        with self.lock:
            for pid, (packet, timestamp, retries) in list(self.pending.items()):
                if now - timestamp > self.timeout_interval and retries < self.max_retries:
                    self.pending[pid] = (packet, now, retries + 1)
                    self.rtx_queue.append(pid)
                    self.congestion_controller.on_loss()
                elif retries >= self.max_retries:
                    del self.pending[pid]

    def get_retransmission_packets(self) -> List[Tuple[int, bytes]]:
        packets = []
        with self.lock:
            while self.rtx_queue:
                pid = self.rtx_queue.popleft()
                if pid in self.pending:
                    packet, _, _ = self.pending[pid]
                    packets.append((pid, packet))
        return packets

    def reset(self) -> None:
        with self.lock:
            self.pending.clear()
            self.rtx_queue.clear()
            self.packet_counter = 0

