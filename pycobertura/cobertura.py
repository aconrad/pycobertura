import codecs
import lxml.etree as ET
import os

from collections import namedtuple

from pycobertura.utils import (
    extrapolate_coverage,
    reconcile_lines,
    hunkify_lines,
    memoize,
)


class Line(namedtuple('Line', ['number', 'source', 'status', 'reason'])):
    """
    A namedtuple object representing a line of source code.

    The namedtuple has the following attributes:
    `number`: line number in the source code
    `source`: actual source code of line
    `status`: True (covered), False (uncovered) or None (coverage unchanged)
    `reason`: If `Line.status` is not `None` the possible values may be
        `"line-edit"`, `"cov-up"` or `"cov-down"`. Otherwise `None`.
    """


class Cobertura(object):
    """
    An XML Cobertura parser.
    """
    def __init__(self, xml_path, base_path=None):
        """
        Initialize a Cobertura report given a path to an XML file `xml_path`
        that is in the Cobertura format.

        The optional argument `base_path` can be provided to resolve the path
        to the source code. If omitted, `base_path` will be set to
        `os.path.dirname(xml_source)`.
        """
        if base_path is None:
            base_path = os.path.dirname(xml_path)

        self.base_path = base_path
        self.xml_path = xml_path
        self.xml = ET.parse(xml_path).getroot()

    @memoize
    def _get_class_element_by_filename(self, filename):
        syntax = "./packages/package/classes/class[@filename='%s'][1]" % (
            filename
        )
        return self.xml.xpath(syntax)[0]

    @memoize
    def _get_lines_by_filename(self, filename):
        el = self._get_class_element_by_filename(filename)
        return el.xpath('./lines/line')

    @property
    def version(self):
        """Return the version number of the coverage report."""
        return self.xml.attrib['version']

    def line_rate(self, filename=None):
        """
        Return the global line rate of the coverage report. If the
        `filename` file is given, return the line rate of the file.
        """
        if filename is None:
            el = self.xml
        else:
            el = self._get_class_element_by_filename(filename)

        return float(el.attrib['line-rate'])

    def branch_rate(self, filename=None):
        """
        Return the global branch rate of the coverage report. If the
        `filename` file is given, return the branch rate of the file.
        """
        if filename is None:
            el = self.xml
        else:
            el = self._get_class_element_by_filename(filename)

        return float(el.attrib['branch-rate'])

    @memoize
    def missed_statements(self, filename):
        """
        Return a list of uncovered line numbers for each of the missed
        statements found for the file `filename`.
        """
        el = self._get_class_element_by_filename(filename)
        lines = el.xpath('./lines/line[@hits=0]')
        return [int(l.attrib['number']) for l in lines]

    @memoize
    def hit_statements(self, filename):
        """
        Return a list of covered line numbers for each of the hit statements
        found for the file `filename`.
        """
        el = self._get_class_element_by_filename(filename)
        lines = el.xpath('./lines/line[@hits>0]')
        return [int(l.attrib['number']) for l in lines]

    def line_statuses(self, filename):
        """
        Return a list of tuples `(lineno, status)` of all the lines found in
        the Cobertura report for the given file `filename` where `lineno` is
        the line number and `status` is coverage status of the line which can
        be either `True` (line hit) or `False` (line miss).
        """
        line_elements = self._get_lines_by_filename(filename)

        lines_w_status = []
        for line in line_elements:
            lineno = int(line.attrib['number'])
            status = line.attrib['hits'] != '0'
            lines_w_status.append((lineno, status))

        return lines_w_status

    def missed_lines(self, filename):
        """
        Return a list of extrapolated uncovered line numbers for the
        file `filename` according to `Cobertura.line_statuses`.
        """
        statuses = self.line_statuses(filename)
        statuses = extrapolate_coverage(statuses)
        return [lno for lno, status in statuses if status is False]

    @memoize
    def file_source(self, filename):
        """
        Return a list of namedtuple `Line` for each line of code found in the
        source file with the given `filename`.
        """
        filepath = self.filepath(filename)

        if not os.path.exists(filepath):
            return [Line(0, '%s not found' % filepath, None, None)]

        with codecs.open(filepath, encoding='utf-8') as f:
            lines = []
            line_statuses = dict(self.line_statuses(filename))
            for lineno, source in enumerate(f, start=1):
                line_status = line_statuses.get(lineno)
                line = Line(lineno, source, line_status, None)
                lines.append(line)

        return lines

    def total_misses(self, filename=None):
        """
        Return the total number of uncovered statements for the file
        `filename`. If `filename` is not given, return the total
        number of uncovered statements for all files.
        """
        if filename is not None:
            return len(self.missed_statements(filename))

        total = 0
        for filename in self.files():
            total += len(self.missed_statements(filename))

        return total

    def total_hits(self, filename=None):
        """
        Return the total number of covered statements for the file
        `filename`. If `filename` is not given, return the total
        number of covered statements for all files.
        """
        if filename is not None:
            return len(self.hit_statements(filename))

        total = 0
        for filename in self.files():
            total += len(self.hit_statements(filename))

        return total

    def total_statements(self, filename=None):
        """
        Return the total number of statements for the file
        `filename`. If `filename` is not given, return the total
        number of statements for all files.
        """
        if filename is not None:
            statements = self._get_lines_by_filename(filename)
            return len(statements)

        total = 0
        for filename in self.files():
            statements = self._get_lines_by_filename(filename)
            total += len(statements)

        return total

    def filepath(self, filename):
        """
        Return the filesystem path to the actual file `filename`. It uses the
        `base_path` value initialized in the constructor by prefixing it to the
        filename using `os.path.join(base_path, filename)`.
        """
        filepath = os.path.join(self.base_path, filename)
        return filepath

    @memoize
    def files(self):
        """
        Return the list of available files in the coverage report.
        """
        return [el.attrib['filename'] for el in self.xml.xpath("//class")]

    def has_file(self, filename):
        """
        Return `True` if the file `filename` is present in the report, return
        `False` otherwise.
        """
        # FIXME: this will lookup a list which is slow, make it O(1)
        return filename in self.files()

    @memoize
    def source_lines(self, filename):
        """
        Return a list for source lines of file `filename`.
        """
        with codecs.open(self.filepath(filename), encoding='utf-8') as f:
            return f.readlines()

    @memoize
    def packages(self):
        """
        Return the list of available packages in the coverage report.
        """
        return [el.attrib['name'] for el in self.xml.xpath("//package")]


