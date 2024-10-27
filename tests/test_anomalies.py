import unittest
import random
from src.simulator.anomalies import *

class TestAnomalies(unittest.TestCase):

    def setUp(self):
        self.stream = [random.uniform(50, 70) for _ in range(1440)]  # Example gas flow data for 24 hours

    def test_apply_outage(self):
        duration = 100  # Example duration
        modified_stream, next_duration = apply_outage(self.stream.copy(), duration, random_start=False)
        self.assertEqual(sum(modified_stream[:duration]), 0, "Outage not correctly applied for the specified duration")
        self.assertEqual(next_duration, 0, "Outage duration not correctly calculated for next stream")

    def test_apply_leak(self):
        duration = 100  # Example duration
        leak_percentage = 0.95  # Example leak percentage
        modified_stream, next_duration, applied_leak = apply_leak(self.stream, duration, random_leak=leak_percentage, random_start=False)
        for i in range(duration):
            self.assertAlmostEqual(modified_stream[i], (self.stream[i] * leak_percentage), delta=0.1,msg="Leak not correctly applied for the specified duration")
        self.assertEqual(next_duration, 0, "Leak duration not correctly calculated for next stream")
        self.assertEqual(applied_leak, 0, "Leakage duration not correctly calculated for next stream")

    def test_apply_surge(self):
        duration = 100  # Example duration
        surge_percentage = 1.05 # Example surge percentage
        modified_stream, next_duration, applied_surge = apply_surge(self.stream.copy(), duration, random_surge=surge_percentage, random_start=False)
        for i in range(duration):
            self.assertAlmostEqual(modified_stream[i], self.stream[i] * surge_percentage, delta=0.1, msg="Surge not correctly applied for the specified duration")
        self.assertEqual(next_duration, 0, "Surge duration not correctly calculated for next stream")
        self.assertEqual(applied_surge, 0, "Surge duration not correctly calculated for next stream")

    def test_apply_sensor_fault(self):
        duration = 100  # Example duration
        modified_stream, next_duration = apply_sensor_fault(self.stream.copy(), duration, random_start=False)
        self.assertEqual(len(modified_stream), 1440, "Sensor fault not correctly applied")
        self.assertEqual(next_duration, 0, "Sensor fault duration not correctly calculated for next stream")

if __name__ == '__main__':
    unittest.main()
