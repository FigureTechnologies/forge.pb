import os

import click

from forgepb import forge, global_, builder, utils, config_handler

def command_required_option_from_option(require_name):

    class CommandOptionRequiredClass(click.Command):

        def invoke(self, ctx):
            require = ctx.params[require_name]
            if ctx.params["network".lower()] is None and ctx.params[require_name]:
                raise click.ClickException(
                    "With {}={} must specify option --{}".format(
                        require_name, require, "network"))
            super(CommandOptionRequiredClass, self).invoke(ctx)

    return CommandOptionRequiredClass
    
@click.command(cls=command_required_option_from_option('boot_args'))
@click.option('-ec', '--edit-config', 'edit_config', is_flag=True, help='Guided set save location for environments')
@click.option('-n', '--network', 'network', type=click.Choice(global_.NETWORK_STRINGS), default=None, help='Choose which network node to initialize')
@click.option('-sl', '--save-loc', 'save_loc', type=click.STRING, help='Save location for environments')
@click.option('-ba', '--boot-args', 'boot_args', type=click.Choice(global_.ARGS_LIST, case_sensitive=True), multiple=True, default=[], help='List of args for building the provenance binary. Requires "--network" tag.')
@click.option('-lsv', '--list-release-version', 'list_release_versions', is_flag=True, help='List all available release versions')
@click.option('-rv', '--release-version', 'release_version', type=click.STRING, help='Enter release version to use for spinning up a localnet. You can get version list using -lsv flag.')
@click.option('-m', '--moniker', 'moniker', type=click.STRING, help='A moniker to be used for spinning up a localnet node. Not required for testnet or mainnet.')
@click.option('-cid', '--chain-id', 'chain_id', type=click.STRING, help='A chain id to be used for spinning up a localnet node. Not required for testnet or mainnet.')
def start(edit_config, network, save_loc, list_release_versions, release_version = None, boot_args = [], moniker = None, chain_id = None):
    if list_release_versions:
        if not os.path.exists(global_.CONFIG_PATH + "/config.json"):
            config = config_handler.set_build_location()
        else:
            config = utils.load_config()
        provenance_path = config['saveDir'] + "/forge" + "/provenance"

        release_versions = utils.get_versions(provenance_path)
        [print(version) for version in release_versions[::-1]]
        exit()

    if edit_config or network or save_loc or release_version:
        if save_loc and not edit_config:
            config_handler.check_save_location(save_loc)['success']
            exit()
        elif save_loc and edit_config:
            click.echo("save_loc and config flag cannot be sent at the same time")
            exit()
        
        elif edit_config and not save_loc:
            config = config_handler.set_build_location()
            exit()
        
        elif network != None or release_version !=None:
            if network == None:
                network = 'localnet'
            if not os.path.exists(global_.CONFIG_PATH + "/config.json"):
                config = config_handler.set_build_location()
            else:
                config = utils.load_config()
            builder.build(global_.CHAIN_ID_STRINGS[network], network, config, release_version, list(boot_args), moniker, chain_id)
        elif network == None:
            utils.select_env()
        else:
            utils.select_env()
    else:
        forge.main()

if __name__ == '__main__':
    start()