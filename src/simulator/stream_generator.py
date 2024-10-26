# Generate stream of floating point numbers, regular patterns, seasonal elements, random noise and anomalies
import random
import pandas as pd
import math
import os

def load_baseline(filename = "Monthly_Baselines.csv"):
  """ Loads the Monthly Flow Multipliers and Standard Deviations from a csv file.

  Parameters
  :param filename (string): The file name of the csv file stored in this directory.

  Returns
  :return (list): A list with 2 lists inside. The former being the monthly flow multipliers
  and the later being the monthly standard deviations.
  """
  # Gets the file path
  base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "simulator"))
  file_path = os.path.join(base_path, filename)

  return [list(pd.read_csv(file_path)["Value"]), list(pd.read_csv(file_path)["Std"])]

def generate_point(lower_bound, upper_bound):
  return random.uniform(lower_bound, upper_bound)

def generate_24_hours(lower_bound, upper_bound):
  return [generate_point(lower_bound, upper_bound) for _ in range(1440)]

def get_point_bounds(month_avg, month_std):
  return month_avg-month_std, month_avg+month_std

def daily_peak_multiplier(x, monthly_avg, daily_max_actual = 74.43):
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
  seasonal_rate = 1 - (monthly_avg/daily_max_actual)
  if seasonal_rate > 0.15:
    seasonal_rate = 0.15
  return seasonal_rate*math.cos(4*math.pi*x/1440 + math.pi) + 1

def gaussian_noise(month_avg, daily_peak, daily_max_actual = 74.43, max_capacity = 75):
  """
  Gaussian Noise to add to stream. Mean is around 0 so shouldn't affect
  the actual daily mean of the data. Sigma is set to 5% of the monthly mean.

  :param month_std:
  :return random float:
  """
  # Values we can play around with to prevent exceeding limit of the pipe
  pipe_difference = max_capacity - daily_peak
  # Desired sigma: 3% of the monthly average
  desired_sigma = month_avg * 0.03
  # Final sigma: min of desired sigma and max allowed noise
  final_sigma = min(desired_sigma, pipe_difference / 4)

  # Generate Gaussian noise and cap the value
  noise = random.gauss(0, final_sigma)
  print("daily peak {} and final sigma {}".format(daily_peak, final_sigma))
  capped_noise = min(max(noise, -pipe_difference), pipe_difference)

  return capped_noise

def apply_patterns(stream,month_avg):
  """
  Takes the seasonally distributed stream values of a single day and applies
  daily peak time and Gaussian noise patterns.

  Parameters
  :param stream (list of floats): Uniformly distributed random stream values.
  :param month (int 0 < month <= 11): The month of that day.
  :return (list of floats): The generated stream with patterns applied.
  """
  new_stream = pd.Series(dtype="float64")
  # Iterates through each minute of the day
  for i in range(1440):
    # Daily peak multiplier
    daily_peak = stream[i]*daily_peak_multiplier(i,month_avg)
    # Each month's standard deviation is used for the Gaussian noise
    noise = gaussian_noise(month_avg,daily_peak)
    # Patterns are applied to each value
    new_stream = new_stream._append(pd.Series([daily_peak+noise]))
  return new_stream

if __name__ == '__main__':
  # Get month multipliers
  avg_months, std_months = load_baseline()

  # Get a random monthly multiplier
  month = random.randint(0, 11)
  month = 5
  month_avg = avg_months[month]
  month_std = std_months[month]
  print(month_avg, month_std)

  # Generate the stream
  lower_bound, upper_bound = get_point_bounds(month_avg, month_std)
  stream = generate_24_hours(lower_bound, upper_bound)

  final_stream = apply_patterns(stream,month_avg)

  # Comparing these values to the actual months they're pretty close so I reckon its a good simulation
  stream_mean = final_stream.mean()
  stream_std = final_stream.std()
  stream_max = final_stream.max()
  print("Values of generated stream for a day in month {}\nMean: {}\nStd: {}\nMax: {}".format(month+1, stream_mean, stream_std, stream_max))


#if __name__ == '__main__':
#  # Instantiate the generator
#  generator = GasFlowGenerator()
#
#  # Generate the stream of data points
#  stream = generator.generate_24_hours()
#
#  # Print the generated stream
#  print(stream)