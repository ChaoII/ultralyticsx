import os
import subprocess
import xml.etree.ElementTree as ET


def generate_qrc(base_path, output_path):
    # 创建RCC根元素
    rcc = ET.Element('RCC')

    # 定义要遍历的目录及其前缀
    directories = {
        '/images': os.path.join(base_path, 'images'),
        '/icons': os.path.join(base_path, 'icons'),
        '/i18n': os.path.join(base_path, 'i18n')
    }
    qresource = ET.SubElement(rcc, 'qresource', prefix="/")
    # 遍历每个目录并创建qresource元素
    for prefix, directory in directories.items():
        # 遍历目录中的文件
        for root, _, files in os.walk(directory):
            for file in files:
                relative_path = os.path.relpath(str(os.path.join(root, file)), start=base_path)
                file_element_path = relative_path.replace("\\", "/")
                file_element = ET.SubElement(qresource, 'file')
                file_element.text = str(file_element_path)

    # 将RCC树转换为字符串并写入文件
    tree = ET.ElementTree(rcc)
    with open(output_path, 'wb') as f:
        tree.write(f, encoding='utf-8', xml_declaration=False)


# 使用示例
base_directory = 'resources'
output_file = os.path.join(base_directory, 'resources.qrc')
generate_qrc(base_directory, output_file)

subprocess.run(['pyside6-rcc', 'resources/resources.qrc', '-o', 'resources/resources.py'])
