import os
import stat

import requests
from shutil import copyfile

network_strings = ["testnet", "mainnet", "localnet"]
chain_id_strings = ["pio-testnet-1", "pio-mainnet-1", "localnet"]
version_info = {"testnet": "v0.2.0", "mainnet": "v1.0.1", "localnet": None}
testnet_seeds = "--testnet --p2p.seeds 2de841ce706e9b8cdff9af4f137e52a4de0a85b2@104.196.26.176:26656,add1d50d00c8ff79a6f7b9873cc0d9d20622614e@34.71.242.51:26656"
mainnet_seeds = "--p2p.seeds 4bd2fb0ae5a123f1db325960836004f980ee09b4@seed-0.provenance.io:26656,048b991204d7aac7209229cbe457f622eed96e5d@seed-1.provenance.io:26656"

def bootstrap_node(environment, network):
    version = version_info[network]

    # Get git repo if it doesn't already exist
    if not os.path.exists("provenance"):
        os.system("git clone https://github.com/provenance-io/provenance.git")
    
    os.chdir("provenance")
    # In case of localnet, list release versions for user to select
    while version == None:
        os.system('git tag -l "v*"')
        try:
            version = str(input("Please enter a release version from above to initialize format: v#.#.#:\n"))
        except ValueError:
            continue

    # Update provenance repo and checkout to branch for obtaining provenance binary
    os.system("git checkout -f main")
    os.system('git pull --ff-only')
    # Version should be integer or sanitized
    os.system("git checkout -f {}|| git checkout -f tags/{} -b {}".format(version, version, version))

    # Construct binary for provenance
    # TODO Hardcoded for now, may need to adjust args to be editable such as with_cleveldb=no
    os.system("make install WITH_CLEVELDB=no")
    go_path = os.path.join(os.path.expanduser('~'), "go", "bin", "provenanced")
    os.chdir("../")

    if network == "localnet":
        # Handle Localnet
        build_path = environment + "/" + version

        if not os.path.exists(build_path + "/config/genesis.json"):
            os.makedirs(build_path + "/bin")
        copyfile(go_path, "{}/bin/provenanced".format(build_path))
        st = os.stat(build_path + "/bin/provenanced")
        os.chmod(build_path + "/bin/provenanced", st.st_mode | stat.S_IEXEC)
        
        populate_genesis(build_path, version)

        print("./{}/bin/provenanced start --home {}".format(build_path, build_path))

    else:
        # Handle Mainnet and Testnet
        GENESIS_JSON_URL = "https://raw.githubusercontent.com/provenance-io/{}/main/{}/genesis.json"

        # Create directory for bootstrapping if it doesn't exist
        if not os.path.exists(environment):
            os.makedirs(environment + "/bin")
            os.makedirs(environment + "/config")

        # move binary to correct location
        copyfile(go_path, environment + "/bin/provenanced")
        st = os.stat(environment + "/bin/provenanced")
        os.chmod(environment + "/bin/provenanced", st.st_mode | stat.S_IEXEC)

        download_genesis = True
        if os.path.exists(environment + "/config/genesis.json"):
            download_genesis = int(input("The genesis file already exists, would you like to overwrite the existing file?\n(1): Yes\n(2): No\n")) == 1

        if download_genesis:
            print("Downloading genesis file...")
            genesis_json_res = requests.get(GENESIS_JSON_URL.format(network, environment)).text
            open(environment + "/config/genesis.json", 'w').write(genesis_json_res)
            
        if network == "testnet":
            seed_info = testnet_seeds
        else:
            seed_info = mainnet_seeds
        print("In order to start the node run\n./{}/bin/provenanced start {} --home {}".format(environment, seed_info, environment))

# Localnet generate genesis and gentx
def populate_genesis(build_path, version):
    command = "./{}/bin/provenanced init localnet-{} --chain-id localnet-{} --home {};".format(build_path, version, version, build_path)
    command += "./{}/bin/provenanced --home {} keys add validator --keyring-backend test;".format(build_path, build_path)
    command += "./{}/bin/provenanced --home {} add-genesis-root-name validator pio --keyring-backend test 2>&- || echo pio root name already exists, skipping...;".format(build_path, build_path)
    command += "./{}/bin/provenanced --home {} add-genesis-root-name validator pb --restrict=false --keyring-backend test 2>&- || echo pb root name already exists, skipping...;".format(build_path, build_path)
    command += "./{}/bin/provenanced --home {} add-genesis-root-name validator io --restrict --keyring-backend test 2>&- || echo io root name already exists, skipping...;".format(build_path, build_path)
    command += "./{}/bin/provenanced --home {} add-genesis-root-name validator provenance --keyring-backend test 2>&- || echo validator root name already exists, skipping...;".format(build_path, build_path)
    command += "./{}/bin/provenanced --home {} add-genesis-account validator 100000000000000000000nhash --keyring-backend test 2>&-;".format(build_path, build_path)
    command += "./{}/bin/provenanced --home {} gentx validator 1000000000000000nhash --keyring-backend test --chain-id=localnet-{} 2>&- || echo gentx file already exists, skipping;".format(build_path, build_path, version)
    command += "./{}/bin/provenanced --home {} add-genesis-marker 100000000000000000000nhash --manager validator --access mint,burn,admin,withdraw,deposit --activate --keyring-backend test 2>&- || echo existing address, skipping;".format(build_path, build_path)
    command += "./{}/bin/provenanced --home {} collect-gentxs".format(build_path, build_path)
    os.system(command)

def main():
    while True:
        
        # Set mode for pbpm, else display choices again
        try:
            input_mode = input("Select Action by Number:\n(1): Bootstrap Node\n(2): Cancel\n")
        except ValueError:
            continue

        input_mode = int(input_mode)

        if input_mode == 1:
            # Set network for bootstapping
            while True:
                try:
                    prompt = "Select Network by Number:\n"
                    for index in range(len(network_strings)):
                        prompt += "({}): {}\n".format(index + 1, network_strings[index])
                    prompt += "({}): cancel\n".format(len(network_strings) + 1)
                    network = int(input(prompt))
                except ValueError:
                    continue

                bootstrap_node(chain_id_strings[network - 1], network_strings[network - 1])
                exit()
        elif input_mode == 2:
            exit()

if __name__ == "__main__":
    main()