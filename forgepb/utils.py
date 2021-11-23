import json

from forgepb import global_

def load_config():
    config_file = open(global_.CONFIG_PATH + "/config.json")
    return json.load(config_file)

def save_config(config_data):
    with open(global_.CONFIG_PATH + "/config.json", 'w') as outfile:
        json.dump(config_data, outfile, indent=4)