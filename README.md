# QuicPro HTTP/3 Client Library

QuicPro is a synchronous HTTP/3 client library that provides a drop‑in alternative to httpx using native threads—without asyncio—while leveraging core QUIC protocols, UDP transport, and TLS-like encryption.

## Key Features

- **Context Managers** :white_check_mark: 
  - Fully implemented with synchronous context management support.
- **Custom Synchronous Event Loop** :white_check_mark: 
  - Built with a thread pool to schedule and execute tasks concurrently.
- **QUIC Transmission** :white_check_mark: 
  - Core QUIC functionality including UDP networking, TLS-based encryption, modular packet/header encoding & decoding, and stream/connection management.
- **HTTP Methods** :white_check_mark: 
  - GET, POST, OPTIONS, and a generic request method are implemented.
- **Query Parameters (`params=`)** :white_check_mark: 
  - Integrated URL parsing and query encoding using Python’s `urllib.parse`.
- **Headers & JSON Support** :white_check_mark: 
  - Fully implemented to match httpx behavior.
- **Response Handling**:
  - `.status_code`, `.headers`, `.text`, `.content`, and `.json()` are fully implemented.
  - `.iter_bytes()` and `.iter_lines()` are fully supported.
  - `.iter_text()` :white_check_mark: Now fully implemented using an incremental decoder.
  - `.raise_for_status()` :white_check_mark: Throws a custom `HTTPStatusError`.
- **Modular Architecture** :white_check_mark: 
  - Clear separation into layers: connection, header, packet, streams, transport, and exceptions.

## Usage Example

Run the client with custom query parameters:

~~~bash
python run_client.py
~~~

`run_client.py` example:
~~~python
#!/usr/bin/env python
from quicpro.client import Client

def main():
    # Create the client with configurable event loop workers.
    client = Client(remote_address=("127.0.0.1", 9090), timeout=5, event_loop_max_workers=4)
    
    # Send a GET request with query parameters.
    response = client.request("GET", "https://example.com", params={"q": "test"})
    print("Response:", response)
    client.close()

if __name__ == "__main__":
    main()
~~~

## Running Tests

To run the full test suite, execute:
~~~bash
pytest tests/
~~~

## License

MIT License