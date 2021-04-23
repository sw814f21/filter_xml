# type hinting a class within that class is not supported until python 3.10
# so we need to import future annotations to allow this
from __future__ import annotations
from typing import Optional, List
from datetime import datetime


class Restaurant:
    REPORT_KEYS = [['seneste_kontrol', 'seneste_kontrol_dato'],
                   ['naestseneste_kontrol', 'naestseneste_kontrol_dato'],
                   ['tredjeseneste_kontrol', 'tredjeseneste_kontrol_dato'],
                   ['fjerdeseneste_kontrol', 'fjerdeseneste_kontrol_dato']]

    def __init__(self, row: dict):
        self.cvrnr = row['cvrnr']  # type: Optional[str]
        self.pnr = row['pnr']  # type: Optional[str]
        self.region = row['region']  # type: Optional[str]
        self.industry_code = row['brancheKode']  # type: Optional[str]
        self.industry_text = row['branche']  # type: Optional[str]
        self.start_date = None  # type: Optional[datetime]
        self.smiley_reports = [SmileyReport(row[x[0]], row[x[1]])
                               for x in self.REPORT_KEYS]  # type: List[SmileyReport]
        self.city = row['By']  # type: Optional[str]
        self.elite_smiley = row['Elite_Smiley']  # type: Optional[str]
        self.geo_lat = float(row['Geo_Lat']) if row['Geo_Lat'] else None  # type: Optional[float]
        self.geo_lng = float(row['Geo_Lng']) if row['Geo_Lng'] else None  # type: Optional[float]
        self.niche_industry = row['Pixibranche']  # type: Optional[str]
        self.url = row['URL']  # type: Optional[str]
        self.address = row['adresse1']  # type: Optional[str]
        self.name = row['navn1'].strip() if row['navn1'] else None  # type: Optional[str]
        self.name_seq_nr = row['navnelbnr']  # type: Optional[str]
        self.zip_code = row['postnr']  # type: Optional[str]
        self.ad_protection = row['reklame_beskyttelse']  # type: Optional[str]
        self.company_type = row['virksomhedstype']  # type: Optional[str]

    def valid_production_unit(self) -> bool:
        pass

    def as_dict(self) -> dict:
        pass

    def has_update(self, old: Restaurant) -> bool:
        pass


class SmileyReport:

    def __init__(self, smiley: int, date: str):
        self.report_id = None  # type: Optional[str]
        self.smiley = int(smiley) if smiley else None  # type: Optional[int]
        self.date = datetime.strptime(date, '%d-%m-%Y %H:%M:%S')


class RestaurantCatalog:

    def __init__(self):
        self.catalog = []  # type: List[Restaurant]

    def add(self, restaurant: Restaurant):
        pass

    def remove(self, restaurant: Restaurant):
        pass

    def insert_set(self) -> list:
        pass

    def update_set(self) -> list:
        pass

    def delete_set(self) -> list:
        pass
