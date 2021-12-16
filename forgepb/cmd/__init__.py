import click

from forgepb.cmd.config import *
from forgepb.cmd.node import *
from forgepb.cmd.provenance import *


@click.group("node", help="Interact with nodes")
def node_cmd(): pass


@click.group("config")
def config_cmd(): pass


@click.group("provenance", help="Retrieve information on provenance")
def provenance_cmd(): pass


# Hook up sub commands for node management.
node_cmd.add_command(node_stop_cmd)
node_cmd.add_command(node_start_cmd)
node_cmd.add_command(node_status_cmd)
node_cmd.add_command(node_init_cmd)
node_cmd.add_command(node_list_mnemonic_cmd)
node_cmd.add_command(node_tail_cmd)

config_cmd.add_command(change_save_loc_cmd)

provenance_cmd.add_command(list_tags_cmd)
provenance_cmd.add_command(list_branches_cmd)
