import os

import lxml.etree as ET


class Cobertura(object):
    """
    An XML cobertura parser.
    """

    def __init__(self, xml_source):
        """
        Initialize a cobertura report given an XML file `xml_source` that is
        in the cobertura format.

        `xml_source` may be:
        - a path to an XML file
        - an open file object
        - an XML string
        """
        self.source = xml_source

        self._classes = None
        self._packages = None

        self._lines_missed = {}
        self._lines_hit = {}

        self._package_list = None
        self._class_list = None

        self.xml = self._parse(xml_source)

    def _parse(self, xml_source):
        if hasattr(xml_source, 'startswith'):
            if xml_source.startswith('<?xml'):
                return self._parse_xml_string(xml_source)

            elif os.path.exists(xml_source):
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

    def missed_lines(self, class_name):
        """
        Return the list of uncovered line numbers for the class `class_name`.
        """
        line_elements = self._get_lines_by_class_name(class_name)
        lines = []
        prev_was_missed = False
        for line in line_elements:
            if line.attrib['hits'] != '0':
                prev_was_missed = False
                continue

            lineno = int(line.attrib['number'])
            if prev_was_missed is False:
                lines.append(lineno)
                prev_was_missed = True
            else:
                # A missed line (hits=0) in the Cobertura report actually
                # indicates a missed statement. A multiline statement will only
                # appear as 1 uncovered line in the source code (the line on
                # which the statement started) so we need to backfill the rest
                # of the lines part of the same statement by showing them as
                # missing too.
                missed_range = range(lines[-1]+1, lineno+1)
                lines += missed_range
        return lines

    def line_hits(self, class_name):
        """
        Return the list of covered line numbers for the class `class_name`.
        """
        el = self._get_element_by_class_name(class_name)
        lines = el.xpath('./lines/line[@hits>0]')
        return [int(l.attrib['number']) for l in lines]

    def total_misses(self, class_name):
        """
        Return the number of uncovered line numbers for the class `class_name`.
        """
        el = self._get_element_by_class_name(class_name)
        statements = el.xpath('./lines/line[@hits=0]')
        return len(statements)

    def total_hits(self, class_name):
        """
        Return the number of covered line numbers for the class `class_name`.
        """
        return len(self.line_hits(class_name))

    def total_lines(self, class_name):
        """
        Return the total number of lines for the class `class_name`.
        """
        el = self._get_element_by_class_name(class_name)
        lines = el.xpath('./lines/line')
        return len(lines)

    def filename(self, class_name):
        """
        Return the filename of the class `class_name`.
        """
        el = self._get_element_by_class_name(class_name)
        filename = el.attrib['filename']
        return filename

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
