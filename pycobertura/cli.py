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
@click.option(
    '-o', '--output', metavar='<file>',
    type=click.File('wb'),
    help='Write output to <file> instead of stdout.'
)
def show(cobertura_file, format, output):
    """show the coverage summary"""
    cobertura = Cobertura(cobertura_file)
    Reporter = reporters[format]
    reporter = Reporter(cobertura)
    report = reporter.generate()

    if not isinstance(report, bytes):
        report = report.encode('utf-8')

    isatty = True if output is None else output.isatty()
    click.echo(report, file=output, nl=isatty)


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
    '-f', '--format', default='text',
    type=click.Choice(list(delta_reporters))
)
@click.option(
    '-o', '--output', metavar='<file>',
    type=click.File('wb'),
    help='Write output to <file> instead of stdout.'
)
def diff(cobertura_file1, cobertura_file2, color, format, output):
    """compare two coverage files"""
    cobertura1 = Cobertura(cobertura_file1)
    cobertura2 = Cobertura(cobertura_file2)
    Reporter = delta_reporters[format]
    reporter_args = [cobertura1, cobertura2]
    reporter_kwargs = {}

    isatty = True if output is None else output.isatty()
    if format == 'text':
        color = isatty if color is None else color is True
        reporter_kwargs['color'] = color

    reporter = Reporter(*reporter_args, **reporter_kwargs)
    report = reporter.generate()

    if not isinstance(report, bytes):
        report = report.encode('utf-8')

    # FIXME: In Click 3.x, the color is stripped out if the output file is
    # detected to not support ANSI codes causing `-o outfile --color` to write
    # to `outfile` without colors. In Click 4.x, `echo()` will take a
    # color=True/False flag which will allow us to override ANSI code
    # auto-detection.
    # https://github.com/mitsuhiko/click/commit/5cf7f2ddfba328070751cbda32782520d4e0d6f5
    # click.echo(report, file=output, nl=isatty, color=color)  # click 4.x
    click.echo(report, file=output, nl=isatty)

    # non-zero exit code if line rate worsened
    exit_code = cobertura1.line_rate() > cobertura2.line_rate()
    raise SystemExit(exit_code)
