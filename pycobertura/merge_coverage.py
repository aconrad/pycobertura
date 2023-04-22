import xml.etree.ElementTree as ET
from typing import List


def update_element_stats(
    update_data, element, package_name=None, class_name=None, method_name=None
):
    element_id = (
        str(element.get("number")) if element.tag == "line" else element.get("name")
    )

    if package_name is not None and class_name is not None and method_name is not None:
        dict_ = update_data["packages"][package_name]["classes"][class_name]["methods"][
            method_name
        ]["lines"]
        if (
            dict_[element_id]["line-rate"] == 0.0
            and int(dict_[element_id].get("hits")) > 0
        ):
            dict_[element_id]["line-rate"] = 1.0
        dict_[element_id]["hits"] += int(dict_[element_id].get("hits"))
        dict_[element_id]["branch-rate"] = 0
    else:
        if package_name is None:
            dict_ = update_data["packages"]
        elif class_name is None:
            dict_ = update_data["packages"][package_name]["classes"]
        elif method_name is None:
            dict_ = update_data["packages"][package_name]["classes"][class_name][
                "methods"
            ]
        dict_[element_id]["line-rate"] += float(dict_[element_id].get("line-rate"))
        dict_[element_id]["branch-rate"] += float(
            dict_[element_id].get("branch-rate", 0)
        )

    return update_data


def merge_coverage(files: List[str], output_file: str) -> str:
    merged_data = {"packages": {}}
    for file in files:
        tree = ET.parse(file)
        root = tree.getroot()
        for package in root.findall("./packages/package"):
            package_name = package.get("name")
            merged_data["packages"][package_name] = {
                "name": package_name,
                "line-rate": float(package.get("line-rate")),
                "branch-rate": float(package.get("branch-rate")),
                "classes": {},
            }
            updated_package_data = update_element_stats(merged_data, package)
            merged_data.update(updated_package_data)

            for class_ in package.findall("./classes/class"):
                class_name = class_.get("name")
                merged_data["packages"][package_name]["classes"][class_name] = {
                    "name": class_name,
                    "line-rate": 0.0,
                    "branch-rate": 0,
                    "methods": {},
                }
                updated_class_data = update_element_stats(
                    merged_data, class_, package_name
                )
                merged_data.update(updated_class_data)

                for method in class_.findall("./methods/method"):
                    method_name = method.get("name")
                    merged_data["packages"][package_name]["classes"][class_name][
                        "methods"
                    ][method_name] = {
                        "name": method_name,
                        "line-rate": 0.0,
                        "branch-rate": 0,
                        "lines": {},
                    }
                    updated_method_data = update_element_stats(
                        merged_data, method, package_name, class_name
                    )
                    merged_data.update(updated_method_data)

                    for line in method.findall("./lines/line"):
                        line_num = line.get("number")
                        merged_data["packages"][package_name]["classes"][class_name][
                            "methods"
                        ][method_name]["lines"][line_num] = {
                            "number": line_num,
                            "line-rate": 0.0,
                            "hits": 0,
                        }
                        updated_line_data = update_element_stats(
                            merged_data, line, package_name, class_name, method_name
                        )
                        merged_data.update(updated_line_data)

    xml_root = ET.Element("coverage")
    total_line_rate = sum(
        [package_data["line-rate"] for package_data in merged_data["packages"].values()]
    ) / len(merged_data["packages"])
    total_branches_rate = sum(
        [
            package_data["branch-rate"]
            for package_data in merged_data["packages"].values()
        ]
    ) / len(merged_data["packages"])

    xml_root.set("line-rate", str(total_line_rate))
    xml_root.set("branch-rate", str(total_branches_rate))

    for package_name, package_data in merged_data["packages"].items():
        if package_name:
            package_element = ET.SubElement(xml_root, "package")
            package_element.set("name", package_name)
            package_element.set(
                "line-rate", str(package_data["line-rate"] / len(package_data))
            )
            package_element.set(
                "branch-rate", str(package_data["branch-rate"] / len(package_data))
            )

    tree = ET.ElementTree(xml_root)
    tree.write(output_file)


if __name__ == "__main__":
    files = ["coverage1.xml", "coverage2.xml", "coverage3.xml"]
    combined_coverage = merge_coverage(files, "overall_coverage.xml")
    print(combined_coverage)
