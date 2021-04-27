from filter_xml.blacklist import Blacklist
from typing import List, Callable
from filter_xml.catalog import Restaurant


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

    @ staticmethod
    def filter_null_control(data: Restaurant) -> bool:
        """
        Checks if row 'data' has received at least 1 control check.
        """
        res = len(data.smiley_reports) > 0
        print(f'control not null: {res}')
        return res

    @ staticmethod
    def filter_null_coordinates(data: Restaurant) -> bool:
        """
        Checks if row 'data' has valid coordinates.
        """
        res = data.geo_lat is not None and data.geo_lng is not None
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
    def filter_industry_codes(data: Restaurant) -> bool:
        """
        Checks if row 'data' has a valid industry code.
        """
        include_codes = ['561010', '561020', '563000']
        res = data.industry_code in include_codes
        print(f'valid industry code: {res}')
        return res
