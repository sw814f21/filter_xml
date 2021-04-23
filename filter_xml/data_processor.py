import time
from datetime import datetime
from filter_xml.config import FilterXMLConfig
from filter_xml.data_outputter import _BaseDataOutputter
from filter_xml.temp_file import TempFile
from filter_xml.prev_processed_file import PrevProcessedFile
from filter_xml.cvr import get_cvr_handler, FindSmileyHandler
from filter_xml.filters import PostFilters


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
        self.post_filters = PostFilters().filters()

    def process_smiley_json(self, data: list) -> None:
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
        prev_processed.add_list(res)

        total_rows = len(data)
        row_index = 0

        for restaurant in data:
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
                    if all([filter_(restaurant) for filter_ in self.post_filters]):
                        res.append(restaurant)
                        row_kept = True

                    temp_file.add_data(restaurant)
                    prev_processed.add(restaurant)

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
        insert, update, delete = self.create_diff(res)

        token = datetime.now().strftime(FilterXMLConfig.iso_fmt())

        self._outputter.insert(insert, token)
        self._outputter.update(update, token)
        self._outputter.delete(delete, token)

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

    def create_diff(self, res: list) -> tuple:
        """
        Construct the difference in data cf. the current contents of the database on the API.

        :param res: the list of new data
        :return: a tuple of the three types of differences, (insert, update, delete)
        """
        current_db = self._outputter.get()
        current_ids = {x['name_seq_nr'] for x in current_db}
        res_ids = {x['name_seq_nr'] for x in res}

        res_by_key = {x['name_seq_nr']: x for x in res}
        current_by_key = {x['name_seq_nr']: x for x in current_db}

        insert_ids = res_ids.difference(current_ids)
        delete_ids = current_ids.difference(res_ids)
        update_ids = res_ids.intersection(current_ids)

        insert = [res_by_key[x] for x in insert_ids]
        update = self.check_rows_for_updates(update_ids, res_by_key, current_by_key)

        return insert, update, list(delete_ids)

    def check_rows_for_updates(self, ids: set, new: dict, old: dict) -> list:
        """
        Compare each row of new data with their corresponding old row. Used to check for updates
        in data.
        """
        out = []

        for id_ in ids:
            if self.has_update(new[id_], old[id_]):
                out.append(new[id_].copy())

        return out

    @staticmethod
    def has_update(new: dict, old: dict) -> bool:
        """
        Key-wise comparison of a single row of data
        """
        comp_keys = ['cvrnr', 'pnr', 'region', 'industry_code', 'industry_text', 'start_date',
                     'city', 'elite_smiley', 'geo_lat', 'geo_lng', 'franchise_name',
                     'niche_industry', 'url', 'address', 'name', 'zip_code', 'ad_protection',
                     'company_type']
        smiley_keys = ['report_id', 'smiley', 'date']

        for k in comp_keys:
            if new[k] != old[k]:
                return True

            for sk in smiley_keys:
                if new['smiley_reports'][sk] != old['smiley_reports'][sk]:
                    return True

        return False
