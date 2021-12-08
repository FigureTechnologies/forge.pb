import os
import json
import git
import requests
import re
import psutil

from forgepb import builder, config_handler, global_, utils

# Pull existing config from file 
def load_config():
    config_file = open(global_.CONFIG_PATH + "/config.json")
    return json.load(config_file)

# Save config to file
def save_config(config_data):
    with open(global_.CONFIG_PATH + "/config.json", 'w') as outfile:
        json.dump(config_data, outfile, indent=4)

# Get version information and checkout to proper provenance tag
def get_version_info(network, environment, provenance_path):
    release_tag = requests.get(global_.GENESIS_VERSION_TXT_URL.format(network, environment))
    if release_tag.status_code != 200:
        version = None
    else:
        version = release_tag.text.strip('\n')

    if network == 'localnet':
        filtered_tags = get_versions(provenance_path)
        for index, version_tag in zip(range(5), filtered_tags[::-1]):
            print(version_tag)
    if not os.path.exists(provenance_path):
        print("Cloning Repository for binary construction, this can take a few seconds...")
        git.Repo.clone_from(global_.PROVENANCE_REPO, provenance_path)
    repo = git.Repo(provenance_path)

    # In case of localnet, list release versions for user to select
    while version == None:
        try:
            version = input("Enter a release version from above. Run forge -v for full list of versions [{}]:\n".format(filtered_tags[-1]))
        except ValueError:
            continue
        if not version:
            version = filtered_tags[-1]
        if not version in filtered_tags:
            version = None

    # Checkout to branch for obtaining provenance binary
    # Version should be integer or sanitized
    try:
        repo.git.checkout("-f", "tags/{}".format(version), "-b", version)
    except git.exc.GitCommandError:
        repo.git.checkout("-f", version)
    return version

# Returns a list of version tags for localnet to use
def get_versions(provenance_path):
    # Get git repo if it doesn't already exist
    if not os.path.exists(provenance_path):
        print("Cloning Repository for binary construction, this can take a few seconds...")
        git.Repo.clone_from(global_.PROVENANCE_REPO, provenance_path)
    
    repo = git.Repo(provenance_path)
    repo.git.checkout('-f', "main")
    repo.remotes.origin.pull()

    regex = re.compile(r'v[0-9]+\.[0-9]+\.[0-9]+$')
    return [str(i) for i in repo.tags if regex.match(str(i))]

# take user input for selecting network
def select_network():
    if not os.path.exists(global_.CONFIG_PATH + "/config.json"):
        config = config_handler.set_build_location()
    else:
        config = utils.load_config()
        
    # Set network for bootstapping
    while True:
        try:
            prompt = "Select Network by Number:\n"
            for index in range(len(global_.NETWORK_STRINGS)):
                prompt += "({}): {}\n".format(index + 1, global_.NETWORK_STRINGS[index])
            prompt += "({}): cancel\n".format(len(global_.NETWORK_STRINGS) + 1)
            network = int(input(prompt))
        except ValueError:
            continue
        if network == len(global_.NETWORK_STRINGS) + 1:
            exit()
        if network > len(global_.NETWORK_STRINGS) or network < 1:
            continue
        builder.build(global_.CHAIN_ID_STRINGS[global_.NETWORK_STRINGS[network - 1]], global_.NETWORK_STRINGS[network - 1], config)
        exit()

# Collect moniker and chain id for a localnet node
def collect_moniker_chain_id(version, config):
    localnet_moniker = ""
    localnet_chain_id = ""
    try:
        default_moniker = config["localnet"][version]["moniker"]
        default_chain_id = config["localnet"][version]["chainId"]
    except KeyError:
        default_moniker = "localnet-{}".format(version)
        default_chain_id = "localnet-{}".format(version)
    while localnet_moniker == "":
        localnet_moniker = input("Enter a moniker for your localnet[{}]:\n".format(default_moniker))
        if not localnet_moniker:
            localnet_moniker = default_moniker
        else:
            for letter in localnet_moniker:
                if not (letter.isalnum() or letter in "-_."):
                    localnet_moniker = ""
    while localnet_chain_id == "":
        localnet_chain_id = input("Enter a chain-id for your localnet[{}]:\n".format(default_chain_id))
        if not localnet_chain_id:
            localnet_chain_id = default_chain_id
        else:
            for letter in localnet_chain_id:
                if not (letter.isalnum() or letter in "-_."):
                    localnet_chain_id = ""
    version_data = {}
    version_data["moniker"] = localnet_moniker
    version_data["chainId"] = localnet_chain_id
    return version_data

# Collect args for constructing provenance binary
def collect_args(args):
    args_complete = args != []
    while not args_complete:
        try:
            cleveldb = input("Build environment with C Level DB? Usually not required for local testing. [No]\n")
            if not cleveldb:
                args.append("WITH_CLEVELDB=no")
                args_complete = True
            elif cleveldb.lower() in ['y', 'yes']:
                args.append("WITH_CLEVELDB=yes")
                args_complete = True
            elif cleveldb.lower() in ['n', 'no']:
                args.append("WITH_CLEVELDB=no")
                args_complete = True
            else:
                continue
        except ValueError:
            continue
    return args

