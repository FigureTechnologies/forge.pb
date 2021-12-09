import click

from forgepb import utils, builder, forge


@click.command(
    "init",
    help="Initialize a new node"
)
def node_init_cmd():
    forge.main()


@click.command(
    "start",
    help="Start a provenance node with default values")
@click.option(
    "--network",
    default="localnet",
    type=click.Choice(["localnet", "mainnet", "testnet"]),
    help="The provenance network to start / connect to")
@click.option(
    "--release-version",
    default=None,
    help="Release version to init the network with")
def node_start_cmd(network, release_version):
    process_information = utils.view_running_node_info()
    if process_information['node-running']:
        utils.handle_running_node(process_information)
        return
    try:
        config = utils.load_config()
        provenance_path = config['saveDir'] + "forge" + "/provenance"
    except Exception:
        print("You haven't initialized a node. Try running 'forge node init' to start the wizard.")
        return

    else:
        try:
            if network != 'localnet':
                node_info = config[network]
            else:
                if release_version is None:
                    release_version = utils.get_latest_version()
                elif release_version not in utils.get_versions(provenance_path):
                    print("Starting a node depends on valid values for release-version and network.")
                    return
                node_info = config[network][release_version]

            builder.spawnDaemon(node_info['run-command'], release_version, network, config, node_info['log-path'])
        except Exception as e:
            print("The combination of network {} and version {} hasn't been initialized yet"
                  .format(network, release_version))


@click.command(
    "status",
    help="Get the status of the currently running node")
def node_status_cmd():
    # Display information on the node that is running
    status = utils.view_running_node_info()['message']
    print(status or "There currently isn't a node running.")


@click.command(
    "stop",
    help="Stop the currently running node")
def node_stop_cmd():
    # Stop the currently running node
    process_information = utils.view_running_node_info()
    utils.stop_active_node(process_information)
