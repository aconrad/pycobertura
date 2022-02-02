from jinja2 import Environment, PackageLoader
from pycobertura.cobertura import CoberturaDiff
from pycobertura.utils import green, red, stringify
from pycobertura.templates import filters
from tabulate import tabulate
import json


env = Environment(loader=PackageLoader("pycobertura", "templates"))
env.filters["line_status"] = filters.line_status
env.filters["line_reason"] = filters.line_reason_icon
env.filters["is_not_equal_to_dash"] = filters.is_not_equal_to_dash
env.filters["misses_color"] = filters.misses_color

headers_without_missing = ["Filename", "Stmts", "Miss", "Cover"]
headers_with_missing = ["Filename", "Stmts", "Miss", "Cover", "Missing"]


class Reporter:
    def __init__(self, cobertura):
        self.cobertura = cobertura

    @staticmethod
    def format_line_rate(line_rate):
        return f"{line_rate:.2%}"

    def get_report_lines(self):
        lines = {
            "Filename": self.cobertura.files().copy(),
            "Stmts": [
                self.cobertura.total_statements(filename)
                for filename in self.cobertura.files()
            ],
            "Miss": [
                self.cobertura.total_misses(filename)
                for filename in self.cobertura.files()
            ],
            "Cover": [
                self.format_line_rate(self.cobertura.line_rate(filename))
                for filename in self.cobertura.files()
            ],
            "Missing": [
                stringify(self.cobertura.missed_lines(filename))
                for filename in self.cobertura.files()
            ],
        }
        lines["Filename"].append("TOTAL")
        lines["Stmts"] += [self.cobertura.total_statements()]
        lines["Miss"] += [self.cobertura.total_misses()]
        lines["Cover"] += [self.format_line_rate(self.cobertura.line_rate())]
        lines["Missing"].append("")

        return lines


class TextReporter(Reporter):
    def generate(self):
        lines = self.get_report_lines()
        return tabulate(lines, headers=headers_with_missing)


class CsvReporter(Reporter):
    def generate(self, delimiter):
        lines = self.get_report_lines()
        list_of_lines = [headers_with_missing] #[[f"{key}" for key in lines]]
        list_of_lines.extend(
            [[f"{item}" for item in row] for row in zip(*lines.values())]
        )

        if "\\n" in repr(delimiter):
            delimiter = "\n"
        if "\\t" in repr(delimiter):
            delimiter = "\t"

        return "\n".join([delimiter.join(line) + delimiter for line in list_of_lines])


class MarkdownReporter(Reporter):
    def generate(self):
        lines = self.get_report_lines()
        return tabulate(lines, headers=headers_with_missing, tablefmt="github")


class JsonReporter(Reporter):
    def generate(self):
        lines = self.get_report_lines()
        rows = {k: v[:-1] for k, v in lines.items()}
        footer = {k: v[-1] for k, v in lines.items() if k != "Missing"}

        return json.dumps({"total": footer, "files": rows}, indent=4)


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
            sources = [
                (filename, self.cobertura.file_source(filename))
                for filename in self.cobertura.files()
            ]

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


class DeltaReporter:
    def __init__(self, cobertura1, cobertura2, show_source=True, *args, **kwargs):
        self.differ = CoberturaDiff(cobertura1, cobertura2)
        self.show_source = show_source
        self.color = kwargs.pop("color", False)

    def format_line_rate(self, line_rate):
        return f"{line_rate:+.2%}" if line_rate else self.not_available

    def format_total_statements(self, total_statements):
        return f"{total_statements:+d}" if total_statements else self.not_available

    @staticmethod
    def format_missed_lines(missed_lines):
        return [f"+{lno:d}" if is_new else f"-{lno:d}" for lno, is_new in missed_lines]

    def determine_color_of_number(self, number):
        return red if number.startswith("+") else green

    def color_number(self, numbers):
        if numbers and self.color:
            if type(numbers) is str:
                color = self.determine_color_of_number(numbers)
                result = color(numbers)
            else:
                result = ", ".join(
                    [
                        self.determine_color_of_number(number)(number)
                        for number in numbers
                    ]
                )
        else:
            if type(numbers) is str:
                result = numbers
            else:
                result = ", ".join(numbers)
        return result

    def format_total_misses(self, total_misses):
        return (
            self.color_number(f"{total_misses:+d}")
            if total_misses
            else self.not_available
        )

    def get_report_lines(self):
        diff_total_stmts = [
            self.differ.diff_total_statements(filename)
            for filename in self.differ.files()
        ]

        diff_total_miss = [
            self.differ.diff_total_misses(filename) for filename in self.differ.files()
        ]

        diff_total_cover = [
            self.differ.diff_line_rate(filename) for filename in self.differ.files()
        ]

        indexes_of_files_with_changes = [
            i
            for i in range(len(self.differ.files()))
            if any(
                (
                    diff_total_stmts[i],
                    diff_total_miss[i],
                    diff_total_cover[i],
                )
            )
        ]

        filenames_of_files_with_changes = [
            self.differ.files()[i] for i in indexes_of_files_with_changes
        ]

        lines = {
            "Filename": filenames_of_files_with_changes,
            "Stmts": [
                self.format_total_statements(diff_total_stmts[i])
                for i in indexes_of_files_with_changes
            ],
            "Miss": [
                self.format_total_misses(diff_total_miss[i])
                for i in indexes_of_files_with_changes
            ],
            "Cover": [
                self.format_line_rate(diff_total_cover[i])
                for i in indexes_of_files_with_changes
            ],
        }

        lines["Filename"].append("TOTAL")
        lines["Stmts"] += [
            self.format_total_statements(self.differ.diff_total_statements())
        ]
        lines["Miss"] += [self.format_total_misses(self.differ.diff_total_misses())]
        lines["Cover"] += [self.format_line_rate(self.differ.diff_line_rate())]

        if self.show_source:
            diff_total_missing = [
                self.differ.diff_missed_lines(filename)
                for filename in self.differ.files()
            ]
            lines["Missing"] = [
                self.format_missed_lines(diff_total_missing[i])
                for i in indexes_of_files_with_changes
            ]
            lines["Missing"].append("")

        return lines


