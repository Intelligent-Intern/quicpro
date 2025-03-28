import threading
import socket
import time
import unittest
from quicpro.client import Client, Response

class TestClientEventLoop(unittest.TestCase):
    def setUp(self) -> None:
        self.remote_address = ("127.0.0.1", 9090)
        self.client = Client(remote_address=self.remote_address, timeout=5.0, event_loop_max_workers=2)

    def tearDown(self) -> None:
        self.client.close()

    def _simulate_udp_response(self) -> None:
        import hashlib
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        from quicpro.sender.tls_encryptor import TLSConfig
        default_config = TLSConfig(key=b"\x00" * 32, iv=b"\x00" * 12)
        aesgcm = AESGCM(default_config.key)
        stream_frame = b"HTTP3:Frame(Simulated response)\n"
        header_marker = b"QUICFRAME:dummy:0:1:"
        length_bytes = len(stream_frame).to_bytes(4, byteorder="big")
        checksum = hashlib.sha256(stream_frame).digest()[:8]
        quic_packet = header_marker + length_bytes + checksum + stream_frame
        nonce = default_config.iv
        ciphertext = aesgcm.encrypt(nonce, quic_packet, None)
        encrypted_packet = b"\x00" * 8 + ciphertext
        time.sleep(0.5)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(encrypted_packet, self.remote_address)

    def test_client_event_loop(self) -> None:
        response_thread = threading.Thread(target=self._simulate_udp_response, daemon=True)
        response_thread.start()
        response: Response = self.client.request("GET", "https://example.com")
        self.assertIsNotNone(response, "Expected a non-None response from client.request().")
        self.assertEqual(response.status_code, 200, "Simulated response should have status code 200.")
        self.assertEqual(response.content, "Simulated response", "Response content mismatch")

if __name__ == '__main__':
    unittest.main()