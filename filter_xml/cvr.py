import json

from requests import get, post
from bs4 import BeautifulSoup
from datetime import datetime

from filter_xml.config import FilterXMLConfig
from filter_xml.catalog import Restaurant


class CVRHandlerBase:
    """
    Base class for CVR handling. Every data retrieval method should be contained in their own
    class and inherit this one.
    """
    URL = ''
    SHOULD_SLEEP = False
    CRAWL_DELAY = 0
    PRE_PROCESSING_STEP = False

    def __init__(self):
        # collect all class methods prefixed by 'append_'
        self.appenders = [getattr(self.__class__, fun)
                          for fun in dir(self.__class__)
                          if callable(getattr(self.__class__, fun))
                          and fun.startswith('append_')]

    def pre_processing(self, data: list):
        return

    def collect_data(self, data: Restaurant) -> Restaurant:
        """
        Data collection method. All inherited classes should override this and return a super() call
        """
        return data


class CVRHandlerElastic(CVRHandlerBase):
    """
    CVR handler for elastic search on virk.dk. Will be implemented once (if) we get access.

    https://data.virk.dk/datakatalog/erhvervsstyrelsen/system-til-system-adgang-til-cvr-data
    """
    URL = 'http://distribution.virk.dk/cvr-permanent/produktionsenhed/_search'
    PRE_PROCESSING_STEP = True

    def __init__(self):
        super().__init__()
        self.lookup_data = {}

    def pre_processing(self, data: list):
        all_pnrs = [r.pnr for r in data if r.pnr is not None]
        chunks = list(self.chunks(all_pnrs, 3000))
        num_reqs = len(chunks)
        print(f'Fetching pnr-info on {len(all_pnrs)} pnrs in {num_reqs} request(s):')

        auth = (FilterXMLConfig.cvr_elastic_username(), FilterXMLConfig.cvr_elastic_password())

        for i in range(len(chunks)):
            data = {
                'from': 0,
                'size': 3000,
                'query': {
                    'terms': {
                        'VrproduktionsEnhed.pNummer': chunks[i]
                    }
                },
                '_source': [
                    'VrproduktionsEnhed.livsforloeb.periode.gyldigFra',
                    'VrproduktionsEnhed.livsforloeb.periode.gyldigTil',
                    'VrproduktionsEnhed.pNummer',
                    'VrproduktionsEnhed.produktionsEnhedMetadata.nyesteHovedbranche.branchekode',
                    'VrproduktionsEnhed.produktionsEnhedMetadata.nyesteHovedbranche.branchetekst'
                ]
            }
            res = post(self.URL, json=data, auth=auth)

            if res.status_code == 200:
                self.parse_response(res.json())
            else:
                print("Bad response code")

            if i + 1 != num_reqs:
                print('.', end="", flush=True)
            else:
                print('Done!', flush=True)

    def parse_response(self, data: dict) -> None:
        for result in data['hits']['hits']:
            curr_res = result['_source']['VrproduktionsEnhed']
            industry = curr_res['produktionsEnhedMetadata']['nyesteHovedbranche']
            period = curr_res['livsforloeb'][0]['periode']
            start_date = period['gyldigFra']
            end_date = period['gyldigTil']
            value = {
                'industrycode': industry['branchekode'],
                'industrydesc': industry['branchetekst'],
                'startdate': datetime.strptime(start_date, '%Y-%m-%d') if start_date else None,
                'enddate': datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
            }
            self.lookup_data[str(curr_res['pNummer'])] = value

    def collect_data(self, data: Restaurant) -> Restaurant:
        if data.pnr in self.lookup_data:
            data.industry_code = self.lookup_data[data.pnr]['industrycode']
            data.industry_text = self.lookup_data[data.pnr]['industrydesc']
            data.start_date = self.lookup_data[data.pnr]['startdate']
            data.end_date = self.lookup_data[data.pnr]['enddate']
        else:
            print(f'Skipping restaurant with p-nr {data.pnr}: record not found remotely')

        return super().collect_data(data)

    #https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
    def chunks(self, lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

class CVRHandlerCVRAPI(CVRHandlerBase):
    """
    CVR handler for requesting JSON formatted data from cvrapi.dk

    https://cvrapi.dk/documentation
    """
    URL = 'https://cvrapi.dk/api'

    def __init__(self):
        super().__init__()

    def pre_processing(self, data: list):
        raise NotImplementedError(f'{self.__class__} not yet implemented')

    def collect_data(self, data: Restaurant) -> Restaurant:
        """
        Retrieve data from cvrapi and modify the data through every class method prefixed by
        'append_'.

        Note that it is important that we set the user agent when requesting. It should be on the
        form:
            '<company_name> - <project_name> - <contact_name> [<contact_phone_or_email>]'
        """
        print('-' * 40)
        print(f'{data.name} | {data.pnr}')
        params = {
            'produ': data.pnr,
            'country': 'dk',
            'token': FilterXMLConfig.cvrapi_api_key()
        }
        headers = {
            'User-Agent': 'sw814f21 - FindSmiley app - Jonas Andersen'
        }

        res = get(self.URL, params=params, headers=headers)
        content = json.loads(res.content.decode('utf-8'))

        if res.status_code == 200:
            for appender in self.appenders:
                data = appender(content, data)
        else:
            print(f'Skipping restaurant with p-nr {data.pnr}: record not found remotely')

        return super().collect_data(data)

    @staticmethod
    def append_cvrapi_industry_code(content: json, row: Restaurant) -> Restaurant:
        """
        Append industry code and description to the row from JSON content, and delete the old
        industry fields.
        """
        row.industry_code = str(content['industrycode'])
        row.industry_text = content['industrydesc']
        return row

    @staticmethod
    def append_cvrapi_start_date(content: json, row: Restaurant) -> Restaurant:
        """
        Append company start date formatted as ISO 8601
        """
        row.start_date = datetime.strptime(content['startdate'], '%d/%m - %Y')
        return row


class CVRHandlerScrape(CVRHandlerBase):
    """
    CVR handler for scraping data from virk.dk

    https://datacvr.virk.dk/data/

    Note that robots.txt specifies a crawl delay of 10 seconds
    https://datacvr.virk.dk/data/robots.txt
    """
    URL = 'https://datacvr.virk.dk/data/visenhed'
    SHOULD_SLEEP = True
    CRAWL_DELAY = 10

    def __init__(self):
        super().__init__()

    def pre_processing(self, data: list):
        raise NotImplementedError(f'{self.__class__} not yet implemented')

    def collect_data(self, data: Restaurant) -> Restaurant:
        """
        Collect HTML soup for the given row, and modify the row through every class method
        prefixed by 'append_'
        """
        print('-' * 40)
        print(f'{data.name} | {data.pnr}')
        params = {
            'enhedstype': 'produktionsenhed',
            'id': data.pnr,
            'language': 'da',
            'soeg': data.pnr,
        }

        print(f'{self.URL} | {params}')
        res = get(self.URL, params=params)
        soup = BeautifulSoup(res.content.decode('utf-8'), 'html.parser')

        for appender in self.appenders:
            data = appender(soup, data)

        return super().collect_data(data)

    @staticmethod
    def append_cvr_industry_code(soup: BeautifulSoup, row: Restaurant) -> Restaurant:
        """
        Appends industry code and text from datacvr.virk.dk to a row
        """
        industry_elem = soup.find(
            'div', attrs={'class': 'Help-stamdata-data-branchekode'})
        if industry_elem:
            industry_elem = industry_elem.parent.parent.parent
            industry = list(industry_elem.children)[3].text.strip()
            row.industry_code = industry.split()[0]
            row.industry_text = industry.replace(row.industry_code, '').strip()
            print(f'code: {row.industry_code}: {row.industry_text}')
        else:
            row.industry_code = row.industry_text = None

        return row

    @staticmethod
    def append_cvr_start_date(soup: BeautifulSoup, row: Restaurant) -> Restaurant:
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
            row.start_date = date
            print(f'date: {row.start_date}')
        else:
            row.start_date = None

        return row


def get_cvr_handler() -> CVRHandlerBase:
    """
    Retrieve CVR handler as specified by 'provider' in config file.
    """
    provider = FilterXMLConfig.cvr_provider()

    if provider == 'cvrapi':
        return CVRHandlerCVRAPI()
    elif provider == 'cvr_elastic':
        return CVRHandlerElastic()
    elif provider == 'scrape':
        return CVRHandlerScrape()
    else:
        raise KeyError(f'provider \"{provider}\" is invalid, please choose one of '
                       f'[ cvrapi | virk | scrape ]')


class FindSmileyHandler:
    """
    Handler for scraping smiley reports from findsmiley.dk
    """

    def __init__(self):
        # collect all class methods prefixed by 'append_'
        self.appenders = [getattr(self.__class__, fun)
                          for fun in dir(self.__class__)
                          if callable(getattr(self.__class__, fun))
                          and fun.startswith('append_')]

    def collect_data(self, data: Restaurant) -> Restaurant:
        """
        Data collection method. Retrieves findsmiley.dk page for the given company and runs
        every appender on it.
        """
        smiley = get(data.url)
        smiley_soup = BeautifulSoup(smiley.content.decode('utf-8'), 'html.parser')

        for appender in self.appenders:
            data = appender(smiley_soup, data)

        return data

    @staticmethod
    def append_smiley_reports(soup: BeautifulSoup, row: Restaurant) -> Restaurant:
        """
        Append smiley report IDs from findsmiley.dk for the given row
        """
        tags = soup.findAll('a', attrs={'target': '_blank'})

        # we assume that pdfs will continue to appear in descending order
        # if we want safe guarding against changes in order we can use
        # date = t.find('p', attrs={'class': 'DateText'}).text
        # and check the date against the fields of param: row
        for tag, report in zip(tags, row.smiley_reports):
            if report:
                url = tag.attrs['href']
                # use default if we cant find urls - will yield error page
                report.report_id = url.split('?')[1] if url else 'Virk'

        return row


class ZipcodeFinder:
    """
    Handler for fetching the name of city from zipcodes
    """
    URL = 'https://api.dataforsyningen.dk/postnumre'

    def __init__(self):
        self.zip_map = {row['nr']: row['navn'] for row in get(self.URL).json()}

    def __getitem__(self, key: str):
        if key not in self.zip_map.keys():
            return None
        return self.zip_map[key]
