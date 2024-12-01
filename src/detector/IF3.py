from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import numpy as np
from typing import List, Tuple, Generator
from src.simulator import simulator, anomalous_simulator, ANOMALY_THRESHOLD


class AnomalyDetector:
  def __init__(self, n_estimators: int = 100, contamination: float = 0.005):
    """
    Initialize the anomaly detector with an Isolation Forest model.

    Args:
        n_estimators: Number of trees in the forest
        contamination: Expected proportion of anomalies in the dataset
    """
    self.model = IsolationForest(
      n_estimators=n_estimators,
      max_samples='auto',
      contamination=contamination,
      random_state=42,  # For reproducibility
      max_features=1.0
    )
    self.scaler = StandardScaler()
    self.is_fitted = False

  def prepare_data(self, data: List[Tuple[float, int]]) -> np.ndarray:
    """
    Convert data to the correct format and scale features.

    Args:
        data: List of (value, timestamp) tuples

    Returns:
        Scaled numpy array of features
    """
    # Convert to numpy array and reshape for 2D features
    values = np.array([x[0] for x in data]).reshape(-1, 1)
    timestamps = np.array([x[1] for x in data]).reshape(-1, 1)

    # Combine features
    features = np.hstack([values, timestamps])

    # Scale the features
    if not self.is_fitted:
      features = self.scaler.fit_transform(features)
      self.is_fitted = True
    else:
      features = self.scaler.transform(features)

    return features

  def train(self, training_data: List[Tuple[float, int]]) -> None:
    """
    Train the Isolation Forest model on new data.

    Args:
        training_data: List of (value, timestamp) tuples for training
    """
    if len(training_data) < 100:  # Minimum sample size check
      raise ValueError("Not enough training data")

    features = self.prepare_data(training_data)
    self.model.fit(features)

  def detect(self, data: List[Tuple[float, int]]) -> List[Tuple[float, int]]:
    """
    Detect anomalies in new data.

    Args:
        data: List of (value, timestamp) tuples to check for anomalies

    Returns:
        List of anomalous points (value, timestamp)
    """
    features = self.prepare_data(data)
    predictions = self.model.predict(features)
    return [point for point, pred in zip(data, predictions) if pred == -1]


def generate_training_data(num_days: int = 7) -> List[Tuple[float, int]]:
  """
  Generate training data from the nominal simulator.

  Args:
      num_days: Number of days of data to generate

  Returns:
      List of (value, timestamp) tuples
  """
  sim = simulator()
  training_data = []
  for day in range(num_days):
    data = next(sim)
    data_2d = [(value, index + (1440 * day)) for index, value in enumerate(data)]
    training_data.extend(data_2d)
  return training_data


def main():
  # Initialize detector with a very low contamination factor
  detector = AnomalyDetector(n_estimators=100, contamination=500 / (1440 * 7))

  # Train initial model on nominal data
  initial_training_data = generate_training_data()
  detector.train(initial_training_data)

  # Run anomaly detection on live data
  sim = anomalous_simulator()
  last_week_data = []

  for day in range(365):
    # Get new data
    data = next(sim)
    data_2d = [(value, index + (1440 * day)) for index, value in enumerate(data)]

    # Detect anomalies
    anomalies = detector.detect(data_2d)
    print(f"Day {day}: Anomalous points: {len(anomalies)}")

    # Update training window
    last_week_data.extend(data_2d)
    if len(last_week_data) > 1440 * 7:  # Keep only last 7 days
      last_week_data = last_week_data[-1440 * 7:]

    # Retrain weekly
    if day % 7 == 0 and day > 0:
      detector.train(last_week_data)


if __name__ == "__main__":
  main()