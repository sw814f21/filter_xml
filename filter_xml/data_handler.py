from filter_xml.data_outputter import get_outputter
from filter_xml.smiley_extractor import SmileyExtractor
from filter_xml.data_processor import DataProcessor


class DataHandler:
    SMILEY_XML = 'smiley_xml.xml'

    def __init__(self, *args, **kwargs) -> None:
        sample_size = kwargs.pop('sample', 0)
        skip_scrape = kwargs.pop('no_scrape', False)
        outputter = get_outputter(kwargs.pop('push', False))
        smiley_file = kwargs.pop('file', None)

        self.smiley_file = smiley_file if smiley_file else self.SMILEY_XML
        self.should_get_xml = False if smiley_file else True

        self.data_processor = DataProcessor(sample_size, skip_scrape, outputter)

    def collect(self) -> None:
        """
            Main runner for collection
        """
        smiley_extractor = SmileyExtractor(self.smiley_file, self.should_get_xml)
        data = smiley_extractor.create_smiley_json()
        self.data_processor.process_smiley_json(data)
