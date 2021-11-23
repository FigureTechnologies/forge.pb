import os

from forgepb import global_, utils

def set_build_location():
    if os.path.exists(global_.CONFIG_PATH + "/config.json"):
        config = utils.load_config()
    else:
        if not os.path.exists(global_.CONFIG_PATH):
            os.makedirs(global_.CONFIG_PATH)
        config = {"saveDir": os.path.expanduser('~')}
    valid_path = False
    while not valid_path:
        save_path = input("Enter a valid absolute path for the node to be initialized in. If no path is given, '{}' will be used.\n".format(config['saveDir']))
        if '~/' in save_path:
            save_path = save_path.replace('~/', os.path.expanduser('~'))
        if not save_path:
            save_path = os.path.expanduser('~')
        if os.path.exists(save_path):
            valid_path = True
    config["saveDir"] = save_path
    utils.save_config(config)
    return config