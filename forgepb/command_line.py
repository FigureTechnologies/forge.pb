import click

from forgepb import forge, cmd


class CustomMultiCommand(click.Group):
    def command(self, *args, **kwargs):
        """Behaves the same as `click.Group.command()` except if passed
        a list of names, all after the first will be aliases for the first.
        """
        def decorator(f):
            if isinstance(args[0], list):
                _args = [args[0][0]] + list(args[1:])
                for alias in args[0][1:]:
                    cmd = super(CustomMultiCommand, self).command(
                        alias, *args[1:], **kwargs)(f)
                    cmd.short_help = "Alias for '{}'".format(_args[0])
            else:
                _args = args
            cmd = super(CustomMultiCommand, self).command(
                *_args, **kwargs)(f)
            return cmd

        return decorator


@click.group("root", cls=CustomMultiCommand)
def root_cmd(): pass


@root_cmd.command(
    ['interactive', 'i'],
    help='Start interactive forge for guided experience'
)
def start_wizard():
    forge.main()


root_cmd.add_command(cmd.node_cmd)
root_cmd.add_command(cmd.config_cmd)
root_cmd.add_command(cmd.provenance_cmd)

# Point for setup.py to point to for installing
start = click.CommandCollection(sources=[root_cmd])
