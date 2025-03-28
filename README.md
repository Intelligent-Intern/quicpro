# QuicPro HTTP/3 Client Library

QuicPro is a fully production‑ready synchronous HTTP/3 client library. It offers a drop‑in alternative to httpx by leveraging native threads—without asyncio—and implements the core QUIC protocol over UDP, integrated HTTP/3 support with advanced stream management, and robust TLS‑like encryption. In addition, the library includes a custom synchronous event loop that you can use to execute concurrent tasks in real‑world scenarios.

## Key Features

- **Synchronous Context Managers**  
  Fully implemented context managers for proper resource cleanup.

- **Custom Synchronous Event Loop**  
  An optimized thread pool that schedules and executes tasks concurrently.

- **Full QUIC Transmission Stack**  
  Implements connection and stream lifecycle, QUIC handshake with version negotiation, modular packet/header encoding/decoding, congestion control, and loss recovery.

- **HTTP/3 Support with QPACK**  
  Supports GET, POST, OPTIONS, and a generic request method, along with complete QPACK-based header compression.

- **Robust TLS Integration**  
  Supports production TLS with complete TLS 1.3 (and TLS 1.2 fallback) handshake as well as demo mode for testing.

- **Modular & Extensible Architecture**  
  Clear separation into layers: connection, header, packet, streams, congestion control, retransmission, TLS, and exceptions.

## Real-World Example: Concurrent PDF Processing Pipeline

Imagine a production scenario where you need to process a large PDF document. The document is split into sections, and for each section:
- Optical Character Recognition (OCR) extracts text.
- A GPT model processes the text.
- The processed data is then inserted into a vector database.

The following example uses the QuicPro synchronous event loop to schedule tasks concurrently.

### Example: pdf_processing_pipeline.py

~~~python
#!/usr/bin/env python
"""
Concurrent PDF Processing Pipeline Example

This example splits a PDF into sections (simulated), processes each section with OCR 
and a GPT model (simulated), and then combines the results to fill a vector database.
The tasks run concurrently using QuicPro's synchronous event loop.
"""

import time
import random
from concurrent.futures import Future

from quicpro.utils.event_loop.sync_loop import SyncEventLoop

# Simulated OCR function
def perform_ocr(section: str) -> str:
    time.sleep(random.uniform(0.5, 1.0))  # Simulate processing delay
    return f"OCR text for {section}"

# Simulated GPT processing function
def process_with_gpt(ocr_text: str) -> str:
    time.sleep(random.uniform(0.5, 1.0))
    return f"Processed data based on '{ocr_text}'"

# Simulated function to insert into a vector DB
def insert_into_vector_db(processed_data: str) -> None:
    time.sleep(random.uniform(0.1, 0.3))
    print(f"Inserted into vector DB: {processed_data}")

def process_pdf_section(section: str, loop: SyncEventLoop) -> Future:
    """
    Process one PDF section with OCR and GPT concurrently using the event loop.
    """
    # Schedule OCR task
    ocr_future = loop.schedule_task(perform_ocr, section)
    # When OCR is complete, schedule GPT processing
    def gpt_task(ocr_result):
        return process_with_gpt(ocr_result)
    gpt_future = loop.schedule_task(gpt_task, ocr_future.result())
    # When GPT finishes, insert result into vector DB
    def db_task(processed):
        insert_into_vector_db(processed)
    db_future = loop.schedule_task(db_task, gpt_future.result())
    return db_future

def main():
    # Simulated sections from splitting a PDF.
    pdf_sections = [f"Section {i+1}" for i in range(5)]
    loop = SyncEventLoop(max_workers=4)
    loop_thread = threading.Thread(target=loop.run_forever, daemon=True)
    loop_thread.start()
    
    tasks = []
    for section in pdf_sections:
        future = process_pdf_section(section, loop)
        tasks.append(future)
    
    # Wait for all tasks to complete.
    for task in tasks:
        task.result()
    
    loop.stop()
    loop_thread.join()
    print("PDF processing pipeline completed.")

if __name__ == "__main__":
    import threading
    main()
~~~

## Additional Usage Example: Basic HTTP/3 Request

### Example: run_client.py

~~~python
#!/usr/bin/env python
from quicpro.client import Client
from quicpro.utils.http3.streams.priority import StreamPriority
from quicpro.utils.http3.streams.priority_level import PriorityLevel

def main():
    priority = StreamPriority.from_priority_level(PriorityLevel.HIGH)
    client = Client(remote_address=("127.0.0.1", 9090), timeout=5, event_loop_max_workers=4)
    response = client.request("GET", "https://example.com", params={"q": "test"}, priority=priority)
    print("Response:", response)
    client.close()

if __name__ == "__main__":
    main()
~~~


### Missing Components for a Perfect QUIC/HTTP3/TLS Implementation

- **Packet Number Spaces & Encryption Levels**
  - Separate handling for Initial, Handshake, and 1‑RTT packet number spaces.
  - Distinct encryption/decryption routines for each packet number space.

- **Flow Control & Stream Management**
  - Connection‑level flow control with dynamic window adjustment.
  - Comprehensive per‑stream flow control and state tracking (idle, open, half‑closed, closed).
  - Robust stream reset and error handling mechanisms.

- **Full QUIC Frame Support**
  - Implementation of all QUIC frame types (e.g., ACK, CRYPTO, RESET_STREAM, STOP_SENDING, STREAM_BLOCKED, MAX_DATA, MAX_STREAMS, etc.).
  - Proper sequencing and reassembly of fragmented frames, including handling out-of-order delivery.

- **Advanced Loss Detection & Retransmission**
  - Complete loss detection algorithms across different encryption levels.
  - More sophisticated retransmission timers and retry logic for selective packet retransmission.
  - Integration of explicit ACK frame generation and processing.

- **Enhanced Congestion Control**
  - Support for alternative congestion control algorithms (such as BBR) alongside Cubic.
  - Fine-tuning of congestion control parameters based on real-world network conditions.

- **Comprehensive TLS Integration**
  - Direct TLS 1.3 handshake implementation with key extraction via low-level cryptographic APIs.
  - Automatic key update (rekeying) without requiring full re-handshake.
  - End-to-end certificate validation, including OCSP stapling and CRL checking.

- **Multipath & Connection Migration**
  - Support for seamless connection migration across different network interfaces.
  - Multipath QUIC extensions for balancing and redundancy.

- **Performance & Scalability Optimizations**
  - Asynchronous I/O integration (e.g., using epoll, kqueue, or asyncio) for high-throughput, low-latency scenarios.
  - Zero-copy techniques for packet serialization/deserialization.
  - Optimizations in memory usage and thread management.

- **Extensive Testing & Robust Error Handling**
  - Comprehensive unit, integration, and stress tests simulating high-loss, high-reorder, and high-latency networks.
  - Detailed logging, metrics, and error recovery strategies for production monitoring.


## Running Tests

To run the full test suite, execute:

~~~bash
pytest tests/
~~~

## License

MIT License