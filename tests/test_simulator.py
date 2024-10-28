import unittest
from unittest.mock import patch
import pandas as pd
import numpy as np
from src.simulator.stream_generator import (
    generate_point, generate_24_hours, get_point_bounds,
    calculate_seasonal_multiplier, daily_peak_multiplier,
    gaussian_noise, apply_patterns, setup, run_simulation
)

class TestGasFlowSimulator(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.sample_daily_avg = 50.0
        self.max_daily_avg = 73.65
        self.max_capacity = 75

    def test_generate_point_normal(self):
        """Test generate_point with normal bounds"""
        lower, upper = 45.0, 55.0
        point = generate_point(lower, upper)
        self.assertTrue(lower <= point <= upper)

    def test_generate_point_equal_bounds(self):
        """Test generate_point with equal bounds"""
        value = 50.0
        point = generate_point(value, value)
        self.assertEqual(point, value)

    def test_generate_point_negative_bounds(self):
        """Test generate_point with negative bounds"""
        lower, upper = -10.0, -5.0
        point = generate_point(lower, upper)
        self.assertTrue(lower <= point <= upper)

    def test_generate_24_hours_length(self):
        """Test generate_24_hours returns correct number of points"""
        points = generate_24_hours(self.sample_daily_avg)
        self.assertEqual(len(points), 1440)  # 24 hours * 60 minutes

    def test_generate_24_hours_bounds(self):
        """Test all points in generate_24_hours are within bounds"""
        points = generate_24_hours(self.sample_daily_avg)
        lower, upper = get_point_bounds(self.sample_daily_avg)
        self.assertTrue(all(lower <= point <= upper for point in points))

    def test_get_point_bounds(self):
        """Test get_point_bounds calculations"""
        daily_avg = 100.0
        lower, upper = get_point_bounds(daily_avg)
        self.assertEqual(lower, 99.0)  # 100 - (100 * 0.01)
        self.assertEqual(upper, 101.0)  # 100 + (100 * 0.01)

    def test_calculate_seasonal_multiplier_normal(self):
        """Test seasonal multiplier calculation with normal value"""
        multiplier = calculate_seasonal_multiplier(50.0)
        self.assertTrue(0 <= multiplier <= 0.15)

    def test_calculate_seasonal_multiplier_max(self):
        """Test seasonal multiplier calculation with maximum daily average"""
        multiplier = calculate_seasonal_multiplier(self.max_daily_avg)
        self.assertEqual(multiplier, 0.0)

    def test_calculate_seasonal_multiplier_high(self):
        """Test seasonal multiplier caps at 0.15"""
        multiplier = calculate_seasonal_multiplier(0.0)
        self.assertEqual(multiplier, 0.15)

    def test_daily_peak_multiplier_key_times(self):
        """Test daily peak multiplier at key times (6am, 12pm, 6pm)"""
        seasonal_rate = 0.1
        # 6 AM (360 minutes)
        self.assertAlmostEqual(
            daily_peak_multiplier(360, seasonal_rate),
            1 + seasonal_rate,
            places=2
        )
        # 6 PM (1080 minutes)
        self.assertAlmostEqual(
            daily_peak_multiplier(1080, seasonal_rate),
            1 + seasonal_rate,
            places=2
        )

    def test_gaussian_noise_distribution(self):
        """Test gaussian noise distribution properties"""
        samples = [gaussian_noise() for _ in range(1000)]
        mean = np.mean(samples)
        std = np.std(samples)
        # Check if mean is close to 0
        self.assertAlmostEqual(mean, 0, places=1)
        # Check if standard deviation is close to 0.02
        self.assertAlmostEqual(std, 0.02, places=1)

    def test_apply_patterns_length(self):
        """Test apply_patterns maintains correct length"""
        stream = [50.0] * 1440
        result = apply_patterns(stream, self.sample_daily_avg)
        self.assertEqual(len(result), 1440)

    def test_apply_patterns_variation(self):
        """Test apply_patterns introduces variation"""
        stream = [50.0] * 1440
        result = apply_patterns(stream, self.sample_daily_avg)
        # Check that values have been modified
        self.assertNotEqual(result, stream)
        # Check that values vary throughout the day
        self.assertNotEqual(result[0], result[720])

    @patch('pandas.read_csv')
    def test_setup_normal(self, mock_read_csv):
        """Test setup with mock CSV file"""
        mock_data = pd.DataFrame({'value': range(365)})
        mock_read_csv.return_value = mock_data
        result = setup()
        self.assertEqual(len(result), 365)

    def test_run_simulation_generator(self):
        """Test run_simulation returns a generator"""
        sim = run_simulation(0, 1)
        self.assertTrue(hasattr(sim, '__iter__'))
        self.assertTrue(hasattr(sim, '__next__'))

    def test_run_simulation_output(self):
        """Test run_simulation output format"""
        sim = run_simulation(0, 1)
        first_day = next(sim)
        self.assertEqual(len(first_day), 1440)
        # Verify values are reasonable
        self.assertTrue(all(isinstance(x, float) for x in first_day))

    def test_run_simulation_wrap_around(self):
        """Test run_simulation handles year wrap-around"""
        sim = run_simulation(364, 2)
        day1 = next(sim)
        day2 = next(sim)
        self.assertEqual(len(day1), 1440)
        self.assertEqual(len(day2), 1440)

if __name__ == '__main__':
    unittest.main()