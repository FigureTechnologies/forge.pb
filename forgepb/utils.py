import os
import json
import git
import requests
import re

from forgepb import builder, config_handler, global_, utils

def load_config():
    config_file = open(global_.CONFIG_PATH + "/config.json")
    return json.load(config_file)

def save_config(config_data):
    with open(global_.CONFIG_PATH + "/config.json", 'w') as outfile:
        json.dump(config_data, outfile, indent=4)

def get_version_info(network, environment, provenance_path):
    release_tag = requests.get(global_.GENESIS_VERSION_TXT_URL.format(network, environment))
    if release_tag.status_code != 200:
        version = None
    else:
        version = release_tag.text.strip('\n')

    filtered_tags = get_versions(provenance_path)
    for index, version_tag in zip(range(5), filtered_tags[::-1]):
        print(version_tag)
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

def select_env():
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
        localnet_moniker = input("Enter a moniker for your localnet({}):\n".format(default_moniker))
        if not localnet_moniker:
            localnet_moniker = default_moniker
        else:
            for letter in localnet_moniker:
                if not (letter.isalnum() or letter in "-_."):
                    localnet_moniker = ""
    while localnet_chain_id == "":
        localnet_chain_id = input("Enter a chain-id for your localnet({}):\n".format(default_chain_id))
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

def collect_args(args):
    args_complete = args != []
    while not args_complete:
        try:
            cleveldb = input("Build environment with C Level DB? Usually not required for local testing. [No]\n")
            if not cleveldb:
                args.append("WITH_CLEVELDB=no")
                args_complete = True
            elif cleveldb.lower() == 'y':
                args.append("WITH_CLEVELDB=yes")
                args_complete = True
            elif cleveldb.lower() == 'n':
                args.append("WITH_CLEVELDB=no")
                args_complete = True
            else:
                continue
        except ValueError:
            continue
    return args

# Save the information for generated mnemonic and validator information. Convert from log output
def persist_localnet_information(path, config, version):
    with open(path + "/temp_log.txt", "r+") as file:
        information = file.read()
        # Remove unused line that can happen when validator already exists
        if information[0] == 'o':
            information = information.replace('override the existing name validator [y/N]: \n', '')
        
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
        
        # Close and remove log file
        file.close()
        os.remove(path + "/temp_log.txt")