import json
import os
import click

from forgepb import config_handler


@click.command(
    'save_location',
    help='Change the save location of forge'
)
@click.option(
    '-p',
    '--path',
    'path',
    type=click.STRING,
    help='Existing path that forge will save initialized nodes into'
)
def change_save_loc_cmd(path):
    config_handler.check_save_location(path)
    return
