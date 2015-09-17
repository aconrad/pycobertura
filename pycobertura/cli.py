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


class ExitCodes:
    OK = 0
    EXCEPTION = 1
    COVERAGE_WORSENED = 2
    NOT_ALL_CHANGES_COVERED = 3


def get_exit_code(differ, source):
    # Compute the non-zero exit code. This is a 2-step process which involves
    # checking whether code coverage is any better first and then check if all
    # changes are covered (stricter) which can only be done if the source code
    # is available (and enabled via the --source option).

    if not differ.has_better_coverage():
        return ExitCodes.COVERAGE_WORSENED

    if source:
        if differ.has_all_changes_covered():
            return ExitCodes.OK
        else:
            return ExitCodes.NOT_ALL_CHANGES_COVERED
    else:
        return ExitCodes.OK


@pycobertura.command()
@click.argument('cobertura_file')
@click.option(
    '-f', '--format', default='text',
    type=click.Choice(list(reporters))
)
@click.option(
    '-o', '--output', metavar='<file>', type=click.File('wb'),
    help='Write output to <file> instead of stdout.'
)
@click.option(
    '-s', '--source', metavar='<source-dir>',
    help='Provide path to source code directory for HTML output.'
)
def show(cobertura_file, format, output, source):
    """show coverage summary of a Cobertura report"""
    cobertura = Cobertura(cobertura_file, base_path=source)
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


@pycobertura.command(help="""\
The diff command compares and shows the changes between two Cobertura reports.

NOTE: Reporting missing lines or showing the source code with the diff command
can only be accurately computed if the versions of the source code used to
generate each of the coverage reports is accessible. By default, the source
will read from the Cobertura report and resolved relatively from the report's
location. If the source is not accessible from the report's location, the
options `--source1` and `--source2` are necessary to point to the source code
directories. If the source is not available at all, pass `--no-source` but
missing lines and source code will not be reported.
""")
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
    '-o', '--output', metavar='<file>', type=click.File('wb'),
    help='Write output to <file> instead of stdout.'
)
@click.option(
    '-s1', '--source1', metavar='<source-dir1>',
    help='Provide path to source code directory of first Cobertura report. '
         'This is necessary if the filename path defined in the report is not '
         'accessible from the location of the report.'
)
@click.option(
    '-s2', '--source2', metavar='<source-dir2>',
    help='Provide path to source code directory of second Cobertura report. '
         'This is necessary if the filename path defined in the report is not '
         'accessible from the location of the report.'
)
@click.option(
    '--source/--no-source', default=True,
    help='Show missing lines and source code. When enabled (default), this '
         'option requires access to the source code that was used to generate '
         'both Cobertura reports (see --source1 and --source2). When '
         '`--no-source` is passed, missing lines and the source code will '
         'not be displayed.'
)
def diff(
        cobertura_file1, cobertura_file2,
        color, format, output, source1, source2, source):
    """compare coverage of two Cobertura reports"""
    cobertura1 = Cobertura(cobertura_file1, base_path=source1)
    cobertura2 = Cobertura(cobertura_file2, base_path=source2)

    Reporter = delta_reporters[format]
    reporter_args = [cobertura1, cobertura2]
    reporter_kwargs = {'show_source': source}

    isatty = True if output is None else output.isatty()

    if format == 'text':
        color = isatty if color is None else color is True
        reporter_kwargs['color'] = color

    reporter = Reporter(*reporter_args, **reporter_kwargs)
    report = reporter.generate()

    if not isinstance(report, bytes):
        report = report.encode('utf-8')

    click.echo(report, file=output, nl=isatty, color=color)

    exit_code = get_exit_code(reporter.differ, source)
    raise SystemExit(exit_code)
