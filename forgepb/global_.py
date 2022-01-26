import os

NETWORK_STRINGS = ["testnet", "mainnet", "localnet"]
ARGS_LIST = [
    "WITH_CLEVELDB=no",
    "WITH_CLEVELDB=yes"
]
CHAIN_ID_STRINGS = {"testnet": "pio-testnet-1",
                    "mainnet": "pio-mainnet-1", "localnet": "localnet"}
TESTNET_SEEDS = "--testnet --p2p.seeds 2de841ce706e9b8cdff9af4f137e52a4de0a85b2@104.196.26.176:26656,add1d50d00c8ff79a6f7b9873cc0d9d20622614e@34.71.242.51:26656"
MAINNET_SEEDS = "--p2p.seeds 4bd2fb0ae5a123f1db325960836004f980ee09b4@seed-0.provenance.io:26656,048b991204d7aac7209229cbe457f622eed96e5d@seed-1.provenance.io:26656"
GENESIS_VERSION_TXT_URL = "https://raw.githubusercontent.com/provenance-io/{}/main/{}/genesis-version.txt"
GENESIS_JSON_URL = "https://raw.githubusercontent.com/provenance-io/{}/main/{}/genesis.json"
PROVENANCE_REPO = "https://github.com/provenance-io/provenance.git"
CONFIG_PATH = os.path.join(os.path.expanduser('~'), ".pio")
COMMAND_REQUIRE_MAP = {'boot_args': 'network', 'skip_build': 'tag'}
GITHUB_URL = "https://api.github.com/repos/provenance-io/provenance/"
BINARY_URL = "https://github.com/provenance-io/provenance/releases/download/{}/provenance-{}-amd64-{}.zip"

FORGE = '''
__________________________________________
___  ____/_  __ \\__  __ \\_  ____/__  ____/
__  /_   _  / / /_  /_/ /  / __ __  __/   
_  __/   / /_/ /_  _, _// /_/ / _  /___   
/_/      \\____/ /_/ |_| \____/  /_____/   

            ____|\\
            ----|_|
            .-------..___
            '-._     :_.-'
                ) _ ( 
               '-' '-'
'''
