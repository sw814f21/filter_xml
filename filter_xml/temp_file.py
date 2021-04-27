import os
import csv

from filter_xml.catalog import Restaurant, RestaurantCatalog


class TempFile:
    """
    Handler for temp.csv file.

    This file is maintained during a session, and is deleted once the session ends. This file
    ensures that we have saved progress in the case of a crash, meaning that this file is in
    charge of maintaining the state of the data collection at any given time. A session does not
    end until every row has been processed.
    """
    FILE_NAME = "temp.csv"

    def __init__(self) -> None:
        file_exists = os.path.exists(self.FILE_NAME)
        read_append = 'r+' if file_exists else 'a+'

        self.__data = dict()
        self.__file = open(self.FILE_NAME, read_append)
        self.__file_writer = None

        if file_exists:
            self.__data = self.__read_temp_data()

    def __create_file(self, data_example: dict) -> None:
        """
        Create temp file with headers from keys in provided data_example
        """
        self.__file_writer = self.__get_file_writer(data_example)
        self.__file_writer.writeheader()
        self.__file.flush()

    def __get_file_writer(self, data_example: dict) -> csv.DictWriter:
        """
        Construct file writer
        """
        fieldnames = list(data_example.keys())

        if 'name_seq_nr' not in fieldnames:
            self.close()
            raise ValueError(
                'Expected "name_seq_nr" field to be provided in data example')

        return csv.DictWriter(
            self.__file, fieldnames=fieldnames, extrasaction='ignore', delimiter=";")

    def __read_temp_data(self) -> dict:
        """
        Read temp file as a dictionary, indexed by p-number
        """
        reader = csv.DictReader(self.__file, delimiter=";")
        out = dict()
        for entry in reader:
            entry = Restaurant.from_json(entry)
            out[entry.name_seq_nr] = entry
        return out

    def add_data(self, data: Restaurant):
        """
        Write a single row to temp file and commit
        """
        if not data.name_seq_nr:
            self.close()
            raise ValueError('Expected data to have "name_seq_nr" key')

        if not self.__file_writer:
            self.__create_file(data.as_dict())

        self.__data[data.name_seq_nr] = data
        self.__file_writer.writerow(data.as_dict())
        self.__file.flush()

    def close(self) -> None:
        """
        Finish the current session by closing and deleting the file
        """
        self.__file.close()
        os.remove(self.FILE_NAME)

    def contains(self, seq_nr: str) -> bool:
        """
        Check if file contains a restaurant, searching by p-number
        """
        return bool(self.__data.get(seq_nr))

    def get_all(self) -> RestaurantCatalog:
        """
        Retrieve all restaurants in file as a list
        """
        catalog = RestaurantCatalog()
        catalog.add_many(list(self.__data.values()))
        return catalog
