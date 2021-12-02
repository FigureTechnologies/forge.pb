import os

import click
import json

from forgepb import forge, global_, builder, utils, config_handler

# Require network flag when -ba is given
def command_required_option_from_option(require_name):

    class CommandOptionRequiredClass(click.Command):

        def invoke(self, ctx):
            require = ctx.params[require_name]
            if ctx.params[global_.COMMAND_REQUIRE_MAP[require_name].lower()] is None and ctx.params[require_name]:
                raise click.ClickException(
                    "With {}={} must specify option --{}".format(
                        require_name, require, global_.COMMAND_REQUIRE_MAP[require_name]))
            super(CommandOptionRequiredClass, self).invoke(ctx)

    return CommandOptionRequiredClass

@click.command(cls=command_required_option_from_option('boot_args'))
@click.option('-ec', '--edit-config', 'edit_config', is_flag=True, help='Guided set save location for environments')
@click.option('-n', '--network', 'network', type=click.Choice(global_.NETWORK_STRINGS), default=None, help='Choose which network node to initialize')
@click.option('-sl', '--save-loc', 'save_loc', type=click.STRING, help='Save location for environments')
@click.option('-ba', '--boot-args', 'boot_args', type=click.Choice(global_.ARGS_LIST, case_sensitive=True), multiple=True, default=[], help='List of args for building the provenance binary. Requires "--network" tag')
@click.option('-lsv', '--list-release-version', 'list_release_versions', is_flag=True, help='List all available release versions')
@click.option('-rv', '--release-version', 'release_version', type=click.STRING, help='Release version of localnet')
@click.option('-m', '--moniker', 'moniker', type=click.STRING, help='A moniker to be used for spinning up a localnet node. Not required for testnet or mainnet')
@click.option('-cid', '--chain-id', 'chain_id', type=click.STRING, help='A chain id to be used for spinning up a localnet node. Not required for testnet or mainnet')
@click.option('-lc', '--list-config', 'list_config', is_flag=True, help='Display the saved config for a given network, including mnemonic and validator information')
@click.option('-ns', '--node-status', 'status', is_flag=True, help='Display running node status')
@click.option('-sn', '--start-node', 'start_node', is_flag=True, help='Starts node with given network and release version')
@click.option('-tn', '--terminate-node', 'terminate_node', is_flag=True, help='Terminates the running node')
def start(edit_config, network, save_loc, list_release_versions, list_config, status, start_node, terminate_node, release_version = None, boot_args = [], moniker = None, chain_id = None):
    # Stop the currently running node
    if terminate_node:
        process_information = utils.view_running_node_info()
        utils.stop_active_node(process_information)
        exit()
    # Start a node
    if start_node:
        process_information = utils.view_running_node_info()
        if process_information['node-running']:
            utils.handle_running_node(process_information)
        try:
            config = utils.load_config()
            provenance_path = config['saveDir'] + "forge" + "/provenance"
        except Exception:
            print("You haven't initialized a node. Try running just forge to start the wizard.")
        if not network or not release_version in utils.get_versions(provenance_path):
            print("Starting a node depends on valid values for release-version and network.")
        else:
            node_info = config[network][release_version]
            builder.spawnDaemon(node_info['run-command'], release_version, network, config, node_info['log-path'])
        exit()

    # Display information on the node that is running
    if status:
        print(utils.view_running_node_info()['message'])
        exit()

    # List the config information about a localnet node. Including mnemonic and validator info
    if list_config:
        # get config or set location of config to be made
        if not os.path.exists(global_.CONFIG_PATH + "/config.json"):
            config = config_handler.set_build_location()
        else:
            config = utils.load_config()
        provenance_path = config['saveDir'] + "forge" + "/provenance"
        # Retrieve the config information if it exists, else display a message saying that it couldn't be found
        try:
            if release_version:
                if release_version not in utils.get_versions(provenance_path):
                    print("The version entered doesn't exist in provenance. Please run 'forge -lsv' to list all versions")
                else:
                    print(json.dumps(config['localnet'][release_version], indent=4))
            else:
                print(json.dumps(config['localnet'], indent=4))
        except KeyError:
            print("There is no node created with that version.")
        exit()
        
    # List all relase versions that could be used to spin up a node
    if list_release_versions:
        if not os.path.exists(global_.CONFIG_PATH + "/config.json"):
            config = config_handler.set_build_location()
        else:
            config = utils.load_config()
        provenance_path = config['saveDir'] + "forge" + "/provenance"

        release_versions = utils.get_versions(provenance_path)
        [print(version) for version in release_versions[::-1]]
        exit()

    # Handle all other args
    if edit_config or network or save_loc or release_version:
        # Set save_location of forge
        if save_loc and not edit_config:
            config_handler.check_save_location(save_loc)
            exit()
        # Display error as these can't be present at the same time
        elif save_loc and edit_config:
            click.echo("save_loc and config flag cannot be sent at the same time")
            exit()
        # go to set location wizard
        elif edit_config and not save_loc:
            config = config_handler.set_build_location()
            exit()
        # Use send args to create node
        elif network != None or release_version != None:
            if network == None:
                network = 'localnet'
            if not os.path.exists(global_.CONFIG_PATH + "/config.json"):
                config = config_handler.set_build_location()
            else:
                config = utils.load_config()
            provenance_path = config['saveDir'] + "forge" + "/provenance"
            if release_version and release_version not in utils.get_versions(provenance_path):
                print("The version entered doesn't exist in provenance. Please run 'forge -lsv' to list all versions")
            else:
                builder.build(global_.CHAIN_ID_STRINGS[network], network, config, release_version, list(boot_args), moniker, chain_id)
        else:
            utils.select_network()
    else:
        # Start wizard at the beginning
        forge.main()

if __name__ == '__main__':
    start()