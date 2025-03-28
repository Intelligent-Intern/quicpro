import logging
import sys
import unittest

# Force logging configuration here.
logging.basicConfig(
    level=logging.DEBUG,
    stream=sys.stdout,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    force=True
)

from quicpro.receiver.quic_receiver import QUICReceiver
from quicpro.exceptions import QUICFrameReassemblyError

# Dummy HTTP3Receiver to capture payloads passed by QUICReceiver.
class DummyHTTP3Receiver:
    def __init__(self):
        self.received_payloads = []
    def receive(self, payload: bytes) -> None:
        self.received_payloads.append(payload)

class TestQUICReceiver(unittest.TestCase):
    def setUp(self):
        self.dummy_http3_receiver = DummyHTTP3Receiver()
        self.quic_receiver = QUICReceiver(http3_receiver=self.dummy_http3_receiver)
    
    def test_receive_single_packet(self):
        # Create a dummy QUIC packet with the expected format:
        # b"QUICFRAME:<frame_id>:<seq_num>:<total_packets>:<payload>"
        # For our test, we use: frame_id "dummy", seq_num "0", total_packets "1"
        packet = b"QUICFRAME:dummy:0:1:" + b"HTTP3:Frame(Hello World)"
        self.quic_receiver.receive(packet)
        # The reassembly logic should extract the payload and forward it.
        self.assertEqual(len(self.dummy_http3_receiver.received_payloads), 1)
        self.assertEqual(self.dummy_http3_receiver.received_payloads[0], b"HTTP3:Frame(Hello World)")

if __name__ == '__main__':
    unittest.main()
