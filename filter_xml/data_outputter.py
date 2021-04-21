import json
import requests
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

    def insert(self, data: Union[dict, list], token: int) -> None:
        """
        Abstract implementation of method for sending a list of restaurants that should be
        inserted to the API

        :param data: a list of restaurants or a single restaurant
        :param token: an identifier for the current session, to ensure that separate
                      POST / PUT / DELETE requests are recognized as a single version of data

        Should be overridden in inherited classes
        """
        raise NotImplementedError('Method called on base class; use inherited')

    def update(self, data: Union[dict, list], token: int) -> None:
        """
        Abstract implementation of method for sending a list of restaurants that should be
        updated to the API

        :param data: a list of restaurants or a single restaurant
        :param token: an identifier for the current session, to ensure that separate
                      POST / PUT / DELETE requests are recognized as a single version of data

        Should be overridden in inherited classes
        """
        raise NotImplementedError('Method called on base class; use inherited')

    def delete(self, data: Union[dict, list], token: int) -> None:
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
    def __init__(self):
        self.file_path = 'smiley_json_processed.json'

    def write(self, data_to_write: Union[dict, list]) -> None:
        """
            An overwritten method that saves the data to a file
        """
        with open(self.file_path, 'w') as f:
            f.write(json.dumps(data_to_write, indent=4))


class DatabaseOutputter(_BaseDataOutputter):
    endpoint = 'https://127.0.0.1/admin/insert'

    def write(self, data: Union[dict, list]) -> None:
        """
            An overwritten method that pipes that data to an api endpoint
        """
        r = requests.post(self.endpoint, json=data)

        if r.status_code != 200:
            print('Failed to send data to database, writing to file instead')
            FileOutputter().write(data)


def get_outputter(should_send_to_db: bool) -> _BaseDataOutputter:
    """
        A helper method used to pick which outputter should be used
    """
    if should_send_to_db:
        return DatabaseOutputter()
    else:
        return FileOutputter()
