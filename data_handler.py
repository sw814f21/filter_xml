import json
import time

from requests import get
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET
from datetime import datetime


class BaseDataHandler:
    """
    Base data handler class

    Handles collection, processing, and filtering of smiley xml data
    """
    SMILEY_XML_URL = 'https://www.foedevarestyrelsen.dk/_layouts/15/sdata/smiley_xml.xml'
    SMILEY_XML = 'smiley_xml.xml'
    SMILEY_JSON = 'smiley_json.json'

    CRAWL_DELAY = 10
    BASE_CVR_URL = 'https://datacvr.virk.dk/data/'
    CRAWL_CVR_URL = f'{BASE_CVR_URL}visenhed'

    def __init__(self):
        self.filters = [getattr(self.__class__, fun)
                        for fun in dir(self.__class__)
                        if callable(getattr(self.__class__, fun))
                        and fun.startswith('filter_')]
        self.data_appenders = [getattr(self.__class__, fun)
                               for fun in dir(self.__class__)
                               if callable(getattr(self.__class__, fun))
                               and fun.startswith('append_')]

    def collect(self):
        """
        Main runner for collection
        """
        self._create_smiley_json()
        self._process_smiley_json()

    def _create_smiley_json(self):
        """
        Create .json file from smiley XML data from Fødevarestyrelsen.
        """
        self._retrieve_smiley_data()

        tree = ET.parse(self.SMILEY_XML)
        root = tree.getroot()

        res = []

        for row in list(root):
            new_obj = {col.tag: col.text for col in row}
            new_obj['Geo_Lat'] = float(new_obj['Geo_Lat']) if new_obj['Geo_Lat'] != None else "null"
            new_obj['Geo_Lng'] = float(new_obj['Geo_Lng']) if new_obj['Geo_Lng'] != None else "null"
            self.convert_control_to_int(new_obj)
            new_obj['navnelbnr'] = row[0].text
            res.append(new_obj)

        with open(self.SMILEY_JSON, 'w') as f:
            f.write(json.dumps(res, indent=4, sort_keys=True))

    def convert_control_to_int(self, data: dict):
        keys = ['seneste_kontrol', 'naestseneste_kontrol', 'tredjeseneste_kontrol', 'fjerdeseneste_kontrol']
        for k in keys:
            data[k] = int(data[k]) if data[k] != None else None

    def _retrieve_smiley_data(self):
        """
        Download smiley XML data from Fødevarestyrelsen.
        """
        res = get(self.SMILEY_XML_URL)
        with open(self.SMILEY_XML, 'w') as f:
            f.write(res.content.decode('utf-8'))

    def _process_smiley_json(self):
        """
        Processes smiley .json file.
            Includes only production units
            Applies filters and appends from DataHandler
        """
        out_path = f'smiley_json_processed.json'

        with open(self.SMILEY_JSON, 'r') as f:
            d = json.loads(f.read())

        valid = self._valid_production_units(d)
        #processed = self._append_additional_data(valid)
        filtered = self._filter_data(valid)

        with open(out_path, 'w') as f:
            f.write(json.dumps(filtered, indent=4))

    def _filter_data(self, data: list) -> list:
        """
        Apply filters
        """
        for _filter in self.filters:
            data = _filter(data)

        return data

    def _append_additional_data(self, smiley_data: list) -> list:
        """
        Iterate over every row of the smiley data and run append methods on the data
        """
        out = []
        row_index = 0
        for data in smiley_data:
            print('-' * 40)
            print(f'{data["navn1"]} | {data["pnr"]}')
            params = {
                'enhedstype': 'produktionsenhed',
                'id': data['pnr'],
                'language': 'da',
                'soeg': data['pnr'],
            }

            print(f'{self.CRAWL_CVR_URL} | {params}')
            res = get(self.CRAWL_CVR_URL, params=params)
            soup = BeautifulSoup(res.content.decode('utf-8'), 'html.parser')

            for appender in self.data_appenders:
                data = appender(soup, data)

            row_index += 1
            row_rem = len(smiley_data) - row_index
            print(f'{row_rem} rows to go')

            out.append(data)

            if row_rem != 0:
                time.sleep(self.CRAWL_DELAY)

        return out

    def _valid_production_units(self, initial: list):
        """
        Reconstruct dict only containing rows that have p-numbers
        """
        return [item for item in initial if self._has_pnr(item) and self._has_cvr(item)]

    @staticmethod
    def _has_cvr(row: dict):
        """
        Check if a smiley data row has a CVR number
        """
        return 'cvrnr' in row.keys() and row['cvrnr'] is not None

    @staticmethod
    def _has_pnr(row: dict):
        """
        Check if a smiley data row has a p-number
        """
        return 'pnr' in row.keys() and row['pnr'] is not None


class DataHandler(BaseDataHandler):
    """
    Define appenders and filters here.

    Appenders should be prefixed by 'append_' and should have params 'soup' and 'row'
        It is assumed that every appender works on an HTML soup from datacvr.virk.dk
    Filters should be prefixed by 'filter_' and should have param 'data'
    """

    def __init__(self):
        super().__init__()

    @staticmethod
    def append_industry_code(soup, row):
        """
        Appends industry code and text from datacvr.virk.dk to a row
        """
        industry_elem = soup.find('div', attrs={'class': 'Help-stamdata-data-branchekode'})
        if industry_elem:
            industry_elem = industry_elem.parent.parent.parent
            industry = list(industry_elem.children)[3].text.strip()
            row['industry_code'] = industry.split()[0]
            row['industry_text'] = industry.replace(row['industry_code'], '').strip()
            print(f'code: {row["industry_code"]}: {row["industry_text"]}')
        else:
            row['industry_code'] = row['industry_text'] = None
        return row

    @staticmethod
    def append_start_date(soup, row):
        """
        Appends start date from datacvr.virk.dk to a row
        """
        start_date_elem = soup.find('div', attrs={'class': 'Help-stamdata-data-startdato'})
        if start_date_elem:
            start_date_elem = start_date_elem.parent.parent.parent
            row['start_date'] = list(start_date_elem.children)[3].text.strip()
            print(f'date: {row["start_date"]}')
        else:
            row['industry_code'] = row['industry_text'] = None
        return row

    @staticmethod
    def _filter_industry_codes(data):
        """
        Filters all companies that do not have a valid industry code.
        """
        include_codes = ['561010', '561020', '563000']
        return [item
                for item in data
                if 'industry_code' in item.keys()
                and item['industry_code'] in include_codes]

    @staticmethod
    def filter_null_control(data):
        """
        Filters all companies that have not yet received a smiley control visit.
        """
        return [item
                for item in data
                if 'seneste_kontrol' in item.keys()
                and item['seneste_kontrol'] is not None]

    @staticmethod
    def filter_null_coordinates(data):
        """
        Filters all companies without a longitude or latitude.
        """
        return [item
                    for item in data
                    if item['Geo_Lat'] != 'null' and item['Geo_Lng'] != 'null']

    @staticmethod
    def _filter_dead_companies(data):
        """
        Excluded for now. Remove leading underscore to include.

        Filters all companies that are presumed dead - i.e., has not received a smiley control visit
        within the last year.
        """
        res = []
        for item in data:
            last_control = datetime.strptime(item['seneste_kontrol_dato'], '%d-%m-%Y %H:%M:%S')
            now = datetime.now()
            diff = now - last_control

            if diff.days < 365:
                res.append(item)
        return res