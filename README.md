# quicpro

**quicpro** (v1.0.0) is an HTTP/3 client library built on a custom synchronous QUIC implementation with integrated TLS encryption. It provides a cohesive solution for making HTTP/3 requests without relying on asyncio. The library supports both a demo mode (using simulated TLS handshakes and dummy certificate values) as well as a path toward a production‑grade solution that integrates more robust security, full protocol compliance, and advanced error handling.

---

## Overview

quicpro brings together the following components into one unified codebase:

- **QUIC Implementation:**  
  - A custom QUIC manager that handles connection state, version negotiation, handshake state machines, and packet encoding/decoding.
  - Congestion control and retransmission management based on a Cubic-inspired algorithm.
  - Support for creating and managing streams with integrated stream priority and flow control.

- **HTTP/3 Integration:**  
  - An HTTP/3 connection layer that uses the QUIC manager to send requests and route incoming frames.
  - QPACK header compression/decompression with both static and dynamic table support (with simulation mode available for testing).
  - Basic support for server push and control frames.

- **TLS Support:**  
  - A TLS manager that operates in two modes:
    - **Demo Mode:** Uses dummy certificate values and a simulated handshake to allow quick testing.
    - **Production Mode (in progress):** Provides a framework for integrating a full TLS 1.3 (or production‑ready TLS) stack with real certificate verification and key derivation.
  - Encryption and decryption of QUIC packets using AES‑GCM.

- **Event Loop & Scheduling:**  
  - A synchronous event loop implemented with a thread‑pool executor.
  - A task scheduler and worker pool to handle timer‑based events and retransmissions in the QUIC connection.

The library is extensively tested with unit and integration tests covering many aspects of the protocol—from QUIC handshake and congestion control to QPACK header processing.

---

## Features

- **Integrated QUIC Stack:**  
  - Version negotiation, multiple packet number spaces, handshake state management, and retransmission.
  - Congestion control using a simplified Cubic algorithm.
  
- **HTTP/3 Support:**  
  - Send requests and receive responses using full HTTP/3 framing.
  - QPACK encoder/decoder in simulation mode (with a path toward full dynamic table support).

- **TLS Encryption:**  
  - Demo‑mode TLS with simulated handshake and AES‑GCM encryption.
  - Integrated TLS manager structure ready for production‑grade TLS (TLS 1.3) integration.

- **Stream Management:**  
  - Create, retrieve, and close streams with priority and flow control.
  - Basic support for server push via push frames.

- **Synchronous Programming:**  
  - A synchronous event loop provides a simpler programming model compared to asynchronous code.
  - Works out of the box on systems without asyncio.

- **Testing and Debugging:**  
  - Comprehensive unit and integration tests for each subsystem.
  - Detailed logging that can help trace protocol state and debug issues.

---

## Installation

