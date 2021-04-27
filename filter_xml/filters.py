import json
import os

from typing import List, Callable, Dict


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
            return data[key]

    def __setitem__(self, key: str, value: int):
        """
        Behaviour on item assignment, i.e.
        >>> log = FilterLog()
        >>> log['hi'] = 1
        """
        with open(self.LOG_FILE, 'r') as f:
            data = json.loads(f.read())

        data[key] = value

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
            return key in data.keys()

    def _create_file(self):
        """
        Create the file and write an empty json structure
        """
        with open(self.LOG_FILE, 'w') as f:
            f.write(json.dumps({}))


class Filters:
    """
    Base class for filters
    """
    LOG = {}  # type: Dict[str, int]
    LOGGER = FilterLog()

    def filters(self) -> List[Callable]:
        return [getattr(self.__class__, fun)
                for fun in dir(self.__class__)
                if callable(getattr(self.__class__, fun))
                and fun.startswith('filter_')]

    def print_log(self) -> None:
        print('Filtered rows:')
        for filter_name, count in self.LOG.items():
            print(f'{filter_name}: {count}')


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
        'null_coordinates': 0
    }

    def __init__(self):
        self.LOGGER['null_control'] = 0
        self.LOGGER['null_coordinates'] = 0

    @classmethod
    def log_pre_filters(cls):
        for key, value in cls.LOG.items():
            cls.LOGGER[key] = value

    @ classmethod
    def filter_null_control(cls, data: dict) -> bool:
        """
        Checks if row 'data' has received at least 1 control check.
        """
        res = 'seneste_kontrol' in data.keys() and data['seneste_kontrol'] is not None
        if not res:
            cls.LOG['null_control'] += 1
        return res

    @ classmethod
    def filter_null_coordinates(cls, data: dict) -> bool:
        """
        Checks if row 'data' has valid coordinates.
        """
        res = 'Geo_Lat' in data.keys() and data['Geo_Lat'] is not None \
              and 'Geo_Lng' in data.keys() and data['Geo_Lng'] is not None
        if not res:
            cls.LOG['null_coordinates'] += 1
        return res


class PostFilters(Filters):
    """
    Define filters that should be run AFTER processing here.

    Filters should be prefixed by 'filter_' and should have param 'data' of type dict, i.e., a row
    of data. All filters should be static.

    A log of filtered rows is maintained in a file during run. For post-filters we have to
    increment for each check to ensure a properly maintained state. As such we only use
    cls.LOGGER[key] here.
    """

    def __init__(self):
        self.LOGGER['industry_code'] = 0

    @classmethod
    def filter_industry_codes(cls, data: dict) -> bool:
        """
        Checks if row 'data' has a valid industry code.
        """
        include_codes = ['561010', '561020', '563000']
        res = 'industry_code' in data.keys() and data['industry_code'] in include_codes
        print(f'valid industry code: {res}')
        if not res:
            cls.LOGGER['industry_code'] += 1
        return res
