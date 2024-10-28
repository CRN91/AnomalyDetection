import numpy as np
from typing import List, Tuple, Optional
from collections import deque

from src.simulator import run_simulation_anomalies


def initialize_baseline(first_day_data: List[float]) -> Tuple[np.ndarray, float]:
  """Initialize the baseline pattern and seasonal rate from first day's data."""
  data = np.array(first_day_data)
  daily_avg = np.mean(data)
  daily_max = np.max(data)
  seasonal_rate = max(0.85, 1 - (daily_avg / daily_max))

  # Remove seasonality to get base pattern
  base_pattern = data / seasonal_rate

  return base_pattern, seasonal_rate


def calculate_expected_value(minute: int, base_pattern: np.ndarray, seasonal_rate: float) -> float:
  """Calculate expected value for a given minute considering daily pattern and seasonality."""
  return base_pattern[minute] * seasonal_rate


def update_ema(current: float, previous: float, alpha: float) -> float:
  """Calculate EMA with smoothing factor alpha."""
  return alpha * current + (1 - alpha) * previous


def detect_anomalies(
    new_data: List[float],
    base_pattern: np.ndarray,
    seasonal_rate: float,
    threshold_std: float = 8.0,
    ema_alpha: float = 0.1,
    pattern_update_alpha: float = 0.05,
    seasonal_update_alpha: float = 0.01,
    history_window: int = 1440 * 7  # 7 days of history
) -> Tuple[List[bool], np.ndarray, float]:
  """
  Detect anomalies in new data while adapting to changing patterns and seasonality.

  Args:
      new_data: List of new measurements (1440 points for one day)
      base_pattern: Current baseline daily pattern
      seasonal_rate: Current seasonal rate
      threshold_std: Number of standard deviations for anomaly threshold
      ema_alpha: Smoothing factor for the main EMA
      pattern_update_alpha: Learning rate for updating the base pattern
      seasonal_update_alpha: Learning rate for updating seasonal rate
      history_window: Number of historical points to keep for threshold calculation

  Returns:
      Tuple of (anomaly flags, updated base pattern, updated seasonal rate)
  """
  anomalies = []
  updated_pattern = base_pattern.copy()
  updated_seasonal_rate = seasonal_rate

  # Initialize historical deviations storage
  historical_deviations = deque(maxlen=history_window)

  # Process each point in the new data
  for i, value in enumerate(new_data):
    # Calculate expected value
    expected = calculate_expected_value(i, updated_pattern, updated_seasonal_rate)

    # Calculate deviation
    deviation = abs(value - expected)
    historical_deviations.append(deviation)

    # Calculate dynamic threshold using historical deviations
    threshold = np.std(historical_deviations) * threshold_std

    # Detect anomaly
    is_anomaly = deviation > threshold
    #anomalies.append(is_anomaly)

    # Update pattern and seasonality only if not an anomaly
    if not is_anomaly:
      # Update base pattern
      normalized_value = value / updated_seasonal_rate
      updated_pattern[i] = update_ema(normalized_value, updated_pattern[i], pattern_update_alpha)

      # Update seasonal rate
      daily_avg = np.mean(new_data[:i + 1])
      daily_max = np.max(new_data[:i + 1])
      new_seasonal_rate = max(0.85, 1 - (daily_avg / daily_max))
      updated_seasonal_rate = update_ema(
        new_seasonal_rate,
        updated_seasonal_rate,
        seasonal_update_alpha
      )
    else:
      anomalies.append(i)

  return anomalies, updated_pattern, updated_seasonal_rate

def generate_simulation_data(start_day=0, duration=365):
  """
  Generate all simulation data upfront to avoid reset issues.

  Args:
      start_day: day to start at in year (int)
      duration: Number of days to process

  Returns:
      List of daily data lists
  """
  sim = run_simulation_anomalies(start_day, duration)
  all_days = []

  for _ in range(duration):
    day_data = next(sim)
    all_days.append(day_data)

  return all_days


def process_simulation(start_day=0, duration=365):
  """
  Process multiple days of simulation data.

  Args:
      start_day: day to start at in year (int)
      duration: Number of days to process

  Yields:
      Tuple of (day_data, anomalies) for each day
  """
  # Get all simulation data upfront
  all_days = generate_simulation_data(start_day, duration)

  # Initialize with first day
  first_day = all_days[0]
  base_pattern, seasonal_rate = initialize_baseline(first_day)

  # Process first day's anomalies
  first_day_anomalies, base_pattern, seasonal_rate = detect_anomalies(
    first_day,
    base_pattern,
    seasonal_rate
  )

  # Yield first day's data and anomalies
  yield first_day, first_day_anomalies

  # Process subsequent days
  for day_data in all_days[1:]:
    anomalies, base_pattern, seasonal_rate = detect_anomalies(
      day_data,
      base_pattern,
      seasonal_rate
    )
    yield day_data, anomalies

if __name__ == '__main__':
  # Example usage
  for day_data, anomalies in process_simulation(start_day=0, duration=365):
    # Do something with each day's data and anomalies
    num_anomalies = sum(anomalies)
    print(f"Found {num_anomalies} anomalies in day")