import click

from .cli import pycobertura

cli = click.CommandCollection(sources=[pycobertura])

if __name__ == "__main__":
    cli()
