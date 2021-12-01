import os
import stat
from shutil import copyfile
import re
import git
import requests

from forgepb import utils, global_

# Build a node in the given environment and network
def build(environment, network, config, version=None, args=[], moniker=None, chain_id=None):
    root_path = config['saveDir'] + "forge"
    provenance_path = config['saveDir'] + "forge" + "/provenance"
    # Get version and checkout to proper provenance tag
    if not version:
        version = utils.get_version_info(network, environment, provenance_path)
    else:
        repo = git.Repo(provenance_path)
        try:
            repo.git.checkout("-f", "tags/{}".format(version), "-b", version)
        except git.exc.GitCommandError:
            repo.git.checkout("-f", version)
    # Construct binary for provenance
    args = utils.collect_args(args)

    os.system("make -C {} install {}".format(provenance_path, " ".join(args)))
    go_path = os.path.join(os.path.expanduser('~'), "go", "bin", "provenanced")

    # Handle Localnet node construction
    if network == "localnet":
        build_path = root_path + "/" + environment + "/" + str(version)

        # Create dirs for node, and move binary
        if not os.path.exists(build_path + "/bin"):
            os.makedirs(build_path + "/bin")
        copyfile(go_path, "{}/bin/provenanced".format(build_path))
        st = os.stat(build_path + "/bin/provenanced")
        os.chmod(build_path + "/bin/provenanced", st.st_mode | stat.S_IEXEC)
        
        # Collect moniker and chain id if they aren't given
        if not moniker or not chain_id:
            version_data = utils.collect_moniker_chain_id(version, config)
        else:
            version_data = {}
            version_data["moniker"] = moniker
            version_data["chainId"] = chain_id

        # Persist data to the config file
        if "localnet" not in config:
            config["localnet"] = {}
        config["localnet"][version] = version_data
        utils.save_config(config)

        populate_genesis(build_path, moniker, chain_id)
        utils.persist_localnet_information(build_path, config, version)
        print("{}/bin/provenanced start --home {}".format(build_path, build_path))

    # Handle mainnet and testnet node construction
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
def populate_genesis(build_path, moniker, chain_id):
    command = "{}/bin/provenanced --home {} init {} --chain-id {};".format(build_path, build_path, moniker, chain_id)
    command += "{}/bin/provenanced --home {} keys add validator --keyring-backend test 2>&1 | tee {}/temp_log.txt;".format(build_path, build_path, build_path)
    command += "{}/bin/provenanced --home {} add-genesis-root-name validator pio --keyring-backend test 2>&- || echo pio root name already exists, skipping...;".format(build_path, build_path)
    command += "{}/bin/provenanced --home {} add-genesis-root-name validator pb --restrict=false --keyring-backend test 2>&- || echo pb root name already exists, skipping...;".format(build_path, build_path)
    command += "{}/bin/provenanced --home {} add-genesis-root-name validator io --restrict --keyring-backend test 2>&- || echo io root name already exists, skipping...;".format(build_path, build_path)
    command += "{}/bin/provenanced --home {} add-genesis-root-name validator provenance --keyring-backend test 2>&- || echo validator root name already exists, skipping...;".format(build_path, build_path)
    command += "{}/bin/provenanced --home {} add-genesis-account validator 100000000000000000000nhash --keyring-backend test 2>&-;".format(build_path, build_path)
    command += "{}/bin/provenanced --home {} gentx validator 1000000000000000nhash --keyring-backend test --chain-id={} 2>&- || echo gentx file already exists, skipping;".format(build_path, build_path, chain_id)
    command += "{}/bin/provenanced --home {} add-genesis-marker 100000000000000000000nhash --manager validator --access mint,burn,admin,withdraw,deposit --activate --keyring-backend test 2>&- || echo existing address, skipping;".format(build_path, build_path)
    command += "{}/bin/provenanced --home {} collect-gentxs".format(build_path, build_path)
    os.system(command)