quicpro is available on [PyPI](https://pypi.org):

~~~bash
pip install quicpro==1.0.0
~~~

Alternatively, you can install the development version from source:

~~~bash
python setup.py install
~~~

---

## Usage

### Example: Single Request (Demo Mode)

Below is an example of how to use quicpro in a demo environment for a single HTTP request:

~~~python
#!/usr/bin/env python
from quicpro.client import Client

def main():
    # Initialize the client using demo mode (with simulated TLS handshake etc.)
    client = Client(
        remote_address=("127.0.0.1", 9090),
        timeout=5,
        event_loop_max_workers=4,
        demo_mode=True
    )
    
    # Send a GET request (query parameters can be passed)
    response = client.request("GET", "https://example.com", params={"q": "test"})
    
    # Print the response payload and status code
    print("Response Status Code:", response.status_code)
    print("Response Content:", response.content)
    
    client.close()

if __name__ == "__main__":
    main()
~~~

### Example: Multiple Parallel Requests (Demo Mode)

The following example demonstrates sending several parallel requests using Python's threading:

~~~python
#!/usr/bin/env python
import threading
from quicpro.client import Client

def make_request(request_number):
    # Each thread creates its own client instance
    client = Client(
        remote_address=("127.0.0.1", 9090),
        timeout=5,
        event_loop_max_workers=4,
        demo_mode=True
    )
    # Pass a unique query parameter for each request
    response = client.request("GET", "https://example.com", params={"q": f"test-{request_number}"})
    print(f"Response #{request_number} - Status Code: {response.status_code}, Content: {response.content}")
    client.close()

threads = []
num_requests = 5  # Adjust the number of parallel requests

# Start multiple threads for parallel requests
for i in range(1, num_requests + 1):
    t = threading.Thread(target=make_request, args=(i,))
    threads.append(t)
    t.start()

# Wait for all threads to complete
for t in threads:
    t.join()
~~~

### Example: Production Mode

For production use, you must supply actual certificate files and disable demo mode. Follow these steps to install and prepare your certificates:

1. **Obtain or Generate Certificates:**  
   You need a valid certificate file (`cert.pem`), a private key (`key.pem`), and optionally a CA bundle (`ca.pem`) if you wish to perform proper certificate verification. For testing, you can generate a self-signed certificate using OpenSSL:

~~~bash
   # Generate a private key
   openssl genpkey -algorithm RSA -out key.pem -pkeyopt rsa_keygen_bits:2048

   # Generate a self-signed certificate valid for 365 days
   openssl req -new -x509 -key key.pem -out cert.pem -days 365 -subj "/CN=example.com"

   # (Optional) For testing, you can use the same cert as a CA bundle
   cp cert.pem ca.pem
~~~

2. **Run in Production Mode:**  
   Set `demo_mode` to `False` and provide the paths to your certificate, key, and optionally your CA bundle:

~~~python
#!/usr/bin/env python
from quicpro.client import Client

def main():
    # Initialize the client in production mode
    client = Client(
        remote_address=("your.server.ip", 443),
        timeout=5,
        event_loop_max_workers=4,
        demo_mode=False,        # Disable demo mode
        certfile="path/to/cert.pem",
        keyfile="path/to/key.pem",
        cafile="path/to/ca.pem"  # Optional, if available
    )
    
    # Send a GET request
    response = client.request("GET", "https://your.server.com", params={"q": "production-test"})
    print("Response Status Code:", response.status_code)
    print("Response Content:", response.content)
    client.close()

if __name__ == "__main__":
    main()
~~~

---

## What’s Next / What Needs Improvement

While quicpro is integrated and functional, future enhancements include:

1. **Standards Compliance & Edge Cases:**  
   - Achieve full adherence to QUIC (RFC 9000–9002) and HTTP/3 RFCs, including support for 0‑RTT, key updates, and comprehensive QPACK dynamic table management.
   - Enhance handling of out‑of‑order packets and fine-tune congestion control under adverse network conditions.

2. **TLS Integration:**  
   - Integrate a production‑grade TLS library for a complete TLS 1.3 handshake.
   - Support certificate chains, perform proper revocation checks, and implement secure key derivation.

3. **Robust Error Handling & Recovery:**  
   - Improve state management, logging, and error recovery procedures.
   - Enhance retransmission logic, timer accuracy, and support for network migration.

4. **Performance & Concurrency:**  
   - Transition to an asynchronous I/O model or further optimize the synchronous thread‑pool model for handling a large number of concurrent connections.

5. **Interoperability Testing:**  
   - Conduct extensive integration tests and interoperability trials with other QUIC/HTTP‑3 implementations.

---

## Acknowledgments

A significant part of the integration and initial development of **quicpro** was achieved with the assistance of OpenAI’s o3‑mini model.

---

## Contributing

Contributions are welcome! Please fork the repository, implement your changes, and open a pull request. Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines and include tests for any modifications.

---

## License

This project is released under the MIT License — see the [LICENSE](LICENSE) file for details.