from xml.etree import ElementTree as ET
from requests import get
from filter_xml.filters import PreFilters
from filter_xml.catalog import Restaurant, RestaurantCatalog


class SmileyExtractor:
    """
    Class responsible for extracting data from the smiley XML file
    """
    SMILEY_XML_URL = 'https://www.foedevarestyrelsen.dk/_layouts/15/sdata/smiley_xml.xml'

    def __init__(self, file_path: str, should_get_xml: bool):
        self.smiley_xml = file_path
        self.should_get_xml = should_get_xml
        self.pre_filters = PreFilters()

    def create_smiley_json(self) -> RestaurantCatalog:
        """
        Create .json file from smiley XML data from Fødevarestyrelsen.
        """
        if self.should_get_xml:
            self._retrieve_smiley_data()
        print("Parsing the smiley file.")
        tree = ET.parse(self.smiley_xml)
        root = tree.getroot()

        catalog = RestaurantCatalog()

        for row in list(root):
            new_obj = Restaurant.from_xml({col.tag: col.text for col in row})

            # run all pre filters and skip if all does not pass
            if not self.pre_filters.filter(new_obj):
                continue

            catalog.add(new_obj)

        self.pre_filters.log_filters()
        return catalog

    def _retrieve_smiley_data(self) -> None:
        """
        Download smiley XML data from Fødevarestyrelsen.
        """
        print("Downloading a new smiley file.")
        res = get(self.SMILEY_XML_URL)
        with open(self.smiley_xml, 'w') as f:
            f.write(res.content.decode('utf-8'))
