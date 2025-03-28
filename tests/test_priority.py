"""
Test module for the priority functionality.
"""

import unittest
from quicpro.utils.http3.streams.priority import StreamPriority
from quicpro.utils.http3.streams.enum.priority_level import PriorityLevel

class TestStreamPriority(unittest.TestCase):
    """Test cases for the StreamPriority class."""
    def test_valid_priority_creation(self):
        """Test valid creation of a StreamPriority."""
        sp = StreamPriority(weight=10, dependency=5)
        self.assertEqual(sp.weight, 10, "Weight should be set correctly.")

    def test_comparison_and_sorting(self):
        """Test comparison and sorting of StreamPriority instances."""
        sp1 = StreamPriority(weight=10, dependency=0)
        sp2 = StreamPriority(weight=5, dependency=0)
        sp3 = StreamPriority(weight=1, dependency=0)
        priorities = [sp1, sp2, sp3]
        sorted_priorities = sorted(priorities)
        self.assertEqual(sorted_priorities, [sp3, sp2, sp1],
                         "Priorities should sort in ascending order by weight.")

    def test_invalid_weight_low(self):
        """Test that a weight below 1 raises ValueError."""
        with self.assertRaises(ValueError):
            StreamPriority(weight=0, dependency=0)

    def test_invalid_weight_high(self):
        """Test that a weight above 256 raises ValueError."""
        with self.assertRaises(ValueError):
            StreamPriority(weight=300, dependency=0)

    def test_equality(self):
        """Test equality comparisons for StreamPriority objects."""
        sp1 = StreamPriority(weight=10, dependency=0)
        sp2 = StreamPriority(weight=10, dependency=0)
        sp3 = StreamPriority(weight=15, dependency=0)
        self.assertEqual(sp1, sp2, "Equal priority objects should be equal.")
        self.assertNotEqual(sp1, sp3, "Different weights should not be equal.")

    def test_from_priority_level(self):
        """Test creating a StreamPriority from a PriorityLevel."""
        sp = StreamPriority.from_priority_level(PriorityLevel.HIGH)
        self.assertEqual(sp.weight, PriorityLevel.HIGH.value, "PriorityLevel conversion failed.")

if __name__ == '__main__':
    unittest.main()
