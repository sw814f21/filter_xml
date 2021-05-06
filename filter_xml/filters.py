import json
import os

from datetime import datetime
from typing import List, Callable, Dict
from filter_xml.blacklist import Blacklist
from filter_xml.catalog import Restaurant
from filter_xml.config import FilterXMLConfig
from filter_xml.cvr import ZipcodeFinder


class FilterLog:
    """
    Log file handler for filters.

    Maintains a file filter_log.json containing mappings from filter methods to the amount of times
    a restaurant has been filtered by them.

    Behaves sort of like a dictionary
        >>> log = FilterLog()
        >>> log['hi'] = 1       # {'hi': 1}
        >>> log['hi'] += 5      # {'hi': 6}

        you can also check existence of keys
        >>> 'hi' in log
        True
        >>> 'yeet' in log
        False
    """
    LOG_FILE = 'filter_log.json'

    def __init__(self):
        if not os.path.isfile(self.LOG_FILE):
            self._create_file()

    def __getitem__(self, key: str):
        """
        Behaviour on item access, i.e.
        >>> log = FilterLog()
        >>> log[key]
        """
        if key not in self:
            raise KeyError(f'key {key} does not exist in log file')

        with open(self.LOG_FILE, 'r') as f:
            data = json.loads(f.read())
            return data['log'][key]

    def __setitem__(self, key: str, value: int):
        """
        Behaviour on item assignment, i.e.
        >>> log = FilterLog()
        >>> log['hi'] = 1
        """
        with open(self.LOG_FILE, 'r') as f:
            data = json.loads(f.read())

        data['log'][key] = value

        with open(self.LOG_FILE, 'w') as f:
            f.write(json.dumps(data, indent=4))

    def __contains__(self, key: str):
        """
        Behaviour on `in` operator, i.e.
        >>> log = FilterLog()
        >>> log['hi'] = 1
        >>> 'hi' in log
        True
        >>> 'yeet' in log
        False
        """
        with open(self.LOG_FILE, 'r') as f:
            data = json.loads(f.read())
            return key in data['log'].keys()

    def _create_file(self):
        """
        Create the file and write an empty json structure
        """
        with open(self.LOG_FILE, 'w') as f:
            f.write(json.dumps({
                'time': datetime.now().strftime(FilterXMLConfig.iso_fmt()),
                'log': {}
            }))


class Filters:
    """
    Base class for filters
    """
    LOG = {}  # type: Dict[str, int]
    LOGGER = FilterLog()

    def _filters(self) -> List[Callable]:
        return [getattr(self.__class__, fun)
                for fun in dir(self.__class__)
                if callable(getattr(self.__class__, fun))
                and fun.startswith('filter_')]

    def print_log(self) -> None:
        print('Filtered rows:')
        for filter_name, count in self.LOG.items():
            print(f'{filter_name}: {count}')

    @classmethod
    def log_filters(cls):
        for key, value in cls.LOG.items():
            cls.LOGGER[key] = value

    def filter(self, restaurant: Restaurant):
        for f in self._filters():
            if not f(restaurant):
                return False
        return True


class PreFilters(Filters):
    """
    Define filters that should be run BEFORE processing here.

    Filters should be prefixed by 'filter_' and should have param 'data' of type dict, i.e., a row
    of data. All filters should be static.

    A log of filtered rows is maintained in a file during run. For pre-filters we are able to
    avoid a read/write on each check, and as such only self.LOG[key] should be incremented, and
    cls.log_pre_filters() should be called once the initial processing is done.
    """
    LOG = {
        'null_control': 0,
        'null_coordinates': 0,
        'blacklisted': 0,
        'null_city': 0,
        'invalid_zip': 0
    }

    ZIP_CODES = ZipcodeFinder()

    @ classmethod
    def filter_null_control(cls, data: Restaurant) -> bool:
        """
        Checks if row 'data' has received at least 1 control check.
        """
        res = len(data.smiley_reports) > 0
        if not res:
            cls.LOG['null_control'] += 1
        return res

    @ classmethod
    def filter_null_coordinates(cls, data: Restaurant) -> bool:
        """
        Checks if row 'data' has valid coordinates.
        """
        res = data.geo_lat is not None and data.geo_lng is not None
        if not res:
            cls.LOG['null_coordinates'] += 1
        return res

    @ classmethod
    def filter_blacklisted(cls, data: Restaurant) -> bool:
        res = not Blacklist.contains(data.name_seq_nr)
        if not res:
            cls.LOG['blacklisted'] += 1
        return res

    @classmethod
    def filter_city(cls, data: Restaurant) -> bool:
        if not data.city:
            cls.LOG['null_city'] += 1
            data.city = cls.ZIP_CODES[data.zip_code]

            if not data.city:
                cls.LOG['invalid_zip'] += 1
                return False
        return True


class PostFilters(Filters):
    """
    Define filters that should be run AFTER processing here.

    Filters should be prefixed by 'filter_' and should have param 'data' of type dict, i.e., a row
    of data. All filters should be static.

    A log of filtered rows is maintained in a file during run. For post-filters we have to
    increment for each check to ensure a properly maintained state. As such we only use
    cls.LOGGER[key] here.
    """

    LOG = {
        'industry_code': 0,
        'end_date': 0
    }

    def __init__(self):
        self.LOGGER['industry_code'] = 0
        self.LOGGER['end_date'] = 0

    @classmethod
    def filter_industry_codes(cls, data: Restaurant) -> bool:
        """
        Checks if row 'data' has a valid industry code.
        """
        include_codes = ['561010', '561020', '563000']
        res = data.industry_code in include_codes
        if not res:
            cls.LOGGER['industry_code'] += 1
        return res

    @classmethod
    def filter_end_date(cls, data: Restaurant) -> bool:
        """
        Checks if row 'data' has an end date
        """
        res = not data.end_date
        if not res:
            print(f'end date: {data.end_date}, pnr: {data.pnr}')
            cls.LOGGER['end_date'] += 1
        return res