class CoberturaDiff(object):
    """
    Diff Cobertura objects.
    """
    def __init__(self, cobertura1, cobertura2):
        self.cobertura1 = cobertura1
        self.cobertura2 = cobertura2

    def has_better_coverage(self):
        """
        Return `True` if coverage of has improved, `False` otherwise.

        This does not ensure that all changes have been covered. If this is
        what you want, use `CoberturaDiff.has_all_changes_covered()` instead.
        """
        for filename in self.files():
            if self.diff_total_misses(filename) > 0:
                return False
        return True

    def has_all_changes_covered(self):
        """
        Return `True` if all changes have been covered, `False` otherwise.
        """
        for filename in self.files():
            for hunk in self.file_source_hunks(filename):
                for line in hunk:
                    if line.reason is None:
                        continue  # line untouched
                    if line.status is False:
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
        if filename is not None:
            files = [filename]
        else:
            files = self.files()

        total_count = 0.0
        for filename in files:
            if self.cobertura1.has_file(filename):
                method = getattr(self.cobertura1, attr_name)
                count1 = method(filename)
            else:
                count1 = 0.0
            method = getattr(self.cobertura2, attr_name)
            count2 = method(filename)
            total_count += count2 - count1

        return total_count

    def diff_total_statements(self, filename=None):
        return int(self._diff_attr('total_statements', filename))

    def diff_total_misses(self, filename=None):
        return int(self._diff_attr('total_misses', filename))

    def diff_total_hits(self, filename=None):
        return int(self._diff_attr('total_hits', filename))

    def diff_line_rate(self, filename=None):
        return self._diff_attr('line_rate', filename)

    def diff_missed_lines(self, filename):
        """
        Return a list of 2-element tuples `(lineno, is_new)` for the given
        file `filename` where `lineno` is a missed line number and `is_new`
        indicates whether the missed line was introduced (True) or removed
        (False).
        """
        line_changed = []
        for line in self.file_source(filename):
            if line.status is not None:
                is_new = not line.status
                line_changed.append((line.number, is_new))
        return line_changed

    def files(self):
        """
        Return `self.cobertura2.files()`.
        """
        return self.cobertura2.files()

    def file_source(self, filename):
        """
        Return a list of namedtuple `Line` for each line of code found in the
        given file `filename`.

        """
        if self.cobertura1.has_file(filename):
            lines1 = self.cobertura1.source_lines(filename)
            line_statuses1 = dict(self.cobertura1.line_statuses(
                filename))
        else:
            lines1 = []
            line_statuses1 = {}

        lines2 = self.cobertura2.source_lines(filename)
        line_statuses2 = dict(self.cobertura2.line_statuses(filename))

        # Build a dict of lineno2 -> lineno1
        lineno_map = reconcile_lines(lines2, lines1)

        lines = []
        for lineno, source in enumerate(lines2, start=1):

            if lineno not in lineno_map:
                # line was added or removed, just use whatever coverage status
                # is available as there is nothing to compare against.
                status = line_statuses2.get(lineno)
                reason = 'line-edit'
            else:
                other_lineno = lineno_map[lineno]
                line_status1 = line_statuses1.get(other_lineno)
                line_status2 = line_statuses2.get(lineno)
                if line_status1 is line_status2:
                    status = None  # unchanged
                    reason = None
                elif line_status1 is True and line_status2 is False:
                    status = False  # decreased
                    reason = 'cov-down'
                elif line_status1 is False and line_status2 is True:
                    status = True  # increased
                    reason = 'cov-up'

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
