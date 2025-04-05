#!/usr/bin/env python
"""
Production-Perfect QUIC Connection Core

This module defines the Connection class which manages connection state,
packet transmission, and incoming packet processing for QUIC.
"""

import time
import logging
import threading
from typing import List, Optional

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class ConnectionError(Exception):
    pass

class Connection:
    def __init__(self, connection_id: str) -> None:
        self.connection_id = connection_id
        self.is_open = False
        self.sent_packets: List[bytes] = []
        self.received_packets: List[bytes] = []
        self.stream_manager = None
        self._lock = threading.Lock()
        self._cv = threading.Condition(self._lock)
        logger.info("Connection %s initialized", self.connection_id)

    def open(self) -> None:
        with self._lock:
            self.is_open = True
        logger.info("Connection %s opened", self.connection_id)

    def close(self) -> None:
        with self._lock:
            if not self.is_open:
                return
            self.is_open = False
        logger.info("Connection %s closed", self.connection_id)

    def send_packet(self, packet: bytes) -> None:
        if not self.is_open:
            raise ConnectionError(f"Connection {self.connection_id} is not open")
        with self._lock:
            self.sent_packets.append(packet)
        logger.debug("Connection %s sent packet: %s", self.connection_id, packet.hex())

    def process_packet(self, packet: bytes) -> None:
        if not self.is_open:
            raise ConnectionError(f"Connection {self.connection_id} is not open")
        with self._cv:
            self.received_packets.append(packet)
            self._cv.notify_all()
        logger.debug("Connection %s processed packet: %s", self.connection_id, packet.hex())

    def receive_packet(self, timeout: float = 0.5) -> Optional[bytes]:
        with self._cv:
            if not self.received_packets:
                self._cv.wait(timeout=timeout)
            if self.received_packets:
                packet = self.received_packets.pop(0)
                logger.debug("Connection %s received packet: %s", self.connection_id, packet.hex())
                return packet
        logger.debug("Connection %s receive_packet timed out", self.connection_id)
        return None
