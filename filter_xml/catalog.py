# type hinting a class within that class is not supported until python 3.10
# so we need to import future annotations to allow this
# note that __future__ imports must be the first line of the file
from __future__ import annotations
import json

from typing import Optional, List, Set, Dict
from datetime import datetime

from filter_xml.config import FilterXMLConfig


class Restaurant:
    """
    A class representing a single row of the smiley data
    """
    REPORT_KEYS = [['seneste_kontrol', 'seneste_kontrol_dato'],
                   ['naestseneste_kontrol', 'naestseneste_kontrol_dato'],
                   ['tredjeseneste_kontrol', 'tredjeseneste_kontrol_dato'],
                   ['fjerdeseneste_kontrol', 'fjerdeseneste_kontrol_dato']]

    COMP_KEYS = ['cvrnr', 'pnr', 'region', 'industry_code', 'industry_text', 'start_date',
                 'city', 'elite_smiley', 'geo_lat', 'geo_lng', 'franchise_name',
                 'niche_industry', 'url', 'address', 'name', 'zip_code', 'ad_protection',
                 'company_type']

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
        self.franchise_name = None  # type: Optional[str]

    def __eq__(self, other: Restaurant) -> bool:
        """
        Overridden equals operator (applies to == and !=). Will short circuit if one member
        of self is not equal to the same member of :param other. The same applies to any given
        element of the list Restaurant.smiley_reports, rather than the full list.
        """
        for k in self.COMP_KEYS:
            if getattr(self, k) != getattr(other, k):
                return False

            for new, old in zip(self.smiley_reports, other.smiley_reports):
                if new != old:
                    return False
        return True

    @classmethod
    def from_xml(cls, row: dict) -> Restaurant:
        """
        Constructs a single Restaurant object

        Expects a dict as defined by:
            https://github.com/sw814f21/filter_xml#after-json-conversion-before-further-processing
        """
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
        self.franchise_name = row['Kaedenavn']

        return self

    @classmethod
    def from_json(cls, row: dict) -> Restaurant:
        """
        Constructs a single Restaurant object

        Expects a dict as as defined by:
            https://github.com/sw814f21/filter_xml#final-output
        """
        self = Restaurant()

        self.cvrnr = row['cvrnr']
        self.pnr = row['pnr']
        self.region = row['region']
        self.industry_code = row['industry_code']
        self.industry_text = row['industry_text']
        self.start_date = datetime.strptime(row['start_date'], FilterXMLConfig.iso_fmt())
        self.smiley_reports = [SmileyReport.from_json(report)
                               for report in row['smiley_reports']]
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
        self.franchise_name = row['franchise_name']

        return self

    @property
    def start_date_string(self) -> str:
        """
        ISO-8601 formatted start date string property
        """
        return self.start_date.strftime(FilterXMLConfig.iso_fmt()) if self.start_date else ''

    def is_valid_production_unit(self) -> bool:
        """
        Determines whether or not this Restaurant is a valid production unit by ensuring that
        both CVR- and P-numbers exist
        """
        return self.cvrnr is not None and self.pnr is not None

    def as_dict(self) -> dict:
        """
        Formats object as a dict
        """
        d = self.__dict__.copy()
        d['smiley_reports'] = [report.as_dict() for report in self.smiley_reports]
        d['start_date'] = self.start_date_string
        return d

    def has_update(self, old: Restaurant) -> bool:
        """
        Compares self with :param old. Checks whether or not self has been updated in accordance
        to :param old
        """
        return self != old


class SmileyReport:
    """
    A class representing a single smiley report for a given restaurant
    """
    COMP_KEYS = ['report_id', 'smiley', 'date']

    def __init__(self):
        self.report_id = None  # type: Optional[str]
        self.smiley = None  # type: Optional[int]
        self.date = None  # type: Optional[datetime]

    def __eq__(self, other: SmileyReport) -> bool:
        """
        Overridden equals operator (applies to == and !=). Will short circuit if one member of self
        is not equal to :param other
        """
        for k in self.COMP_KEYS:
            if getattr(self, k) != getattr(other, k):
                return False
        return True

    @classmethod
    def from_xml(cls, smiley: str, date: str) -> SmileyReport:
        """
        Constructs a single SmileyReport object.

        Expects a smiley identifier and a date string as defined by the *_kontrol* fields in:
            https://github.com/sw814f21/filter_xml#after-json-conversion-before-further-processing
        """
        self = SmileyReport()

        self.report_id = None
        self.smiley = int(smiley) if smiley else None
        self.date = datetime.strptime(date, '%d-%m-%Y %H:%M:%S')

        return self

    @classmethod
    def from_json(cls, row: dict) -> SmileyReport:
        """
        Constructs a single SmileyReport object.

        Expects a dict as defined by a row in the smiley_reports list in:
            https://github.com/sw814f21/filter_xml#final-output
        """
        self = SmileyReport()

        self.report_id = row['report_id']
        self.smiley = int(row['smiley'])
        self.date = datetime.strptime(row['date'], FilterXMLConfig.iso_fmt())

        return self

    @property
    def date_string(self) -> str:
        """
        ISO-8601 formatted date string property
        """
        return self.date.strftime(FilterXMLConfig.iso_fmt())

    def as_dict(self) -> dict:
        """
        Formats object as a dict
        """
        d = self.__dict__.copy()
        d['date'] = self.date_string
        return d


class RestaurantCatalog:
    """
    A class representing a catalog of Restaurant objects
    """

    def __init__(self):
        self.catalog = []  # type: List[Restaurant]

        # maintain the size of the catalog in add() and remove() to avoid using len()
        self.catalog_size = 0

        # these should only be properly assigned in self.setup_diff()
        self.old_ids = set()  # type: Set[str]
        self.old_by_key = dict()  # type: Dict[str, Restaurant]
        self.new_ids = set()  # type: Set[str]
        self.new_by_key = dict()  # type: Dict[str, Restaurant]

    def add(self, restaurant: Restaurant) -> None:
        """
        Add a single restaurant to catalog and increment size
        """
        self.catalog.append(restaurant)
        self.catalog_size += 1

    def add_many(self, restaurants: list) -> None:
        """
        Add a list of restaurants to catalog and increase size
        """
        self.catalog.extend(restaurants)
        self.catalog_size += len(restaurants)

    def setup_diff(self, current_db: RestaurantCatalog) -> None:
        """
        Basic setup for calculating diffs.
        We could set the current database state (self.old_*) in __init__() and maintain the new
        state (self.new_*) in add() and add_many(), but we don't to avoid memory bloat - we use
        RestaurantCatalog both for the new data and for maintaining the result of the current run,
        and we only need to calculate the diff on the result.
        """
        self.new_by_key = {res.name_seq_nr: res for res in self.catalog}
        self.new_ids = set(self.new_by_key.keys())
        self.old_by_key = {res.name_seq_nr: res for res in current_db.catalog}
        self.old_ids = set(self.old_by_key.keys())

    def insert_set(self) -> list:
        """
        Construct the insert set using
            new_set \ old_set
        """
        return [self.new_by_key[x].as_dict() for x in self.new_ids.difference(self.old_ids)]

    def update_set(self) -> list:
        """
        Construct the update candidates using
            new_set ∩ old_set
        and collecting rows that have been updated by comparing them to their old counterparts
        """
        return [self.new_by_key[x].as_dict() for x in self.new_ids.intersection(self.old_ids)
                if self.new_by_key[x] != self.old_by_key[x]]

    def delete_set(self) -> list:
        """
        Construct the delete set using
            old_set \ new_set
        """
        return list(self.old_ids.difference(self.new_ids))
