from src.data_outputter import get_outputter
from src.smiley_extractor import SmileyExtractor
from src.data_processor import DataProcessor


class DataHandler:
    def __init__(self, *args, **kwargs) -> None:
        sample_size = kwargs.pop('sample', 0)
        skip_scrape = kwargs.pop('no_scrape', False)
        outputter = get_outputter(kwargs.pop('push', False))
        self.dataProcessor = DataProcessor(sample_size, skip_scrape, outputter)

    def collect(self) -> None:
        """
            Main runner for collection
        """

        data = SmileyExtractor.create_smiley_json()
        self.dataProcessor.process_smiley_json(data)
