import json

from filter_xml.data_outputter import get_outputter
from filter_xml.smiley_extractor import SmileyExtractor
from filter_xml.data_processor import DataProcessor
from filter_xml.util import is_file_old
from filter_xml.catalog import RestaurantCatalog, Restaurant
from filter_xml.filters import PreFilters


class DataHandler:
    SMILEY_XML = 'smiley_xml.xml'
    SMILEY_JSON = 'smiley_json.json'

    def __init__(self, *args, **kwargs) -> None:
        sample_size = kwargs.pop('sample', 0)
        skip_scrape = kwargs.pop('no_scrape', False)
        outputter = get_outputter(kwargs.pop('push', False))
        smiley_file = kwargs.pop('file', None)

        self.smiley_file = smiley_file if smiley_file else self.SMILEY_XML
        self.should_get_xml = False if smiley_file else is_file_old(self.SMILEY_XML)

        self.data_processor = DataProcessor(sample_size, skip_scrape, outputter)

    def collect(self) -> None:
        """
            Main runner for collection
        """
        if not is_file_old(self.SMILEY_JSON):
            data = RestaurantCatalog()
            pre_filters = PreFilters()
            with open(self.SMILEY_JSON, 'r') as f:
                temp = [Restaurant.from_json(row) for row in json.loads(f.read())]
            temp = [r for r in temp if pre_filters.filter(r)]
            data.add_many(temp)
        else:
            smiley_extractor = SmileyExtractor(self.smiley_file, self.should_get_xml)
            data = smiley_extractor.create_smiley_json()

            with open(self.SMILEY_JSON, 'w') as f:
                f.write(json.dumps(data.as_dict(), indent=4))

        self.data_processor.process_smiley_json(data)
