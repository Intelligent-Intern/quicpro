#!/usr/bin/env python3
"""
Prometheus Metrics Server for Prod Pipeline
--------------------------------------------
This module starts an HTTP server to expose Prometheus metrics.
It supports configurable bind address and port, and handles graceful shutdown.
"""

import argparse
import logging
import signal
import sys
import time
from prometheus_client import start_http_server

# Configure logging for production-grade output.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Start the Prometheus metrics server for the Prod Pipeline."
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the metrics server (default: 8000)",
    )
    parser.add_argument(
        "--address",
        type=str,
        default="0.0.0.0",
        help="Address to bind the metrics server (default: 0.0.0.0)",
    )
    return parser.parse_args()


def setup_signal_handlers():
    def shutdown_handler(sig, frame):
        logger.info("Received signal %s, shutting down metrics server...", sig)
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)


def main():
    args = parse_args()
    logger.info("Starting Prometheus metrics server on %s:%d", args.address, args.port)
    try:
        start_http_server(port=args.port, addr=args.address)
    except Exception as e:
        logger.error("Failed to start metrics server: %s", e)
        sys.exit(1)

    setup_signal_handlers()

    # Keep the process alive to serve metrics.
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
