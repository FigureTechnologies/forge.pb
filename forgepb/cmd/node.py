import json
import os
import click
import git

from forgepb import utils, builder, config_handler, global_


@click.command(
    "stop",
    help="Stop the currently running node"
)
def node_stop_cmd():
    process_information, _ = utils.view_running_node_info()
    utils.stop_active_node(process_information)
    return


@click.command(
    "start",
    help="Start a provenance node with default values")
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
def node_start_cmd(network, tag, moniker, chain_id, provenance_branch, boot_args):
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
            boot_args), moniker, chain_id, start_node=True)
    return


@click.command(
    "init",
    help="Initialize a new node"
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
def node_init_cmd(network, tag, moniker, chain_id, provenance_branch, boot_args):
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

    builder.build(global_.CHAIN_ID_STRINGS[network], network, config, provenance_branch, tag, list(
        boot_args), moniker, chain_id, start_node=False)
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
    exit()
