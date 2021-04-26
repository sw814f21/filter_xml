from filter_xml.blacklist import Blacklist
from typing import List, Callable


class Filters:
    """
    Abstract class for filters
    """

    def filters(self) -> List[Callable]:
        return [getattr(self.__class__, fun)
                for fun in dir(self.__class__)
                if callable(getattr(self.__class__, fun))
                and fun.startswith('filter_')]


class PreFilters(Filters):
    """
    Define filters that should be run BEFORE processing here.

    Filters should be prefixed by 'filter_' and should have param 'data' of type dict, i.e., a row
    of data. All filters should be static.
    """

    Blacklist.read_restaurants_file()

    @ staticmethod
    def filter_null_control(data: dict) -> bool:
        """
        Checks if row 'data' has received at least 1 control check.
        """
        res = 'seneste_kontrol' in data.keys() and data['seneste_kontrol'] is not None
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

    @ staticmethod
    def filter_blacklisted(data: dict) -> bool:
        res = not Blacklist.contains(data['navnelbnr'])
        print(f'not in blacklist: {res}')
        return res


class PostFilters(Filters):
    """
    Define filters that should be run AFTER processing here.

    Filters should be prefixed by 'filter_' and should have param 'data' of type dict, i.e., a row
    of data. All filters should be static.
    """

    @staticmethod
    def filter_industry_codes(data: dict) -> bool:
        """
        Checks if row 'data' has a valid industry code.
        """
        include_codes = ['561010', '561020', '563000']
        res = 'industry_code' in data.keys() and data['industry_code'] in include_codes
        print(f'valid industry code: {res}')
        return res
