import sys
import json
import yaml
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog


class ConverterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Converter")
        self.layout = QVBoxLayout()
        self.label = QLabel("Wybierz pliki wejœciowe i wyjœciowe:", self)
        self.layout.addWidget(self.label)
        self.button = QPushButton("Wybierz pliki")
        self.button.clicked.connect(self.convert_files)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

    def convert_files(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file1, _ = QFileDialog.getOpenFileName(self, "Wybierz plik wejœciowy", "", "Pliki (*.xml *.json *.yaml)",
                                               options=options)
        file2, _ = QFileDialog.getSaveFileName(self, "Wybierz plik wyjœciowy", "", "Pliki (*.xml *.json *.yaml)",
                                               options=options)

        if file1 and file2:
            input_format = file1.split(".")[-1]
            output_format = file2.split(".")[-1]

            if input_format == output_format:
                self.label.setText("B³¹d: Nie mo¿na przekonwertowaæ do tego samego formatu.")
            elif input_format == "xml" and output_format == "json":
                with open(file1, "r", encoding="utf-8") as file:
                    xml_data = file.read()
                json_data = self.convert_xml_to_json(xml_data)
                with open(file2, "w", encoding="utf-8") as file:
                    file.write(json_data)
                self.label.setText("Konwersja z XML do JSON zakoñczona.")
            elif input_format == "json" and output_format == "yaml":
                with open(file1, "r", encoding="utf-8") as file:
                    json_data = file.read()
                yaml_data = self.convert_json_to_yaml(json_data)
                with open(file2, "w", encoding="utf-8") as file:
                    file.write(yaml_data)
                self.label.setText("Konwersja z JSON do YAML zakoñczona.")
            elif input_format == "yaml" and output_format == "xml":
                with open(file1, "r", encoding="utf-8") as file:
                    yaml_data = file.read()
                xml_data = self.convert_yaml_to_xml(yaml_data)
                with open(file2, "w", encoding="utf-8") as file:
                    file.write(xml_data)
                self.label.setText("Konwersja z YAML do XML zakoñczona.")
            else:
                self.label.setText("B³¹d: Nieobs³ugiwana kombinacja formatów.")

    def convert_xml_to_json(self, xml_data):
        tree = ET.ElementTree(ET.fromstring(xml_data))
        root = tree.getroot()
        data = {}
        data[root.tag] = self._parse_element(root)
        return json.dumps(data)

    def _parse_element(self, element):
        if len(element) == 0:
            return element.text
        else:
            data = {}
            for child in element:
                child_data = self._parse_element(child)
                if child.tag in data:
                    if isinstance(data[child.tag], list):
                        data[child.tag].append(child_data)
                    else:
                        data[child.tag] = [data[child.tag], child_data]
                else:
                    data[child.tag] = child_data
            return data

    def convert_json_to_yaml(self, json_data):
        data = json.loads(json_data)
        return yaml.dump(data)

    def convert_yaml_to_xml(self, yaml_data):
        data = yaml.safe_load(yaml_data)
        root = self._create_element(data)
        return ET.tostring(root, encoding="unicode")

    def _create_element(self, data):
        if isinstance(data, dict):
            element = ET.Element(list(data.keys())[0])
            for key, value in data.items():
                if isinstance(value, list):
                    for item in value:
                        element.append(self._create_element({key: item}))
                else:
                    element.append(self._create_element({key: value}))
            return element
        else:
            element = ET.Element("item")
            element.text = str(data)
            return element


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConverterApp()
    window.show()
    sys.exit(app.exec_())


