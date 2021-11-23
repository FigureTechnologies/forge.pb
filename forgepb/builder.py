import os
import stat
from shutil import copyfile
import re
import git
import requests

from forgepb import utils, global_, config_handler

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
        build(global_.CHAIN_ID_STRINGS[network - 1], global_.NETWORK_STRINGS[network - 1], config)
        exit()

# Build a node in the given environment and network
def build(environment, network, config):
    root_path = config['saveDir'] + "/pbpm"
    provenance_path = config['saveDir'] + "/pbpm" + "/provenance"
    # Get version information
    release_tag = requests.get(global_.GENESIS_VERSION_TXT_URL.format(network, environment))
    if release_tag.status_code != 200:
        version = None
    else:
        version = release_tag.text.strip('\n')

    # Get git repo if it doesn't already exist
    if not os.path.exists(provenance_path):
        print("Cloning Repository for binary construction, this can take a few seconds...")
        git.Repo.clone_from(global_.PROVENANCE_REPO, provenance_path)
    
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
            version_index = int(input("Enter a release version from above by number:\n"))
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
    args = []
    args_complete = False
    while not args_complete:
        try:
            cleveldb = input("Build environment with C Level DB? Usually not required for local testing. Default no. (1): Yes (2): No\n")
            if not cleveldb:
                args.append("WITH_CLEVELDB=no")
                args_complete = True
            elif int(cleveldb) == 1:
                args.append("WITH_CLEVELDB=yes")
                args_complete = True
            elif int(cleveldb) == 2:
                args.append("WITH_CLEVELDB=no")
                args_complete = True
            else:
                continue
        except ValueError:
            continue

    os.system("make -C {} install {}".format(provenance_path, " ".join(args)))
    go_path = os.path.join(os.path.expanduser('~'), "go", "bin", "provenanced")

    if network == "localnet":
        # Handle Localnet
        build_path = root_path + "/" + environment + "/" + str(version)

        # Create dirs for node, and move binary
        if not os.path.exists(build_path + "/bin"):
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
            genesis_json_res = requests.get(global_.GENESIS_JSON_URL.format(network, environment)).text
            open(build_path + "/config/genesis.json", 'w').write(genesis_json_res)

        # Take seed information for testnet and mainnet
        if network == "testnet":
            seed_info = global_.TESTNET_SEEDS
        else:
            seed_info = global_.MAINNET_SEEDS
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

    utils.save_config(config)

    command = "{}/bin/provenanced --home {} init {} --chain-id {};".format(build_path, build_path, localnet_moniker, localnet_chain_id)
    command += "{}/bin/provenanced --home {} keys add validator --keyring-backend test;".format(build_path, build_path)
    command += "{}/bin/provenanced --home {} add-genesis-root-name validator pio --keyring-backend test 2>&- || echo pio root name already exists, skipping...;".format(build_path, build_path)
    command += "{}/bin/provenanced --home {} add-genesis-root-name validator pb --restrict=false --keyring-backend test 2>&- || echo pb root name already exists, skipping...;".format(build_path, build_path)
    command += "{}/bin/provenanced --home {} add-genesis-root-name validator io --restrict --keyring-backend test 2>&- || echo io root name already exists, skipping...;".format(build_path, build_path)
    command += "{}/bin/provenanced --home {} add-genesis-root-name validator provenance --keyring-backend test 2>&- || echo validator root name already exists, skipping...;".format(build_path, build_path)
    command += "{}/bin/provenanced --home {} add-genesis-account validator 100000000000000000000nhash --keyring-backend test 2>&-;".format(build_path, build_path)
    command += "{}/bin/provenanced --home {} gentx validator 1000000000000000nhash --keyring-backend test --chain-id={} 2>&- || echo gentx file already exists, skipping;".format(build_path, build_path, localnet_chain_id)
    command += "{}/bin/provenanced --home {} add-genesis-marker 100000000000000000000nhash --manager validator --access mint,burn,admin,withdraw,deposit --activate --keyring-backend test 2>&- || echo existing address, skipping;".format(build_path, build_path)
    command += "{}/bin/provenanced --home {} collect-gentxs".format(build_path, build_path)
    os.system(command)