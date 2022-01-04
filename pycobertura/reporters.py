from collections import namedtuple
from jinja2 import Environment, PackageLoader
from pycobertura.cobertura import CoberturaDiff
from pycobertura.utils import green, rangify, red
from pycobertura.templates import filters
from tabulate import tabulate


env = Environment(loader=PackageLoader("pycobertura", "templates"))
env.filters["line_status"] = filters.line_status
env.filters["line_reason"] = filters.line_reason_icon

row_attributes = ["filename", "total_statements", "total_misses", "line_rate"]
file_row = namedtuple("FileRow", row_attributes)
file_row_missed = namedtuple("FileRowMissed", row_attributes + ["missed_lines"])


class Reporter(object):
    def __init__(self, cobertura):
        self.cobertura = cobertura

    def format_line_rate(self, line_rate):
        return f"{line_rate:.2%}"

    def format_missed_lines(self, missed_lines):
        return ", ".join([f"{line_start}" if line_start == line_stop else f"{line_start}-{line_stop}" for line_start, line_stop in rangify(missed_lines)])

    def get_report_lines(self):
        rows = tuple(
            (
                filename,
                self.cobertura.total_statements(filename),
                self.cobertura.total_misses(filename),
                self.format_line_rate(self.cobertura.line_rate(filename)),
                self.cobertura.missed_lines(filename)
            )
            for filename in self.cobertura.files()
        )
        footer = (
            (
            "TOTAL",
            self.cobertura.total_statements(),
            self.cobertura.total_misses(),
            self.format_line_rate(self.cobertura.line_rate()),
            [],  # dummy missed lines
        ),
        )

        rows += footer

        return tuple(file_row_missed(*row) for row in rows)


class TextReporter(Reporter):
    def format_row(self, row):
        filename, total_lines, total_misses, line_rate, missed_lines = row

        formatted_missed_lines = self.format_missed_lines(missed_lines)

        row = file_row_missed(
            filename,
            total_lines,
            total_misses,
            line_rate,
            formatted_missed_lines,
        )

        return row

    def generate(self):
        lines = self.get_report_lines()
        formatted_lines = [self.format_row(row) for row in lines]

        return  tabulate(formatted_lines, headers=["Filename", "Stmts", "Miss", "Cover", "Missing"])


class HtmlReporter(TextReporter):
    def __init__(self, *args, **kwargs):
        self.title = kwargs.pop("title", "pycobertura report")
        self.render_file_sources = kwargs.pop("render_file_sources", True)
        self.no_file_sources_message = kwargs.pop(
            "no_file_sources_message", "Rendering of source files was disabled."
        )
        super(HtmlReporter, self).__init__(*args, **kwargs)

    def get_source(self, filename):
        lines = self.cobertura.file_source(filename)
        return lines

    def generate(self):
        lines = self.get_report_lines()

        formatted_lines = [self.format_row(row) for row in lines]

        sources = []
        if self.render_file_sources:
            sources = [(filename, self.get_source(filename)) for filename in self.cobertura.files()]

        template = env.get_template("html.jinja2")
        return template.render(
            title=self.title,
            lines=formatted_lines[:-1],
            footer=formatted_lines[-1],
            sources=sources,
            no_file_sources_message=self.no_file_sources_message,
        )


