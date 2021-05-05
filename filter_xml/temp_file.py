import os
import json

from filter_xml.catalog import Restaurant, RestaurantCatalog


class TempFile:
    """
    Handler for temp.json file.

    This file is maintained during a session, and is deleted once the session ends. This file
    ensures that we have saved progress in the case of a crash, meaning that this file is in
    charge of maintaining the state of the data collection at any given time. A session does not
    end until every row has been processed.
    """
    FILE_NAME = "temp.json"

    def __init__(self) -> None:
        file_exists = os.path.exists(self.FILE_NAME)

        self.__data = dict()

        if file_exists:
            self.__data = self.__read_temp_data()

    def __read_temp_data(self) -> dict:
        """
        Read temp file as a dictionary, indexed by p-number
        """

        out = dict()

        with open(self.FILE_NAME) as json_file:
            data = json.load(json_file)
            
            for entry in data:
                restaurant = Restaurant.from_json(entry)
                out[restaurant.name_seq_nr] = restaurant

        return out


    def add_data(self, data: Restaurant):
        """
        Write a single row to temp file and commit
        """
        if not data.name_seq_nr:
            raise ValueError('Expected data to have "name_seq_nr" key')

        self.__data[data.name_seq_nr] = data

        data_to_dump = []
        for restaurant in self.__data.values():
            data_to_dump.append(restaurant.as_dict())
        
        self._write_json(data_to_dump)

    def _write_json(self, data: list):
        with open(self.FILE_NAME, 'w') as json_file:
            json.dump(data, json_file)

    def close(self) -> None:
        """
        Finish the current session by closing and deleting the file
        """
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
