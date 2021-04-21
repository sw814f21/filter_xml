from xml.etree import ElementTree as ET
from requests import get


class SmileyExtractor:
    """
    Class responsible for extracting data from the smiley XML file
    """
    SMILEY_XML_URL = 'https://www.foedevarestyrelsen.dk/_layouts/15/sdata/smiley_xml.xml'
    SMILEY_XML = 'smiley_xml.xml'

    @classmethod
    def create_smiley_json(cls) -> dict:
        """
        Create .json file from smiley XML data from Fødevarestyrelsen.
        """
        cls._retrieve_smiley_data()

        tree = ET.parse(cls.SMILEY_XML)
        root = tree.getroot()

        res = []

        for row in list(root):
            new_obj = {col.tag: col.text for col in row}
            cls._convert_to_float(new_obj, 'Geo_Lat', 'Geo_Lng')
            cls._convert_to_int(new_obj, 'seneste_kontrol', 'naestseneste_kontrol',
                                'tredjeseneste_kontrol', 'fjerdeseneste_kontrol')
            cls._strip_whitespace(new_obj, 'navn1')
            res.append(new_obj)

        return res

    @staticmethod
    def _convert_to_int(data: dict, *keys) -> None:
        """
        Convert a set of values to ints if they exist
        """
        for k in keys:
            data[k] = int(data[k]) if data[k] is not None else None

    @staticmethod
    def _convert_to_float(data: dict, *keys) -> None:
        """
        Convert a set of values to floats if they exist
        """
        for k in keys:
            data[k] = float(data[k]) if data[k] is not None else None

    @staticmethod
    def _strip_whitespace(data: dict, *keys) -> None:
        """
        Strip whitespace from a set of values if applicable
        """
        for k in keys:
            data[k] = data[k].strip() if data[k] is not None and type(
                data[k]) == str else data[k]

    @classmethod
    def _retrieve_smiley_data(cls) -> None:
        """
        Download smiley XML data from Fødevarestyrelsen.
        """
        res = get(cls.SMILEY_XML_URL)
        with open(cls.SMILEY_XML, 'w') as f:
            f.write(res.content.decode('utf-8'))
