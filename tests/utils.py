import os
import shutil
import json

from tests import test_variables
from forgepb import global_, utils


TEST_SAVE_LOCATION = os.path.expanduser('~') + '/forge'

def clear_saves(test_start = False):
    try:
        if os.path.exists(global_.CONFIG_PATH + "/config.json"):
            shutil.rmtree(global_.CONFIG_PATH)
        if os.path.exists(TEST_SAVE_LOCATION):
            shutil.rmtree(TEST_SAVE_LOCATION)
        if test_start:
            os.mkdir(TEST_SAVE_LOCATION)
    except FileNotFoundError:
        pass

def init_config():
    if not os.path.exists(global_.CONFIG_PATH):
        os.makedirs(global_.CONFIG_PATH)
    config = json.loads(test_variables.CONFIG.format(os.path.join(os.path.expanduser('~')), os.path.join(os.path.expanduser('~')), os.path.join(os.path.expanduser('~')), os.path.join(
        os.path.expanduser('~')), os.path.join(os.path.expanduser('~')), os.path.join(os.path.expanduser('~')), os.path.join(os.path.expanduser('~')), os.path.join(os.path.expanduser('~'))))
    utils.save_config(config)
    return config