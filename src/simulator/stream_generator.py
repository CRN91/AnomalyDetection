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
  #new_stream = pd.Series(dtype="float64")
  new_stream = []
  # Iterates through each minute of the day
  for i in range(1440):
    # Daily peak multiplier
    daily_peak = stream[i]*daily_peak_multiplier(i,month_avg)
    # Each month's standard deviation is used for the Gaussian noise
    noise = gaussian_noise(month_avg,daily_peak)
    # Patterns are applied to each value
    #new_stream = new_stream._append(pd.Series([daily_peak+noise]))
    new_stream.append(daily_peak + noise)
  return new_stream

def random_day():
  """
  Gets a random day and its corresponding month. I used this for initial testing.

  :return: day (0<=day<365), month (0<=month<12)
  """
  # Get a random day and month
  month_lengths = {
    0: 30, 1: 27, 2: 30,
    3: 29, 4: 30, 5: 29,
    6: 30, 7: 30, 8: 29,
    9: 30, 10: 29, 11: 30
  }
  month = random.randint(0, 11)
  day_of_month = random.randint(0, month_lengths[month])
  count = 0
  day = day_of_month
  for key, value in month_lengths.items():
    if count == month:
      break
    count += 1
    day += value
  return day, month

def day_to_month(find_day):
  """
  Takes a value 0<=day<365, and returns the month it is in

  :param find_day (int): day to find
  :return month (int): (0<=month<12)
  """
  month_lengths = {
    0: 30, 1: 27, 2: 30,
    3: 29, 4: 30, 5: 29,
    6: 30, 7: 30, 8: 29,
    9: 30, 10: 29, 11: 30
  }
  month = -1
  count_day = 0
  for key, value in month_lengths.items():
    if count_day >  find_day:
      break
    count_day += value
    month+=1
  return month

def setup():
  """
  Reads and returns baseline values

  :return: avg_days list of mean daily values, std_months list of monthly standard deviations
  """
  # Get baseline values
  avg_months, std_months = load_baseline()  # Old values, std_months is still used
  # Lookup table of interpolated gas flow graph
  file_path = os.path.join(os.path.dirname(__file__),"gas_flow_lookup_table.csv")
  avg_days = list(pd.read_csv(file_path)['value'])
  return avg_days, std_months

def run_simulation(start_day = 0, duration = 365):
  """
  Runs the main simulation loop after setting up. Default to 1 year of data.
  Returns the completed datastream.

  :param start_day (int): day to begin the sim 0<=day<365
  :param duration (int): how many days to simulate
  :return: completed datastream where each value represents the gas flow per day at that minute.
  """
  print("Starting Simulation")
  avg_days, std_months = setup()
  #datastream = []
  # Iterate through each day, generating a stream of data for each minute
  for day in range(start_day, start_day+duration):
    if start_day > 364:
      start_day = start_day % 364

    # Gets the baselines for these values
    month = day_to_month(day)
    daily_flow_mean = avg_days[day]
    month_flow_std = std_months[month] # Probably don't need this

    # Generate the stream
    lower_bound, upper_bound = get_point_bounds(daily_flow_mean, month_flow_std)
    stream = generate_24_hours(lower_bound, upper_bound)

    #final_stream = apply_patterns(stream, daily_flow_mean)
    #datastream = datastream + final_stream

    # Yields a single minute of data
    #for i in apply_patterns(stream, daily_flow_mean):
    #  yield i
    yield apply_patterns(stream, daily_flow_mean)

  #print("Simulation Complete")
  #return datastream

if __name__ == '__main__':
  run_simulation()
  #avg_days, std_months = setup()
  #day, month = random_day()
#
  ## Get the daily mean and standard deviation
  ##month_avg = avg_months[month]
  #month_avg = avg_days[day]
  #month_std = std_months[month]
#
  ## Generate the stream
  #lower_bound, upper_bound = get_point_bounds(month_avg, month_std)
  #stream = generate_24_hours(lower_bound, upper_bound)
#
  #final_stream = apply_patterns(stream,month_avg)
#
  ## Comparing these values to the actual months they're pretty close so I reckon its a good simulation
  #stream_mean = final_stream.mean()
  #stream_std = final_stream.std()
  #stream_max = final_stream.max()
  #print("Values of generated stream for day {} of the year\nMean: {}\nStd: {}\nMax: {}".format(day, stream_mean, stream_std, stream_max))
