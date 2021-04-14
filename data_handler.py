import json
import time

from temp_file import TempFile
from prev_processed_file import PrevProcessedFile
from requests import get
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET
from datetime import datetime


ISO8601_FMT = '%Y-%m-%dT%H:%M:%SZ'


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

    def __init__(self, *args, **kwargs):
        self._sample_size = kwargs.pop('sample', 0)
        self._skip_scrape = kwargs.pop('no_scrape', False)

        self.filters = [getattr(self.__class__, fun)
                        for fun in dir(self.__class__)
                        if callable(getattr(self.__class__, fun))
                        and fun.startswith('filter_')]
        self.cvr_appenders = [getattr(self.__class__, fun)
                              for fun in dir(self.__class__)
                              if callable(getattr(self.__class__, fun))
                              and fun.startswith('append_cvr')]
        self.smiley_appenders = [getattr(self.__class__, fun)
                                 for fun in dir(self.__class__)
                                 if callable(getattr(self.__class__, fun))
                                 and fun.startswith('append_smiley')]

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
            self.convert_to_float(new_obj, 'Geo_Lat', 'Geo_Lng')
            self.convert_to_int(new_obj, 'seneste_kontrol', 'naestseneste_kontrol',
                                'tredjeseneste_kontrol', 'fjerdeseneste_kontrol')
            self._strip_whitespace(new_obj, 'navn1')
            res.append(new_obj)

        with open(self.SMILEY_JSON, 'w') as f:
            f.write(json.dumps(res, indent=4, sort_keys=True))

    def convert_to_int(self, data: dict, *keys):
        for k in keys:
            data[k] = int(data[k]) if data[k] is not None else None

    def convert_to_float(self, data: dict, *keys):
        for k in keys:
            data[k] = float(data[k]) if data[k] is not None else None

    @staticmethod
    def _strip_whitespace(data: dict, *keys):
        for k in keys:
            data[k] = data[k].strip() if data[k] is not None and type(
                data[k]) == str else data[k]

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

        temp_file = TempFile(d[0])

        prev_processed = PrevProcessedFile('processed_pnrs.csv')

        sample_size = self._sample_size if self._sample_size else len(d)
        row_index = 0

        for restaurant in d:
            if not temp_file.contains(restaurant['pnr']) and self.valid_production_unit(restaurant):
                row_index += 1
                row_rem = sample_size - row_index
                if prev_processed.should_process_restaurant(restaurant['pnr'], restaurant['seneste_kontrol_dato']):

                    processed = restaurant if self._skip_scrape \
                        else self._append_additional_data(restaurant)
                    temp_file.add_data(processed)

                    if row_rem != 0 and not self._skip_scrape:
                        time.sleep(self.CRAWL_DELAY)

                print(f'{row_rem} rows to go')

                if row_rem == 0:
                    break
            else:
                row_index += 1

        filtered = self._filter_data(temp_file.get_all())

        prev_processed.output_processed_companies(filtered)
        temp_file.close()

        filtered = self._rename_keys(filtered)

        with open(out_path, 'w') as f:
            f.write(json.dumps(filtered, indent=4))

    def valid_production_unit(self, restaurant: dict) -> bool:
        return self._has_pnr(restaurant) and self._has_cvr(restaurant)

    def _filter_data(self, data: list) -> list:
        """
        Apply filters
        """
        for _filter in self.filters:
            data = _filter(data)

        return data

    def _append_additional_data(self, data: dict) -> dict:
        """
        run append methods on the data
        """

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

        for appender in self.cvr_appenders:
            data = appender(soup, data)

        smiley = get(data['URL'])
        smiley_soup = BeautifulSoup(
            smiley.content.decode('utf-8'), 'html.parser')

        for appender in self.smiley_appenders:
            data = appender(smiley_soup, data)

        return data

    @ staticmethod
    def _has_cvr(row: dict):
        """
        Check if a smiley data row has a CVR number
        """
        return 'cvrnr' in row.keys() and row['cvrnr'] is not None

    @ staticmethod
    def _has_pnr(row: dict):
        """
        Check if a smiley data row has a p-number
        """
        return 'pnr' in row.keys() and row['pnr'] is not None

    @staticmethod
    def _rename_keys(data: list):
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
    Define appenders and filters here.

    Appenders should be prefixed by 'append_' and should have params 'soup' and 'row'
        It is assumed that every appender works on an HTML soup from datacvr.virk.dk
    Filters should be prefixed by 'filter_' and should have param 'data'
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @ staticmethod
    def append_cvr_industry_code(soup, row):
        """
        Appends industry code and text from datacvr.virk.dk to a row
        """
        industry_elem = soup.find(
            'div', attrs={'class': 'Help-stamdata-data-branchekode'})
        if industry_elem:
            industry_elem = industry_elem.parent.parent.parent
            industry = list(industry_elem.children)[3].text.strip()
            row['industry_code'] = industry.split()[0]
            row['industry_text'] = industry.replace(
                row['industry_code'], '').strip()
            print(f'code: {row["industry_code"]}: {row["industry_text"]}')
        else:
            row['industry_code'] = row['industry_text'] = None
        return row

    @staticmethod
    def append_cvr_start_date(soup, row):
        """
        Appends start date from datacvr.virk.dk to a row
        """
        start_date_elem = soup.find(
            'div', attrs={'class': 'Help-stamdata-data-startdato'})
        if start_date_elem:
            start_date_elem = start_date_elem.parent.parent.parent
            date = datetime.strptime(
                list(start_date_elem.children)[3].text.strip(),
                '%d.%m.%Y'
            )
            row['start_date'] = date.strftime(ISO8601_FMT)
            print(f'date: {row["start_date"]}')
        else:
            row['industry_code'] = row['industry_text'] = None

        del row['branche']
        del row['brancheKode']

        return row

    @staticmethod
    def append_smiley_reports(soup, row):
        tags = soup.findAll('a', attrs={'target': '_blank'})
        keys = ['seneste_kontrol', 'naestseneste_kontrol', 'tredjeseneste_kontrol',
                'fjerdeseneste_kontrol']
        reports = []

        # we assume that pdfs will continue to appear in descending order
        # if we want safe guarding against changes in order we can use
        # date = t.find('p', attrs={'class': 'DateText'}).text
        # and check the date against the fields of param: row
        for tag, key in zip(tags, keys):
            if row[key]:
                url = tag.attrs['href']
                date = datetime.strptime(
                    row[f'{key}_dato'],
                    '%d-%m-%Y %H:%M:%S'
                )

                d = {
                    'report_id': url.split('?')[1],
                    'smiley': row[key],
                    'date': date.strftime(ISO8601_FMT)
                }

                reports.append(d)

                del row[key]
                del row[f'{key}_dato']

        row['smiley_reports'] = reports

        return row

    @ staticmethod
    def _filter_industry_codes(data):
        """
        Filters all companies that do not have a valid industry code.
        """
        include_codes = ['561010', '561020', '563000']
        return [item
                for item in data
                if 'industry_code' in item.keys()
                and item['industry_code'] in include_codes]

    @ staticmethod
    def filter_null_control(data):
        """
        Filters all companies that have not yet received a smiley control visit.
        """
        return [item
                for item in data
                if 'seneste_kontrol' in item.keys()
                and item['seneste_kontrol'] is not None]

    @ staticmethod
    def filter_null_coordinates(data):
        """
        Filters all companies without a longitude or latitude.
        """
        return [item
                for item in data
                if item['Geo_Lat'] is not None and item['Geo_Lng'] is not None]

    @ staticmethod
    def _filter_dead_companies(data):
        """
        Excluded for now. Remove leading underscore to include.

        Filters all companies that are presumed dead - i.e., has not received a smiley control visit
        within the last year.
        """
        res = []
        for item in data:
            last_control = datetime.strptime(
                item['seneste_kontrol_dato'], '%d-%m-%Y %H:%M:%S')
            now = datetime.now()
            diff = now - last_control

            if diff.days < 365:
                res.append(item)
        return res
