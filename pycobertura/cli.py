import click

from pycobertura.cobertura import Cobertura
from pycobertura.reports import TextReport, TextReportDelta


pycobertura = click.Group()


@pycobertura.command()
@click.argument('cobertura_file')
def show(cobertura_file):
    """show the coverage summary"""
    cobertura = Cobertura(cobertura_file)
    report = TextReport(cobertura)
    print(report.generate())


@pycobertura.command()
@click.argument('cobertura_file1')
@click.argument('cobertura_file2')
@click.option(
    '--color/--no-color', default=None,
    help='Colorize the output. By default, pycobertura emits color codes only '
         'when standard output is connected to a terminal.')
def diff(cobertura_file1, cobertura_file2, color):
    """compare two coverage files"""
    cobertura1 = Cobertura(cobertura_file1)
    cobertura2 = Cobertura(cobertura_file2)
    report = TextReportDelta(cobertura1, cobertura2, color=color)
    print(report.generate())
