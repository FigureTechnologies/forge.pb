import json
import os
import click
import git
import subprocess
import select

from forgepb import utils, builder, config_handler, global_


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

@click.command(
    "stop",
    help="Stop the currently running node"
)
def node_stop_cmd():
    process_information, _ = utils.view_running_node_info()
    utils.stop_active_node(process_information)
    return

@click.command(
    "tail",
    help="Access the logs of the running node"
)
@click.option(
    '-f',
    '--follow',
    'follow',
    is_flag=True,
    help='Follow the logs of the currently running node')
def node_tail_cmd(follow):
    if not utils.exists_config():
        print('There is no node running')
        return

    config = utils.load_config()
    try:
        network = config['running-node-info']['network']
        version = config['running-node-info']['version']
        if network == 'localnet':
            log_path = config[network][version]['log-path']
        else:
            log_path = config[network]['log-path']

        if not follow:
            utils.print_logs(log_path)
        else:
            utils.follow_logs(log_path)

    except Exception:
        print('There is no node running')

@click.command(
    "start",
    help="Start a provenance node with default values",
    cls=command_required_option_from_option('skip_build')
)
@click.option(
    "-n",
    "--network",
    "network",
    type=click.Choice(["localnet", "mainnet", "testnet"]),
    help="The provenance network to start / connect to")
@click.option(
    "-t",
    "--tag",
    "tag",
    default=None,
    help="Release tag to init the network with")
@click.option(
    '-b',
    '--provenance-branch',
    'provenance_branch',
    type=click.STRING,
    help='A branch of Provenance to be used to build the binary instead of tag')
@click.option(
    '-m',
    '--moniker',
    'moniker',
    type=click.STRING,
    default=None,
    help='A moniker to be used for spinning up a localnet node. Not required for testnet or mainnet')
@click.option(
    '-c',
    '--chain-id',
    'chain_id',
    type=click.STRING,
    default=None,
    help='A chain id to be used for spinning up a localnet node. Not required for testnet or mainnet')
@click.option(
    '-a',
    '--boot-args',
    'boot_args',
    type=click.Choice(global_.ARGS_LIST, case_sensitive=True),
    multiple=True,
    default=[],
    help='List of args for building the provenance binary. Requires "--network" tag')
@click.option(
    '--no-build',
    'skip_build',
    is_flag=True,
    default=False,
    help='Skip building binary on local machine. Downloads from github repo instead. Requires --tag arg to be given for binary download. --network can be given to specify mainnet/testnet for genesis download.')
def node_start_cmd(network, tag, moniker, chain_id, provenance_branch, boot_args, skip_build):
    process_information, _ = utils.view_running_node_info()
    if process_information:
        utils.stop_active_node(process_information)
    try:
        config = utils.load_config()
        provenance_path = config['saveDir'] + "forge" + "/provenance"
    except:
        config = config_handler.check_save_location(
            os.path.expanduser('~'))['config']
        provenance_path = config['saveDir'] + "forge" + "/provenance"
        print("Cloning repo, this can take a few seconds...")
        git.Repo.clone_from(global_.PROVENANCE_REPO, provenance_path)
    if not tag and not provenance_branch and not network:
        provenance_branch = 'main'
    if not moniker:
        if provenance_branch:
            moniker = "localnet-{}".format(provenance_branch)
        else:
            moniker = "localnet-{}".format(tag)
    if not chain_id:
        if provenance_branch:
            chain_id = "localnet-{}".format(provenance_branch)
        else:
            chain_id = "localnet-{}".format(tag)
    if not network:
        network = 'localnet'
    if not boot_args:
        boot_args = ['WITH_CLEVELDB=no']
    try:
        if network == 'localnet':
            if provenance_branch:
                node_info = config[network][provenance_branch]
            else:
                node_info = config[network][tag]
        else:
            node_info = config[network]
        if provenance_branch:
            builder.spawnDaemon(
                node_info['run-command'], provenance_branch, network, config, node_info['log-path'])
        else:
            builder.spawnDaemon(
                node_info['run-command'], tag, network, config, node_info['log-path'])
    except KeyError:
        builder.build(global_.CHAIN_ID_STRINGS[network], network, config, provenance_branch, tag, list(
            boot_args), moniker, chain_id, start_node=True, skip_build=skip_build)
    return


@click.command(
    "init",
    help="Initialize a new node",
    cls=command_required_option_from_option('skip_build')
)
@click.option(
    "-n",
    "--network",
    "network",
    type=click.Choice(["localnet", "mainnet", "testnet"]),
    help="The provenance network to start / connect to")
