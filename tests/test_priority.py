import unittest
from quicpro.utils.http3.streams.priority import StreamPriority

class TestStreamPriority(unittest.TestCase):
    def test_valid_priority_creation(self):
        # Test that a valid StreamPriority instance can be created
        sp = StreamPriority(weight=10, dependency=5)
        self.assertEqual(sp.weight, 10, "Weight should be set correctly.")
        self.assertEqual(sp.dependency, 5, "Dependency should be set correctly.")

    def test_comparison_and_sorting(self):
        # Create multiple StreamPriority instances with different weights
        sp1 = StreamPriority(weight=10, dependency=0)
        sp2 = StreamPriority(weight=5, dependency=0)
        sp3 = StreamPriority(weight=1, dependency=0)
        priorities = [sp1, sp2, sp3]
        # Sorting should order by ascending weight (lower weight indicates higher priority)
        sorted_priorities = sorted(priorities)
        self.assertEqual(sorted_priorities, [sp3, sp2, sp1],
                         "Priorities should be sorted by ascending weight.")

    def test_invalid_weight_low(self):
        # Test that a weight lower than 1 is rejected
        with self.assertRaises(ValueError, msg="Weight of 0 should raise a ValueError."):
            StreamPriority(weight=0, dependency=0)

    def test_invalid_weight_high(self):
        # Test that a weight higher than 256 is rejected
        with self.assertRaises(ValueError, msg="Weight of 300 should raise a ValueError."):
            StreamPriority(weight=300, dependency=0)

    def test_equality(self):
        # Test that two StreamPriority instances with the same weight (and dependency) are equal
        sp1 = StreamPriority(weight=10, dependency=0)
        sp2 = StreamPriority(weight=10, dependency=0)
        sp3 = StreamPriority(weight=15, dependency=0)
        self.assertEqual(sp1, sp2, "StreamPriority instances with identical parameters should be equal.")
        self.assertNotEqual(sp1, sp3, "StreamPriority instances with different weights should not be equal.")

if __name__ == '__main__':
    unittest.main()
