import json
import os
import click

from forgepb import utils, builder, forge, config_handler, global_


@click.command(
    'list',
    help='List config information about localnet nodes that have been initialized'
)
@click.option(
    "-t",
    "--tag",
    "tag",
    default=None,
    help="Release tag used to specify the localnet config to display")
@click.option(
    '-b',
    '--provenance-branch',
    'provenance_branch',
    type=click.STRING,
    help='Provenance branch used to specify the localnet config to display')
def list_config_cmd(tag, provenance_branch):
    # get config or set location of config to be made
    if not os.path.exists(global_.CONFIG_PATH + "/config.json"):
        config = config_handler.set_build_location()
    else:
        config = utils.load_config()
    provenance_path = config['saveDir'] + "forge" + "/provenance"
    # Retrieve the config information if it exists, else display a message saying that it couldn't be found
    try:
        if tag:
            if tag not in utils.get_versions(provenance_path):
                print(
                    "The version entered doesn't exist in provenance. Please run 'forge -lsv' to list all versions")
            else:
                print(json.dumps(config['localnet'][tag], indent=4))
        elif provenance_branch:
            if provenance_branch not in utils.get_remote_branches(provenance_path=provenance_path):
                print(
                    "The version entered doesn't exist in provenance. Please run 'forge -lsv' to list all versions")
            else:
                print(json.dumps(config['localnet']
                      [provenance_branch], indent=4))
        else:
            print(json.dumps(config['localnet'], indent=4))
    except KeyError:
        print("No nodes found.")
    except:
        print("No nodes have been initialized.")


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
