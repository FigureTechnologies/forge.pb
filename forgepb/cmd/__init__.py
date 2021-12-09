import click

from cmd.node import *


@click.group("node")
def node_cmd(): pass


# Hook up sub commands for node management.
node_cmd.add_command(node_stop_cmd)
node_cmd.add_command(node_start_cmd)
node_cmd.add_command(node_status_cmd)
node_cmd.add_command(node_init_cmd)
