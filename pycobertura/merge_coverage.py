import xml.etree.ElementTree as ET
from collections import defaultdict

def merge_coverage_data(files):
    merged_data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(int))))

    for file in files:
        tree = ET.parse(file)
        root = tree.getroot()
        
        for package in root.findall('./packages/package'):
            package_name = package.attrib['name']
            for class_ in package.findall('classes/class'):
                class_name = class_.attrib['name']
                for method in class_.findall('methods/method'):
                    method_name = method.attrib['name']
                    for line in method.findall('lines/line'):
                        line_number = line.attrib['number']
                        hits = int(line.attrib['hits'])
                        merged_data[package_name][class_name][method_name][line_number] += hits

    return merged_data

def generate_merged_xml(merged_data):
    root = ET.Element('coverage')

    for package_name, package_data in merged_data.items():
        package_elem = ET.SubElement(root, 'package', name=package_name)
        for class_name, class_data in package_data.items():
            class_elem = ET.SubElement(package_elem, 'class', name=class_name)
            for method_name, method_data in class_data.items():
                method_elem = ET.SubElement(class_elem, 'method', name=method_name)
                lines_elem = ET.SubElement(method_elem, 'lines')
                for line_number, hits in method_data.items():
                    ET.SubElement(lines_elem, 'line', number=line_number, hits=str(hits))

    return ET.ElementTree(root)

def main():
    files = ['cobertura1.xml', 'cobertura2.xml']  # List of Cobertura XML files to merge
    merged_data = merge_coverage_data(files)

    merged_xml_tree = generate_merged_xml(merged_data)
    merged_xml_tree.write('merged_cobertura.xml', encoding='utf-8', xml_declaration=True)

if __name__ == "__main__":
    main()

