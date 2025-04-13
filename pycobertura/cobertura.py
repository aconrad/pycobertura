import lxml.etree as ET
from collections import namedtuple
from pycobertura.utils import (
    LineStatus,
    LineStatusTuple,
    extrapolate_coverage,
    get_line_status,
    reconcile_lines,
    hunkify_lines,
    get_filenames_that_do_not_match_regex,
    memoize,
)

from typing import Dict, List, Tuple

try:
    from typing import Literal
except ImportError:  # pragma: no cover
    from typing_extensions import Literal


class Line(namedtuple("Line", ["number", "source", "status", "reason"])):
    """
    A namedtuple object representing a line of source code.

    The namedtuple has the following attributes:
    `number`: line number in the source code
    `source`: actual source code of line
    `status`: "hit" (covered), "miss" (uncovered), "partial", or None (coverage
    unchanged)
    `reason`: If `Line.status` is not `None` the possible values may be
        `"line-edit"`, `"cov-up"` or `"cov-down"`. Otherwise `None`.
    """


class Cobertura:
    """
    An XML Cobertura parser.
    """

    class InvalidCoverageReport(Exception):
        pass

    class MissingFileSystem(Exception):
        pass

    def __init__(self, report, filesystem=None):
        """
        Initialize a Cobertura report given a coverage report `report` that is
        an XML file in the Cobertura format. It can represented as either:

            - a file object
            - a file path
            - an XML string

        The optional keyword argument `filesystem` describes how to retrieve the
        source files referenced in the report. Please check the
        `pycobertura.filesystem` module to learn more about filesystems.
        """
        errors = []
        for load_func in [
            self._load_from_file,
            self._load_from_string,
        ]:
            try:
                self.xml: ET._Element = load_func(report)
                break
            except BaseException as e:
                errors.append(e)
                pass
        else:
            raise self.InvalidCoverageReport(
                """\
Invalid coverage report: {}.
The following exceptions occurred while attempting to parse the report:
* While treating the report as a filename: {}.
* While treating the report as an XML Cobertura string: {}""".format(
                    report, errors[0], errors[1]
                )
            )

        self.filesystem = filesystem
        self.report = report

        self._class_elements_by_file_name = self._make_class_elements_by_filename()

    def _make_class_elements_by_filename(self):
        result = {}
        for elem in self.xml.xpath("./packages//class"):
            filename = elem.attrib["filename"]
            result.setdefault(filename, []).append(elem)

        return result

    def __eq__(self, other):
        return self.report and other.report and self.report == other.report

    def _load_from_file(self, report_file):
        return ET.parse(report_file).getroot()

    def _load_from_string(self, s):
        return ET.fromstring(s)

    @memoize
    def _get_lines_by_filename(self, filename):
        classElements = self._class_elements_by_file_name[filename]
        return [
            line
            for classElement in classElements
            for line in classElement.xpath("./lines/line")
        ]

    @property
    def version(self):
        """Return the version number of the coverage report."""
        return self.xml.get("version")

    def line_rate(self, filename=None, ignore_regex=None):
        """
        Return the global line rate of the coverage report. If the
        `filename` file is given, return the line rate of the file.
        """

        if filename is None and ignore_regex is None:
            return float(self.xml.get("line-rate"))

        if ignore_regex is None:
            elements = self._class_elements_by_file_name[filename]
            if len(elements) == 1:
                return float(elements[0].get("line-rate"))
        total = self.total_statements(filename, ignore_regex)
        return (
            float(self.total_hits(filename, ignore_regex) / total) if total != 0 else 0
        )

    def branch_rate(self, filename=None):
        """
        Return the global branch rate of the coverage report. If the
        `filename` file is given, return the branch rate of the file.
        """
        branch_rate = None
        if filename is None:
            branch_rate = self.xml.get("branch-rate")
        else:
            classElement = self._class_elements_by_file_name[filename][0]
            branch_rate = classElement.get("branch-rate")
        return None if branch_rate is None else float(branch_rate)

    @memoize
    def missed_statements(self, filename):
        """
        Return a list of uncovered line numbers for each of the missed
        statements found for the file `filename`.
        """
        classElements = self._class_elements_by_file_name[filename]
        return [
            int(line.get("number"))
            for classElement in classElements
            for line in classElement.xpath("./lines/line")
            if get_line_status(line) != "hit"
        ]

    @memoize
    def hit_statements(self, filename):
        """
        Return a list of covered line numbers for each of the hit statements
        found for the file `filename`.
        """
        classElements = self._class_elements_by_file_name[filename]
        return [
            int(line.get("number"))
            for classElement in classElements
            for line in classElement.xpath("./lines/line[@hits>0]")
            if get_line_status(line) == "hit"
        ]

    def line_statuses(self, filename: str):
        """
        Return a list of tuples `(lineno, status)` of all the lines found in
        the Cobertura report for the given file `filename` where `lineno` is
        the line number and `status` is coverage status of the line which can
        be either `True` (line hit) or `False` (line miss).
        """
        line_elements = self._get_lines_by_filename(filename)

        output: List[LineStatusTuple] = []
        for line in line_elements:
            lineno = int(line.get("number"))
            status = get_line_status(line)
            output.append((lineno, status))

        return output

    def missed_lines(self, filename):
        """
        Return a list of extrapolated uncovered or partially uncovered line
        numbers for the file `filename` according to `Cobertura.line_statuses`.
        """
        statuses = self.line_statuses(filename)
        extrapolated_statuses = extrapolate_coverage(statuses)
        return [
            (lineno, status)
            for lineno, status in extrapolated_statuses
            if (status == "miss" or status == "partial")
        ]

    def _raise_MissingFileSystem(self, filename):
        raise self.MissingFileSystem(
            f"Unable to read file: {filename}. "
            f"A FileSystem instance must be provided via "
            f"Cobertura(filesystem=...) to locate and read the source "
            f"content of the file."
        )

    @memoize
    def file_source(self, filename):
        """
        Return a list of namedtuple `Line` for each line of code found in the
        source file with the given `filename`.
        """
        if self.filesystem is None:
            self._raise_MissingFileSystem(filename)

        lines = []
        try:
            with self.filesystem.open(filename) as f:
                line_statuses = dict(self.line_statuses(filename))
                for lineno, source in enumerate(f, start=1):
                    line_status = line_statuses.get(lineno)
                    line = Line(lineno, source, line_status, None)
                    lines.append(line)

        except self.filesystem.FileNotFound as file_not_found:
            lines.append(Line(0, f"{file_not_found.path} not found", None, None))

        return lines

    def total_misses(self, filename=None, ignore_regex=None):
        """
        Return the total number of uncovered statements for the file
        `filename`. If `filename` is not given, return the total
        number of uncovered statements for all files.
        """
        if filename is not None:
            return len(self.missed_statements(filename))

        return sum(
            [
                len(self.missed_statements(filename))
                for filename in self.files(ignore_regex)
            ]
        )

    def total_hits(self, filename=None, ignore_regex=None):
        """
        Return the total number of covered statements for the file
        `filename`. If `filename` is not given, return the total
        number of covered statements for all files.
        """
        if filename is not None:
            return len(self.hit_statements(filename))
        return sum(
            [
                len(self.hit_statements(filename))
                for filename in self.files(ignore_regex)
            ]
        )

    def total_statements(self, filename=None, ignore_regex=None):
        """
        Return the total number of statements for the file
        `filename`. If `filename` is not given, return the total
        number of statements for all files.
        """
        if filename is not None:
            return len(self._get_lines_by_filename(filename))
        return sum(
            [
                len(self._get_lines_by_filename(filename))
                for filename in self.files(ignore_regex)
            ]
        )

    @memoize
    def files(self, ignore_regex=None):
        """
        Return the list of available files in the coverage report.
        """
        # maybe replace with a trie at some point? see has_file FIXME
        already_seen = set()
        filenames = []

        for el in self.xml.xpath("//class"):
            filename = el.get("filename")
            if filename in already_seen:
                continue
            already_seen.add(filename)
            filenames.append(filename)

        return (
            filenames
            if not ignore_regex
            else get_filenames_that_do_not_match_regex(filenames, ignore_regex)
        )

    def has_file(self, filename):
        """
        Return `True` if the file `filename` is present in the report, return
        `False` otherwise.
        """
        # FIXME: this will lookup a list which is slow, make it O(1)
        return filename in self.files()

    @memoize
    def source_lines(self, filename: str):
        """
        Return a list for source lines of file `filename`.
        """
        if self.filesystem is None:
            self._raise_MissingFileSystem(filename)

        with self.filesystem.open(filename) as f:
            return f.readlines()

    @memoize
    def packages(self):
        """
        Return the list of available packages in the coverage report.
        """
        return [el.get("name") for el in self.xml.xpath("//package")]


