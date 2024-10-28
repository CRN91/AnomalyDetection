import unittest
from unittest.mock import patch
import random
from src.simulator.anomalies import (
    inject_anomaly,
    anomalous_simulator,
    ANOMALY_MULTIPLIER_BOUNDS,
    ANOMALY_MIN_DURATION,
    ANOMALY_MAX_DURATION,
    ANOMALY_THRESHOLD
)


class TestAnomalyInjection(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.sample_stream = [50.0] * 1440  # One day of constant values
        random.seed(42)  # For reproducible tests

    def test_apply_anomaly_normal_case(self):
        """Test normal anomaly application within stream bounds"""
        stream = self.sample_stream.copy()
        multiplier = 1.1
        start = 100
        duration = 200

        modified_stream, remaining_duration = inject_anomaly(stream, multiplier, start, duration)

        # Check modified values
        self.assertNotEqual(modified_stream[start:start + duration], self.sample_stream[start:start + duration])
        # Check unmodified values
        self.assertEqual(modified_stream[:start], self.sample_stream[:start])
        self.assertEqual(modified_stream[start + duration:], self.sample_stream[start + duration:])
        # Check remaining duration
        self.assertEqual(remaining_duration, 0)

    def test_apply_anomaly_capacity_limit(self):
        """Test anomaly application respects maximum capacity limit of 75"""
        stream = [70.0] * 1440
        multiplier = 1.5  # Should trigger capacity limit
        start = 100
        duration = 100

        modified_stream, _ = inject_anomaly(stream, multiplier, start, duration)

        # Check that no values exceed capacity
        self.assertTrue(all(value <= 75 for value in modified_stream))

    def test_apply_anomaly_zero_duration(self):
        """Test anomaly application with zero duration"""
        stream = self.sample_stream.copy()
        original_stream = stream.copy()
        multiplier = 1.1
        start = 100
        duration = 0

        modified_stream, remaining_duration = inject_anomaly(stream, multiplier, start, duration)

        # Check nothing was modified
        self.assertEqual(modified_stream, original_stream)
        self.assertEqual(remaining_duration, 0)

    def test_apply_anomaly_negative_duration(self):
        """Test anomaly application with negative duration"""
        stream = self.sample_stream.copy()
        original_stream = stream.copy()
        multiplier = 1.1
        start = 100
        duration = -100

        modified_stream, remaining_duration = inject_anomaly(stream, multiplier, start, duration)

        # Check nothing was modified
        self.assertEqual(modified_stream, original_stream)
        self.assertEqual(remaining_duration, 0)

    def test_apply_anomaly_out_of_bounds_start(self):
        """Test anomaly application with start index beyond stream length"""
        stream = self.sample_stream.copy()
        original_stream = stream.copy()
        multiplier = 1.1
        start = 2000  # Beyond stream length
        duration = 100

        modified_stream, remaining_duration = inject_anomaly(stream, multiplier, start, duration)

        # Check nothing was modified
        self.assertEqual(modified_stream, original_stream)
        self.assertEqual(remaining_duration, 0)

    def test_apply_anomaly_cross_boundary(self):
        """Test anomaly application that crosses stream boundary"""
        stream = self.sample_stream.copy()
        multiplier = 1.1
        start = 1400  # Near end of stream
        duration = 100  # Extends beyond stream

        modified_stream, remaining_duration = inject_anomaly(stream, multiplier, start, duration)

        # Check remaining duration calculation
        self.assertEqual(remaining_duration, duration - (len(stream) - start))
        # Check modification at end of stream
        self.assertNotEqual(modified_stream[start:], self.sample_stream[start:])

    def test_apply_anomaly_all_types(self):
        """Test all types of anomalies from ANOMALY_MULTIPLIER_BOUNDS"""
        stream = self.sample_stream.copy()
        start = 100
        duration = 100

        for bounds in ANOMALY_MULTIPLIER_BOUNDS:
            multiplier = random.uniform(bounds[0], bounds[1])
            modified_stream, _ = inject_anomaly(stream.copy(), multiplier, start, duration)

            if bounds[0] == 0 and bounds[1] == 0:  # Outage
                self.assertTrue(all(val == 0 for val in modified_stream[start:start + duration]))
            elif bounds[0] < 1 and bounds[1] < 1:  # Leak
                self.assertTrue(all(val < stream[i] for i, val in enumerate(modified_stream[start:start + duration])))
            elif bounds[0] > 1 and bounds[1] > 1:  # Surge
                self.assertTrue(all(val > stream[i] for i, val in enumerate(modified_stream[start:start + duration])))

    @patch('src.simulator.simulator')
    def test_anomalous_simulator_normal(self, mock_simulator):
        """Test normal operation of simulation with anomalies"""
        # Mock the base simulation
        mock_simulator.return_value = iter([self.sample_stream.copy() for _ in range(5)])

        sim = anomalous_simulator(0, 5)
        streams = list(sim)

        self.assertEqual(len(streams), 5)
        self.assertTrue(all(len(stream) == 1440 for stream in streams))

    def test_edge_cases(self):
        """Test various edge cases"""
        # Test with empty stream
        empty_stream, _ = inject_anomaly([], 1.1, 0, 100)
        self.assertEqual(empty_stream, [])

        # Test with single value stream
        single_stream, _ = inject_anomaly([50.0], 1.1, 0, 1)
        self.assertEqual(len(single_stream), 1)

        # Test with very large duration
        large_duration = 10000
        stream = self.sample_stream.copy()
        _, remaining = inject_anomaly(stream, 1.1, 0, large_duration)
        self.assertTrue(remaining > 0)


if __name__ == '__main__':
    unittest.main()
