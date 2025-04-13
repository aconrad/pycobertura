from jinja2 import Environment, PackageLoader
from pycobertura.cobertura import Cobertura, CoberturaDiff
from pycobertura.utils import (
    green,
    rangify_by_status,
    red,
    stringify,
    calculate_line_rate,
)
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

headers_with_missing = ["Filename", "Stmts", "Miss", "Cover", "Missing"]
headers_without_missing = ["Filename", "Stmts", "Miss", "Cover"]


class Reporter:
    def __init__(self, cobertura, ignore_regex=None):
        self.cobertura: Cobertura = cobertura
        self.ignore_regex = ignore_regex

    @staticmethod
    def format_line_rates(summary_lines):
        for i, line_rate in enumerate(summary_lines["Cover"]):
            summary_lines["Cover"][i] = f"{line_rate:.2%}"

    @staticmethod
    def format_missing_lines(summary_lines):
        for i, missing_lines in enumerate(summary_lines["Missing"]):
            summary_lines["Missing"][i] = stringify(missing_lines)

    def get_summary_lines(self):
        filenames = self.cobertura.files(ignore_regex=self.ignore_regex)
        summary_lines = {
            "Filename": filenames.copy(),
            "Stmts": [],
            "Miss": [],
            "Cover": [],
            "Missing": [],
        }
        for filename in filenames:
            file_statements = self.cobertura.total_statements(
                filename, ignore_regex=self.ignore_regex
            )
            file_misses = self.cobertura.total_misses(
                filename, ignore_regex=self.ignore_regex
            )
            file_rate = calculate_line_rate(file_statements, file_misses)
            summary_lines["Stmts"].append(file_statements)
            summary_lines["Miss"].append(file_misses)
            summary_lines["Cover"].append(file_rate)
            summary_lines["Missing"].append(self.cobertura.missed_lines(filename))

        # Generate TOTAL row
        total_statements = self.cobertura.total_statements(
            ignore_regex=self.ignore_regex
        )
        total_misses = self.cobertura.total_misses(ignore_regex=self.ignore_regex)
        total_rate = calculate_line_rate(total_statements, total_misses)
        summary_lines["Filename"].append("TOTAL")
        summary_lines["Stmts"].append(total_statements)
        summary_lines["Miss"].append(total_misses)
        summary_lines["Cover"].append(total_rate)
        summary_lines["Missing"].append([])

        return summary_lines

    def per_file_stats(self, summary_lines):
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
        file_stats_dict_items = summary_lines.items()
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
        summary_lines = self.get_summary_lines()
        self.format_line_rates(summary_lines)
        self.format_missing_lines(summary_lines)
        return tabulate(summary_lines, headers=headers_with_missing)


class CsvReporter(Reporter):
    def generate(self, delimiter):
        summary_lines = self.get_summary_lines()
        self.format_line_rates(summary_lines)
        self.format_missing_lines(summary_lines)

        list_of_lines = [headers_with_missing]
        list_of_lines.extend(
            [[f"{item}" for item in row] for row in zip(*summary_lines.values())]
        )

        # Explanation here:
        # https://stackoverflow.com/a/55889036/9698518
        delimiter = delimiter.encode().decode("unicode_escape")

        return "\n".join([delimiter.join(line) for line in list_of_lines])


class MarkdownReporter(Reporter):
    def generate(self):
        summary_lines = self.get_summary_lines()
        self.format_line_rates(summary_lines)
        self.format_missing_lines(summary_lines)
        return tabulate(summary_lines, headers=headers_with_missing, tablefmt="github")


class JsonReporter(Reporter):
    def generate(self):
        summary_lines = self.get_summary_lines()
        self.format_line_rates(summary_lines)
        self.format_missing_lines(summary_lines)
        stats_dict = self.per_file_stats(summary_lines)
        return json.dumps(stats_dict, indent=4)


