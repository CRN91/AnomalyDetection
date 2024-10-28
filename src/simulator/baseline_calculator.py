# Uses data on Easington-Langeled entry point to get baselines for the simulator
import pandas as pd

if __name__ == "__main__":
  """ 
  Calculating monthly averages for the baseline as daily averages have outliers.
    
  Encountering lots of issues when it comes to the simulating the mean. The values are almost
  there and I think the issue is the days that the pipeline is offline is skewing the results.
  My solution will be to filter out these values and then try to simulate the offline days separately.
  """

  # Load the data of daily averages of flow volume between 2023 and 2024
  entry_volumes = pd.read_csv("SystemEntryVolumeEasingtonLangeledD+1-10_23-09_24.csv")

  # Filter out 0 and low values
  threshold = 3
  filtered_volumes = entry_volumes[entry_volumes["Value"] < threshold]
  entry_volumes = entry_volumes[entry_volumes['Value'] > threshold]

  # Find monthly flow averages
  entry_volumes["Month"] = entry_volumes['Applicable At'].str[3:5]
  monthly_averages = entry_volumes.groupby('Month')['Value'].mean().reset_index()
  monthly_averages["Std"] = (entry_volumes.groupby('Month')['Value'].std().reset_index())['Value']

  # Calculate a multiplier to use for seasonality values
  yearly_average = entry_volumes["Value"].mean()

  # Save to a file as we only need to calculate once
  monthly_averages.to_csv("Monthly_Baselines.csv")

  # Analysing filtered out values
  number_of_filtered = len(filtered_volumes)
  filtered_mean = filtered_volumes['Value'].mean()
  filtered_zeros = len(filtered_volumes['Value'] == 0)
  print("There are {} filtered values\nMean: {}\nZeros: {}".format(number_of_filtered, filtered_mean, filtered_zeros))
  print(filtered_volumes[['Applicable At','Value']].head(18))

  # Average Flow = 61.28..
  max_value = entry_volumes["Value"].max() #74.43
  min_value = entry_volumes["Value"].min()
  std_value = entry_volumes["Value"].std() # 15.19..
  upper_bound = max_value * 0.85 # Pattern in function will multiply by 1.15 so need to adjust here
  print("\nAverage Flow: {}\nMax Flow: {}\nMin Flow: {}\nFlow Standard Deviation: {}".format(yearly_average,max_value,min_value,std_value))
  print()
  print(monthly_averages.head(12))