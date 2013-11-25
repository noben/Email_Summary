import xml.etree.ElementTree as ET
tree = ET.parse('corpus.xml')
root = tree.getroot()
for thread in root:
    thread
