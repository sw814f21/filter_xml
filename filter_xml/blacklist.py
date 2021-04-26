import csv

from datetime import datetime
from typing import List
from filter_xml.config import FilterXMLConfig


class Blacklist:
    """
    Handler for processed_companies.csv file.

    In this file every restaurant that has been previously processed is maintained. That is,
    every restaurant for which we have already collected external CVR data. The file is updated
    after every ended session.
    """
    _file_path = 'blacklist.csv'
    _restaurants = []

    @classmethod
    def add(cls, restaurant: dict) -> None:
        seq_nr = restaurant['navnelbnr']
        cls._restaurants.append(seq_nr)

    @classmethod
    def output_to_file(cls) -> None:
        """
        Write processed restaurants to file processed_companies.csv
        """
        with open(cls._file_path, 'w+') as f:
            writer = csv.writer(f)

            for seq_nr in cls._restaurants:
                writer.writerow([seq_nr])

    @classmethod
    def read_restaurants_file(cls):
        """
        Retrieve all previously processed restaurants
        """
        try:
            with open(cls._file_path, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    cls._restaurants.append(row[0])
        except FileNotFoundError:
            return {}

    @classmethod
    def contains(cls, seq_nr):
        """
        Check if blacklist contains entry with given sequence number
        """
        return seq_nr in cls._restaurants