@click.option(
    "-t",
    "--tag",
    "tag",
    default=None,
    help="Release tag to init the network with")
@click.option(
    '-b',
    '--provenance-branch',
    'provenance_branch',
    type=click.STRING,
    help='A branch of Provenance to be used to build the binary instead of tag')
@click.option(
    '-m',
    '--moniker',
    'moniker',
    type=click.STRING,
    default=None,
    help='A moniker to be used for spinning up a localnet node. Not required for testnet or mainnet')
@click.option(
    '-c',
    '--chain-id',
    'chain_id',
    type=click.STRING,
    default=None,
    help='A chain id to be used for spinning up a localnet node. Not required for testnet or mainnet')
@click.option(
    '-a',
    '--boot-args',
    'boot_args',
    type=click.Choice(global_.ARGS_LIST, case_sensitive=True),
    multiple=True,
    default=[],
    help='List of args for building the provenance binary. Requires "--network" tag')
@click.option(
    '--no-build',
    'skip_build',
    is_flag=True,
    default=False,
    help='Skip building binary on local machine. Downloads from github repo instead. Requires --tag arg to be given for binary download. --network can be given to specify mainnet/testnet for genesis download.')
def node_init_cmd(network, tag, moniker, chain_id, provenance_branch, boot_args, skip_build):
    try:
        config = utils.load_config()
        provenance_path = config['saveDir'] + "forge" + "/provenance"
    except:
        config = config_handler.check_save_location(
            os.path.expanduser('~'))['config']
        provenance_path = config['saveDir'] + "forge" + "/provenance"
        print("Cloning repo, this can take a few seconds...")
        if not os.path.exists(provenance_path):
            git.Repo.clone_from(global_.PROVENANCE_REPO, provenance_path)
    if not tag and not provenance_branch and not network:
        provenance_branch = 'main'
    if not moniker:
        if provenance_branch:
            moniker = "localnet-{}".format(provenance_branch)
        else:
            moniker = "localnet-{}".format(tag)
    if not chain_id:
        if provenance_branch:
            chain_id = "localnet-{}".format(provenance_branch)
        else:
            chain_id = "localnet-{}".format(tag)
    if not network:
        network = 'localnet'
    if not boot_args:
        boot_args = ['WITH_CLEVELDB=no']

    builder.build(global_.CHAIN_ID_STRINGS[network], network, config, provenance_branch, tag, list(
        boot_args), moniker, chain_id, start_node=False, skip_build=skip_build)
    return


@click.command(
    "status",
    help="Get the status of the currently running node")
def node_status_cmd():
    # Display information on the node that is running
    node_status, message = utils.view_running_node_info()
    if node_status:
        print(json.dumps(node_status, indent=4))
    else:
        print(message)
    return

@click.command(
    'mnemonic',
    help='List mnemonic for initialized nodes'
)
@click.option(
    "-t",
    "--tag",
    "tag",
    default=None,
    help="Release tag used to specify the localnet mnemonic to display")
@click.option(
    '-b',
    '--provenance-branch',
    'provenance_branch',
    type=click.STRING,
    help='Provenance branch used to specify the localnet mnemonic to display')
def node_list_mnemonic_cmd(tag, provenance_branch):
    # get config or set location of config to be made
    if not os.path.exists(global_.CONFIG_PATH + "/config.json"):
        config = config_handler.set_build_location()
    else:
        config = utils.load_config()
    provenance_path = config['saveDir'] + "forge" + "/provenance"
    # Retrieve the config information if it exists, else display a message saying that it couldn't be found
    try:
        if tag:
            if tag not in utils.get_versions():
                print(
                    "The tag entered doesn't exist in provenance. Please run 'forge provenance tags' to list all tags")
            else:
                print(" ".join(config['localnet'][tag]['mnemonic']))
        elif provenance_branch:
            if provenance_branch not in utils.get_remote_branches():
                print(
                    "The branch entered doesn't exist in provenance. Please run 'forge provenance branches' to list all branches")
            else:
                print(" ".join(config['localnet'][provenance_branch]['mnemonic']))
        else:
            for version in config['localnet'].keys():
                print("Localnet version: {}\nMnemonic: {}".format(version, " ".join(config['localnet'][version]['mnemonic'])))
    except KeyError:
        print("No nodes found.")
    except:
        print("No nodes have been initialized.")