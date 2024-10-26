import unittest
from unittest.mock import patch, mock_open

from src.simulator.stream_generator import *

class TestFlowGenerator(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Sample test data
        self.sample_csv_data = '''Value,Std
                                1.2,0.1
                                0.8,0.2
                                1.0,0.15'''

        # Mock baseline values for testing
        self.mock_baseline = [[1.2, 0.8, 1.0], [0.1, 0.2, 0.15]]

    def test_load_baseline(self):
        """Test the load_baseline function with mock data."""
        with patch('builtins.open', mock_open(read_data=self.sample_csv_data)):
            with patch('pandas.read_csv') as mock_read_csv:
                mock_read_csv.return_value = pd.DataFrame({
                    'Value': [1.2, 0.8, 1.0],
                    'Std': [0.1, 0.2, 0.15]
                })
                result = load_baseline('test.csv')

                self.assertEqual(len(result), 2)
                self.assertEqual(len(result[0]), 3)
                self.assertEqual(len(result[1]), 3)
                self.assertEqual(result[0], [1.2, 0.8, 1.0])
                self.assertEqual(result[1], [0.1, 0.2, 0.15])

    def test_generate_point(self):
        """Test the generate_point function."""
        # Test with various bounds
        for _ in range(100):  # Run multiple times to ensure consistency
            lower, upper = 1.0, 2.0
            point = generate_point(lower, upper)
            self.assertTrue(lower <= point <= upper)

        # Test with equal bounds
        point = generate_point(1.0, 1.0)
        self.assertEqual(point, 1.0)

        # Test with negative bounds
        point = generate_point(-2.0, -1.0)
        self.assertTrue(-2.0 <= point <= -1.0)

    def test_generate_24_hours(self):
        """Test the generate_24_hours function."""
        lower, upper = 1.0, 2.0
        result = generate_24_hours(lower, upper)

        # Test length (1440 minutes in 24 hours)
        self.assertEqual(len(result), 1440)

        # Test all values are within bounds
        for value in result:
            self.assertTrue(lower <= value <= upper)

    def test_get_point_bounds(self):
        """Test the get_point_bounds function."""
        test_cases = [
            (10.0, 2.0, (8.0, 12.0)),  # Normal case
            (0.0, 1.0, (-1.0, 1.0)),  # Zero average
            (-5.0, 2.0, (-7.0, -3.0)),  # Negative average
        ]

        for avg, std, expected in test_cases:
            result = get_point_bounds(avg, std)
            self.assertEqual(result, expected)

    def test_daily_peak_multiplier(self):
        """Test the daily_peak_multiplier function."""
        # Test at specific times
        test_times = [
            (360, 1.0),  # 6 AM
            (1080, 1.0),  # 6 PM
            (0, 1.0),  # Midnight
            (720, 1.0),  # Noon
        ]

        monthly_avg = 50.0
        for minute, expected_base in test_times:
            result = daily_peak_multiplier(minute, monthly_avg)
            self.assertTrue(0.85 <= result <= 1.15)  # Allow for seasonal variation

    def test_gaussian_noise(self):
        """Test the gaussian_noise function."""
        month_avg = 50.0
        daily_peak = 60.0

        # Test multiple times to ensure statistical properties
        noises = [gaussian_noise(month_avg, daily_peak) for _ in range(1000)]

        # Test mean is approximately 0
        mean_noise = sum(noises) / len(noises)
        self.assertTrue(-1 < mean_noise < 1)  # Allow for some random variation

        # Test values are within reasonable bounds
        for noise in noises:
            self.assertTrue(-15 <= noise <= 15)  # Based on pipe capacity

    def test_apply_patterns(self):
        """Test the apply_patterns function."""
        # Create sample stream data
        sample_stream = [50.0] * 1440  # Constant stream for testing
        month_avg = 50.0

        result = apply_patterns(sample_stream, month_avg)

        # Test output length
        self.assertEqual(len(result), 1440)

        # Test values are within reasonable bounds
        for value in result:
            self.assertTrue(0 <= value <= 75)  # Based on max capacity

class TestSimulatorFunctions(unittest.TestCase):

    def test_load_baseline(self):
        result = load_baseline()
        self.assertIsInstance(result, list, "load_baseline did not return a list")
        self.assertEqual(len(result), 2, "load_baseline did not return a list with 2 elements")
        self.assertEqual(len(result[0]), 12, "The first list does not have 12 monthly flow multipliers")
        self.assertEqual(len(result[1]), 12, "The second list does not have 12 monthly standard deviations")

    def test_generate_point(self):
        lower_bound = 10
        upper_bound = 20
        for _ in range(100):
            point = generate_point(lower_bound, upper_bound)
            self.assertGreaterEqual(point, lower_bound, "Generated point is less than lower bound")
            self.assertLessEqual(point, upper_bound, "Generated point is greater than upper bound")

    def test_generate_24_hours(self):
        lower_bound = 10
        upper_bound = 20
        stream = generate_24_hours(lower_bound, upper_bound)
        self.assertEqual(len(stream), 1440, "The length of the generated stream is not 1440")
        for point in stream:
            self.assertGreaterEqual(point, lower_bound, "A point in the stream is less than lower bound")
            self.assertLessEqual(point, upper_bound, "A point in the stream is greater than upper bound")

    def test_get_point_bounds(self):
        month_avg = 50
        month_std = 10
        lower_bound, upper_bound = get_point_bounds(month_avg, month_std)
        self.assertGreater(lower_bound, 20.26, "Lower bound is incorrect")
        self.assertLess(upper_bound, 74.33, "Upper bound is incorrect")

    def test_daily_peak_multiplier(self):
        x = 720  # Example minute (12:00 PM)
        monthly_avg = 60
        multiplier = daily_peak_multiplier(x, monthly_avg)
        self.assertTrue(0.85 <= multiplier <= 1.15, "Multiplier is out of expected range")

    def test_gaussian_noise(self):
        month_avg = 50
        daily_peak = 74.0  # Example peak usage
        noise = gaussian_noise(month_avg, daily_peak)
        self.assertTrue(isinstance(noise, float), "Gaussian noise is not a float")
        self.assertTrue(-0.57 <= noise <= 0.57, "Gaussian noise is out of expected range")

    def test_apply_patterns(self):
        stream = [65] * 1440  # Example uniform stream
        month_avg = 65
        final_stream = apply_patterns(stream, month_avg)
        self.assertEqual(len(final_stream), 1440, "The length of the result stream is not 1440")

if __name__ == '__main__':
    unittest.main()