import os
import json

def load_config(file_path='config.json'):
  config_path = os.path.join(os.path.dirname(__file__), file_path)
  with open(config_path, 'r') as file:
    config = json.load(file)
  return config