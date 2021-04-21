import json
import requests
from requests.exceptions import ConnectionError
from typing import Union


class _BaseDataOutputter:
    """
        An abstract class that is used to define different output strategies
    """

    def get(self) -> list:
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

    def get(self) -> list:
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
        with open(f'{self.FILE_BASE}insert.json', 'w') as f:
            f.write(json.dumps(data, indent=4))

    def update(self, data: Union[dict, list], token: str) -> None:
        """
        Output restaurants marked as update to smiley_json_processed_POST.json

        :param data: a list of restaurants or a single restaurant
        :param token: an identifier for the current session, to ensure that separate
                      POST / PUT / DELETE requests are recognized as a single version of data
        """
        with open(f'{self.FILE_BASE}update.json', 'w') as f:
            f.write(json.dumps(data, indent=4))

    def delete(self, data: Union[dict, list], token: str) -> None:
        """
        Output restaurants marked as delete to smiley_json_processed_DELETE.json

        :param data: a list of restaurants or a single restaurant
        :param token: an identifier for the current session, to ensure that separate
                      POST / PUT / DELETE requests are recognized as a single version of data
        """
        with open(f'{self.FILE_BASE}delete.json', 'w') as f:
            f.write(json.dumps(data, indent=4))


class DatabaseOutputter(_BaseDataOutputter):
    ENDPOINT = 'https://127.0.0.1/admin/load'

    def get(self) -> list:
        """
        Retrieve all current restaurants from the API
        """
        try:
            res = requests.get(self.ENDPOINT, timeout=4)
            if res.status_code == 200:
                return json.loads(res.content.decode('utf-8'))
        except ConnectionError:
            print('Failed to connect to API')
        return []

    def insert(self, data: Union[dict, list], token: str) -> None:
        """
        Send restaurants marked as insert to API

        :param data: a list of restaurants or a single restaurant
        :param token: an identifier for the current session, to ensure that separate
                      POST / PUT / DELETE requests are recognized as a single version of data
        """
        put_data = {
            'timestamp': token,
            'data': data
        }
        res = requests.put(self.ENDPOINT, data=put_data)

        if res.status_code != 200:
            print('Failed to send data to database, writing to file instead')
            FileOutputter().insert(data, token)

    def update(self, data: Union[dict, list], token: str) -> None:
        """
        Send restaurants marked as update to API

        :param data: a list of restaurants or a single restaurant
        :param token: an identifier for the current session, to ensure that separate
                      POST / PUT / DELETE requests are recognized as a single version of data
        """
        post_data = {
            'timestamp': token,
            'data': data
        }
        res = requests.post(self.ENDPOINT, data=post_data)

        if res.status_code != 200:
            print('Failed to send data to database, writing to file instead')
            FileOutputter().update(data, token)

    def delete(self, data: Union[dict, list], token: str) -> None:
        """
        Send restaurants marked as delete to API

        :param data: a list of restaurants or a single restaurant
        :param token: an identifier for the current session, to ensure that separate
                      POST / PUT / DELETE requests are recognized as a single version of data
        """
        delete_data = {
            'timestamp': token,
            'data': data
        }
        res = requests.delete(self.ENDPOINT, data=delete_data)

        if res.status_code != 200:
            print('Failed to send data to database, writing to file instead')
            FileOutputter().delete(data, token)


def get_outputter(should_send_to_db: bool) -> _BaseDataOutputter:
    """
        A helper method used to pick which outputter should be used
    """
    if should_send_to_db:
        return DatabaseOutputter()
    else:
        return FileOutputter()
