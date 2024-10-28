from dataclasses import dataclass
from typing import List, Optional, Tuple, Callable
from src.simulator import run_simulation_anomalies
import random
import math
from statistics import mean

sim = run_simulation_anomalies()


# Enhanced data structures to handle time context
@dataclass(frozen=True)
class TimePoint:
  """Represents a single time point with its minute-of-day context"""
  value: float
  minute: int  # 0-1439 (24*60-1)


@dataclass(frozen=True)
class IsolationNode:
  """Immutable node for isolation tree with time awareness"""
  split_value: Optional[float]
  time_window: Tuple[int, int]  # Start and end minutes of the window
  below: Optional['IsolationNode'] = None
  above: Optional['IsolationNode'] = None
  size: int = 0


@dataclass(frozen=True)
class IsolationTree:
  root: IsolationNode
  max_depth: int


@dataclass(frozen=True)
class IsolationForest:
  trees: Tuple[IsolationTree, ...]
  sample_size: int
  n_trees: int


def get_batch():
  return next(sim)


def convert_to_timepoints(data: List[float]) -> List[TimePoint]:
  """Convert raw values to TimePoints with minute-of-day context"""
  return [TimePoint(value, minute % 1440) for minute, value in enumerate(data)]


def get_expected_range(minute: int, window_size: int = 60) -> Tuple[int, int]:
  """Get the expected range for a given minute considering daily cycles"""
  start_minute = (minute - window_size // 2) % 1440
  end_minute = (minute + window_size // 2) % 1440
  return start_minute, end_minute


def is_similar_time(point_minute: int, window_start: int, window_end: int) -> bool:
  """Check if a point falls within the time window, handling day wraparound"""
  if window_start <= window_end:
    return window_start <= point_minute <= window_end
  else:  # Window wraps around midnight
    return point_minute >= window_start or point_minute <= window_end


def get_data_bounds(timepoints: List[TimePoint]) -> Tuple[float, float]:
  """Get min and max values from TimePoints"""
  values = [tp.value for tp in timepoints]
  return min(values), max(values)


def gen_split_value(min_val: float, max_val: float) -> float:
  return random.uniform(min_val, max_val)


def split_data(timepoints: List[TimePoint], split_value: float) -> Tuple[List[TimePoint], List[TimePoint]]:
  """Split TimePoints based on their values"""
  below = [tp for tp in timepoints if tp.value < split_value]
  above = [tp for tp in timepoints if tp.value >= split_value]
  return below, above


def build_isolation_tree(timepoints: List[TimePoint], max_depth: int, current_depth: int = 0) -> IsolationNode:
  n_samples = len(timepoints)

  if current_depth >= max_depth or n_samples <= 1:
    # Get time window for the leaf node
    if timepoints:
      minutes = [tp.minute for tp in timepoints]
      time_window = (min(minutes), max(minutes))
    else:
      time_window = (0, 0)

    return IsolationNode(
      split_value=None,
      time_window=time_window,
      size=n_samples
    )

  min_val, max_val = get_data_bounds(timepoints)

  if min_val == max_val:
    minutes = [tp.minute for tp in timepoints]
    time_window = (min(minutes), max(minutes))
    return IsolationNode(
      split_value=None,
      time_window=time_window,
      size=n_samples
    )

  split_value = gen_split_value(min_val, max_val)
  below_data, above_data = split_data(timepoints, split_value)

  # Calculate time window for current node
  minutes = [tp.minute for tp in timepoints]
  time_window = (min(minutes), max(minutes))

  return IsolationNode(
    split_value=split_value,
    time_window=time_window,
    below=build_isolation_tree(below_data, max_depth, current_depth + 1),
    above=build_isolation_tree(above_data, max_depth, current_depth + 1),
    size=n_samples
  )


def sample_data(timepoints: List[TimePoint], sample_size: int) -> List[TimePoint]:
  return random.sample(timepoints, min(sample_size, len(timepoints)))

def build_isolation_forest(
    data: List[float],
    n_trees: int = 100,
    sample_size: Optional[int] = None
) -> IsolationForest:
  timepoints = convert_to_timepoints(data)

  if sample_size is None:
    sample_size = min(256, len(timepoints))

  max_depth = int(math.ceil(math.log2(sample_size)))

  trees = tuple(
    IsolationTree(
      root=build_isolation_tree(
        sample_data(timepoints, sample_size),
        max_depth
      ),
      max_depth=max_depth
    )
    for _ in range(n_trees)
  )

  return IsolationForest(
    trees=trees,
    sample_size=sample_size,
    n_trees=n_trees
  )

def average_path_length(n: int) -> float:
  """
  Compute average path length in unsuccessful search in BST.
  This is the normalization factor for the isolation forest.

  Args:
      n: number of samples
  Returns:
      float: average path length
  """
  if n <= 1:
    return 0
  return 2 * (math.log(n - 1) + 0.5772156649) - (2 * (n - 1) / n)

def compute_anomaly_score(
    value: float,
    minute: int,
    forest: IsolationForest
) -> float:
  point = TimePoint(value, minute)
  path_lengths = [
    compute_path_length(point, tree.root)
    for tree in forest.trees
  ]

  mean_path_length = mean(path_lengths)
  c = average_path_length(forest.sample_size)
  score = 2 ** (-(mean_path_length / c))

  return score

def get_expected_value(minute: int, seasonal_rate: float = 0.15) -> float:
  """Calculate expected value for a given minute based on seasonal pattern"""
  return seasonal_rate * math.cos(4 * math.pi * minute / 1440 + math.pi) + 1


def get_noise_bounds() -> float:
  """Get expected noise bounds (3 standard deviations)"""
  return 3 * 0.02  # 3 sigma for 99.7% of normal distribution


def is_within_normal_bounds(point: TimePoint) -> bool:
  """Check if a point falls within expected bounds given time and noise"""
  expected = get_expected_value(point.minute)
  noise_margin = get_noise_bounds()
  return abs(point.value - expected) <= noise_margin


def compute_path_length(point: TimePoint, node: IsolationNode, current_height: int = 0) -> int:
  """Compute path length considering time context and expected variation"""
  if node.below is None and node.above is None:
    return current_height

  # If the point is within expected bounds, treat it as normal
  if is_within_normal_bounds(point):
    return max(current_height - 1, 0)  # Reduce path length for normal points

  # Consider the point's time context when computing path length
  if not is_similar_time(point.minute, node.time_window[0], node.time_window[1]):
    return current_height  # Stop early if we're in a different time context

  if point.value < node.split_value:
    return compute_path_length(point, node.below, current_height + 1)
  return compute_path_length(point, node.above, current_height + 1)


def find_anomalies(
    data: List[float],
    threshold: float = 0.8,  # Increased threshold to be even more conservative
    n_trees: int = 100,
    sample_size: Optional[int] = None
) -> Tuple[List[float], List[float]]:
  """Find anomalies considering time-of-day patterns and noise tolerance"""
  forest = build_isolation_forest(data, n_trees, sample_size)

  # Score each point with its time context
  scored_data = [
    (value, compute_anomaly_score(value, minute % 1440, forest))
    for minute, value in enumerate(data)
  ]

  # First filter: basic threshold
  potential_anomalies = [
    (value, minute)
    for minute, (value, score) in enumerate(scored_data)
    if score > threshold
  ]

  # Second filter: check against expected pattern
  true_anomalies = [
    value
    for value, minute in potential_anomalies
    if not is_within_normal_bounds(TimePoint(value, minute % 1440))
  ]

  normal_points = [
    value
    for value in data
    if value not in true_anomalies
  ]

  return normal_points, true_anomalies

def example_usage():
  data = get_batch()
  normal_points, anomaly_points = find_anomalies(
    data,
    threshold=0.95,  # More conservative threshold
    n_trees=100
  )

  print(f"Number of normal points: {len(normal_points)}")
  print(f"Number of anomalies detected: {len(anomaly_points)}")
  print(data)
  if anomaly_points:
    print("\nDetected anomalies:")
    print(sorted(anomaly_points))


##########
from dataclasses import dataclass
from typing import List, Optional, Tuple, Callable, Generator, Iterator
from src.simulator import run_simulation_anomalies
import random
import math
from statistics import mean


# Keep all existing classes and helper functions...
# (TimePoint, IsolationNode, IsolationTree, IsolationForest definitions remain the same)

def continuous_anomaly_detection(
    data_generator: Iterator[List[float]],
    threshold: float = 0.8,
    n_trees: int = 100,
    sample_size: Optional[int] = None
) -> Generator[Tuple[List[float], List[int]], None, None]:
  """
  Continuously process batches of data and yield both the data and anomaly indices.

  Args:
      data_generator: Generator/Iterator that yields batches of data
      threshold: Anomaly score threshold
      n_trees: Number of trees in the isolation forest
      sample_size: Sample size for building trees

  Yields:
      Tuple containing:
      - List[float]: The original data batch
      - List[int]: Indices of detected anomalies in the batch
  """
  while True:
    try:
      # Get next batch of data
      data = next(data_generator)

      # Build forest and get anomaly scores
      forest = build_isolation_forest(data, n_trees, sample_size)

      # Score each point with its time context and track indices
      scored_data = [
        (value, compute_anomaly_score(value, minute % 1440, forest), minute)
        for minute, value in enumerate(data)
      ]

      # First filter: basic threshold
      potential_anomalies = [
        (value, minute)
        for value, score, minute in scored_data
        if score > threshold
      ]

      # Second filter: check against expected pattern and collect indices
      anomaly_indices = [
        minute
        for value, minute in potential_anomalies
        if not is_within_normal_bounds(TimePoint(value, minute % 1440))
      ]

      yield data, sorted(anomaly_indices)

    except StopIteration:
      break

def run_sim_anomaly_detector(start_day=0,duration = 365):
  # Create the simulator
  sim = run_simulation_anomalies(start_day,duration)

  # Create the continuous detector
  detector = continuous_anomaly_detection(
    data_generator=sim,
    threshold=0.95,  # More conservative threshold
    n_trees=100
  )

  # Process multiple batches
  for batch_num, (data, anomaly_indices) in enumerate(detector, 1):
    yield (data, anomaly_indices)

if __name__ == "__main__":
  run_sim_anomaly_detector()