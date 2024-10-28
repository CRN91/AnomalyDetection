import random
from src.simulator import simulator
from src.utils import load_config

# Global Sim Values
try:
  MAX_CAPACITY = float(load_config()['max_capacity'])
except KeyError:
  MAX_CAPACITY = 75

ANOMALY_MULTIPLIER_BOUNDS = [
  (0,0), # outage
  (0.9,0.95), # leak
  (1.05,1.1), # surge
  (-5,5) # sensor fault
]
ANOMALY_MIN_DURATION = 1 # minutes
ANOMALY_MAX_DURATION = 5000 # minutes
ANOMALY_THRESHOLD = 0.005

def inject_anomaly(stream, anomaly_multiplier, start, duration):
  """
  Applies a multiplier to values in the datastream, depending on start and duration conditions.

  :param stream: Stream to apply anomaly to
  :param anomaly_multiplier: Data point is multiplied by this number
  :param start: start index of anomaly
  :param duration: Duration for the anomaly to apply for
  :return: altered stream, anomaly duration for the consecutive stream
  """
  stream_length = len(stream)
  end = start + duration
  duration =  max(0, end - stream_length) # Remaining duration
  end = min(stream_length, end) # End can't be out of index

  # Handles incorrect start values
  if start < stream_length:
    for i in range(start, end):
      anomaly = min(MAX_CAPACITY, stream[i] * anomaly_multiplier) # Max capacity is 75
      stream[i] = anomaly
  else:
    duration = 0 # No remaining duration for incorrect start

  return stream, duration # duration for next stream

def anomalous_simulator(start_day = 0, sim_duration = 365):
  """
  Runs the Gas Flow Simulation and randomly applying anomalies to the datastream.

  :param start_day: The day of the year to start the simulation
  :param sim_duration: Length of the simulation (Each event represents a minute)
  :return: 24 hours of Gas Flow data represented as a list of floats, chance to have anomalies
  """
  sim = simulator(start_day, sim_duration)

  # Initial anomalies setup
  anomaly = False

  for _ in range(sim_duration-start_day):
    datastream =  next(sim)

    # Inserting anomaly
    if anomaly:
      # Values are random
      anomaly_start = random.randint(0,1440)
      anomaly_duration = random.randint(ANOMALY_MIN_DURATION,ANOMALY_MAX_DURATION)
      anomaly_multiplier_bounds = random.choices(ANOMALY_MULTIPLIER_BOUNDS) # Type of anomaly
      anomaly_multiplier = random.uniform(anomaly_multiplier_bounds[0],anomaly_multiplier_bounds[1])

      datastream, anomaly_duration = inject_anomaly(datastream, anomaly_multiplier, anomaly_start, anomaly_duration)

      # Sets outage for next stream
      anomaly = (anomaly_duration == 0)
    else:
      # Randomly assigns next stream to be an anomaly
      anomaly = random.random() < ANOMALY_THRESHOLD

    yield datastream

if __name__ == '__main__':
  sim = anomalous_simulator()
  count = 0
  for i in sim:
    print(i)
    if count == 5:
      break
    count +=1