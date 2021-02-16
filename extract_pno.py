import xml.etree.ElementTree as ET

FILENAME = 'smiley_xml.xml'

tree = ET.parse(FILENAME)
root = tree.getroot()
rows = [r for r in list(root) if r[6].text.lower() == 'detail']

pnrs = [r.find('pnr').text for r in rows if r.find('pnr').text]

with open('pnr', 'w') as f:
    for pnr in pnrs:
        f.write(pnr + '\n')