class CoberturaDiff:
    """
    Diff Cobertura objects.
    """

    def __init__(self, cobertura1, cobertura2):
        self.cobertura1: Cobertura = cobertura1
        self.cobertura2: Cobertura = cobertura2

    def has_better_coverage(self):
        """
        Return `True` if coverage of has improved, `False` otherwise.

        This does not ensure that all changes have been covered. If this is
        what you want, use `CoberturaDiff.has_all_changes_covered()` instead.
        """
        return not (
            any(self.diff_total_misses(filename) > 0 for filename in self.files())
        )

    def has_all_changes_covered(self):
        """
        Return `True` if all changes have been covered, `False` otherwise.
        """
        for filename in self.files():
            for hunk in self.file_source_hunks(filename):
                for line in hunk:
                    if line.reason is None:
                        continue  # line untouched
                    if line.status != "hit":
                        return False  # line not covered
        return True

    def _diff_attr(self, attr_name, filename):
        """
        Return the difference between
        `self.cobertura2.<attr_name>(filename)` and
        `self.cobertura1.<attr_name>(filename)`.

        This generic method is meant to diff the count of methods that return
        counts for a given file `filename`, e.g. `Cobertura.total_statements`,
        `Cobertura.total_misses`, ...

        The returned count may be a float.
        """
        files = [filename] if filename else self.files()

        total_count = 0.0
        for filename in files:
            count = [0, 0]
            if self.cobertura1.has_file(filename):
                method = getattr(self.cobertura1, attr_name)
                count[0] = method(filename)
            if self.cobertura2.has_file(filename):
                method = getattr(self.cobertura2, attr_name)
                count[1] = method(filename)
            total_count += count[1] - count[0]

        return total_count

    def diff_total_statements(self, filename=None):
        return int(self._diff_attr("total_statements", filename))

    def diff_total_misses(self, filename=None):
        return int(self._diff_attr("total_misses", filename))

    def diff_total_hits(self, filename=None):
        return int(self._diff_attr("total_hits", filename))

    def diff_line_rate(self, filename=None):
        if filename is not None:
            return self._diff_attr("line_rate", filename)
        return self.cobertura2.line_rate() - self.cobertura1.line_rate()

    def diff_missed_lines(
        self, filename: str
    ) -> List[Tuple[int, Literal["miss", "partial"]]]:
        """
        Return a list of 2-element tuples `(lineno, status)` for uncovered lines.
        The given file `filename` where `lineno` is a missed line number.
        """
        return [
            (line.number, line.status)
            for line in self.file_source(filename)
            if (line.status == "miss" or line.status == "partial")
        ]

    def files(self, ignore_regex=None):
        """
        Return the total of all files we're comparing.
        """
        f = list(
            set(
                self.cobertura2.files(ignore_regex)
                + self.cobertura1.files(ignore_regex)
            )
        )
        f.sort()
        return f

    def file_source(self, filename: str):
        """
        Return a list of namedtuple `Line` for each line of code found in the
        given file `filename`.

        """
        nonexistent = True
        if self.cobertura1.has_file(filename) and self.cobertura1.filesystem.has_file(
            filename
        ):
            lines1 = self.cobertura1.source_lines(filename)
            line_statuses1 = dict(self.cobertura1.line_statuses(filename))
            nonexistent = False
        else:
            lines1 = []
            line_statuses1: Dict[int, LineStatus] = {}

        if self.cobertura2.has_file(filename) and self.cobertura2.filesystem.has_file(
            filename
        ):
            lines2 = self.cobertura2.source_lines(filename)
            line_statuses2 = dict(self.cobertura2.line_statuses(filename))
            nonexistent = False
        else:
            lines2 = []
            line_statuses2 = {}

        if nonexistent:
            # try to get source lines anyway, to get the exception traceback
            self.cobertura2.source_lines(filename)

        # Build a dict of lineno2 -> lineno1
        lineno_map = reconcile_lines(lines2, lines1)

        # if we are using a single coverage file, we need to translate the
        # coverage of lines1 so that it corresponds to its real lines.
        if self.cobertura1 == self.cobertura2:
            line_statuses1 = {}
            for l2, l1 in lineno_map.items():
                line_statuses1[l1] = line_statuses2.get(l2)

        lines = []
        for lineno, source in enumerate(lines2, start=1):
            status = None
            reason = None
            if lineno not in lineno_map:
                # line was added or removed, just use whatever coverage status
                # is available as there is nothing to compare against.
                status = line_statuses2.get(lineno)
                reason = "line-edit"
            else:
                other_lineno = lineno_map[lineno]
                line_status1 = line_statuses1.get(other_lineno)
                line_status2 = line_statuses2.get(lineno)
                if line_status1 == line_status2:
                    status = None  # unchanged
                    reason = None
                elif (line_status1 == "hit" and line_status2 != "hit") or (
                    line_status1 == "partial" and line_status2 == "miss"
                ):
                    status = line_status2  # decreased
                    reason = "cov-down"
                elif (line_status1 != "hit" and line_status2 == "hit") or (
                    line_status1 == "miss" and line_status2 == "partial"
                ):
                    status = line_status2  # increased
                    reason = "cov-up"

            line = Line(lineno, source, status, reason)
            lines.append(line)

        return lines

    def file_source_hunks(self, filename):
        """
        Like `CoberturaDiff.file_source`, but returns a list of line hunks of
        the lines that have changed for the given file `filename`. An empty
        list means that the file has no lines that have a change in coverage
        status.
        """
        lines = self.file_source(filename)
        hunks = hunkify_lines(lines)
        return hunks
