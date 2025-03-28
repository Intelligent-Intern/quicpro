import threading
import socket
import time
import unittest
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from quicpro.sender.tls_encryptor import TLSConfig
from quicpro.client import Client, Response  

class TestClient(unittest.TestCase):
    """Unit tests for the Client class functionality with integrated stream management and priority."""
    
    def setUp(self) -> None:
        # Use a local UDP bind address and a short timeout for testing.
        self.remote_address = ("127.0.0.1", 9090)
        # Initialize the client with a custom event_loop_max_workers if needed.
        self.client = Client(remote_address=self.remote_address, timeout=5.0, event_loop_max_workers=4)
        
    def tearDown(self) -> None:
        self.client.close()
        
    def _simulate_udp_response(self) -> None:
        """
        Simulate an external UDP response by sending a properly encrypted TLS record.
        We construct a dummy QUIC packet with the following structure:
          - Legacy header marker: b'QUICFRAME:dummy:0:1:'
          - 4-byte big-endian length of the stream frame.
          - 8-byte truncated SHA256 checksum of the stream frame.
          - Stream frame: b"HTTP3:Frame(Simulated response)\n"
        The packet is then encrypted with AES-GCM (using a nonce derived from the IV
        for sequence number 0) and an 8-byte sequence number is prepended.
        """
        default_config = TLSConfig(key=b"\x00" * 32, iv=b"\x00" * 12)
        aesgcm = AESGCM(default_config.key)
        # Construct the stream frame.
        stream_frame = b"HTTP3:Frame(Simulated response)\n"
        # Build the QUIC packet with the proper legacy header marker.
        header_marker = b"QUICFRAME:dummy:0:1:"
        length_bytes = len(stream_frame).to_bytes(4, byteorder='big')
        checksum = hashlib.sha256(stream_frame).digest()[:8]
        quic_packet = header_marker + length_bytes + checksum + stream_frame
        # Encrypt the QUIC packet.
        nonce = default_config.iv  # For sequence number 0.
        ciphertext = aesgcm.encrypt(nonce, quic_packet, None)
        # Prepend an 8-byte sequence number (0).
        encrypted_packet = b"\x00" * 8 + ciphertext
        time.sleep(0.5)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(encrypted_packet, self.remote_address)
            
    def test_request_simulated_response(self) -> None:
        """
        Ensure that a client request produces a simulated response via the receiver pipeline.
        This test verifies the full flow: sending a request, receiving a UDP response,
        and routing the response through the integrated stream management.
        """
        response_thread = threading.Thread(target=self._simulate_udp_response, daemon=True)
        response_thread.start()
        response: Response = self.client.request("GET", "https://example.com")
        self.assertIsNotNone(response, "Expected a non-None response from client.request().")
        self.assertEqual(response.status_code, 200, "Simulated response should have status code 200.")
        self.assertEqual(response.content, "Simulated response",
                         "Response content did not match the expected simulated response.")
        
    def test_request_stream_integration(self) -> None:
        """
        Verify that when a client sends a request, a new stream is created via the
        integrated StreamManager, and that stream management (including priority)
        is in place.
        """
        # Simulate a UDP response in a separate thread.
        response_thread = threading.Thread(target=self._simulate_udp_response, daemon=True)
        response_thread.start()
        # Send a request with an additional parameter to indicate priority (for demonstration).
        response: Response = self.client.request("GET", "https://example.com?priority=high")
        # Access the underlying QuicManager's stream manager.
        stream_manager = self.client.quic_manager.stream_manager
        # For this test we assume the default stream_id used is 1.
        stream = stream_manager.get_stream(1)
        self.assertIsNotNone(stream, "A stream should be created for the client request.")
        # If the stream object has a 'priority' attribute (set by the new priority integration), check it.
        # For example, we expect a high priority stream to have a lower weight (e.g., weight 1).
        if hasattr(stream, 'priority'):
            self.assertEqual(stream.priority.weight, 1,
                             "Stream priority weight should be 1 for high priority requests.")
        # Validate the response as well.
        self.assertEqual(response.status_code, 200, "Simulated response should have status code 200.")
        self.assertEqual(response.content, "Simulated response",
                         "Response content did not match expected simulated response.")

    def test_close_function(self) -> None:
        """
        Verify that invoking close() on the client properly shuts down all underlying resources
        (including streams and event loops) without raising errors.
        """
        try:
            self.client.close()
        except Exception as exc:
            self.fail(f"Client.close() raised an exception: {exc}")

if __name__ == '__main__':
    unittest.main()
