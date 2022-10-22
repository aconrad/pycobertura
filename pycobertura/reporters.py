from jinja2 import Environment, PackageLoader
from pycobertura.cobertura import CoberturaDiff
from pycobertura.utils import green, red, stringify
from pycobertura.templates import filters
from tabulate import tabulate
from ruamel import yaml
import json
import io


env = Environment(loader=PackageLoader("pycobertura", "templates"))
env.filters["line_status"] = filters.line_status
env.filters["line_reason"] = filters.line_reason_icon
env.filters["is_not_equal_to_dash"] = filters.is_not_equal_to_dash
env.filters["misses_color"] = filters.misses_color
env.filters[
    "get_max_number_of_values_in_dict"
] = filters.get_max_number_of_values_in_dict

headers_with_missing = ["Filename", "Stmts", "Miss", "Cover", "Missing"]
headers_without_missing = ["Filename", "Stmts", "Miss", "Cover"]
headers_hideable = headers_without_missing.remove("Filename")


class Reporter:
    def __init__(self, cobertura, ignore_regex=None, hide_columns=[]):
        self.cobertura = cobertura
        self.ignore_regex = ignore_regex
        #print(f"hide columns = {hide_columns}")
        self.set_hide_columns = set(
            ",".join([x for x in hide_columns if x not in ("[", "]")]).split(",")
        )
        #print(f"hide columns = {self.set_hide_columns}")
        self.show_columns = [
            col for col in headers_with_missing if col not in self.set_hide_columns
        ]
        #print(f"show columns = {self.show_columns}")

    @staticmethod
    def format_line_rate(line_rate):
        return f"{line_rate:.2%}"

    def lines_dict_entry(self, key):
        filenames = self.cobertura.files(ignore_regex=self.ignore_regex)
        rows_func_dict = {
            "Filename": filenames,
            "Stmts": [
                self.cobertura.total_statements(filename) for filename in filenames
            ],
            "Miss": [self.cobertura.total_misses(filename) for filename in filenames],
            "Cover": [
                self.format_line_rate(self.cobertura.line_rate(filename))
                for filename in filenames
            ],
            "Missing": [
                stringify(self.cobertura.missed_lines(filename))
                for filename in filenames
            ],
        }
        footer_func_dict = {
            "Filename": ["TOTAL"],
            "Stmts": [self.cobertura.total_statements()],
            "Miss": [self.cobertura.total_misses()],
            "Cover": [self.format_line_rate(self.cobertura.line_rate())],
            "Missing": [""],
        }
        return rows_func_dict[key] + footer_func_dict[key]

    def get_summary_lines(self):
        lines = {}
        for column in self.show_columns:
            lines[column] = self.lines_dict_entry(column)
        return lines

    def per_file_stats(self, file_stats_dict):
        """
        Returns dict with keys `files` and `total` that contain coverage
        statistics per file and overall, respectively.

        {
            "files": [
                {
                    "Filename": "dummy/__init__.py",
                    "Stmts": 0,
                    "Miss": 0,
                    "Cover": "0.00%",
                    "Missing": "9"
                },
                ...
            ],
            "total": {
                "Filename": "TOTAL",
                "Stmts": "...",
                "Miss": "...",
                "Cover": "..."
            }
        }
        """
        file_stats_dict_items = file_stats_dict.items()
        number_of_files = len(self.cobertura.files()) + 1
        file_stats_list = [
            {
                header_name: header_value[file_index]
                for header_name, header_value in file_stats_dict_items
            }
            for file_index in range(number_of_files)
        ]
        file_stats_list[-1].pop("Missing", 'Key "Missing" not found')
        return {
            "files": file_stats_list[:-1],
            "total": file_stats_list[-1],
        }


class TextReporter(Reporter):
    def generate(self):
        lines = self.get_summary_lines()
        return tabulate(lines, headers=self.show_columns)


class CsvReporter(Reporter):
    def generate(self, delimiter):
        lines = self.get_summary_lines()
        list_of_lines = [self.show_columns]
        list_of_lines.extend(
            [[f"{item}" for item in row] for row in zip(*lines.values())]
        )

        # Explanation here:
        # https://stackoverflow.com/a/55889036/9698518
        delimiter = delimiter.encode().decode("unicode_escape")

        return "\n".join([delimiter.join(line) for line in list_of_lines])


