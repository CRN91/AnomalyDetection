# Generate stream of floating point numbers, regular patterns, seasonal elements, random noise and anomalies
import random
import pandas as pd
import math
import os

def generate_point(lower_bound, upper_bound):
  return random.uniform(lower_bound, upper_bound)

def generate_24_hours(lower_bound, upper_bound):
  return [generate_point(lower_bound, upper_bound) for _ in range(1440)]

def get_point_bounds(daily_avg):
  return daily_avg*0.99, daily_avg*1.01

def daily_peak_multiplier(x, daily_avg, daily_max_actual = 74.43):
  """
  Calculates a value multiplier according to peak times of the day.
  No data available so assumption is it follows energy usage with peak
  times being at 6am and 6pm, using a cosine to gradually transition
  between.

  Parameters
  :param x (int): The minute of the day.

  Returns
  :return (float): The peak time multiplier of that minute.
  """
  # Cosine graph with 2 peaks in our range of 1440 minutes located at 6am and 6pm
  seasonal_rate = 1 - (daily_avg/daily_max_actual)
  if seasonal_rate > 0.15:
    seasonal_rate = 0.15
  return seasonal_rate*math.cos(4*math.pi*x/1440 + math.pi) + 1

def gaussian_noise(daily_avg, daily_peak, daily_max_actual = 74.43, max_capacity = 75):
  """
  Gaussian Noise to add to stream. Mean is around 0 so shouldn't affect
  the actual daily mean of the data. Sigma is set to 5% of the monthly mean.

  :param daily_avg: The daily average of the data.
  :param daily_peak: The daily peak of the data.
  :return random float:
  """
  # Values we can play around with to prevent exceeding limit of the pipe
  pipe_difference = max_capacity - daily_peak
  # Desired sigma: 3% of the monthly average
  desired_sigma = daily_avg * 0.03
  # Final sigma: min of desired sigma and max allowed noise
  final_sigma = min(desired_sigma, pipe_difference / 4)

  # Generate Gaussian noise and cap the value
  noise = random.gauss(0, final_sigma)
  capped_noise = min(max(noise, -pipe_difference), pipe_difference)

  return capped_noise

def apply_patterns(stream,daily_avg):
  """
  Takes the seasonally distributed stream values of a single day and applies
  daily peak time and Gaussian noise patterns.

  Parameters
  :param stream (list of floats): Uniformly distributed random stream values.
  :param daily_avg (float): The daily average of the stream.
  :return (list of floats): The generated stream with patterns applied.
  """
  #new_stream = pd.Series(dtype="float64")
  new_stream = []
  # Iterates through each minute of the day
  for i in range(1440):
    # Daily peak multiplier
    daily_peak = stream[i]*daily_peak_multiplier(i,daily_avg)
    # Each month's standard deviation is used for the Gaussian noise
    noise = gaussian_noise(daily_avg,daily_peak)
    # Patterns are applied to each value
    #new_stream = new_stream._append(pd.Series([daily_peak+noise]))
    new_stream.append(daily_peak + noise)
  return new_stream

def setup():
  """
  Reads and returns baseline values

  :return: avg_days list of mean daily values
  """
  # Lookup table of interpolated gas flow graph
  file_path = os.path.join(os.path.dirname(__file__),"gas_flow_lookup_table.csv")
  avg_days = list(pd.read_csv(file_path)['value'])
  return avg_days

def run_simulation(start_day = 0, duration = 365):
  """
  Runs the main simulation loop after setting up. Default to 1 year of data.
  Returns the completed datastream.

  :param start_day (int): day to begin the sim 0<=day<365
  :param duration (int): how many days to simulate
  :return: completed datastream where each value represents the gas flow per day at that minute.
  """
  print("Starting Simulation")
  avg_days = setup()
  #datastream = []
  # Iterate through each day, generating a stream of data for each minute
  for day in range(start_day, start_day+duration):
    if start_day > 364:
      start_day = start_day % 364

    # Gets the baselines for these values
    daily_flow_mean = avg_days[day]

    # Generate the stream
    lower_bound, upper_bound = get_point_bounds(daily_flow_mean)
    stream = generate_24_hours(lower_bound, upper_bound)

    final_stream = apply_patterns(stream, daily_flow_mean)

    yield final_stream

if __name__ == '__main__':
  run_simulation()