class TextReporterDelta(DeltaReporter):
    not_available = "-"

    def generate(self):
        lines = self.get_report_lines()
        headers = headers_without_missing

        if self.show_source:
            missed_lines_colored = [
                self.color_number(line) for line in lines["Missing"]
            ]
            lines["Missing"] = missed_lines_colored
            headers = headers_with_missing
        return tabulate(lines, headers=headers)

class CsvReporterDelta(DeltaReporter):
    not_available = "-"

    def generate(self, delimiter):
        lines = self.get_report_lines()
        print(f"{lines}")
        list_of_lines = [headers_without_missing]
        list_of_lines.extend(
            [[f"{item}" for item in row if item!="Missing"] for row in zip(*lines.values())]
        )

        print(f"lines['Missing'] = {lines['Missing']}")

        if self.show_source:
            print(f"list_of_lines={list_of_lines}")
            list_of_lines[0].append("Missing")
            for count in range(1,len(list_of_lines)):
                print(f"count={count}")
                print(f"{lines['Missing'][count-1]}")
                list_of_lines[count].append(f"{lines['Missing'][count-1]}")
            print(f"list_of_lines={list_of_lines}")

        if "\\n" in repr(delimiter):
            delimiter = "\n"
        if "\\t" in repr(delimiter):
            delimiter = "\t"

        print(f"list_of_lines={list_of_lines}")

        return "\n".join([delimiter.join(line) + delimiter for line in list_of_lines])


class MarkdownReporterDelta(DeltaReporter):
    not_available = "-"

    def generate(self):
        lines = self.get_report_lines()
        headers = headers_without_missing

        if self.show_source:
            missed_lines_colored = [
                self.color_number(line) for line in lines["Missing"]
            ]
            lines["Missing"] = missed_lines_colored
            headers = headers_with_missing
        return tabulate(lines, headers=headers, tablefmt="github")


class JsonReporterDelta(DeltaReporter):
    not_available = None

    def generate(self):
        lines = self.get_report_lines()

        if self.show_source:
            missed_lines_colored = [
                self.color_number(line) for line in lines["Missing"]
            ]
            lines["Missing"] = missed_lines_colored

        rows = {k: v[:-1] for k, v in lines.items()}
        footer = {k: v[-1] for k, v in lines.items() if k != "Missing"}

        json_string = json.dumps({"total": footer, "files": rows}, indent=4)

        # for colors, explanation see here:
        # https://stackoverflow.com/a/61273717/9698518
        colored_json_string = json_string.encode("utf-8").decode("unicode_escape")

        return colored_json_string


class HtmlReporterDelta(DeltaReporter):
    not_available = "-"

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

        rows = {k: v[:-1] for k, v in lines.items()}
        footer = {k: v[-1] for k, v in lines.items()}

        render_kwargs = {
            "lines": rows,
            "footer": footer,
            "show_missing": self.show_missing,
            "show_source": self.show_source,
        }

        if self.show_source is True:
            render_kwargs["sources"] = []
            for filename in self.differ.files():
                differ_file_source_hunks = self.differ.file_source_hunks(filename)
                if differ_file_source_hunks:
                    render_kwargs["sources"].append(
                        (filename, differ_file_source_hunks)
                    )

        return template.render(**render_kwargs)
