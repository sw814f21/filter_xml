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
    file_path = 'blacklist.csv'
    restaurants = []

    @classmethod
    def add(cls, restaurant: dict) -> None:
        seq_nr = restaurant['navnelbnr']
        cls.restaurants.append(seq_nr)

    @classmethod
    def output_to_file(cls) -> None:
        """
        Write processed restaurants to file processed_companies.csv
        """
        with open(cls.file_path, 'w+') as f:
            writer = csv.writer(f)

            for seq_nr in cls.restaurants:
                writer.writerow([seq_nr])

    @classmethod
    def read_restaurants_file(cls):
        """
        Retrieve all previously processed restaurants
        """
        try:
            with open(cls.file_path, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    cls.restaurants.append(row[0])
        except FileNotFoundError:
            return {}
