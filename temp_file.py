import os
import csv


class TempFile:
    def __init__(self, data_example: dict) -> None:
        file_exists = os.path.exists('temp.csv')
        read_append = 'r+' if file_exists else 'a+'

        self.__data = dict()
        self.__file = open('temp.csv', read_append)
        self.__file_writer = self.get_file_writer(data_example)

        if(file_exists):
            self.__data = self.read_temp_data()
        else:
            self.__file_writer.writeheader()

    def get_file_writer(self, data_example: dict):
        fieldnames = list(data_example.keys())
        return csv.DictWriter(
            self.__file, fieldnames=fieldnames, extrasaction='ignore')

    def read_temp_data(self) -> dict:
        reader = csv.DictReader(self.__file)
        out = dict()
        for entry in reader:
            out[entry['pnr']] = entry
        return out

    def add_data(self, data: dict):
        self.__data[data['pnr']] = data
        self.__file_writer.writerow(data)
        self.__file.flush()

    def close(self):
        self.__file.close()

    def contains(self, pnr: str) -> bool:
        return bool(self.__data.get(pnr))

    def get_all(self) -> list:
        return self.__data.values()
