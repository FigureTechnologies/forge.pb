import os

from forgepb import global_, utils


# Take user input for save location
def set_build_location(path=None):
    valid_path = False
    while not valid_path:
        save_path = input("Enter a valid absolute path for the node to be initialized in. [{}]\n".format(
            os.path.expanduser('~')))
        if not save_path:
            save_path = os.path.expanduser('~')
        result = check_save_location(save_path)
        valid_path = result['success']
        if valid_path:
            return result['config']

# Check that the save location given is valid display message if failed


def check_save_location(save_path):
    if os.path.exists(global_.CONFIG_PATH + "/config.json"):
        config = utils.load_config()
    else:
        if not os.path.exists(global_.CONFIG_PATH):
            os.makedirs(global_.CONFIG_PATH)
        config = {}
    path_str = save_path
    if '~/' in path_str:
        path_str = path_str.replace('~/', os.path.expanduser('~') + '/')
    if not path_str:
        path_str = os.path.expanduser('~')
    if os.path.exists(path_str):
        if not path_str.endswith('/'):
            path_str = path_str + '/'
        config['saveDir'] = path_str
        config['running-node'] = False
        utils.save_config(config)
        return {'success': True, 'config': config}
    else:
        print("Invalid save path given, path does not exist")
        return {'success': False}
