import os
import stat

import re
import git
import json
import requests
from shutil import copyfile

from utils import load_config, save_config

NETWORK_STRINS = ["testnet", "mainnet", "localnet"]
CHAIN_ID_STRINGS = ["pio-testnet-1", "pio-mainnet-1", "localnet"]
TESTNET_SEEDS = "--testnet --p2p.seeds 2de841ce706e9b8cdff9af4f137e52a4de0a85b2@104.196.26.176:26656,add1d50d00c8ff79a6f7b9873cc0d9d20622614e@34.71.242.51:26656"
MAINNET_SEEDS = "--p2p.seeds 4bd2fb0ae5a123f1db325960836004f980ee09b4@seed-0.provenance.io:26656,048b991204d7aac7209229cbe457f622eed96e5d@seed-1.provenance.io:26656"
GENESIS_VERSION_TXT_URL = "https://raw.githubusercontent.com/provenance-io/{}/main/{}/genesis-version.txt"
GENESIS_JSON_URL = "https://raw.githubusercontent.com/provenance-io/{}/main/{}/genesis.json"
PROVENANCE_REPO = "https://github.com/provenance-io/provenance.git"
CONFIG_PATH = os.path.join(os.path.expanduser('~'), ".pio")

def bootstrap_node(environment, network, config):
    root_path = config['saveDir'] + "/pbpm"
    provenance_path = config['saveDir'] + "/pbpm" + "/provenance"
    # Get version information
    release_tag = requests.get(GENESIS_VERSION_TXT_URL.format(network, environment))
    if release_tag.status_code != 200:
        version = None
    else:
        version = release_tag.text.strip('\n')

    # Get git repo if it doesn't already exist
    if not os.path.exists(provenance_path):
        print("Cloning Repository for binary construction, this can take a few seconds...")
        git.Repo.clone_from(PROVENANCE_REPO, provenance_path)
    
    repo = git.Repo(provenance_path)
    repo.git.checkout('-f', "main")
    repo.remotes.origin.pull()

    # In case of localnet, list release versions for user to select
    while version == None:
        regex = re.compile(r'v[0-9]+\.[0-9]+\.[0-9]+$')
        filtered_tags = [i for i in repo.tags if regex.match(str(i))]
        for index in range(len(filtered_tags)):
            print("({}): {}".format(index + 1, filtered_tags[index]))
        try:
            version_index = int(input("Please enter a release version from above by number:\n"))
        except ValueError:
            continue
        if version_index > len(filtered_tags) or version_index < 1:
            continue
        version = str(filtered_tags[version_index - 1])

    # Update provenance repo and checkout to branch for obtaining provenance binary
    # Version should be integer or sanitized
    try:
        repo.git.checkout("-f", "tags/{}".format(version), "-b", version)
    except git.exc.GitCommandError:
        repo.git.checkout("-f", version)

    # Construct binary for provenance
    # TODO Hardcoded for now, may need to adjust args to be editable such as with_cleveldb=no
    os.system("make -C {} install WITH_CLEVELDB=no".format(provenance_path))
    go_path = os.path.join(os.path.expanduser('~'), "go", "bin", "provenanced")

    if network == "localnet":
        # Handle Localnet
        build_path = root_path + "/" + environment + "/" + str(version)

        # Create dirs for node, and move binary
        if not os.path.exists(build_path + "/config/genesis.json"):
            os.makedirs(build_path + "/bin")
        copyfile(go_path, "{}/bin/provenanced".format(build_path))
        st = os.stat(build_path + "/bin/provenanced")
        os.chmod(build_path + "/bin/provenanced", st.st_mode | stat.S_IEXEC)
        
        populate_genesis(build_path, version, config)

        print("{}/bin/provenanced start --home {}".format(build_path, build_path))

    else:
        build_path = root_path + "/" + environment

        # Handle Mainnet and Testnet
        # Create directory for bootstrapping if it doesn't exist
        if not os.path.exists(build_path):
            os.makedirs(build_path + "/bin")
            os.makedirs(build_path + "/config")

        # move binary to correct location
        copyfile(go_path, build_path + "/bin/provenanced")
        st = os.stat(build_path + "/bin/provenanced")
        os.chmod(build_path + "/bin/provenanced", st.st_mode | stat.S_IEXEC)

        # Download genesis file which is used to bring up the node with certain information
        download_genesis = None
        if os.path.exists(build_path + "/config/genesis.json"):
            while download_genesis == None or download_genesis not in [1, 2]:
                try:
                    download_genesis = int(input("The genesis file already exists, would you like to overwrite the existing file?\n(1): Yes\n(2): No\n"))
                except ValueError:
                    continue
        if download_genesis == 1 or download_genesis == None:
            print("Downloading genesis file...")
            genesis_json_res = requests.get(GENESIS_JSON_URL.format(network, environment)).text
            open(build_path + "/config/genesis.json", 'w').write(genesis_json_res)

        # Take seed information for testnet and mainnet
        if network == "testnet":
            seed_info = TESTNET_SEEDS
        else:
            seed_info = MAINNET_SEEDS
        print("In order to start the node run\n{}/bin/provenanced start {} --home {}".format(build_path, seed_info, build_path))

