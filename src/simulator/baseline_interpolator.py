import pandas as pd
from scipy.interpolate import interp1d
from src.utils import load_config, load_csv_pd

def get_mid_points(filename):
    """
    Uses monthly baselines to create a dictionary with keys representing
    days of the year and the values are the averages.

    :param filename:
    :return:
    """
    # Load file with error handling

    monthly_baseline = load_csv_pd(filename)['value']
    try:
        monthly_baseline = pd.to_numeric(monthly_baseline, errors='raise')
    except ValueError:
        print("ERROR: Values are not numeric")
    if not len(monthly_baseline) == 12:
        raise ValueError("ERROR: Should be 12 values in monthly baseline")

    # Middle points of each month
    mid_points = {}
    mid_point_keys = [15,45,74,105,135,166,196,227,258,288,319,349]
    i = 0
    for key in mid_point_keys:
        mid_points[key] = monthly_baseline[i]
        i += 1

    # Ensures interpolation is valid for the entire year
    extremes = (monthly_baseline[0] + monthly_baseline[1]) / 2
    mid_points[364] = extremes
    mid_points[0] = extremes

    return mid_points

def generate_interpolation(middle_points):
    # Extract days and values from middle_points
    days = list(middle_points.keys())
    values = list(middle_points.values())

    # Interpolation function
    return interp1d(days, values, kind='cubic')

# Function to get value for any day of the year
def get_value_for_day(day, interpolating_func):
    return float(interpolating_func(day))

def generate_lookup_table(interpolating_func):
    lookup_list = []
    index_list = []
    for i in range(365):
        lookup_list.append(get_value_for_day(i, interpolating_func))
        index_list.append(i)
    return pd.DataFrame({'day':index_list, 'value':lookup_list})

def write_dataframe_to_file(filename, df):
    try:
        df.to_csv(filename, index=False)
    except IOError as e:
        print("Error writing to file {}: {}".format(filename, e))
        raise

def main():
    try:
        config = load_config()
        baseline_filename = config['baseline_file']
    except FileNotFoundError as e:
        print("Error! The config file was not found: {}".format(e))
        baseline_filename = "Monthly_Baselines.csv"

    middle_points = get_mid_points(baseline_filename)
    interpolation = generate_interpolation(middle_points)
    lookup_table = generate_lookup_table(interpolation)
    write_dataframe_to_file('gas_flow_lookup_table.csv', lookup_table)

    return lookup_table

if __name__ == '__main__':
    main()
