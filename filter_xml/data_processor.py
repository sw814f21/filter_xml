import time
from datetime import datetime
from filter_xml.config import FilterXMLConfig
from filter_xml.data_outputter import _BaseDataOutputter
from filter_xml.temp_file import TempFile
from filter_xml.prev_processed_file import PrevProcessedFile
from filter_xml.cvr import get_cvr_handler, FindSmileyHandler
from filter_xml.filters import PostFilters
from filter_xml.catalog import RestaurantCatalog


class DataProcessor:
    """
    Responsible for processing the data in smiley json file
    """

    def __init__(self, sample_size: int, skip_scrape: bool, outputter: _BaseDataOutputter) -> None:
        self._cvr_handler = get_cvr_handler()
        self._smiley_handler = FindSmileyHandler()
        self._sample_size = sample_size
        self._skip_scrape = skip_scrape
        self._outputter = outputter

        # collect all class methods prefixed by 'filter_'
        self.post_filters = PostFilters()

    def process_smiley_json(self, data: RestaurantCatalog) -> None:
        """
        Processes smiley .json file.
            Includes only production units
            Applies filters from DataHandler
            Collects additional, external data through CVRHandler

        Restaurants that have already been processed (i.e., external data has been collected) are
        stored in processed_companies.csv - handled by PrevProcessedFile.

        Restaurants that have been processed during the current session are stored in
        temp.csv - handled by TempFile. This is done to save progress in the case of a crash
        during the run.

        Once data has been processed, keys are renamed. Cf. the translation map in _rename_keys()
        """

        temp_file = TempFile()

        res = temp_file.get_all()

        prev_processed = PrevProcessedFile('processed_companies.csv')
        prev_processed.add_list(res.catalog)

        total_rows = data.catalog_size
        row_index = 0

        for restaurant in data.catalog:
            # we use this to avoid using the same fallback in three separate if statements
            row_kept = False

            # if sample size CLI arg is supplied, stop when its reached
            if self._sample_size and res.catalog_size >= self._sample_size:
                break

            # first check if the restaurant is valid
            if restaurant.is_valid_production_unit():

                # then ensure it hasn't already been processed prior to a crash, and
                # that it should be processed at all cf. previously processed restaurants
                if prev_processed.should_process_restaurant(restaurant):

                    # only sleep if --no-scrape is not passed, and if our cvr provider requests it.
                    if not self._skip_scrape and self._cvr_handler.SHOULD_SLEEP and row_index > 0:
                        time.sleep(self._cvr_handler.CRAWL_DELAY)

                    # only collect data if we haven't passed --no-scrape
                    if not self._skip_scrape:
                        restaurant = self._cvr_handler.collect_data(restaurant)
                        restaurant = self._smiley_handler.collect_data(restaurant)

                    # check filters to see if we should keep the row
                    if all([filter_(restaurant) for filter_ in self.post_filters.filters()]):
                        res.add(restaurant)
                        row_kept = True

                    temp_file.add_data(restaurant)
                    prev_processed.add(restaurant)

            # if any check resulted in a row skip, decrement the total row count
            # for terminal output purposes
            if not row_kept:
                total_rows -= 1

            if self._sample_size:
                print(f'Collected {res.catalog_size} of {self._sample_size} samples')
            else:
                print(f'{total_rows - res.catalog_size} rows to go')

            row_index += 1

        prev_processed.add_list(temp_file.get_all().catalog)
        prev_processed.output_processed_companies()
        temp_file.close()

        token = datetime.now().strftime(FilterXMLConfig.iso_fmt())
        res.setup_diff(self._outputter.get())

        self._outputter.insert(res.insert_set(), token)
        self._outputter.update(res.update_set(), token)
        self._outputter.delete(res.delete_set(), token)
