import json
import os

import git
import psutil
import requests

from forgepb import builder, config_handler, global_


# Pull existing config from file
def load_config():
    config_file = open(global_.CONFIG_PATH + "/config.json")
    return json.load(config_file)


def exists_config():
    return os.path.exists(global_.CONFIG_PATH + "/config.json")


# Save config to file
def save_config(config_data):
    with open(global_.CONFIG_PATH + "/config.json", 'w') as outfile:
        json.dump(config_data, outfile, indent=4)


# Get version information and checkout to proper provenance tag
def get_version_info(network, environment, provenance_path):
    release_tag = requests.get(
        global_.GENESIS_VERSION_TXT_URL.format(network, environment))
    if release_tag.status_code != 200:
        version = None
    else:
        version = release_tag.text.strip('\n')

    if network == 'localnet':
        filtered_tags = get_versions()
        for index, version_tag in zip(range(5), filtered_tags):
            print(version_tag)
    repo = git.Repo(provenance_path)

    # In case of localnet, list release versions for user to select
    while version == None:
        try:
            version = input("Enter a release version from above. Run forge -v for full list of versions [{}]:\n".format(
                filtered_tags[0]))
        except ValueError:
            continue
        if not version:
            version = filtered_tags[0]
        if not version in filtered_tags:
            version = None

    # Checkout to branch for obtaining provenance binary
    # Version should be integer or sanitized
    try:
        repo.git.checkout("-f", "tags/{}".format(version), "-b", version)
    except git.exc.GitCommandError:
        repo.git.checkout("-f", version)
    return version


def select_network():
    if not os.path.exists(global_.CONFIG_PATH + "/config.json"):
        config = config_handler.set_build_location()
    else:
        config = load_config()

    # Set network for bootstapping
    while True:
        try:
            prompt = "Select Network by Number:\n"
            for index in range(len(global_.NETWORK_STRINGS)):
                prompt += "({}): {}\n".format(index + 1,
                                              global_.NETWORK_STRINGS[index])
            prompt += "({}): cancel\n".format(len(global_.NETWORK_STRINGS) + 1)
            network = int(input(prompt))
        except ValueError:
            continue
        if network == len(global_.NETWORK_STRINGS) + 1:
            exit()
        if network > len(global_.NETWORK_STRINGS) or network < 1:
            continue
        builder.build(global_.CHAIN_ID_STRINGS[global_.NETWORK_STRINGS[network - 1]],
                      global_.NETWORK_STRINGS[network - 1], config)
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
        localnet_moniker = input(
            "Enter a moniker for your localnet[{}]:\n".format(default_moniker))
        if not localnet_moniker:
            localnet_moniker = default_moniker
        else:
            for letter in localnet_moniker:
                if not (letter.isalnum() or letter in "-_."):
                    localnet_moniker = ""
    while localnet_chain_id == "":
        localnet_chain_id = input(
            "Enter a chain-id for your localnet[{}]:\n".format(default_chain_id))
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
            cleveldb = input(
                "Build environment with C Level DB? Usually not required for local testing. [No]\n")
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
            information = information.replace(
                'override the existing name validator [y/N]: \n', '')
        elif information.startswith('\n'):
            information = information[2:]
        print(information)
        # Split into mnemonic and validator information list
        information = information.split(
            '**Important** write this mnemonic phrase in a safe place.\nIt is the only way to recover your account if you ever forget your password.')

        # Construct json object from validator information
        validator_text_raw = information[0].replace(
            "'{", "{").replace("}'", "}").replace('  ', '').split('-')
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


# Fetch info stored for currently executing process.
def view_running_node_info():
    if not exists_config():
        return None, "no forge config"

    config = load_config()
    if not 'running-node-info' in config:
        return None, "node not started"

    try:
        node_information = config['running-node-info']
        process = psutil.Process(node_information['pid'])
        # Can't match by name here. Linux runs subcommands under a subshell (sh -c ...).
        # Verify the process is running. psutil has catches in place to check for pid reuse.
        if not process.is_running():
            return None, "cannot locate process"

        return node_information, "Node running"
    except Exception:
        return None, "Could not find a running node"


def stop_active_node(process_information):
    if not process_information:
        print("There is not a node running currently.")
        return

    process = psutil.Process(process_information['pid'])
    process.kill()

    # Clear the running info only on stop.
    config = load_config()
    config['running-node-info'] = None
    save_config(config)


def start_node():
    try:
        config = load_config()
        # Display available nodes
        print('Nodes available to be started:')
        if 'localnet' in config:
            print('Network = localnet:\nVersions: {}'.format(
                list(config['localnet'].keys())))
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
        builder.spawnDaemon(
            node_info['run-command'], version, network, config, node_info['log-path'])
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
            return

# Returns a list of version tags for localnet to use


def get_versions():
    try:
        tag_info = requests.get(global_.GITHUB_URL + 'tags').json()
        return [tag['name'] for tag in tag_info]
    except:
        print("Something went wrong reaching out to {}".format(
            global_.GITHUB_URL + 'branches'))

# Returns a list of all remote branches


def get_remote_branches():
    try:
        branch_info = requests.get(global_.GITHUB_URL + 'branches').json()
        return [branch['name'] for branch in branch_info]
    except:
        print("Something went wrong reaching out to {}".format(
            global_.GITHUB_URL + 'branches'))


def take_start_node_input(run_command, version, network, config, log_path):
    input_entered = False
    while not input_entered:
        start_node = input("Start node? [y]/n: ")
        if not start_node:
            start_node = 'y'
        if start_node.lower() == 'y':
            input_entered = True
            process_information, _ = view_running_node_info()
            if process_information:
                handle_running_node(process_information)
            builder.spawnDaemon(run_command, version,
                                network, config, log_path)
        elif start_node.lower() == 'n':
            if network == 'localnet':
                config[network][version]['run-command'] = run_command
                config[network][version]['log-path'] = log_path
            else:
                config[network]['run-command'] = run_command
                config[network]['log-path'] = log_path
            save_config(config)
            print(
                "Exiting. You can run the node using forge or on your own by opening a terminal and running \n{}".format(
                    ' '.join(run_command)))
            exit()
