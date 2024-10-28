import os
import json

def load_config(file_path='config.json'):
  config_path = os.path.join(os.path.dirname(__file__), file_path)
  try:
    with open(config_path, 'r') as file:
      config = json.load(file)
  except FileNotFoundError:
    # Default config is hard coded
     config = {
      "pipeline_name": "Easington-Langeled",
      "max_capacity": 75,
      "baseline_file": "Monthly_Baselines.csv"
    }
  return config