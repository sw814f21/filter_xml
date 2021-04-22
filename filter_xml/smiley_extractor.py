from xml.etree import ElementTree as ET
from requests import get
from filter_xml.filters import PreFilters


class SmileyExtractor:
    """
    Class responsible for extracting data from the smiley XML file
    """
    SMILEY_XML_URL = 'https://www.foedevarestyrelsen.dk/_layouts/15/sdata/smiley_xml.xml'

    def __init__(self, file_path: str, should_get_xml: bool):
        self.smiley_xml = file_path
        self.should_get_xml = should_get_xml
        self.pre_filters = PreFilters().filters()

    def create_smiley_json(self) -> list:
        """
        Create .json file from smiley XML data from Fødevarestyrelsen.
        """
        if self.should_get_xml:
            self._retrieve_smiley_data()

        tree = ET.parse(self.smiley_xml)
        root = tree.getroot()

        res = []

        for row in list(root):
            new_obj = {col.tag: col.text for col in row}

            # run all pre filters and skip if all does not pass
            if not all([filter_(new_obj) for filter_ in self.pre_filters]):
                continue

            self._convert_to_float(new_obj, 'Geo_Lat', 'Geo_Lng')
            self._convert_to_int(new_obj, 'seneste_kontrol', 'naestseneste_kontrol',
                                 'tredjeseneste_kontrol', 'fjerdeseneste_kontrol')
            self._strip_whitespace(new_obj, 'navn1')
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

    def _retrieve_smiley_data(self) -> None:
        """
        Download smiley XML data from Fødevarestyrelsen.
        """
        res = get(self.SMILEY_XML_URL)
        with open(self.smiley_xml, 'w') as f:
            f.write(res.content.decode('utf-8'))
