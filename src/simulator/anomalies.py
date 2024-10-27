import random
from src.simulator import run_simulation

# Global Sim Values
OUTAGE_THRESHOLD = 0.8

def apply_outage(stream, duration, random_start = True):
  """
  Sets all values in the stream to 0, for the length of the duration

  :param stream: Data stream
  :param duration: Duration of outage in minutes
  :param random_start: Set to False if a continuing outage
  :return: Anomaly inserted stream and duration of next outage
  """
  stream_length = len(stream)
  if random_start:
    start = random.randint(0, stream_length)
  else:
    start = 0

  # Allows the outage to be spread across multiple days
  available = stream_length - start
  if available < duration:
    end = stream_length
    # Duration for the next stream of data
    new_duration = duration - stream_length
  else:
    end = start + duration
    # Duration set to 0 to indicate outage is finished
    new_duration = 0

  for i in range(start, end):
      stream[i] = 0

  return stream, new_duration

def run_simulation_anomalies(start_day = 0, sim_duration = 365):
  sim = run_simulation(start_day, sim_duration)

  # Initial anomalies setup
  outage = False

  for _ in range(sim_duration-start_day):
    datastream =  next(sim)

    # Inserting outage anomaly
    if outage:
      outage_duration = random.randint(1,5000)
      datastream, outage_duration = apply_outage(datastream, outage_duration)

      # Sets outage for next stream
      if outage_duration == 0:
        outage = False
      else:
        outage = True
    else:
      outage = random.random() < OUTAGE_THRESHOLD

    yield datastream

if __name__ == '__main__':
  sim = run_simulation_anomalies()
  for i in sim:
    print(i)
    break