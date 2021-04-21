import json
import requests


class BaseDataOutputter:
    """
        An abstract class that is used to define different output strategies
    """

    def write(self, data_to_write: dict) -> None:
        """
            An abstract method that takes in some data that should be outputtet as a dictionary

            Different implementations will then save this data in different places
        """
        pass


class FileOutputter(BaseDataOutputter):
    def __init__(self):
        self.file_path = 'smiley_json_processed.json'

    def write(self, data_to_write: dict) -> None:
        """
            An overwritten method that saves the data to a file
        """
        with open(self.file_path, 'w') as f:
            f.write(json.dumps(data_to_write, indent=4))


class DatabaseOutputter(BaseDataOutputter):
    endpoint = 'https://127.0.0.1/admin/insert'

    def write(self, data: dict) -> None:
        """
            An overwritten method that pipes that data to an api endpoint
        """
        r = requests.post(self.endpoint, json=data)

        if r.status_code != 200:
            print('Failed to send data to database, writing to file instead')
            FileOutputter().write(data)


def get_outputter(should_send_to_db) -> BaseDataOutputter:
    """
        A helper method used to pick which outputter should be used
    """
    if should_send_to_db:
        return DatabaseOutputter()
    else:
        return FileOutputter()