class MarkdownReporter(Reporter):
    def generate(self):
        lines = self.get_summary_lines()
        return tabulate(lines, headers=self.show_columns, tablefmt="github")


class JsonReporter(Reporter):
    def generate(self):
        lines = self.get_summary_lines()
        stats_dict = self.per_file_stats(lines)
        return json.dumps(stats_dict, indent=4)


class YamlReporter(Reporter):
    def generate(self):
        lines = self.get_summary_lines()
        stats_dict = self.per_file_stats(lines)
        # need to write to a buffer as yml packages are using a streaming interface
        buf = io.BytesIO()
        yaml.YAML().dump(stats_dict, buf)
        return buf.getvalue()


class HtmlReporter(Reporter):
    def __init__(self, *args, **kwargs):
        self.title = kwargs.pop("title", "pycobertura report")
        self.render_file_sources = kwargs.pop("render_file_sources", True)
        self.no_file_sources_message = kwargs.pop(
            "no_file_sources_message", "Rendering of source files was disabled."
        )
        super(HtmlReporter, self).__init__(*args, **kwargs)

    def generate(self):
        lines = self.get_summary_lines()

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
    def __init__(
        self,
        cobertura1,
        cobertura2,
        ignore_regex=None,
        hide_columns="",
        show_source=True,
        *args,
        **kwargs,
    ):
        self.differ = CoberturaDiff(cobertura1, cobertura2)
        self.set_hide_columns = set(
            "".join([x for x in hide_columns if x not in ("[", "]")]).split(",")
        )
        self.show_columns = [
            col for col in headers_with_missing if col not in self.set_hide_columns
        ]
        self.show_source = show_source
        self.color = kwargs.pop("color", False)
        self.ignore_regex = ignore_regex

    def format_line_rate(self, line_rate):
        return f"{line_rate:+.2%}" if line_rate else "+100.00%"

    def format_total_statements(self, total_statements):
        return f"{total_statements:+d}" if total_statements else "0"

    @staticmethod
    def format_missed_lines(missed_lines):
        return [f"{lno:d}" for lno in missed_lines]

    @staticmethod
    def determine_ANSI_color_code_function_of_number(number):
        if number.startswith("+") or number[0].isdigit():
            return red
        return green

    @classmethod
    def convert_signed_number_to_ANSI_color_coded_signed_number(cls, number):
        color_function = cls.determine_ANSI_color_code_function_of_number(number)
        return color_function(number)

    def color_number(self, numbers):
        if numbers and self.color and isinstance(numbers, str):
            return self.convert_signed_number_to_ANSI_color_coded_signed_number(numbers)
        if numbers and self.color and not isinstance(numbers, str):
            return ", ".join(
                [
                    self.convert_signed_number_to_ANSI_color_coded_signed_number(number)
                    for number in numbers
                ]
            )
        return numbers if isinstance(numbers, str) else ", ".join(numbers)

    def format_total_misses(self, total_misses):
        return self.color_number(f"{total_misses:+d}") if total_misses else "0"

    def lines_dict_entry(
        self,
        key,
        indexes_of_files_with_changes,
        diff_total_stmts,
        diff_total_miss,
        diff_total_cover,
    ):
        rows_func_dict = {
            "Filename": [self.differ.files()[i] for i in indexes_of_files_with_changes],
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
        footer_func_dict = {
            "Filename": ["TOTAL"],
            "Stmts": [
                self.format_total_statements(self.differ.diff_total_statements())
            ],
            "Miss": [self.format_total_misses(self.differ.diff_total_misses())],
            "Cover": [self.format_line_rate(self.differ.diff_line_rate())],
        }
        if self.show_source:
            diff_total_missing = [
                self.differ.diff_missed_lines(filename)
                for filename in self.differ.files()
            ]
            rows_func_dict["Missing"] = [
                self.format_missed_lines(diff_total_missing[i])
                for i in indexes_of_files_with_changes
            ]
            footer_func_dict["Missing"] = [""]
        return rows_func_dict[key] + footer_func_dict[key]

    def get_summary_lines(self):
        filenames = self.differ.files(ignore_regex=self.ignore_regex)
        diff_total_stmts = [
            self.differ.diff_total_statements(filename) for filename in filenames
        ]

        diff_total_miss = [
            self.differ.diff_total_misses(filename) for filename in filenames
        ]

        diff_total_cover = [
            self.differ.diff_line_rate(filename) for filename in filenames
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

        lines = {}

        for column_name in self.show_columns:
            if column_name != "Missing":
                lines[column_name] = self.lines_dict_entry(
                    column_name,
                    indexes_of_files_with_changes,
                    diff_total_stmts,
                    diff_total_miss,
                    diff_total_cover,
                )
            else:
                if self.show_source:
                    lines["Missing"] = self.lines_dict_entry(
                        "Missing",
                        indexes_of_files_with_changes,
                        diff_total_stmts,
                        diff_total_miss,
                        diff_total_cover,
                    )

        return lines

    def per_file_stats(self, file_stats_dict):
        file_stats_dict_items = file_stats_dict.items()
        number_of_files = len(self.differ.files())
        file_stats_list = [
            {
                header_name: header_value[file_index]
                for header_name, header_value in file_stats_dict_items
            }
            for file_index in range(number_of_files)
        ]
        file_stats_list[-1].pop("Missing", 'Key "Missing" not found')
        return {
            "files": file_stats_list[:-1],
            "total": file_stats_list[-1],
        }


class TextReporterDelta(DeltaReporter):
    def generate(self):
        lines = self.get_summary_lines()

        if self.show_source:
            missed_lines_colored = [
                self.color_number(line) for line in lines["Missing"]
            ]
            lines["Missing"] = missed_lines_colored
        return tabulate(lines, headers=self.show_columns)


class CsvReporterDelta(DeltaReporter):
    def generate(self, delimiter):
        lines = self.get_summary_lines()

        # lines_values: List of lines dictionary values arranged in
        # tuples of Table row values
        lines_values = list(zip(*lines.values()))

        # Stringify every item in Table row values without using the Missing column
        # and store in the list list_of_lines
        list_of_lines = [self.show_columns]
        list_of_lines.extend([[f"{item}" for item in row[:-1]] for row in lines_values])

        if self.show_source:
            # Add the Missing header to list_of_lines first inner list
            # This is a direct assignment to avoid appending an additional "Missing"
            # header in every iteration of the tests which would fail them
            list_of_lines[0] = self.show_columns
            # Add to every list inside the list_of_lines the Missing column value
            for line_index, missing_line in enumerate(lines["Missing"]):
                # for colors, explanation see here:
                # https://stackoverflow.com/a/61273717/9698518
                list_of_lines[line_index + 1] += [
                    f"{[self.color_number(number) for number in missing_line]}".encode(
                        "utf-8"
                    ).decode("unicode_escape")
                ]

        # Explanation here:
        # https://stackoverflow.com/a/55889036/9698518
        delimiter = delimiter.encode().decode("unicode_escape")

        return "\n".join([delimiter.join(line) for line in list_of_lines])


class MarkdownReporterDelta(DeltaReporter):
    def generate(self):
        lines = self.get_summary_lines()

        if self.show_source and "Missing" in self.show_columns:
            missed_lines_colored = [
                self.color_number(line) for line in lines["Missing"]
            ]
            lines["Missing"] = missed_lines_colored
        return tabulate(lines, headers=self.show_columns, tablefmt="github")


class JsonReporterDelta(DeltaReporter):
    def generate(self):
        lines = self.get_summary_lines()

        if self.show_source:
            missed_lines_colored = [
                self.color_number(line) for line in lines["Missing"]
            ]
            lines["Missing"] = missed_lines_colored

        stats_dict = self.per_file_stats(lines)

        json_string = json.dumps(stats_dict, indent=4)

        # for colors, explanation see here:
        # https://stackoverflow.com/a/61273717/9698518
        colored_json_string = json_string.encode("utf-8").decode("unicode_escape")

        return colored_json_string


class YamlReporterDelta(DeltaReporter):
    def generate(self):
        lines = self.get_summary_lines()

        if self.show_source:
            missed_lines_colored = [
                self.color_number(line) for line in lines["Missing"]
            ]
            lines["Missing"] = missed_lines_colored

        stats_dict = self.per_file_stats(lines)
        # need to write to a buffer as yml packages are using a streaming interface
        buf = io.BytesIO()
        yaml.YAML().dump(stats_dict, buf)
        # need to replace \e escape sequence with \x1b,
        # because only the latter is supported, see also
        # the Python docs for supported formats:
        # https://docs.python.org/3/reference/lexical_analysis.html#string-and-bytes-literals
        yaml_string = buf.getvalue().replace(rb"\e", b"\x1b")
        return yaml_string


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
        lines = self.get_summary_lines()
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
