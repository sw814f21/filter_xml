from xml.etree import ElementTree
import xmltodict
import json

FILE = 'enrichment_subsidiaries.csv'
XML = 'smiley_xml.xml'
CODE = 'DD.56.10.99'

xml = ElementTree.parse(XML)
xml_root = xml.getroot()

with open(FILE, 'r') as f:
    data = f.readlines()

headers = data[0].split(';')
del data[0]

data_by_pnr = [{header.strip('\n'): entry.strip('\n').strip('"')
                for entry, header in zip(row.split(';'), headers)}
               for row in data]

pnrs = {x['subsidiarynumber']: x for x in data_by_pnr}
res = []

for row in xml_root.findall('row'):
    if row.find('brancheKode').text.strip() != CODE:
        continue

    pnr = row.find('pnr').text
    if str(pnr) in pnrs.keys():
        start_date = ElementTree.SubElement(row, 'start_date')
        start_date.text = pnrs[str(pnr)]['startdate']

        end_date = ElementTree.SubElement(row, 'end_date')
        end_date.text = pnrs[str(pnr)]['enddate']

        res.append(xmltodict.parse(ElementTree.tostring(row, method='xml')))

with open('out.json', 'w') as f:
    f.write(json.dumps(res, indent=4))
