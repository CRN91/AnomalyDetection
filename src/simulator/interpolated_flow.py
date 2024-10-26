import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import pandas as pd

# Example values for the middle of each month
middle_points = {
    0: (72.314516 + 71.353548)/2, # Average of Jan / Dec
    15: 71.353548,  # January
    45: 65.201517,  # February
    74: 70.239355,  # March
    105: 55.138333, # April
    135: 37.303968, # May
    166: 54.601923, # June
    196: 66.513871, # July
    227: 62.635484, # August
    258: 53.043125, # September
    288: 51.425161, # October
    319: 70.872667, # November
    349: 72.314516,  # December
    364: (72.314516 + 71.353548)/2 # Average of Jan / Dec
}

# Extract days and values from middle_points
days = list(middle_points.keys())
values = list(middle_points.values())

# Interpolation function
interpolating_function = interp1d(days, values, kind='cubic')

# Function to get value for any day of the year
def get_value_for_day(day):
    return interpolating_function(day)

def generate_lookup_table():
    lookup_list = []
    index_list = []
    for i in range(365):
        lookup_list.append(get_value_for_day(i))
        index_list.append(i)
    return pd.DataFrame({'day':index_list, 'value':lookup_list})

def write_dataframe_to_file(filename, df):
    df.to_csv(filename, index=False)


if __name__ == '__main__':
    # Creating lookup table
    write_dataframe_to_file('gas_flow_lookup_table.csv', generate_lookup_table())

    # Example usage
    day = 185  # Example day  of the year
    value = get_value_for_day(day)
    print(f'Value for day {day}: {value}')

    # Plot the data and the interpolation
    x_values = np.linspace(0, 364)
    fitted_values = interpolating_function(x_values)

   #plt.figure(figsize=(10, 6))
   #plt.plot(days, values, 'o', label='Middle Points')
   #plt.plot(x_values, fitted_values, '-', label='Interpolated Values')
   #plt.xlabel('Day of the Year')
   #plt.ylabel('Value')
   #plt.legend()
   #plt.title('Interpolated Values for Each Day of the Year')
   #plt.show()