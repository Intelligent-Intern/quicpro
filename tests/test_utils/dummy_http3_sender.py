# pylint: disable=duplicate-code
"""
Dummy HTTP/3 sender for testing purposes.
"""
from tests.test_utils.dummy_quic_sender import DummyQUICSender

class DummyHTTP3Sender:
    """A dummy HTTP/3 sender that wraps a QUIC sender."""
    def __init__(self, quic_sender: DummyQUICSender, stream_id: int):
        self.quic_sender = quic_sender
        self.stream_id = stream_id
        self.sent_frames = []

    def send(self, frame: bytes) -> None:
        self.sent_frames.append(frame)
