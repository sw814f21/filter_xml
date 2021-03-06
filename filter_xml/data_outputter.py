import json
import requests
from requests.exceptions import ConnectionError
from typing import Union
from filter_xml.catalog import RestaurantCatalog, Restaurant
from filter_xml.config import FilterXMLConfig


class _BaseDataOutputter:
    """
        An abstract class that is used to define different output strategies
    """

    def get(self) -> RestaurantCatalog:
        """
        Abstract implementation of method for retrieving a list of all restaurants

        Should be overridden in inherited classes
        """
        raise NotImplementedError('Method called on base class; use inherited')

    def insert(self, data: Union[dict, list], token: str) -> None:
        """
        Abstract implementation of method for sending a list of restaurants that should be
        inserted to the API

        :param data: a list of restaurants or a single restaurant
        :param token: an identifier for the current session, to ensure that separate
                      POST / PUT / DELETE requests are recognized as a single version of data

        Should be overridden in inherited classes
        """
        raise NotImplementedError('Method called on base class; use inherited')

    def update(self, data: Union[dict, list], token: str) -> None:
        """
        Abstract implementation of method for sending a list of restaurants that should be
        updated to the API

        :param data: a list of restaurants or a single restaurant
        :param token: an identifier for the current session, to ensure that separate
                      POST / PUT / DELETE requests are recognized as a single version of data

        Should be overridden in inherited classes
        """
        raise NotImplementedError('Method called on base class; use inherited')

    def delete(self, data: Union[dict, list], token: str) -> None:
        """
        Abstract implementation of method for sending a list of restaurants that should be
        deleted to the API

        :param data: a list of restaurants or a single restaurant
        :param token: an identifier for the current session, to ensure that separate
                      POST / PUT / DELETE requests are recognized as a single version of data

        Should be overridden in inherited classes
        """
        raise NotImplementedError('Method called on base class; use inherited')


class FileOutputter(_BaseDataOutputter):
    FILE_BASE = 'smiley_json_processed_'

    def get(self) -> RestaurantCatalog:
        """
        Retrieve sample restaurants from file
        """
        return DatabaseOutputter().get()

    def insert(self, data: Union[dict, list], token: str) -> None:
        """
        Output restaurants marked as insert to smiley_json_processed_PUT.json

        :param data: a list of restaurants or a single restaurant
        :param token: an identifier for the current session, to ensure that separate
                      POST / PUT / DELETE requests are recognized as a single version of data
        """
        put_data = {
            'timestamp': token,
            'data': data
        }
        with open(f'{self.FILE_BASE}insert.json', 'w') as f:
            f.write(json.dumps(put_data, indent=4))

    def update(self, data: Union[dict, list], token: str) -> None:
        """
        Output restaurants marked as update to smiley_json_processed_POST.json

        :param data: a list of restaurants or a single restaurant
        :param token: an identifier for the current session, to ensure that separate
                      POST / PUT / DELETE requests are recognized as a single version of data
        """
        post_data = {
            'timestamp': token,
            'data': data
        }
        with open(f'{self.FILE_BASE}update.json', 'w') as f:
            f.write(json.dumps(post_data, indent=4))

    def delete(self, data: Union[dict, list], token: str) -> None:
        """
        Output restaurants marked as delete to smiley_json_processed_DELETE.json

        :param data: a list of restaurants or a single restaurant
        :param token: an identifier for the current session, to ensure that separate
                      POST / PUT / DELETE requests are recognized as a single version of data
        """
        delete_data = {
            'timestamp': token,
            'data': data
        }
        with open(f'{self.FILE_BASE}delete.json', 'w') as f:
            f.write(json.dumps(delete_data, indent=4))


class DatabaseOutputter(_BaseDataOutputter):
    ENDPOINT = FilterXMLConfig.data_endpoint()

    def get(self) -> RestaurantCatalog:
        """
        Retrieve all current restaurants from the API
        """
        catalog = RestaurantCatalog()
        try:
            res = requests.get(self.ENDPOINT, timeout=4)
            if res.status_code == 200:
                catalog.add_many([Restaurant.from_json(row)
                                  for row in res.json()])
        except ConnectionError:
            print('Failed to connect to API')
        return catalog

    def insert(self, data: Union[dict, list], token: str) -> None:
        """
        Send restaurants marked as insert to API

        :param data: a list of restaurants or a single restaurant
        :param token: an identifier for the current session, to ensure that separate
                      POST / PUT / DELETE requests are recognized as a single version of data
        """
        if len(data) == 0:
            return

        put_data = {
            'timestamp': token,
            'data': data
        }
        res = requests.post(self.ENDPOINT, json=put_data)

        if res.status_code != 200:
            print('Failed to send insert data to database, writing to file instead')
            FileOutputter().insert(data, token)

    def update(self, data: Union[dict, list], token: str) -> None:
        """
        Send restaurants marked as update to API

        :param data: a list of restaurants or a single restaurant
        :param token: an identifier for the current session, to ensure that separate
                      POST / PUT / DELETE requests are recognized as a single version of data
        """
        if len(data) == 0:
            return

        post_data = {
            'timestamp': token,
            'data': data
        }
        res = requests.put(self.ENDPOINT, json=post_data)

        if res.status_code != 200:
            print('Failed to send update data to database, writing to file instead')
            FileOutputter().update(data, token)

    def delete(self, data: Union[dict, list], token: str) -> None:
        """
        Send restaurants marked as delete to API

        :param data: a list of restaurants or a single restaurant
        :param token: an identifier for the current session, to ensure that separate
                      POST / PUT / DELETE requests are recognized as a single version of data
        """
        if len(data) == 0:
            return

        delete_data = {
            'timestamp': token,
            'data': data
        }
        res = requests.delete(self.ENDPOINT, json=delete_data)

        if res.status_code != 200:
            print('Failed to send delete data to database, writing to file instead')
            FileOutputter().delete(data, token)


def get_outputter(should_send_to_db: bool) -> _BaseDataOutputter:
    """
        A helper method used to pick which outputter should be used
    """
    if should_send_to_db:
        return DatabaseOutputter()
    else:
        return FileOutputter()
