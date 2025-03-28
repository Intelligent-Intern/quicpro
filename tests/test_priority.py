import unittest
from quicpro.utils.http3.streams.priority import StreamPriority
from quicpro.utils.http3.streams.enum.priority_level import PriorityLevel

class TestStreamPriority(unittest.TestCase):
    def test_valid_priority_creation(self):
        sp = StreamPriority(weight=10, dependency=5)
        self.assertEqual(sp.weight, 10, "Weight should be set correctly.")
    def test_comparison_and_sorting(self):
        sp1 = StreamPriority(weight=10, dependency=0)
        sp2 = StreamPriority(weight=5, dependency=0)
        sp3 = StreamPriority(weight=1, dependency=0)
        priorities = [sp1, sp2, sp3]
        sorted_priorities = sorted(priorities)
        self.assertEqual(sorted_priorities, [sp3, sp2, sp1], "Priorities should sort in ascending order by weight.")
    def test_invalid_weight_low(self):
        with self.assertRaises(ValueError):
            StreamPriority(weight=0, dependency=0)
    def test_invalid_weight_high(self):
        with self.assertRaises(ValueError):
            StreamPriority(weight=300, dependency=0)
    def test_equality(self):
        sp1 = StreamPriority(weight=10, dependency=0)
        sp2 = StreamPriority(weight=10, dependency=0)
        sp3 = StreamPriority(weight=15, dependency=0)
        self.assertEqual(sp1, sp2, "Equal priority objects should be equal.")
        self.assertNotEqual(sp1, sp3, "Different weights should not be equal.")
    def test_from_priority_level(self):
        sp = StreamPriority.from_priority_level(PriorityLevel.HIGH)
        self.assertEqual(sp.weight, PriorityLevel.HIGH.value, "PriorityLevel conversion failed.")

if __name__ == '__main__':
    unittest.main()
