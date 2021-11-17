import os

import json

CONFIG_PATH = os.path.join(os.path.expanduser('~'), ".pio", "config.json")

def load_config():
    config_file = open(CONFIG_PATH)
    return json.load(config_file)

def save_config(config_data):
    with open(CONFIG_PATH, 'w') as outfile:
        json.dump(config_data, outfile, indent=4)