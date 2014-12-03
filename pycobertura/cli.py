import click

from pycobertura.cobertura import Cobertura
from pycobertura.reporters import (
    HtmlReporter, TextReporter, HtmlReporterDelta, TextReporterDelta
)


pycobertura = click.Group()


reporters = {
    'html': HtmlReporter,
    'text': TextReporter,
}


@pycobertura.command()
@click.argument('cobertura_file')
@click.option(
    '-f', '--format',
    default='text',
    type=click.Choice(list(reporters))
)
def show(cobertura_file, format):
    """show the coverage summary"""
    cobertura = Cobertura(cobertura_file)
    Reporter = reporters[format]
    report = Reporter(cobertura)
    print(report.generate())


delta_reporters = {
    'text': TextReporterDelta,
    'html': HtmlReporterDelta,
}


@pycobertura.command()
@click.argument('cobertura_file1')
@click.argument('cobertura_file2')
@click.option(
    '--color/--no-color', default=None,
    help='Colorize the output. By default, pycobertura emits color codes only '
         'when standard output is connected to a terminal. This has no effect '
         'with the HTML output format.')
@click.option(
    '-f', '--format',
    default='text',
    type=click.Choice(list(delta_reporters))
)
def diff(cobertura_file1, cobertura_file2, color, format):
    """compare two coverage files"""
    cobertura1 = Cobertura(cobertura_file1)
    cobertura2 = Cobertura(cobertura_file2)
    Reporter = delta_reporters[format]
    report = Reporter(cobertura1, cobertura2, color=color)
    print(report.generate())