# Localnet generate genesis and gentx
def populate_genesis(build_path, version, config):
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
    if "localnet" not in config:
        config["localnet"] = {}
    config["localnet"][version] = version_data

    save_config(config)
    
    command = "{}/bin/provenanced --home {} init localnet-{} --chain-id localnet-{};".format(build_path, build_path, version, version)
    command += "{}/bin/provenanced --home {} keys add validator --keyring-backend test;".format(build_path, build_path)
    command += "{}/bin/provenanced --home {} add-genesis-root-name validator pio --keyring-backend test 2>&- || echo pio root name already exists, skipping...;".format(build_path, build_path)
    command += "{}/bin/provenanced --home {} add-genesis-root-name validator pb --restrict=false --keyring-backend test 2>&- || echo pb root name already exists, skipping...;".format(build_path, build_path)
    command += "{}/bin/provenanced --home {} add-genesis-root-name validator io --restrict --keyring-backend test 2>&- || echo io root name already exists, skipping...;".format(build_path, build_path)
    command += "{}/bin/provenanced --home {} add-genesis-root-name validator provenance --keyring-backend test 2>&- || echo validator root name already exists, skipping...;".format(build_path, build_path)
    command += "{}/bin/provenanced --home {} add-genesis-account validator 100000000000000000000nhash --keyring-backend test 2>&-;".format(build_path, build_path)
    command += "{}/bin/provenanced --home {} gentx validator 1000000000000000nhash --keyring-backend test --chain-id=localnet-{} 2>&- || echo gentx file already exists, skipping;".format(build_path, build_path, version)
    command += "{}/bin/provenanced --home {} add-genesis-marker 100000000000000000000nhash --manager validator --access mint,burn,admin,withdraw,deposit --activate --keyring-backend test 2>&- || echo existing address, skipping;".format(build_path, build_path)
    command += "{}/bin/provenanced --home {} collect-gentxs".format(build_path, build_path)
    os.system(command)

# Entry point
def main():
    if not os.path.exists(CONFIG_PATH + "/config.json"):
        if not os.path.exists(CONFIG_PATH):
            os.makedirs(CONFIG_PATH)
        valid_path = False
        config = {}
        while not valid_path:
            save_path = input("Enter a valid absolute path for the node to be initialized in. If no path is given, '~/' will be used.\n")
            if '~/' in save_path:
                save_path = save_path.replace('~/', os.path.expanduser('~'))
            if not save_path:
                save_path = os.path.expanduser('~')
            if os.path.exists(save_path):
                valid_path = True
        config["saveDir"] = save_path
        save_config(config)
    else:
        config = load_config()
    while True:
        # Set mode for pbpm, else display choices again
        try:
            input_mode = int(input("Select Action by Number:\n(1): Bootstrap Node\n(2): Cancel\n"))
        except ValueError:
            continue

        if input_mode == 1:
            # Set network for bootstapping
            while True:
                try:
                    prompt = "Select Network by Number:\n"
                    for index in range(len(NETWORK_STRINS)):
                        prompt += "({}): {}\n".format(index + 1, NETWORK_STRINS[index])
                    prompt += "({}): cancel\n".format(len(NETWORK_STRINS) + 1)
                    network = int(input(prompt))
                except ValueError:
                    continue
                if network == len(NETWORK_STRINS) + 1:
                    exit()
                if network > len(NETWORK_STRINS) or network < 1:
                    continue
                bootstrap_node(CHAIN_ID_STRINGS[network - 1], NETWORK_STRINS[network - 1], config)
                exit()
        elif input_mode == 2:
            exit()

if __name__ == "__main__":
    main()