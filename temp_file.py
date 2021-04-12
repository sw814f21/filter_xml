import os
import csv


class TempFile:
    FILE_NAME = "temp.csv"

    def __init__(self, data_example: dict) -> None:
        file_exists = os.path.exists(self.FILE_NAME)
        read_append = 'r+' if file_exists else 'a+'

        self.__data = dict()
        self.__file = open(self.FILE_NAME, read_append)
        self.__file_writer = self.__get_file_writer(data_example)

        if(file_exists):
            self.__data = self.__read_temp_data()
        else:
            self.__file_writer.writeheader()

    def __get_file_writer(self, data_example: dict):
        fieldnames = list(data_example.keys())

        if 'pnr' not in fieldnames:
            self.close()
            raise ValueError(
                'Expected pnr field to be provided in data example')

        return csv.DictWriter(
            self.__file, fieldnames=fieldnames, extrasaction='ignore')

    def __read_temp_data(self) -> dict:
        reader = csv.DictReader(self.__file)
        out = dict()
        for entry in reader:
            out[entry['pnr']] = entry
        return out

    def add_data(self, data: dict):
        if 'pnr' not in data:
            self.close()
            raise ValueError('Expected data to have "pnr" key')

        self.__data[data['pnr']] = data
        self.__file_writer.writerow(data)
        self.__file.flush()

    def close(self):
        self.__file.close()
        os.remove(self.FILE_NAME)

    def contains(self, pnr: str) -> bool:
        return bool(self.__data.get(pnr))

    def get_all(self) -> list:
        return list(self.__data.values())
