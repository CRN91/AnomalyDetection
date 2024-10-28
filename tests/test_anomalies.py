import unittest
import random
from src.simulator.anomalies import *

class TestAnomalies(unittest.TestCase):

    def setUp(self):
        self.stream = [random.uniform(50, 70) for _ in range(1440)]  # Example gas flow data for 24 hours

    def test_apply_anomaly(self):
        start = 0
        duration = 100  # Example duration
        multiplier = 0 # Example anomaly multiplier
        modified_stream, next_duration = apply_anomaly(self.stream.copy(), multiplier, start, duration)
        self.assertEqual(sum(modified_stream[:duration]), 0, "Anomaly not correctly applied for the specified duration")
        self.assertEqual(next_duration, 0, "Anomaly duration not correctly calculated for next stream")

if __name__ == '__main__':
    unittest.main()
