import sys

import click

sys.path.insert(1, './forgepb')
from cmd.interactive import start_wizard
from cmd import node_cmd, config_cmd, list_cmd


@click.group("root")
def root_cmd(): pass


root_cmd.add_command(node_cmd)
root_cmd.add_command(config_cmd)
root_cmd.add_command(list_cmd)
root_cmd.add_command(start_wizard)

# Point for setup.py to point to for installing
start = click.CommandCollection(sources=[root_cmd])
