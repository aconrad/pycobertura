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
def diff(cobertura_file1, cobertura_file2):
    """compare two coverage files"""
    from pycobertura.cobertura import Cobertura
    from pycobertura.reports import TextReportDelta

    cobertura1 = Cobertura(cobertura_file1)
    cobertura2 = Cobertura(cobertura_file2)
    report = TextReportDelta(cobertura1, cobertura2)
    print(report.generate())