class DeltaReporter(object):
    def __init__(self, cobertura1, cobertura2, show_source=True):
        self.differ = CoberturaDiff(cobertura1, cobertura2)
        self.show_source = show_source

    def get_file_row(self, filename):
        row_values = [
            filename,
            self.differ.diff_total_statements(filename),
            self.differ.diff_total_misses(filename),
            self.differ.diff_line_rate(filename),
        ]

        if self.show_source is True:
            missed_lines = self.differ.diff_missed_lines(filename)
            row_values.append(missed_lines)
            row = file_row_missed(*row_values)
        else:
            row = file_row(*row_values)

        return row

    def get_footer_row(self):
        footer_values = [
            "TOTAL",
            self.differ.diff_total_statements(),
            self.differ.diff_total_misses(),
            self.differ.diff_line_rate(),
        ]

        if self.show_source:
            footer_values.append([])  # dummy missed lines
            footer = file_row_missed(*footer_values)
        else:
            footer = file_row(*footer_values)

        return footer

    def get_report_lines(self):
        lines = []

        for filename in self.differ.files():
            file_row = self.get_file_row(filename)
            if any(file_row[1:]):  # don't report unchanged class files
                lines.append(file_row)

        footer = self.get_footer_row()
        lines.append(footer)

        return lines


class TextReporterDelta(DeltaReporter):
    def __init__(self, *args, **kwargs):
        """
        Takes the same arguments as `DeltaReporter` but also takes the keyword
        argument `color` which can be set to True or False depending if the
        generated report should be colored or not (default `color=False`).
        """
        self.color = kwargs.pop("color", False)
        super(TextReporterDelta, self).__init__(*args, **kwargs)

    def format_row(self, row):
        total_statements = f"{row.total_statements:+d}"  if row.total_statements else "-"
        line_rate = f"{row.line_rate:+.2%}" if row.line_rate else "-"
        total_misses = f"{row.total_misses:+d}" if row.total_misses else "-"

        if self.color is True and total_misses != "-":
            colorize = [green, red][total_misses[0] == "+"]
            total_misses = colorize(total_misses)

        if self.show_source is True:
            missed_lines = [f"+{lno:d}" if is_new else f"-{lno:d}" for lno, is_new in row.missed_lines]

            if self.color is True:
                missed_lines_colored = []
                for line in missed_lines:
                    colorize = [green, red][line[0] == "+"]
                    colored_line = colorize(line)
                    missed_lines_colored.append(colored_line)
            else:
                missed_lines_colored = missed_lines

            missed_lines = ", ".join(missed_lines_colored)

        row = [
            row.filename,
            total_statements,
            total_misses,
            line_rate,
        ]

        if self.show_source is True:
            row.append(missed_lines)

        return row

    def generate(self):
        lines = self.get_report_lines()

        formatted_lines = [self.format_row(row) for row in lines]

        headers = ["Filename", "Stmts", "Miss", "Cover"]

        if self.show_source is True:
            headers.append("Missing")

        report = tabulate(formatted_lines, headers=headers)

        return report


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
        hunks = self.differ.file_source_hunks(filename)
        return hunks

    def format_row(self, row):
        total_statements = f"{row.total_statements:+d}"  if row.total_statements else "-"
        line_rate = f"{row.line_rate:+.2%}" if row.line_rate else "-"
        total_misses = f"{row.total_misses:+d}" if row.total_misses else "-"

        if self.show_source is True and self.show_missing is True:
            missed_lines = [f"+{lno:d}" if is_new else f"-{lno:d}" for lno, is_new in row.missed_lines]


        row_values = [
            row.filename,
            total_statements,
            total_misses,
            line_rate,
        ]

        if self.show_source is True and self.show_missing is True:
            row_values.append(missed_lines)
            row = file_row_missed(*row_values)
        else:
            row = file_row(*row_values)

        return row

    def generate(self):
        lines = self.get_report_lines()

        formatted_lines = [self.format_row(row) for row in lines]

        if self.show_source is True:
            sources = []
            for filename in self.differ.files():
                source_hunks = self.get_source_hunks(filename)
                if not source_hunks:
                    continue
                sources.append((filename, source_hunks))

        template = env.get_template("html-delta.jinja2")

        render_kwargs = {
            "lines": formatted_lines[:-1],
            "footer": formatted_lines[-1],
            "show_missing": self.show_missing,
            "show_source": self.show_source,
        }

        if self.show_source is True:
            render_kwargs["sources"] = sources

        return template.render(**render_kwargs)
