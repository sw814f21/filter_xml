import json
import requests

class BaseDataOutputter:

    def write(self, data_to_write: dict):
        pass


class FileOutputter(BaseDataOutputter):
    def __init__(self):
        self.file_path = 'smiley_json_processed.json'
    

    def write(self, data: dict):
        with open(self.file_path, 'w') as f:
            f.write(json.dumps(data, indent=4))

class DatabaseOutputter(BaseDataOutputter):
    endpoint = 'https://127.0.0.1/admin/insert'

    def write(self, data: dict):
        r = requests.post(self.endpoint, json=data)

        if r.status_code != 200:
            print('Failed to send data to database, writing to file instead')
            FileOutputter().write(data)


def get_outputter(should_send_to_db) -> BaseDataOutputter:
    if should_send_to_db:
        return DatabaseOutputter()
    else:
        return FileOutputter()




