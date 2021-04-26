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
    _file_writer = None
    _file = None

    @classmethod
    def add(cls, restaurant: dict) -> None:
        """
        Add a resturant to the blacklist and write it to the file
        """
        seq_nr = restaurant['navnelbnr']
        cls._write_to_file(seq_nr)

    @classmethod
    def contains(cls, seq_nr):
        """
        Check if blacklist contains entry with given sequence number
        """
        if not cls._restaurants:
            cls._read_restaurants_file()
        return seq_nr in cls._restaurants

    @classmethod
    def close_file(cls):
        """
        Close the blacklist file
        """
        cls._file.close()

    @classmethod
    def _write_to_file(cls, seq_nr):
        if not cls._file_writer:
            cls._file = open(cls._file_path, 'a+')
            cls._file_writer = csv.writer(cls._file)
        
        cls._file_writer.writerow([seq_nr])
        cls._file.flush()

    @classmethod
    def _read_restaurants_file(cls):
        """
        Retrieve all blacklisted restaurants from the blacklist file
        """
        try:
            with open(cls._file_path, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    cls._restaurants.append(row[0])
        except FileNotFoundError:
            return {}
