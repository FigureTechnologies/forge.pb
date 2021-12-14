import click

from forgepb import config_handler, utils


@click.command(
    'save_location',
    help='Change the save location of forge'
)
@click.argument(
    'path',
    type=str,
    required=False,
)
def change_save_loc_cmd(path):
    if path is None:
        if not utils.exists_config():
            print("save_location=None")
            return

        cfg = utils.load_config()
        print(cfg["saveDir"])
        return
    else:
        config_handler.check_save_location(path)
    return
