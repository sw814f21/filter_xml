# type hinting a class within that class is not supported until python 3.10
# so we need to import future annotations to allow this
# note that __future__ imports must be the first line of the file
from __future__ import annotations

from typing import Optional, List
from datetime import datetime

from filter_xml.config import FilterXMLConfig


class Restaurant:
    REPORT_KEYS = [['seneste_kontrol', 'seneste_kontrol_dato'],
                   ['naestseneste_kontrol', 'naestseneste_kontrol_dato'],
                   ['tredjeseneste_kontrol', 'tredjeseneste_kontrol_dato'],
                   ['fjerdeseneste_kontrol', 'fjerdeseneste_kontrol_dato']]

    def __init__(self):
        self.cvrnr = None  # type: Optional[str]
        self.pnr = None  # type: Optional[str]
        self.region = None  # type: Optional[str]
        self.industry_code = None  # type: Optional[str]
        self.industry_text = None  # type: Optional[str]
        self.start_date = None  # type: Optional[datetime]
        self.smiley_reports = []  # type: List[SmileyReport]
        self.city = None  # type: Optional[str]
        self.elite_smiley = None  # type: Optional[str]
        self.geo_lat = None  # type: Optional[float]
        self.geo_lng = None  # type: Optional[float]
        self.niche_industry = None  # type: Optional[str]
        self.url = None  # type: Optional[str]
        self.address = None  # type: Optional[str]
        self.name = None  # type: Optional[str]
        self.name_seq_nr = None  # type: Optional[str]
        self.zip_code = None  # type: Optional[str]
        self.ad_protection = None  # type: Optional[str]
        self.company_type = None  # type: Optional[str]

    @classmethod
    def from_xml(cls, row: dict):
        self = Restaurant()

        self.cvrnr = row['cvrnr']
        self.pnr = row['pnr']
        self.region = row['region']
        self.industry_code = row['brancheKode']
        self.industry_text = row['branche']
        self.start_date = None
        self.smiley_reports = [SmileyReport.from_xml(row[x[0]], row[x[1]])
                               for x in cls.REPORT_KEYS if row[x[0]]]
        self.city = row['By']
        self.elite_smiley = row['Elite_Smiley']
        self.geo_lat = float(row['Geo_Lat']) if row['Geo_Lat'] else None
        self.geo_lng = float(row['Geo_Lng']) if row['Geo_Lng'] else None
        self.niche_industry = row['Pixibranche']
        self.url = row['URL']
        self.address = row['adresse1']
        self.name = row['navn1'].strip() if row['navn1'] else None
        self.name_seq_nr = row['navnelbnr']
        self.zip_code = row['postnr']
        self.ad_protection = row['reklame_beskyttelse']
        self.company_type = row['virksomhedstype']

        return self

    @classmethod
    def from_json(cls, row: dict):
        self = Restaurant()

        self.cvrnr = row['cvrnr']
        self.pnr = row['pnr']
        self.region = row['region']
        self.industry_code = row['industry_code']
        self.industry_text = row['industry_text']
        self.start_date = row['start_date']
        self.smiley_reports = [SmileyReport.from_json(report) for report in row['smiley_reports']]
        self.city = row['city']
        self.elite_smiley = row['elite_smiley']
        self.geo_lat = float(row['geo_lat']) if row['geo_lat'] else None
        self.geo_lng = float(row['geo_lng']) if row['geo_lng'] else None
        self.niche_industry = row['niche_industry']
        self.url = row['url']
        self.address = row['address']
        self.name = row['name'].strip() if row['name'] else None
        self.name_seq_nr = row['name_seq_nr']
        self.zip_code = row['zip_code']
        self.ad_protection = row['ad_protection']
        self.company_type = row['company_type']

        return self

    @property
    def start_date_string(self):
        return self.start_date.strftime(FilterXMLConfig.iso_fmt())

    def is_valid_production_unit(self) -> bool:
        return self.cvrnr is not None and self.pnr is not None

    def as_dict(self) -> dict:
        d = self.__dict__.copy()
        d['smiley_reports'] = [report.as_dict() for report in self.smiley_reports]
        d['start_date'] = self.start_date_string
        return d

    def has_update(self, old: Restaurant) -> bool:
        pass


class SmileyReport:

    def __init__(self):
        self.report_id = None  # type: Optional[str]
        self.smiley = None  # type: Optional[int]
        self.date = None  # type: Optional[datetime]

    @classmethod
    def from_xml(cls, smiley: int, date: str):
        self = SmileyReport()

        self.report_id = None
        self.smiley = int(smiley) if smiley else None
        self.date = datetime.strptime(date, '%d-%m-%Y %H:%M:%S')

        return self

    @classmethod
    def from_json(cls, row: dict):
        self = SmileyReport()

        self.report_id = row['report_id']
        self.smiley = int(row['smiley'])
        self.date = datetime.strptime(row['date'], FilterXMLConfig.iso_fmt())

        return self

    @property
    def date_string(self) -> str:
        return self.date.strftime(FilterXMLConfig.iso_fmt())

    def as_dict(self) -> dict:
        d = self.__dict__.copy()
        d['date'] = self.date_string
        return d


class RestaurantCatalog:

    def __init__(self):
        self.catalog = []  # type: List[Restaurant]

        # maintain the size of the catalog in add() and remove() to avoid using len()
        self.catalog_size = 0

    def add(self, restaurant: Restaurant):
        self.catalog.append(restaurant)
        self.catalog_size += 1

    def add_many(self, restaurants: list):
        self.catalog.extend(restaurants)
        self.catalog_size += len(restaurants)

    def remove(self, restaurant: Restaurant):
        pass

    def remove_many(self, restaurants: list):
        pass

    def insert_set(self) -> list:
        pass

    def update_set(self) -> list:
        pass

    def delete_set(self) -> list:
        pass
