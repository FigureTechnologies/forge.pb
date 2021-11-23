import os

from forgepb import builder
from forgepb import utils
from forgepb import config_handler
from forgepb import global_

# Entry point
def cli():
    if not os.path.exists(global_.CONFIG_PATH + "/config.json"):
        config = config_handler.set_build_location()
    else:
        config = utils.load_config()
    while True:
        # Set mode for pbpm, else display choices again
        try:
            input_mode = int(input("Select Action by Number:\n(1): Bootstrap Node\n(2): Edit Save Location\n(3): Cancel\n"))
        except ValueError:
            continue

        if input_mode == 1:
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
                builder.build(global_.CHAIN_ID_STRINGS[network - 1], global_.NETWORK_STRINGS[network - 1], config)
                exit()
        elif input_mode == 2:
            config_handler.set_build_location()
        elif input_mode == 3:
            exit()

if __name__ == "__main__":
    cli()