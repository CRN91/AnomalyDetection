import random
from src.simulator import run_simulation

# Global Sim Values
ANOMALY_MIN_DURATION = 1 # minutes
ANOMALY_MAX_DURATION = 5000 # minutes

OUTAGE_THRESHOLD = 0.001
LEAK_THRESHOLD = 0.001
SURGE_THRESHOLD = 0.001
FAULT_THRESHOLD = 0.8

def duration_calculator(stream_length, duration, random_start=True):
  """
  Calculates the start and end indexes for the data to be affected by an anomaly.
  Calculates the remainder of the duration to apply to the next stream.

  :param stream_length: Length of the datastream list
  :param duration: Length for the anomaly to be applied
  :param random_start: random start if True, else start at beginning
  :return: start index, end index, anomaly duration for the consecutive stream
  """
  # Used on the first affected datastream of duration
  if random_start:
    start = random.randint(0, stream_length)
  else:
    start = 0

  # Allows the anomaly to be spread across multiple days
  available = stream_length - start
  if available < duration:
    end = stream_length
    # Duration for the next stream of data
    next_duration = duration - stream_length
  else:
    end = start + duration
    # Duration set to 0 to indicate anomaly is finished
    next_duration = 0

  return start, end, next_duration

def apply_outage(stream, duration, random_start = True):
  """
  Sets values in the datastream to 0, depending on start and duration conditions.

  :param stream: Datastream to apply outage
  :param duration: Duration for the outage to be applied
  :param random_start: starts at a random index if True, else start at beginning
  :return: altered stream, outage duration for the consecutive stream
  """
  stream_length = len(stream)
  start, end, next_duration = duration_calculator(stream_length, duration, random_start)

  # Python will modify the stream outside of the function so make a copy
  modified_stream = stream.copy()

  for i in range(start, end):
    modified_stream[i] = 0

  return modified_stream, next_duration

def apply_leak(stream, duration, random_leak = 0, random_start = True):
  """
  Applies a multiplier to values in the datastream, depending on start and duration conditions.

  :param stream: Stream to apply leak to
  :param duration: Duration for the leak to apply for
  :param random_leak: The multiplier of the leak, 0 will apply a random leak
  :return: altered stream, leak duration for the consecutive stream, leak percentage
  """
  # If not already set leak percentage, can be between 1% and 10%
  if random_leak == 0:
    random_leak = random.uniform(0.9, 0.99)

  stream_length = len(stream)
  start, end, next_duration = duration_calculator(stream_length, duration, random_start)

  # Python will modify the stream outside of the function so make a copy
  modified_stream = stream.copy()

  for i in range(start, end):
    modified_stream[i] = stream[i] * random_leak

  # Reset leak if completed
  if next_duration == 0:
    random_leak = 0

  return modified_stream, next_duration, random_leak

def apply_surge(stream, duration, random_surge = 0, random_start = True):
  """
  Applies a positive multiplier to values in the datastream, depending on start and duration conditions.
  Caps value at 75.

  :param stream: Stream to apply surge to
  :param duration: Duration for the surge to apply for
  :param random_surge: The multiplier of the surge, 0 will apply a random surge
  :return: altered stream, surge duration for the consecutive stream, surge percentage
  """
  # If not already set surge percentage, can be between 1% and 10%
  if random_surge == 0:
    random_surge = random.uniform(1.01, 1.1)

  stream_length = len(stream)
  start, end, next_duration = duration_calculator(stream_length, duration, random_start)

  # Python will modify the stream outside of the function so make a copy
  modified_stream = stream.copy()

  for i in range(start, end):
    surge_value = min(75, stream[i] * random_surge) # Max capacity is 75
    modified_stream[i] = surge_value

  # Reset surge if completed
  if next_duration == 0:
    random_surge = 0

  return modified_stream, next_duration, random_surge

def apply_sensor_fault(stream, duration, random_start = True):
  """
  Makes values in the datastream random with a gaussian function, depending on start and duration conditions.
  Mu and sigma set to the data point and 5 respectively

  :param stream: Stream to apply fault to
  :param duration: Duration for the fault to apply for
  :param random_start: starts at a random index if True, else start at beginning
  :return: altered stream, fault duration for the consecutive stream
  """
  stream_length = len(stream)
  start, end, next_duration = duration_calculator(stream_length, duration, random_start)

  # Python will modify the stream outside of the function so make a copy
  modified_stream = stream.copy()

  for i in range(start, end):
    fault_value = random.gauss(stream[i], 5)
    if fault_value > 75: # min function doesn't work with floats
      fault_value = 75
    modified_stream[i] = fault_value

  return modified_stream, next_duration

def run_simulation_anomalies(start_day = 0, sim_duration = 365):
  """
  Runs the Gas Flow Simulation and randomly applying anomalies to the datastream.

  :param start_day: The day of the year to start the simulation
  :param sim_duration: Length of the simulation (Each event represents a minute)
  :return: 24 hours of Gas Flow data represented as a list of floats, chance to have anomalies
  """
  sim = run_simulation(start_day, sim_duration)

  # Initial anomalies setup
  outage = False
  leak = False
  leak_percentage = 0
  surge = False
  surge_percentage = 0
  fault = False

  for _ in range(sim_duration-start_day):
    datastream =  next(sim)

    # Inserting outage anomaly
    if outage:
      outage_duration = random.randint(ANOMALY_MIN_DURATION,ANOMALY_MAX_DURATION)
      datastream, outage_duration = apply_outage(datastream, outage_duration, random_start = False)

      # Sets outage for next stream
      if outage_duration == 0:
        outage = False
      else:
        outage = True
    else:
      outage = random.random() < OUTAGE_THRESHOLD

    # Inserting leak anomaly
    if leak:
      leak_duration = random.randint(ANOMALY_MIN_DURATION, ANOMALY_MAX_DURATION)
      datastream, leak_duration, leak_percentage = apply_leak(datastream, leak_duration, leak_percentage)

      # Sets leak for next stream
      if leak_duration == 0:
        leak = False
      else:
        leak = True
    else:
      leak = random.random() < LEAK_THRESHOLD

    # Inserting surge anomaly
    if surge:
      surge_duration = random.randint(ANOMALY_MIN_DURATION, ANOMALY_MAX_DURATION)
      datastream, surge_duration, surge_percentage = apply_surge(datastream, surge_duration, surge_percentage)

      # Sets surge for next stream
      if surge_duration == 0:
        surge = False
      else:
        surge = True
    else:
      surge = random.random() < SURGE_THRESHOLD

    # Inserting sensor fault anomaly
    if fault:
      fault_duration = random.randint(ANOMALY_MIN_DURATION, ANOMALY_MAX_DURATION)
      datastream, fault_duration = apply_sensor_fault(datastream, fault_duration, random_start=False)

      # Sets outage for next stream
      if fault_duration == 0:
        fault = False
      else:
        fault = True
    else:
      fault = random.random() < FAULT_THRESHOLD

    yield datastream

if __name__ == '__main__':
  sim = run_simulation_anomalies()
  count = 0
  for i in sim:
    print(i)
    if count == 1:
      break
    count +=1