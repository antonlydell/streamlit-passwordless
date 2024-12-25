r"""The entry point of the Streamlit passwordless CLI."""

# Third party
import click

# Local
from streamlit_passwordless import __releasedate__
from streamlit_passwordless.cli.commands.run import run

COMMANDS = (run,)


@click.group(
    name='stp',
    context_settings={'help_option_names': ['-h', '--help'], 'max_content_width': 1000},
)
@click.version_option(
    message=(
        f'%(prog)s, version: %(version)s, '
        f'release date: {__releasedate__}, '
        'maintainer: Anton Lydell'
    )
)
def main() -> None:
    r"""Manage the Streamlit Passwordless user database."""


for cmd in COMMANDS:
    main.add_command(cmd)

if __name__ == '__main__':
    main()