class YamlReporter(Reporter):
    def generate(self):
        summary_lines = self.get_summary_lines()
        self.format_line_rates(summary_lines)
        self.format_missing_lines(summary_lines)
        stats_dict = self.per_file_stats(summary_lines)
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
        summary_lines = self.get_summary_lines()
        self.format_line_rates(summary_lines)
        self.format_missing_lines(summary_lines)

        filenames = summary_lines["Filename"]
        sources = []
        if self.render_file_sources:
            for i, filename in enumerate(filenames):
                if i != len(filenames) - 1:  # exclude TOTAL, not a filename
                    sources.append((filename, self.cobertura.file_source(filename)))

        template = env.get_template("html.jinja2")
        rows = {k: v[:-1] for k, v in summary_lines.items()}
        footer = {k: v[-1] for k, v in summary_lines.items()}

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
        show_source=True,
        *args,
        **kwargs,
    ):
        self.differ = CoberturaDiff(cobertura1, cobertura2)
        self.show_source = show_source
        self.color = kwargs.pop("color", False)
        self.ignore_regex = ignore_regex

    def format_line_rate(self, line_rate):
        return f"{line_rate:+.2%}" if line_rate else "+100.00%"

    def format_total_statements(self, total_statements):
        return f"{total_statements:+d}" if total_statements else "0"

    @staticmethod
    def format_missed_lines(missed_lines):
        output = []
        if not missed_lines:
            return output

        for lineno, status in missed_lines:
            prefix = "~" if status == "partial" else ""
            output.append(f"{prefix}{lineno:d}")
        return output

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

    def get_summary_lines(self):
        filenames = self.differ.files(ignore_regex=self.ignore_regex)
        diff_total_stmts = []
        diff_total_miss = []
        diff_total_cover = []

        for filename in filenames:
            diff_total_stmts.append(self.differ.diff_total_statements(filename))
            diff_total_miss.append(self.differ.diff_total_misses(filename))
            diff_total_cover.append(self.differ.diff_line_rate(filename))

        indexes_of_files_with_changes = [
            i
            for i in range(len(filenames))
            if any(
                (
                    diff_total_stmts[i],
                    diff_total_miss[i],
                    diff_total_cover[i],
                )
            )
        ]

        summary_lines = {
            "Filename": [],
            "Stmts": [],
            "Miss": [],
            "Cover": [],
        }

        for i in indexes_of_files_with_changes:
            summary_lines["Filename"].append(filenames[i])
            summary_lines["Stmts"].append(
                self.format_total_statements(diff_total_stmts[i])
            )
            summary_lines["Miss"].append(self.format_total_misses(diff_total_miss[i]))
            summary_lines["Cover"].append(self.format_line_rate(diff_total_cover[i]))

        summary_lines["Filename"].append("TOTAL")
        summary_lines["Stmts"].append(
            self.format_total_statements(self.differ.diff_total_statements())
        )
        summary_lines["Miss"].append(
            self.format_total_misses(self.differ.diff_total_misses())
        )
        summary_lines["Cover"].append(
            self.format_line_rate(self.differ.diff_line_rate())
        )

        if self.show_source:
            diff_total_missing = [
                self.differ.diff_missed_lines(filename) for filename in filenames
            ]
            summary_lines["Missing"] = [
                diff_total_missing[i] for i in indexes_of_files_with_changes
            ]
            summary_lines["Missing"].append("")  # for total line

        return summary_lines

    def per_file_stats(self, summary_lines):
        file_stats_dict_items = summary_lines.items()
        number_of_files = len(summary_lines["Filename"])
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
        summary_lines = self.get_summary_lines()
        headers = headers_without_missing

        if self.show_source:
            missed_lines_colored = [
                self.color_number([str(m[0]) for m in missing])
                for missing in summary_lines["Missing"]
            ]

            summary_lines["Missing"] = missed_lines_colored
            headers = headers_with_missing
        return tabulate(summary_lines, headers=headers)


class CsvReporterDelta(DeltaReporter):
    def generate(self, delimiter):
        summary_lines = self.get_summary_lines()

        # lines_values: List of lines dictionary values arranged in
        # tuples of Table row values
        lines_values = list(zip(*summary_lines.values()))

        # Stringify every item in Table row values without using the Missing column
        # and store in the list list_of_lines
        list_of_lines = [headers_without_missing]
        list_of_lines.extend([[f"{item}" for item in row[:-1]] for row in lines_values])

        if self.show_source:
            # Add the Missing header to list_of_lines first inner list
            # This is a direct assignment to avoid appending an additional "Missing"
            # header in every iteration of the tests which would fail them
            list_of_lines[0] = headers_with_missing
            # Add to every list inside the list_of_lines the Missing column value
            for line_index, missing_line in enumerate(summary_lines["Missing"]):
                # for colors, explanation see here:
                # https://stackoverflow.com/a/61273717/9698518
                colored = [
                    self.color_number(str(lineno_status[0]))
                    for lineno_status in missing_line
                ]
                list_of_lines[line_index + 1] += [
                    f"{colored}".encode("utf-8").decode("unicode_escape")
                ]

        # Explanation here:
        # https://stackoverflow.com/a/55889036/9698518
        delimiter = delimiter.encode().decode("unicode_escape")

        return "\n".join([delimiter.join(line) for line in list_of_lines])


