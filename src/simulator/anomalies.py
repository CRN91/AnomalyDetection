import random
from src.simulator import run_simulation

# Global Sim Values
OUTAGE_THRESHOLD = 0.001
LEAK_THRESHOLD = 0.8

def duration_calculator(stream_length, duration, random_start=True):
  if random_start:
    start = random.randint(0, stream_length)
  else:
    start = 0

  # Allows the outage to be spread across multiple days
  available = stream_length - start
  if available < duration:
    end = stream_length
    # Duration for the next stream of data
    next_duration = duration - stream_length
  else:
    end = start + duration
    # Duration set to 0 to indicate outage is finished
    next_duration = 0

  return start, end, next_duration

def apply_outage(stream, duration, random_start = True):
  stream_length = len(stream)
  start, end, next_duration = duration_calculator(stream_length, duration, random_start)

  for i in range(start, end):
    stream[i] = 0

  return stream, next_duration

def apply_leak(stream, duration, random_leak = 0):
  stream_length = len(stream)
  start, end, next_duration = duration_calculator(stream_length, duration)

  # If not already set leak percentage can be between 1% and 10%
  if random_leak == 0:
    random_leak = random.uniform(0.9,0.99)

  for i in range(start, end):
    stream[i] = stream[i] * random_leak

  # Reset leak if completed
  if next_duration == 0:
    random_leak = 0

  return stream, next_duration, random_leak

def run_simulation_anomalies(start_day = 0, sim_duration = 365):
  sim = run_simulation(start_day, sim_duration)

  # Initial anomalies setup
  outage = False
  leak = False
  leak_percentage = 0

  for _ in range(sim_duration-start_day):
    datastream =  next(sim)

    # Inserting outage anomaly
    if outage:
      outage_duration = random.randint(1,5000)
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
      leak_duration = random.randint(1, 5000)
      datastream, leak_duration, leak_percentage = apply_leak(datastream, leak_duration, leak_percentage)

      # Sets outage for next stream
      if leak_duration == 0:
        leak = False
      else:
        leak = True
    else:
      leak = random.random() < LEAK_THRESHOLD



    yield datastream

if __name__ == '__main__':
  sim = run_simulation_anomalies()
  count = 0
  for i in sim:
    print(i)
    if count == 1:
      break
    count +=1