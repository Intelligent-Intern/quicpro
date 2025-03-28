# Files to Upgrade / Add for Full Integration of Streams & Priority

Below is the list of files and tests you should review, upgrade, or add in order to fully integrate the new streams management (and stream priority) functionality into your HTTP/3 and QUIC codebase.

---

## Main Library Files

- **utils/http3/streams/stream_manager.py**  
  *Upgrade*:  
  - Ensure that the API for creating, retrieving, and closing streams is robust and thread-safe.  
  - Integrate stream state and buffering, and support unique stream IDs.

- **utils/http3/streams/priority.py**  
  *Upgrade*:  
  - Confirm that the priority API (e.g. `StreamPriority`) enforces correct weight and dependency values.  
  - Integrate or expose comparison operators for proper ordering based on priority.

- **utils/http3/connection/http3_connection.py**  
  *Upgrade*:  
  - Modify this module so that it retrieves or creates streams via the new `StreamManager`.  
  - Integrate stream priority (using `StreamPriority` objects) into connection scheduling and request dispatching.  
  - Ensure that incoming frames are routed to the correct stream based on stream ID.

- **quicpro/client.py**  
  *Upgrade*:  
  - Update the client so that when sending HTTP/3 requests, streams are created and managed via the new HTTP/3 streams API.  
  - Ensure that stream priorities and dependencies are assigned as required.  
  - Make sure that multiplexed streams and responses are correctly demultiplexed to their respective streams.

- **quicpro/receiver/http3_receiver.py**  
  *Upgrade*:  
  - If this module processes incoming HTTP/3 frames for individual streams, update it to route data to streams managed by the `StreamManager`.  
  - Integrate proper handling of stream states and ordering.

- **utils/http3/qpack/**  
  *Review & Verify*:  
  - Although the QPACK modules (encoder/decoder/huffman) have been updated for production, ensure that any integration with stream buffering and header block processing follows the new streams design.

---

## Test Files

- **tests/test_stream_manager.py**  
  *New Tests*:  
  - Tests for creating new streams, retrieving them by ID, and closing streams.  
  - Validate correct stream state transitions (open, half-closed, closed) and proper buffering of stream data.  
  - Verify thread safety and concurrent access.

- **tests/test_priority.py**  
  *New Tests*:  
  - Tests for the `StreamPriority` class that validate proper ordering based on weight and dependency.  
  - Ensure that invalid weight values trigger appropriate errors.

- **tests/test_http3_connection.py** (or similar)  
  *New/Updated Tests*:  
  - Tests for the upgraded HTTP/3 connection that ensure streams are correctly created or retrieved via the `StreamManager`.  
  - Verify that stream priority assignments are applied and checked during connection setup and data transmission.  
  - Validate round-trip communication and correct demultiplexing of streams.

- **tests/test_client.py / tests/test_integration.py**  
  *Update Existing Tests*:  
  - Modify or add integration tests to exercise the new streams API.  
  - Confirm that when a client sends a request, an appropriate stream is assigned and that responses are routed correctly based on stream IDs and priorities.

---

Updating these files and ensuring your test suite covers the new streams and priority functionality will help guarantee that your production-grade HTTP/3/QUIC implementation meets the rigorous requirements needed for high-assurance products.