import os

import click

from forgepb import forge, global_, builder, utils, config_handler

@click.command()
@click.option('-m', '--mode', type=click.Choice(['1', '2']), default=None,
    help='''Options\n
    1 - Bootstrap Node\n
    2 - Change Save Location''',
    required=False
)
@click.option('-n', '--network', type=click.Choice(['1', '2', '3']), default=None,
    help='''Options\n
    1 - testnet\n
    2 - mainnet\n
    3 - localnet'''
)
def start(mode, network):
    if mode == None and network == None:
        forge.main()
    elif network != None:
        if not os.path.exists(global_.CONFIG_PATH + "/config.json"):
            config = config_handler.set_build_location()
        else:
            config = utils.load_config()
        builder.build(global_.CHAIN_ID_STRINGS[int(network) - 1], global_.NETWORK_STRINGS[int(network) - 1], config)
    else:
        builder.select_env()

if __name__ == '__main__':
    start()