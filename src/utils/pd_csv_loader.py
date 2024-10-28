import pandas as pd

def load_csv_pd(filename):
  try:
    df = pd.read_csv(filename)['Value']
  except FileNotFoundError as e:
    print("ERROR: The monthly baseline csv file was not found: {}".format(e))
    raise
  except pd.errors.EmptyDataError as e:
    print("ERROR: The monthly baseline csv file is empty: {}".format(e))
    raise
  except pd.errors.ParserError as e:
    print("ERROR: The monthly baseline csv file is corrupted: {}".format(e))
    raise
  except Exception as e:
    print("An unexpected error occurred: {}".format(e))
    raise

  return df