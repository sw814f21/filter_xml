from src.data_outputter import BaseDataOutputter
import json
import time
from src.temp_file import TempFile
from src.prev_processed_file import PrevProcessedFile
from src.cvr import get_cvr_handler, FindSmileyHandler
from src.filters import Filters


class DataProcessor:
    """
    Responsible for processing the data in smiley json file
    """

    def __init__(self, sample_size: int, skip_scrape: bool, outputter: BaseDataOutputter) -> None:
        self._cvr_handler = get_cvr_handler()
        self._smiley_handler = FindSmileyHandler()
        self._sample_size = sample_size
        self._skip_scrape = skip_scrape
        self._outputter = outputter

        # collect all class methods prefixed by 'filter_'
        filters = Filters()
        self.filters = [getattr(filters.__class__, fun)
                        for fun in dir(filters.__class__)
                        if callable(getattr(filters.__class__, fun))
                        and fun.startswith('filter_')]

    def process_smiley_json(self, json_file_path: str) -> None:
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
        with open(json_file_path, 'r') as f:
            d = json.loads(f.read())

        temp_file = TempFile()

        res = temp_file.get_all()

        prev_processed = PrevProcessedFile('processed_companies.csv')
        prev_processed.add_list(res)

        total_rows = len(d)
        row_index = 0

        for restaurant in d:
            # we use this to avoid using the same fallback in three separate if statements
            row_kept = False

            # if sample size CLI arg is supplied, stop when its reached
            if self._sample_size and len(res) >= self._sample_size:
                break

            # first check if the restaurant is valid
            if self.valid_production_unit(restaurant):

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
                    if self._should_keep(restaurant):
                        res.append(restaurant)
                        row_kept = True

                    temp_file.add_data(restaurant)

            # if any check resulted in a row skip, decrement the total row count
            # for terminal output purposes
            if not row_kept:
                total_rows -= 1

            if self._sample_size:
                print(f'Collected {len(res)} of {self._sample_size} samples')
            else:
                print(f'{total_rows - len(res)} rows to go')

            row_index += 1

        prev_processed.add_list(temp_file.get_all())
        prev_processed.output_processed_companies()
        temp_file.close()

        res = self._rename_keys(res)

        self._outputter.write(res)

    @ staticmethod
    def _has_cvr(row: dict) -> bool:
        """
        Check if a smiley data row has a CVR number
        """
        return 'cvrnr' in row.keys() and row['cvrnr'] is not None

    @ staticmethod
    def _has_pnr(row: dict) -> bool:
        """
        Check if a smiley data row has a p-number
        """
        return 'pnr' in row.keys() and row['pnr'] is not None

    @staticmethod
    def _rename_keys(data: list) -> list:
        """
        Rename keys in each row.
        """
        trans = {
            'By': 'city',
            'Elite_Smiley': 'elite_smiley',
            'Geo_Lat': 'geo_lat',
            'Geo_Lng': 'geo_lng',
            'Kaedenavn': 'franchise_name',
            'Pixibranche': 'niche_industry',
            'URL': 'url',
            'adresse1': 'address',
            'navn1': 'name',
            'navnelbnr': 'name_seq_nr',
            'postnr': 'zip_code',
            'reklame_beskyttelse': 'ad_protection',
            'virksomhedstype': 'company_type'
        }

        for row in data:
            for key, _trans in trans.items():
                row[_trans] = row[key]
                del row[key]

        return data

    def valid_production_unit(self, restaurant: dict) -> bool:
        """
        Check if a restaurant is a valid production unit, by checking if they have both a
        p-number and a CVR number.
        """
        return self._has_pnr(restaurant) and self._has_cvr(restaurant)

    def _should_keep(self, data: dict) -> bool:
        """
        Apply filters to see if row should be kept in result
        """
        res = [_filter(data) for _filter in self.filters]
        return all(res)