class MarkdownReporterDelta(DeltaReporter):
    def generate(self):
        summary_lines = self.get_summary_lines()
        headers = headers_without_missing

        if self.show_source:
            missed_lines_colored = [
                self.color_number([str(m[0]) for m in missing])
                for missing in summary_lines["Missing"]
            ]
            summary_lines["Missing"] = missed_lines_colored
            headers = headers_with_missing
        return tabulate(summary_lines, headers=headers, tablefmt="github")


class JsonReporterDelta(DeltaReporter):
    def generate(self):
        summary_lines = self.get_summary_lines()

        if self.show_source:
            missed_lines_colored = [
                self.color_number([str(m[0]) for m in missing])
                for missing in summary_lines["Missing"]
            ]
            summary_lines["Missing"] = missed_lines_colored

        stats_dict = self.per_file_stats(summary_lines)

        json_string = json.dumps(stats_dict, indent=4)

        # for colors, explanation see here:
        # https://stackoverflow.com/a/61273717/9698518
        colored_json_string = json_string.encode("utf-8").decode("unicode_escape")

        return colored_json_string


class YamlReporterDelta(DeltaReporter):
    def generate(self):
        summary_lines = self.get_summary_lines()

        if self.show_source:
            missed_lines_colored = [
                self.color_number([str(m[0]) for m in missing])
                for missing in summary_lines["Missing"]
            ]
            summary_lines["Missing"] = missed_lines_colored

        stats_dict = self.per_file_stats(summary_lines)
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
        summary_lines = self.get_summary_lines()
        template = env.get_template("html-delta.jinja2")

        rows = {k: v[:-1] for k, v in summary_lines.items()}
        footer = {k: v[-1] for k, v in summary_lines.items()}

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


class GitHubAnnotationReporter(Reporter):
    def generate(
        self,
        annotation_level: str,
        annotation_title: str,
        annotation_message: str,
    ):
        file_names = self.cobertura.files(ignore_regex=self.ignore_regex)
        result_strs = []
        for file_name in file_names:
            for range_start, range_end, status in rangify_by_status(
                self.cobertura.missed_lines(file_name)
            ):
                result_strs.append(
                    self.to_github_annotation_message(
                        file_name=file_name,
                        start_line_num=range_start,
                        end_line_num=range_end,
                        annotation_level=annotation_level,
                        annotation_title=annotation_title,
                        annotation_message=f"{annotation_message} ({status})",
                    )
                )
        result = "\n".join(result_strs)
        return result

    @staticmethod
    def to_github_annotation_message(
        file_name: str,
        start_line_num: int,
        end_line_num: int,
        annotation_level: str,
        annotation_title: str,
        annotation_message: str,
    ):
        return f"::{annotation_level} file={file_name},line={start_line_num},endLine={end_line_num},title={annotation_title}::{annotation_message}"  # noqa


class GitHubAnnotationReporterDelta(DeltaReporter):
    def generate(
        self,
        annotation_level: str,
        annotation_title: str,
        annotation_message: str,
    ):
        summary_lines = self.get_summary_lines()
        stats_dict = self.per_file_stats(summary_lines)
        result_strs = []
        # import pdb; pdb.set_trace()

        for file_stat in stats_dict["files"]:
            for range_start, range_end, status in rangify_by_status(
                file_stat["Missing"]
            ):
                result_strs.append(
                    GitHubAnnotationReporter.to_github_annotation_message(
                        file_name=file_stat["Filename"],
                        start_line_num=range_start,
                        end_line_num=range_end,
                        annotation_level=annotation_level,
                        annotation_title=annotation_title,
                        annotation_message=f"{annotation_message} ({status})",
                    )
                )
        result = "\n".join(result_strs)
        return result
