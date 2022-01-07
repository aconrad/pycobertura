from collections import namedtuple
from jinja2 import Environment, PackageLoader
from pycobertura.cobertura import CoberturaDiff
from pycobertura.utils import green, red, stringify
from pycobertura.templates import filters
from tabulate import tabulate


env = Environment(loader=PackageLoader("pycobertura", "templates"))
env.filters["line_status"] = filters.line_status
env.filters["line_reason"] = filters.line_reason_icon

row_attributes = ["filename", "total_statements", "total_misses", "line_rate"]
file_row = namedtuple("FileRow", row_attributes)
file_row_missed = namedtuple("FileRowMissed", row_attributes + ["missed_lines"])

headers_without_missing = ["Filename", "Stmts", "Miss", "Cover"]
headers_missing = ["Filename", "Stmts", "Miss", "Cover", "Missing"]


class Reporter(object):
    def __init__(self, cobertura):
        self.cobertura = cobertura

    @staticmethod
    def format_line_rate(line_rate):
        return f"{line_rate:.2%}"

    def get_report_lines(self):
        rows = tuple(
            (
                filename,
                self.cobertura.total_statements(filename),
                self.cobertura.total_misses(filename),
                self.format_line_rate(self.cobertura.line_rate(filename)),
                stringify(self.cobertura.missed_lines(filename))
            )
            for filename in self.cobertura.files()
        )
        footer = (
            (
                "TOTAL",
                self.cobertura.total_statements(),
                self.cobertura.total_misses(),
                self.format_line_rate(self.cobertura.line_rate()),
                '',  # stringify([]); dummy missed lines
            ),
        )

        rows += footer

        return tuple(file_row_missed(*row) for row in rows)


class TextReporter(Reporter):
    def generate(self):
        lines = self.get_report_lines()
        return tabulate(lines, headers=headers_missing)


class HtmlReporter(Reporter):
    def __init__(self, *args, **kwargs):
        self.title = kwargs.pop("title", "pycobertura report")
        self.render_file_sources = kwargs.pop("render_file_sources", True)
        self.no_file_sources_message = kwargs.pop(
            "no_file_sources_message", "Rendering of source files was disabled."
        )
        super(HtmlReporter, self).__init__(*args, **kwargs)

    def generate(self):
        lines = self.get_report_lines()

        sources = []
        if self.render_file_sources:
            sources = [(filename, self.cobertura.file_source(filename))
                       for filename in self.cobertura.files()]

        template = env.get_template("html.jinja2")
        return template.render(
            title=self.title,
            lines=lines[:-1],
            footer=lines[-1],
            sources=sources,
            no_file_sources_message=self.no_file_sources_message,
        )


class DeltaReporter(object):
    def __init__(self, cobertura1, cobertura2, show_source=True, *args, **kwargs):
        self.differ = CoberturaDiff(cobertura1, cobertura2)
        self.show_source = show_source
        self.color = kwargs.pop("color", False)
    
    def color_row(self, row):
        if self.color is True:
            return red(row) if row[0] == "+" else green(row)
        return row

    def get_report_lines(self):
        if not self.show_source:
            row_values = tuple(
                (
                    filename,
                    self.differ.diff_total_statements(filename),
                    self.differ.diff_total_misses(filename),
                    self.differ.diff_line_rate(filename),
                )
                    for filename in self.differ.files() if any(
                    (
                    self.differ.diff_total_statements(filename),
                    self.differ.diff_total_misses(filename),
                    self.differ.diff_line_rate(filename),
                    )
                )
            )

            footer_values = (
                (
                "TOTAL",
                self.differ.diff_total_statements(),
                self.differ.diff_total_misses(),
                self.differ.diff_line_rate(),
                ),
            )
            row_values += footer_values
            return tuple(file_row(*row) for row in row_values)
        else:
            row_values = tuple(
                (
                    filename,
                    self.differ.diff_total_statements(filename),
                    self.differ.diff_total_misses(filename),
                    self.differ.diff_line_rate(filename),
                    self.differ.diff_missed_lines(filename),
                )
                for filename in self.differ.files() if any(
                    (
                    self.differ.diff_total_statements(filename),
                    self.differ.diff_total_misses(filename),
                    self.differ.diff_line_rate(filename),
                    self.differ.diff_missed_lines(filename),
                    )
                )
            )
            footer_values = (
                (
                "TOTAL",
                self.differ.diff_total_statements(),
                self.differ.diff_total_misses(),
                self.differ.diff_line_rate(),
                [],
                ),
            )
            row_values += footer_values
            return tuple(file_row_missed(*row) for row in row_values)


class TextReporterDelta(DeltaReporter):
    def __init__(self, *args, **kwargs):
        super(TextReporterDelta, self).__init__(*args, **kwargs)

    def get_row_values(self, row):
        return [
            row.filename,
            f"{row.total_statements:+d}" if row.total_statements else "-",
            self.color_row(f"{row.total_misses:+d}") if row.total_misses else "-",
            f"{row.line_rate:+.2%}" if row.line_rate else "-",
        ]

    def format_row(self, row):
        row_values = self.get_row_values(row)

        if self.show_source is True:
            missed_lines = [
                f"+{lno:d}" if is_new else f"-{lno:d}" for lno, is_new in row.missed_lines]
            missed_lines_colored = ", ".join(
                [self.color_row(line) for line in missed_lines])
            row_values.append(missed_lines_colored)

        return row_values

    def generate(self):
        lines = self.get_report_lines()
        formatted_lines = [self.format_row(row) for row in lines]

        headers = headers_missing if self.show_source is True else headers_without_missing

        return tabulate(formatted_lines, headers=headers)


class HtmlReporterDelta(TextReporterDelta):
    def __init__(self, *args, **kwargs):
        """
        Takes the same arguments as `TextReporterDelta` but also takes the keyword
        argument `show_missing` which can be set to True or False to set whether
        or not the generated report should contain a listing of missing lines in
        the summary table.
        """
        self.show_missing = kwargs.pop("show_missing", True)
        super(HtmlReporterDelta, self).__init__(*args, **kwargs)

    def get_source_hunks(self, filename):
        return self.differ.file_source_hunks(filename)

    def format_row(self, row):
        row_values = self.get_row_values(row)

        if self.show_source is True and self.show_missing is True:
            missed_lines = [
                f"+{lno:d}" if is_new else f"-{lno:d}" for lno, is_new in row.missed_lines]
            row_values.append(missed_lines)
            return file_row_missed(*row_values)

        return file_row(*row_values)

    def generate(self):
        lines = self.get_report_lines()
        formatted_lines = [self.format_row(row) for row in lines]

        template = env.get_template("html-delta.jinja2")

        render_kwargs = {
            "lines": formatted_lines[:-1],
            "footer": formatted_lines[-1],
            "show_missing": self.show_missing,
            "show_source": self.show_source,
        }

        if self.show_source is True:
            render_kwargs["sources"] = [(filename, self.get_source_hunks(
                filename)) for filename in self.differ.files() if self.get_source_hunks(filename)]

        return template.render(**render_kwargs)