# Save the information for generated mnemonic and validator information. Convert from log output
def persist_localnet_information(path, config, version, information):
    if not information.startswith('override the existing name validator [y/N]: Error: aborted'):
        # Remove unused line that can happen when validator already exists
        if information[0] == 'o':
            information = information.replace('override the existing name validator [y/N]: \n', '')
        elif information.startswith('\n'):
            information = information[2:]
        print(information)
        # Split into mnemonic and validator information list
        information = information.split('**Important** write this mnemonic phrase in a safe place.\nIt is the only way to recover your account if you ever forget your password.')
        
        # Construct json object from validator information
        validator_text_raw = information[0].replace("'{", "{").replace("}'", "}").replace('  ', '').split('-')
        validator_text_raw = list(filter(None, validator_text_raw))
        validator_persist = []
        for validator_obj_raw in validator_text_raw:
            validator_obj_raw = validator_obj_raw.strip()
            validator_obj = {}
            for attribute in validator_obj_raw.split('\n'):
                key_value = attribute.split(': ')
                if key_value[1].startswith('{'):
                    validator_obj[key_value[0]] = json.loads(key_value[1])
                elif key_value[1] == '""':
                    validator_obj[key_value[0]] = ''
                else:
                    validator_obj[key_value[0]] = key_value[1]
            validator_persist.append(validator_obj)
        mnemonic_info = information[1].split()
        
        # Save config
        config['localnet'][version]['mnemonic'] = mnemonic_info
        config['localnet'][version]['validator-information'] = validator_persist
        save_config(config)

def view_running_node_info():
    if os.path.exists(global_.CONFIG_PATH + "/config.json"):
        config = utils.load_config()
        if config['running-node']:
            try:
                node_information = config['running-node-info']
                process = psutil.Process(node_information['pid'])
                if process.name() != 'provenanced':
                    config['running-node'] = False
                    config['running-node-info'] = {}
                    save_config(config)
                    return {
                        "node-running": False,
                        "message": "A node was running but stopped unexpectedly:\nNetwork: {}    Provenance Version: {}    PID: {}    Status: Not Running\nThis information will be deleted so a new node can be started. Logs can be found in the forge save directory for the individual nodes.".format(node_information['network'], node_information['version'], node_information['pid'])
                    }
                else:
                    return {
                        "node-running": True,
                        "process": process,
                        "message": "A node is currently running:\nNetwork: {}    Provenance Version: {}    PID: {}    Status: {}".format(node_information['network'], node_information['version'], node_information['pid'], process.status())
                    }
            except Exception as e:
                config['running-node'] = False
                config['running-node-info'] = {}
                save_config(config)
                return {
                    "node-running": False,
                    "message": "A node was running but stopped unexpectedly:\nNetwork: {}    Provenance Version: {}    PID: {}    Status: Not Running\nThis information will be deleted so a new node can be started. Logs can be found in the forge save directory for the individual nodes.".format(node_information['network'], node_information['version'], node_information['pid'])
                }
    return {
        "node-running": False,
        "message": ""
    }

def stop_active_node(process_information):
    if process_information['node-running']:
        process_information['process'].terminate()
        config = utils.load_config()
        config['running-node'] = False
        config['running-node-info'] = {}
    else:
        print("There is not a node running currently.")

def start_node():
    try:
        config = utils.load_config()
        # Display available nodes
        print('Nodes available to be started:')
        if 'localnet' in config:
            print('Network = localnet:\nVersions: {}'.format(list(config['localnet'].keys())))
        if 'mainnet' in config:
            print('Network = mainnet')
        if 'testnet' in config:
            print('Network = testnet')

        network = None
        while not network:
            network_input = input("Select network from above: ")
            if network_input in global_.NETWORK_STRINGS:
                network = network_input
        
        version = None
        if not network == 'localnet':
            version = config[network]['version']
            node_info = config[network]
        else:
            while not version:
                version_input = input("Select version from above: ")
                if version_input in config['localnet'].keys():
                    version = version_input
            node_info = config[network][version]
        builder.spawnDaemon(node_info['run-command'], version, network, config, node_info['log-path'])
    except Exception:
        print("You haven't initialized a node. Try running 'forge' to start the wizard.")

def handle_running_node(process_information):
    node_stopped = False
    while not node_stopped:
        start_node = input("A node is currently running. Stop node? [y]/n: ")
        if not start_node:
            start_node = 'y'
        if start_node.lower() == 'y':
            stop_active_node(process_information)
            node_stopped = True
        elif start_node.lower() == 'n':
            print('Exiting...')
            exit()

def get_remote_branches(repo=None, provenance_path=None):
    if repo == None:
        repo = git.Repo(provenance_path)
    return [branch.name for branch in repo.remote().refs]