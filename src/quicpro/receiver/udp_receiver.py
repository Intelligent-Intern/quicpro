"""
UDPReceiver module.
This module implements a UDPReceiver that listens on a specified bind_address,
receives UDP packets using nonblocking I/O and processes them concurrently.
It supports automatic socket rebind on errors.
"""

import socket
import selectors
import threading
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Tuple, Optional, Any

logger = logging.getLogger(__name__)


class UDPReceiver:
    """
    A UDPReceiver that listens for UDP packets and processes them concurrently.
    """

    def __init__(
        self,
        bind_address: Tuple[str, int],
        *,
        tls_decryptor: Optional[Any] = None,
        packet_handler: Optional[Callable[[
            bytes, Tuple[str, int]], None]] = None,
        buffer_size: int = 4096,
        max_rebind_attempts: int = 3,
        rebind_backoff: float = 1.0,
        max_workers: int = 8,
    ) -> None:
        self.bind_address = bind_address
        self.config = {
            "buffer_size": buffer_size,
            "max_rebind_attempts": max_rebind_attempts,
            "rebind_backoff": rebind_backoff,
        }
        self.selector = selectors.DefaultSelector()
        self._state = {"socket": None, "running": False, "thread": None}
        self._thread_state = {"executor": ThreadPoolExecutor(max_workers=max_workers),
                              "lock": threading.Lock()}
        self.tls_decryptor = tls_decryptor
        if packet_handler is None and tls_decryptor is not None:
            self.packet_handler = lambda data, addr: tls_decryptor.decrypt(
                data)
        elif packet_handler is not None:
            self.packet_handler = packet_handler
        else:
            raise ValueError(
                "Either 'packet_handler' or 'tls_decryptor' must be provided.")

    def __enter__(self) -> "UDPReceiver":
        """Enter the runtime context, starting the receiver."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Exit the runtime context and stop the receiver."""
        self.stop()

    def _create_and_bind_socket(self) -> None:
        if self._state["socket"]:
            self._cleanup_socket()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setblocking(False)
        try:
            s.bind(self.bind_address)
        except Exception as e:
            s.close()
            raise e
        self._state["socket"] = s
        self.selector.register(s, selectors.EVENT_READ)
        logger.info("Socket bound to %s", self.bind_address)

    def start(self) -> None:
        """Start the UDPReceiver."""
        with self._thread_state["lock"]:
            if self._state["running"]:
                logger.warning("UDPReceiver is already running.")
                return
            self._state["running"] = True
            self._create_and_bind_socket()
            self._state["thread"] = threading.Thread(
                target=self._event_loop, daemon=True)
            self._state["thread"].start()
            logger.info("UDPReceiver started.")

    def _event_loop(self) -> None:
        rebind_attempts = 0
        while self._state["running"]:
            try:
                events = self.selector.select(timeout=1)
                for _, mask in events:
                    if mask & selectors.EVENT_READ:
                        try:
                            assert self._state["socket"] is not None
                            data, addr = self._state["socket"].recvfrom(
                                self.config["buffer_size"])
                        except BlockingIOError:
                            continue
                        except Exception as e:
                            logger.exception("Error receiving data: %s", e)
                            raise e
                        self._thread_state["executor"].submit(
                            self._handle_packet, data, addr)
            except Exception as e:
                logger.exception("Event loop encountered error: %s", e)
                rebind_attempts += 1
                if rebind_attempts > self.config["max_rebind_attempts"]:
                    logger.error(
                        "Max rebind attempts exceeded; stopping UDPReceiver.")
                    self.stop()
                else:
                    logger.info("Rebinding socket (attempt %d)",
                                rebind_attempts)
                    time.sleep(self.config["rebind_backoff"] * rebind_attempts)
                    try:
                        self._create_and_bind_socket()
                        rebind_attempts = 0
                    except Exception as bind_error:
                        logger.exception(
                            "Failed to rebind socket: %s", bind_error)
            time.sleep(0.01)
        logger.info("Event loop terminated.")

    def _handle_packet(self, data: bytes, addr: Tuple[str, int]) -> None:
        try:
            self.packet_handler(data, addr)
        except Exception as e:
            logger.exception("Packet handler error for %s: %s", addr, e)

    def _cleanup_socket(self) -> None:
        if self._state["socket"]:
            try:
                self.selector.unregister(self._state["socket"])
            except Exception as e:
                logger.debug("Error unregistering socket: %s", e)
            try:
                self._state["socket"].close()
            except Exception as e:
                logger.debug("Error closing socket: %s", e)
            self._state["socket"] = None

    def stop(self) -> None:
        """Stop the UDPReceiver gracefully."""
        with self._thread_state["lock"]:
            if not self._state["running"]:
                return
            self._state["running"] = False
            self._cleanup_socket()
        if self._state["thread"]:
            self._state["thread"].join(timeout=5)
        self._thread_state["executor"].shutdown(wait=True)
        logger.info("UDPReceiver stopped gracefully.")
