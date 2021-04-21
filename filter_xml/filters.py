class Filters:
    """
    Define filters here.

    Filters should be prefixed by 'filter_' and should have param 'data' of type dict, i.e., a row
    of data. All filters should be static.
    """

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
