import lxml.etree as ET
import os

from pycobertura.utils import reconcile_lines


class Cobertura(object):
    """
    An XML cobertura parser.

    """
    def __init__(self, xml_source, base_path=None):
        """
        Initialize a Cobertura report given an XML file `xml_source` that is
        in the cobertura format.

        The optional argument `base_path` can be provided to resolve the path
        to the source code. `base_path` will prefix the filename attribute
        found in the Cobertura report.

        `xml_source` may be:
        - a path to an XML file
        - an open file object
        - an XML string

        """
        self.base_path = base_path
        self.source = xml_source
        self.xml = self._parse(xml_source)

    def _parse(self, xml_source):
        if hasattr(xml_source, 'startswith'):
            if xml_source.startswith('<?xml'):
                return self._parse_xml_string(xml_source)

            return self._parse_xml_file(xml_source)

        elif hasattr(xml_source, 'read'):
            return self._parse_xml_fileobj(xml_source)

    def _parse_xml_file(self, xml_file):
        return ET.parse(xml_file).getroot()

    def _parse_xml_fileobj(self, xml_fileobj):
        return self._parse_xml_string(xml_fileobj.read())

    def _parse_xml_string(self, xml_string):
        return ET.fromstring(xml_string)

    def _get_element_by_class_name(self, class_name):
        return self.xml.xpath("//class[@name='%s'][1]" % class_name)[0]

    def _get_lines_by_class_name(self, class_name):
        el = self._get_element_by_class_name(class_name)
        return el.xpath('./lines/line')

    @property
    def version(self):
        """Return the version number of the coverage report."""
        return self.xml.attrib['version']

    def line_rate(self, class_name=None):
        """
        Return the global line rate of the coverage report. If the class
        `class_name` is given, return the line rate of the class.

        """
        if class_name is None:
            el = self.xml
        else:
            el = self._get_element_by_class_name(class_name)

        return float(el.attrib['line-rate'])

    def branch_rate(self, class_name=None):
        """
        Return the global branch rate of the coverage report. If the class
        `class_name` is given, return the branch rate of the class.
        """
        if class_name is None:
            el = self.xml
        else:
            el = self._get_element_by_class_name(class_name)

        return float(el.attrib['branch-rate'])

    def missed_statements(self, class_name):
        """
        Return a list of uncovered line numbers for each of the missed
        statements found for the class `class_name`.

        """
        el = self._get_element_by_class_name(class_name)
        lines = el.xpath('./lines/line[@hits=0]')
        return [int(l.attrib['number']) for l in lines]

    def hit_statements(self, class_name):
        """
        Return a list of covered line numbers for each of the hit statements
        found for the class `class_name`.

        """
        el = self._get_element_by_class_name(class_name)
        lines = el.xpath('./lines/line[@hits>0]')
        return [int(l.attrib['number']) for l in lines]

    def line_statuses(self, class_name):
        """
        Return a list of tuples `(lineno, status)` of all the lines found in
        the Cobertura report where `lineno` is the line number and `status` is
        coverage status of the line which can be either `True` (line hit) or
        `False` (line miss).

        """
        line_elements = self._get_lines_by_class_name(class_name)

        lines_w_status = []
        for line in line_elements:
            lineno = int(line.attrib['number'])
            status = line.attrib['hits'] != '0'
            lines_w_status.append((lineno, status))

        return lines_w_status

    def missed_lines(self, class_name):
        """
        Return a list of line numbers that are uncovered according to
        `Cobertura.line_statuses`.
        """
        statuses = self.line_statuses(class_name)
        return [lno for lno, status in statuses if status is False]

    def class_source(self, class_name):
        """
        Return a list of 3-element tuples `(lineno, source, status)` for each
        lines of code found in the source file of the class `class_name`.

        The 3 elements in each tuple are:
        `lineno`: line number in the source code
        `source`: actual source code for line number `lineno`
        `status`: True (hit), False (miss) or None (unknown)

        See `Cobertura.line_statuses` for more information about the meaning of
        a status of `None`.

        """
        filename = self.filename(class_name)

        if not os.path.exists(filename):
            return [(0, '%s not found' % filename, None)]

        with open(filename) as f:
            lines = []
            line_statuses = dict(self.line_statuses(class_name))
            for lineno, source in enumerate(f, start=1):
                line_status = line_statuses.get(lineno)
                lines.append((lineno, source, line_status))

        return lines

    def total_misses(self, class_name):
        """
        Return the number of uncovered statements for the class `class_name`.

        """
        return len(self.missed_statements(class_name))

    def total_hits(self, class_name):
        """
        Return the number of covered statements for the class `class_name`.

        """
        return len(self.hit_statements(class_name))

    def total_statements(self, class_name):
        """
        Return the total number of statements for the class `class_name`.

        """
        statements = self._get_lines_by_class_name(class_name)
        return len(statements)

    def filename(self, class_name):
        """
        Return the filename of the class `class_name`. If `base_path` was
        provided in the constructor, it will be prefixed to the filename using
        `os.path.join`.

        """
        el = self._get_element_by_class_name(class_name)
        filename = el.attrib['filename']

        if self.base_path is None:
            return filename

        path = os.path.join(self.base_path, filename)
        return path

    def classes(self):
        """
        Return the list of available classes in the coverage report.

        """
        return [el.attrib['name'] for el in self.xml.xpath("//class")]

    def has_class(self, class_name):
        """
        Return `True` if the class `class_name` is present in the report,
        return `False` otherwise.

        """
        # FIXME: this will lookup a list which is slow, make it O(1)
        return class_name in self.classes()

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

    def class_source(self, class_name):
        filename1 = self.cobertura1.filename(class_name)
        filename2 = self.cobertura2.filename(class_name)

        for filename in (filename1, filename2):
            if not os.path.exists(filename):
                return [(0, '%s not found' % filename, None)]

        try:
            f1 = open(filename1)
            f2 = open(filename2)
            lines1 = f1.readlines()
            lines2 = f2.readlines()
        finally:
            f1.close()
            f2.close()

        # Build a dict of lineno2 -> lineno1
        lineno_map = reconcile_lines(lines2, lines1)

        line_statuses1 = dict(self.cobertura1.line_statuses(class_name))
        line_statuses2 = dict(self.cobertura2.line_statuses(class_name))

        lines = []
        for lineno, line in enumerate(lines2, start=1):

            if lineno not in lineno_map:
                # line was added or removed, just use whatever coverage status
                # is available as there is nothing to compare against.
                line_status = line_statuses2.get(lineno)
            else:
                other_lineno = lineno_map[lineno]
                line_status1 = line_statuses1.get(other_lineno)
                line_status2 = line_statuses2.get(lineno)
                if line_status1 is line_status2:
                    line_status = None  # unchanged
                elif line_status1 is True and line_status2 is False:
                    line_status = False  # decreased
                elif line_status1 is False and line_status2 is True:
                    line_status = True  # increased

            lines.append((lineno, line, line_status))

        return lines
