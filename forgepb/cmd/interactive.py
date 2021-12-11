import sys
import click

import forge


sys.path.insert(1, './forgepb')


@click.command(
    'interactive',
    help='Start interactive forge for guided experience'
)
def start_wizard():
    forge.main()
