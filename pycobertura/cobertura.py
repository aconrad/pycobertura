import os
import lxml.etree as ET

from pycobertura.utils import extrapolate_coverage


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
        coverage status of the line which can be either `True` (line hit),
        `False` (line miss) or `None` (unknown).

        When `status` is `None`, it usually means that the source at the at the
        line number `lineno` is not a statement (a comment, whitespace, ...).
        That said, an attempt is made to extrapolate the status of
        non-statement lines to hit/miss. This makes computing ranges of line
        hits/misses more concise. For example, given this code and line
        statuses::

          def foo():                  # line1, status `True`
              "docstring"             # line2, status `None`
              foo = "foo"             # line3, status `True`
                                      # line4, status `None`
              # this is a commment    # line5, status `True`
              if not foo:             # line6, status `True`
                  pass                # line7, status `False`
                                      # line8, status `None`
              # we are now returning  # line9, status `None`
              return foo              # line10, status `True`

        The ranges of line hits would be represented as::

          1, 3, 5-6, 10

        After extrapolation of the line coverage, it would result in the
        following statuses::

          def foo():                  # line1, status `True`
              "docstring"             # line2, status `True`
              foo = "foo"             # line3, status `True`
                                      # line4, status `True`
              # this is a commment    # line5, status `True`
              if not foo:             # line6, status `True`
                  pass                # line7, status `False`
                                      # line8, status `None`
              # we are now returning  # line9, status `None`
              return foo              # line10, status `True`

        The ranges of line hits would be represented as::

          1-6, 10

        """
        line_elements = self._get_lines_by_class_name(class_name)

        lines_w_status = []
        for line in line_elements:
            lineno = int(line.attrib['number'])
            status = line.attrib['hits'] != '0'
            lines_w_status.append((lineno, status))

        lines_w_status = extrapolate_coverage(lines_w_status)

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
            last_status = None
            for lineno, source in enumerate(f, start=1):
                line_status = line_statuses.get(lineno, last_status)
                lines.append((lineno, source, line_status))
                last_status = line_status

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
