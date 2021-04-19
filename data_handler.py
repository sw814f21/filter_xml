import json
import time

from requests import get
from xml.etree import ElementTree as ET

from temp_file import TempFile
from prev_processed_file import PrevProcessedFile
from cvr import get_cvr_handler
from data_outputter import get_outputter


class BaseDataHandler:
    """
    Base data handler class

    Handles collection, processing, and filtering of smiley xml data
    """
    SMILEY_XML_URL = 'https://www.foedevarestyrelsen.dk/_layouts/15/sdata/smiley_xml.xml'
    SMILEY_XML = 'smiley_xml.xml'
    SMILEY_JSON = 'smiley_json.json'

    def __init__(self, *args, **kwargs):
        self._sample_size = kwargs.pop('sample', 0)
        self._skip_scrape = kwargs.pop('no_scrape', False)
        self._outputter = get_outputter(kwargs.pop('push', False))
        self._file = kwargs.pop('file', '')

        self.smiley_file = self._file if self._file else self.SMILEY_XML

        self.cvr_handler = get_cvr_handler()

        # collect all class methods prefixed by 'filter_'
        self.filters = [getattr(self.__class__, fun)
                        for fun in dir(self.__class__)
                        if callable(getattr(self.__class__, fun))
                        and fun.startswith('filter_')]

    def collect(self) -> None:
        """
        Main runner for collection
        """
        self._create_smiley_json()
        self._process_smiley_json()

    def _create_smiley_json(self) -> None:
        """
        Create .json file from smiley XML data from Fødevarestyrelsen.
        """
        if not self._file:
            self._retrieve_smiley_data()

        tree = ET.parse(self.smiley_file)
        root = tree.getroot()

        res = []

        for row in list(root):
            new_obj = {col.tag: col.text for col in row}
            self.convert_to_float(new_obj, 'Geo_Lat', 'Geo_Lng')
            self.convert_to_int(new_obj, 'seneste_kontrol', 'naestseneste_kontrol',
                                'tredjeseneste_kontrol', 'fjerdeseneste_kontrol')
            self._strip_whitespace(new_obj, 'navn1')
            res.append(new_obj)

        with open(self.SMILEY_JSON, 'w') as f:
            f.write(json.dumps(res, indent=4, sort_keys=True))

    @staticmethod
    def convert_to_int(data: dict, *keys) -> None:
        """
        Convert a set of values to ints if they exist
        """
        for k in keys:
            data[k] = int(data[k]) if data[k] is not None else None

    @staticmethod
    def convert_to_float(data: dict, *keys) -> None:
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
        with open(self.SMILEY_XML, 'w') as f:
            f.write(res.content.decode('utf-8'))

    def _process_smiley_json(self) -> None:
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
        with open(self.SMILEY_JSON, 'r') as f:
            d = json.loads(f.read())

        temp_file = TempFile(d[0])

        prev_processed = PrevProcessedFile('processed_companies.csv')

        res = temp_file.get_all()
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
                if not temp_file.contains(restaurant['pnr']) \
                        and prev_processed.should_process_restaurant(restaurant):

                    # only sleep if --no-scrape is not passed, and if our cvr provider requests it.
                    if not self._skip_scrape and self.cvr_handler.SHOULD_SLEEP and row_index > 0:
                        time.sleep(self.cvr_handler.CRAWL_DELAY)

                    # only collect data if we haven't passed --no-scrape
                    processed = restaurant if self._skip_scrape \
                        else self.cvr_handler.collect_data(restaurant)

                    # check filters to see if we should keep the row
                    if self._should_keep(processed):
                        res.append(processed)
                        temp_file.add_data(processed)
                        row_kept = True

            # if any check resulted in a row skip, decrement the total row count
            # for terminal output purposes
            if not row_kept:
                total_rows -= 1

            if self._sample_size:
                print(f'Collected {len(res)} of {self._sample_size} samples')
            else:
                print(f'{total_rows - len(res)} rows to go')

            row_index += 1

        prev_processed.output_processed_companies(res)
        temp_file.close()

        res = self._rename_keys(res)

        self._outputter.write(res)

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


class DataHandler(BaseDataHandler):
    """
    Define filters here.

    Filters should be prefixed by 'filter_' and should have param 'data' of type dict, i.e., a row
    of data. All filters should be static.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @ staticmethod
    def filter_industry_codes(data: dict) -> bool:
        """
        Checks if row 'data' has a valid industry code.
        """
        include_codes = ['561010', '561020', '563000']
        res = 'industry_code' in data.keys() and data['industry_code'] in include_codes
        print(f'valid industry code: {res}')
        return res

    @ staticmethod
    def filter_null_control(data: dict) -> bool:
        """
        Checks if row 'data' has received at least 1 control check.
        """
        res = 'smiley_reports' in data.keys() and len(data['smiley_reports']) > 0
        print(f'control not null: {res}')
        return res

    @ staticmethod
    def filter_null_coordinates(data: dict) -> bool:
        """
        Checks if row 'data' has valid coordinates.
        """
        res = 'Geo_Lat' in data.keys() and data['Geo_Lat'] is not None \
              and 'Geo_Lng' in data.keys() and data['Geo_Lng'] is not None
        print(f'coords not null: {res}')
        return res
