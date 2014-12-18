import os

import lxml.etree as ET


class Cobertura(object):
    def __init__(self, xml_source):
        """
        `xml_source` may be:
        - a path to an XML file
        - an open file object
        - an XML `string

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

    @property
    def version(self):
        return self.xml.attrib['version']

    def _get_element_by_class_name(self, class_name):
        return self.xml.xpath("//class[@name='%s'][1]" % class_name)[0]

    def line_rate(self, class_name=None):
        if class_name is None:
            el = self.xml
        else:
            el = self._get_element_by_class_name(class_name)

        return float(el.attrib['line-rate'])

    def branch_rate(self, class_name=None):
        if class_name is None:
            el = self.xml
        else:
            el = self._get_element_by_class_name(class_name)
        return float(el.attrib['branch-rate'])

    def missed_lines(self, class_name):
        el = self._get_element_by_class_name(class_name)
        lines = el.xpath('./lines/line[@hits=0]')
        return [int(l.attrib['number']) for l in lines]

    def line_hits(self, class_name):
        el = self._get_element_by_class_name(class_name)
        lines = el.xpath('./lines/line[@hits>0]')
        return [int(l.attrib['number']) for l in lines]

    def total_misses(self, class_name):
        return len(self.missed_lines(class_name))

    def total_hits(self, class_name):
        return len(self.line_hits(class_name))

    def total_lines(self, class_name):
        el = self._get_element_by_class_name(class_name)
        lines = el.xpath('./lines/line')
        return len(lines)

    def filename(self, class_name):
        el = self._get_element_by_class_name(class_name)
        filename = el.attrib['filename']
        return filename

    def classes(self):
        return [el.attrib['name'] for el in self.xml.xpath("//class")]

    def has_class(self, class_name):
        # FIXME: this will lookup a list which is slow, make it O(1)
        return class_name in self.classes()

    def packages(self):
        return [el.attrib['name'] for el in self.xml.xpath("//package")]
