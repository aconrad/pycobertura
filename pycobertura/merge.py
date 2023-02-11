from pycobertura.cobertura import Cobertura
import os
import sys
import xml.etree.ElementTree as ET


class CoberturaMerge:
    def __init__(self, list_of_xml_filepaths, output_filepath, file_separator=os.sep):
        self.xml_filepaths = [
            filepath
            for filepath in list_of_xml_filepaths
            if filepath.split[file_separator][-1].endswith("xml")
        ]
        self.output_filepath = output_filepath

    def merge(self):
        if len(self.xml_filepaths) == 0:
            print("No xml files found")
            sys.exit(1)

        if len(self.xml_filepaths) == 1:
            print("Only one file given")
            xml = ET.parse(self.xml_filepaths[0])
            xml.write(self.output_filepath, encoding="UTF-8", xml_declaration=True)
            sys.exit(0)

        dict_cobertura = {
            xml_filepath: Cobertura(xml_filepath) for xml_filepath in self.xml_filepaths
        }

        dict_packages_root = {
            xml_filepath: dict_cobertura.get(xml_filepath).root_package()
            for xml_filepath in self.xml_filepaths
        }
        dict_packages_list = {
            xml_filepath: dict_cobertura.get(xml_filepath).packages()
            for xml_filepath in self.xml_filepaths
        }

        dict_class_root = {
            xml_filepath: dict_cobertura.get(xml_filepath)._get_root_class_by_filename
            for xml_filepath in self.xml_filepaths
        }
        dict_classes_list = {
            xml_filepath: dict_cobertura.get(
                xml_filepath
            )._make_class_elements_by_filename
            for xml_filepath in self.xml_filepaths
        }

        dict_method_root = {
            xml_filepath: dict_cobertura.get(xml_filepath)._get_method_root_by_filename
            for xml_filepath in self.xml_filepaths
        }
        dict_methods_list = {
            xml_filepath: dict_cobertura.get(
                xml_filepath
            )._make_method_elements_by_filename
            for xml_filepath in self.xml_filepaths
        }

        dict_line_root = {
            xml_filepath: dict_cobertura.get(xml_filepath)._get_line_root_by_filename
            for xml_filepath in self.xml_filepaths
        }
        dict_lines_list = {
            xml_filepath: dict_cobertura.get(
                xml_filepath
            )._make_list_elements_by_filename
            for xml_filepath in self.xml_filepaths
        }

        output_cobertura = dict_packages_root[self.xml_filepaths[0]]
        output_cobertura.append(set(dict_packages_list.values()))

        output_cobertura.append(set(dict_classes_root.values()))
        output_cobertura.append(set(dict_classes_list.values()))

        output_cobertura.append(set(dict_method_root.values()))
        output_cobertura.append(set(dict_method_list.values()))

        output_cobertura.append(set(dict_lines_root.values()))
        self.merge_lines(dict_lines, output_cobertura)

        return output_cobertura

    def merge_lines(self, dict_lines, output_cobertura):
        out_list = dict_lines[self.xml_filepaths[0]]
        for values in zip(dict_lines.values()):
            out_list.set("Hits", any([int(v.get("hits")) for v in values]))
            out_list.set("Cover", max([int(v.get("line-rate")) for v in values]))
            output_cobertura.append(out_list)
