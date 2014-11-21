import os

from xml.etree import ElementTree as ET


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

    def _scan(self):
        self._packages = {}
        self._classes = {}
        current_class = None

        for event, el in ET.iterparse(self.source, events=['start', 'end']):
            if event == 'start' and el.tag == 'class':
                current_class = el

            elif event == 'end':
                if el.tag == 'line':
                    class_name = current_class.attrib['name']
                    line_number = int(el.attrib['number'])
                    line_hit_count = int(el.attrib['hits'])
                    if class_name not in self._classes:
                        self._classes[class_name] = {
                            'line_hits': {},
                            'line_rate': float(
                                current_class.attrib['line-rate']),
                            'complexity': float(
                                current_class.attrib['complexity']),
                            'branch_rate': float(
                                current_class.attrib['branch-rate']),
                            'filename': current_class.attrib['filename'],
                        }

                    line_hits = self._classes[class_name]['line_hits']
                    if line_number not in line_hits:
                        line_hits[line_number] = 0
                    line_hits[line_number] += line_hit_count

                elif el.tag == 'class':
                    current_class = None
                elif el.tag == 'package':
                    package_name = el.attrib['name']

                    if package_name not in self._packages:
                        self._packages[package_name] = {
                            'line_rate': float(el.attrib['line-rate']),
                            'complexity': float(el.attrib['complexity']),
                            'branch_rate': float(el.attrib['branch-rate'])
                        }

    @property
    def version(self):
        return self.xml.attrib['version']

    def line_rate(self, class_name=None):
        if class_name is None:
            return float(self.xml.attrib['line-rate'])
        return self._classes[class_name]['line_rate']

    @property
    def branch_rate(self):
        return float(self.xml.attrib['branch-rate'])

    def missed_lines(self, class_name):
        if class_name not in self._lines_missed:
            if self._classes is None:
                self._scan()

            line_hits = self._classes[class_name]['line_hits']
            self._lines_missed[class_name] = \
                [l for l in sorted(line_hits) if line_hits[l] == 0]

        return self._lines_missed[class_name]

    def line_hits(self, class_name):
        if class_name not in self._lines_hit:
            if self._classes is None:
                self._scan()

            line_hits = self._classes[class_name]['line_hits']
            self._lines_hit[class_name] = \
                [l for l in sorted(line_hits) if line_hits[l] > 0]

        return self._lines_hit[class_name]

    def total_misses(self, class_name):
        return len(self.missed_lines(class_name))

    def total_hits(self, class_name):
        return len(self.line_hits(class_name))

    def total_lines(self, class_name):
        line_hits = self._classes[class_name]['line_hits']
        return len(line_hits)

    def classes(self):
        if self._class_list is None:

            if self._classes is None:
                self._scan()

            self._class_list = sorted(self._classes)

        return self._class_list

    def has_class(self, class_name):
        # FIXME: this will lookup a list which is slow, make it O(1)
        return class_name in self.classes()

    def packages(self):
        if self._package_list is None:

            if self._packages is None:
                self._scan()

            self._package_list = sorted(self._packages)

        return self._package_list
