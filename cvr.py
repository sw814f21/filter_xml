import json

from requests import get
from bs4 import BeautifulSoup
from datetime import datetime
from config import FilterXMLConfig


class CVRHandlerBase:
    URL = ''
    SHOULD_SLEEP = False
    CRAWL_DELAY = 0

    def __init__(self):
        self.appenders = [getattr(self.__class__, fun)
                          for fun in dir(self.__class__)
                          if callable(getattr(self.__class__, fun))
                          and fun.startswith('append_')]
        self.smiley_appenders = [self.findsmiley_append_reports]

    def collect_data(self, data: dict):
        smiley = get(data['URL'])
        smiley_soup = BeautifulSoup(smiley.content.decode('utf-8'), 'html.parser')

        for appender in self.smiley_appenders:
            data = appender(smiley_soup, data)

        return data

    @staticmethod
    def findsmiley_append_reports(soup, row):
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
                    'date': date.strftime(FilterXMLConfig.iso_fmt())
                }

                reports.append(d)

                del row[key]
                del row[f'{key}_dato']

        row['smiley_reports'] = reports

        return row


class CVRHandlerVirk(CVRHandlerBase):
    URL = ''

    def __init__(self):
        super().__init__()

    def collect_data(self, data: dict):
        raise NotImplementedError(f'{self.__class__} not yet implemented')


class CVRHandlerCVRAPI(CVRHandlerBase):
    URL = 'https://cvrapi.dk/api'

    def __init__(self):
        super().__init__()

    def collect_data(self, data: dict):
        print('-' * 40)
        print(f'{data["navn1"]} | {data["pnr"]}')
        params = {
            'produ': data["pnr"],
            'country': 'dk',
            'token': FilterXMLConfig.cvrapi_api_key()
        }

        res = get(self.URL, params=params)
        content = json.loads(res.content.decode('utf-8'))

        if content:
            for appender in self.appenders:
                data = appender(content, data)

        return super().collect_data(data)

    @staticmethod
    def append_cvrapi_industry_code(content, row):
        row['industry_code'] = str(content['industrycode'])
        row['industry_text'] = content['industrydesc']
        del row['branche']
        del row['brancheKode']
        return row

    @staticmethod
    def append_cvrapi_start_date(content, row):
        date = datetime.strptime(content['startdate'], '%d/%m - %Y')
        row['start_date'] = date.strftime(FilterXMLConfig.iso_fmt())
        return row


class CVRHandlerScrape(CVRHandlerBase):
    URL = 'https://datacvr.virk.dk/data/visenhed'
    SHOULD_SLEEP = True
    CRAWL_DELAY = 10

    def __init__(self):
        super().__init__()

    def collect_data(self, data: dict):
        print('-' * 40)
        print(f'{data["navn1"]} | {data["pnr"]}')
        params = {
            'enhedstype': 'produktionsenhed',
            'id': data['pnr'],
            'language': 'da',
            'soeg': data['pnr'],
        }

        print(f'{self.URL} | {params}')
        res = get(self.URL, params=params)
        soup = BeautifulSoup(res.content.decode('utf-8'), 'html.parser')

        for appender in self.appenders:
            data = appender(soup, data)

        return super().collect_data(data)

    @staticmethod
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

        del row['branche']
        del row['brancheKode']

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
            row['start_date'] = date.strftime(FilterXMLConfig.iso_fmt())
            print(f'date: {row["start_date"]}')
        else:
            row['start_date'] = None

        return row


def get_cvr_handler() -> CVRHandlerBase:
    provider = FilterXMLConfig.cvr_provider()

    if provider == 'cvrapi':
        return CVRHandlerCVRAPI()
    elif provider == 'virk':
        return CVRHandlerVirk()
    elif provider == 'scrape':
        return CVRHandlerScrape()
    else:
        raise KeyError(f'provider \"{provider}\" is invalid, please choose one of '
                       f'[ cvrapi | virk | scrape ]')