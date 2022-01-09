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
        lines = {
            "Filename": [filename for filename in self.cobertura.files()]+["TOTAL"],
            "Stmts": [self.cobertura.total_statements(filename) for filename in self.cobertura.files()]+[self.cobertura.total_statements()],
            "Miss": [self.cobertura.total_misses(filename) for filename in self.cobertura.files()]+[self.cobertura.total_misses()],
            "Cover": [self.format_line_rate(self.cobertura.line_rate(filename)) for filename in self.cobertura.files()]+[self.format_line_rate(self.cobertura.line_rate())],
            "Missing": [stringify(self.cobertura.missed_lines(filename)) for filename in self.cobertura.files()]+['']
        }

        return lines

class TextReporter(Reporter):
    def generate(self):
        lines = self.get_report_lines()
        return  tabulate(lines, headers=headers_missing)

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
            sources = [(filename, self.cobertura.file_source(filename)) for filename in self.cobertura.files()]

        template = env.get_template("html.jinja2")
        rows = {k: v[:-1] for k, v in lines.items()}
        footer = {k: v[-1] for k, v in lines.items()}

        return template.render(
            title=self.title,
            lines=rows,
            footer=footer,
            sources=sources,
            no_file_sources_message=self.no_file_sources_message,
        )

class DeltaReporter(object):
    def __init__(self, cobertura1, cobertura2, show_source=True, *args, **kwargs):
        self.differ = CoberturaDiff(cobertura1, cobertura2)
        self.show_source = show_source
        self.color = kwargs.pop("color", False)

    @staticmethod
    def format_line_rate(line_rate):
        return f"{line_rate:+.2%}" if line_rate else "-"

    @staticmethod
    def format_total_statements(total_statements):
        return f"{total_statements:+d}" if total_statements else "-"

    @staticmethod
    def format_missed_lines(missed_lines):
        return [f"+{lno:d}" if is_new else f"-{lno:d}" for lno, is_new in missed_lines]

    def color_row(self, row):
        if self.color is True:
            return red(row) if row[0] == "+" else green(row)
        return row

    def format_total_misses(self, total_misses):
        return self.color_row(f"{total_misses:+d}") if total_misses else "-"

    def get_report_lines(self):
        if not self.show_source:
            row_values = tuple(
                (
                    filename,
                    self.format_total_statements(self.differ.diff_total_statements(filename)),
                    self.format_total_misses(self.differ.diff_total_misses(filename)),
                    self.format_line_rate(self.differ.diff_line_rate(filename)),
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
                    self.format_total_statements(self.differ.diff_total_statements()),
                    self.format_total_misses(self.differ.diff_total_misses()),
                    self.format_line_rate(self.differ.diff_line_rate()),
                ),
            )
            row_values += footer_values
            return tuple(file_row(*row) for row in row_values)
        else:
            row_values = tuple(
                (
                    filename,
                    self.format_total_statements(self.differ.diff_total_statements(filename)),
                    self.format_total_misses(self.differ.diff_total_misses(filename)),
                    self.format_line_rate(self.differ.diff_line_rate(filename)),
                    self.format_missed_lines(self.differ.diff_missed_lines(filename)),
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
                    self.format_total_statements(self.differ.diff_total_statements()),
                    self.format_total_misses(self.differ.diff_total_misses()),
                    self.format_line_rate(self.differ.diff_line_rate()),
                    [],
                ),
            )
            row_values += footer_values
            return tuple(file_row_missed(*row) for row in row_values)


class TextReporterDelta(DeltaReporter):
    def __init__(self, *args, **kwargs):
        super(TextReporterDelta, self).__init__(*args, **kwargs)

    def format_row_if_show_source(self, row):
        missed_lines_colored = ", ".join([self.color_row(line) for line in row.missed_lines])
        row_values = row[:-1]
        row_values += (missed_lines_colored,)
        return row_values

    def generate(self):
        lines = self.get_report_lines()

        if self.show_source:
            formatted_lines = [self.format_row_if_show_source(row) for row in lines]
            lines = formatted_lines

        headers = headers_missing if self.show_source is True else headers_without_missing

        return tabulate(lines, headers=headers)


class HtmlReporterDelta(DeltaReporter):
    def __init__(self, *args, **kwargs):
        """
        Takes the same arguments as `TextReporterDelta` but also takes the keyword
        argument `show_missing` which can be set to True or False to set whether
        or not the generated report should contain a listing of missing lines in
        the summary table.
        """
        self.show_missing = kwargs.pop("show_missing", True)
        super(HtmlReporterDelta, self).__init__(*args, **kwargs)

    def generate(self):
        lines = self.get_report_lines()

        template = env.get_template("html-delta.jinja2")

        render_kwargs = {
            "lines": lines[:-1],
            "footer": lines[-1],
            "show_missing": self.show_missing,
            "show_source": self.show_source,
        }

        if self.show_source is True:
            render_kwargs["sources"] = [
                (
                    filename, self.differ.file_source_hunks(filename)
                )
                for filename in self.differ.files()
                if self.differ.file_source_hunks(filename)
            ]

        return template.render(**render_kwargs)
