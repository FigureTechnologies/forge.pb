import os
import stat
from shutil import copyfile
import re
import git
import requests
import subprocess
import datetime

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
        if not os.path.exists(build_path + "/logs"):
            os.makedirs(build_path + "/logs")
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
        if version not in config["localnet"]:
            config["localnet"][version] = version_data
        else:
            config["localnet"][version]["moniker"] = version_data["moniker"]
            config["localnet"][version]["chainId"] = version_data["chainId"]
        utils.save_config(config)

        validator_info = populate_genesis(build_path, moniker, chain_id)
        utils.persist_localnet_information(build_path, config, version, validator_info)
        
        run_command = "{}/bin/provenanced start --home {}".format(build_path, build_path)
        log_path = '{}/logs/{}.txt'.format(build_path, datetime.datetime.now())
        
        input_entered = False
        while not input_entered:
            start_node = input("Start node? [y]/n: ")
            if not start_node:
                start_node = 'y'
            if start_node.lower() == 'y':
                input_entered = True
                process_information = utils.view_running_node_info()
                if process_information['node-running']:
                    utils.handle_running_node(process_information)
                spawnDaemon(run_command, version, network, config, log_path)
            elif start_node.lower() == 'n':
                print("Exiting. You can run the node using forge by running \n'forge -sn -network {} -rv {}\nor on your own by opening a terminal and running \n{}".format(network, version, run_command))
                exit()

    # Handle mainnet and testnet node construction
    else:
        build_path = root_path + "/" + environment

        # Handle Mainnet and Testnet
        # Create directory for bootstrapping if it doesn't exist
        if not os.path.exists(build_path):
            os.makedirs(build_path)
        if not os.path.exists(build_path + "/bin"):
            os.makedirs(build_path + "/bin")
        if not os.path.exists(build_path + "/config"):
            os.makedirs(build_path + "/config")
        if not os.path.exists(build_path + "/logs"):
            os.makedirs(build_path + "/logs")

        # move binary to correct location
        copyfile(go_path, build_path + "/bin/provenanced")
        st = os.stat(build_path + "/bin/provenanced")
        os.chmod(build_path + "/bin/provenanced", st.st_mode | stat.S_IEXEC)

        # Download genesis file which is used to bring up the node with certain information
        download_genesis = None
        if os.path.exists(build_path + "/config/genesis.json"):
            genesis_complete = False
            while not genesis_complete:
                try:
                    download_genesis = input("The genesis file already exists, would you like to overwrite the existing file?[y]/n:\n")
                    if download_genesis == None or download_genesis.lower() == 'y':
                        print("Downloading genesis file...")
                        genesis_json_res = requests.get(global_.GENESIS_JSON_URL.format(network, environment)).text
                        open(build_path + "/config/genesis.json", 'w').write(genesis_json_res)
                except ValueError:
                    continue
        

        # Take seed information for testnet and mainnet
        if network == "testnet":
            seed_info = global_.TESTNET_SEEDS
        else:
            seed_info = global_.MAINNET_SEEDS
        
        if network not in config:
            config[network] = {}
        config[network]['version'] = version
        utils.save_config(config)

        run_command = "{}/bin/provenanced start {} --home {}".format(build_path, seed_info, build_path)
        log_path =  '{}/logs/{}.txt'.format(build_path, str(datetime.datetime.now()).replace(' ', '-'))

        input_entered = False
        while not input_entered:
            start_node = input("Start node? [y]/n: ")
            if not start_node:
                start_node = 'y'
            if start_node.lower() == 'y':
                input_entered = True
                process_information = utils.view_running_node_info()
                if process_information['node-running']:
                    utils.handle_running_node(process_information)
                spawnDaemon(run_command, version, network, config, log_path)
            elif start_node.lower() == 'n':
                print("Exiting. You can run the node using forge by running \n'forge -sn -network {} -rv {}\nor on your own by opening a terminal and running \n{}".format(network, version, run_command))
                exit()

# Localnet generate genesis and gentx
def populate_genesis(build_path, moniker, chain_id):
    command1 = "{}/bin/provenanced --home {} init {} --chain-id {};".format(build_path, build_path, moniker, chain_id)
    command2 = "{}/bin/provenanced --home {} keys add validator --keyring-backend test 2>&1;".format(build_path, build_path, build_path)
    command3 = "{}/bin/provenanced --home {} add-genesis-root-name validator pio --keyring-backend test 2>&- || echo pio root name already exists, skipping...;".format(build_path, build_path)
    command3 += "{}/bin/provenanced --home {} add-genesis-root-name validator pb --restrict=false --keyring-backend test 2>&- || echo pb root name already exists, skipping...;".format(build_path, build_path)
    command3 += "{}/bin/provenanced --home {} add-genesis-root-name validator io --restrict --keyring-backend test 2>&- || echo io root name already exists, skipping...;".format(build_path, build_path)
    command3 += "{}/bin/provenanced --home {} add-genesis-root-name validator provenance --keyring-backend test 2>&- || echo validator root name already exists, skipping...;".format(build_path, build_path)
    command3 += "{}/bin/provenanced --home {} add-genesis-account validator 100000000000000000000nhash --keyring-backend test 2>&-;".format(build_path, build_path)
    command3 += "{}/bin/provenanced --home {} gentx validator 1000000000000000nhash --keyring-backend test --chain-id={} 2>&- || echo gentx file already exists, skipping;".format(build_path, build_path, chain_id)
    command3 += "{}/bin/provenanced --home {} add-genesis-marker 100000000000000000000nhash --manager validator --access mint,burn,admin,withdraw,deposit --activate --keyring-backend test 2>&- || echo existing address, skipping;".format(build_path, build_path)
    command3 += "{}/bin/provenanced --home {} collect-gentxs".format(build_path, build_path)
    validator_check_command = "{}/bin/provenanced --home {} keys show validator".format(build_path, build_path)
    os.system(command1)
    validator_check_process = subprocess.Popen(validator_check_command, shell=True, stdout=subprocess.PIPE)
    validator_check_process.wait()
    validators_out, err = validator_check_process.communicate()
    if validators_out.decode('utf-8').startswith('- name:'):
        print("override the existing name validator [y/N]:")
    process = subprocess.Popen(command2, shell=True, stdout=subprocess.PIPE)
    process.wait()

    out, err = process.communicate()
    os.system(command3)
    return out.decode('utf-8')

def spawnDaemon(node_command, version, network, config, log_path):
    try: 
        pid = os.fork() 
        if pid > 0:
            return
    except OSError as e:
        print("fork #1 failed: {} ({})".format(e.errno, e.strerror))

    os.setsid()

    try: 
        pid = os.fork() 
        if pid > 0:
            exit()
    except OSError as e:
        print("fork #1 failed: {} ({})".format(e.errno, e.strerror))

    start_node(node_command, version, network, config, log_path)

    os._exit(os.EX_OK)

def start_node(node_command, version, network, config, log_path):
    log = open(log_path, 'w+')
    process = subprocess.Popen(node_command, shell=True, stdout=log, stderr=log)
    if network == 'localnet':
        config[network][version]['run-command'] = node_command
        config[network][version]['log-path'] = log_path
    else:
        config[network]['run-command'] = node_command
        config[network]['log-path'] = log_path
    config['running-node'] = True
    config['running-node-info'] = {
        "pid": process.pid,
        "version": version,
        "network": network
    }
    utils.save_config(config)
    process.wait()