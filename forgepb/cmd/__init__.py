import click

from cmd.node import *
from cmd.config import *
from cmd.list import *


@click.group("node")
def node_cmd(): pass


@click.group("config")
def config_cmd(): pass


@click.group("list")
def list_cmd(): pass


# Hook up sub commands for node management.
node_cmd.add_command(node_stop_cmd)
node_cmd.add_command(node_start_cmd)
node_cmd.add_command(node_status_cmd)
node_cmd.add_command(node_init_cmd)

config_cmd.add_command(list_config_cmd)
config_cmd.add_command(change_save_loc_cmd)

list_cmd.add_command(list_branches_cmd)
list_cmd.add_command(list_tags_cmd)
