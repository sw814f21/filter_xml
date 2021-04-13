import csv
from datetime import datetime


class PrevProcessedFile:
    def __init__(self, file_path) -> None:
        self.file_path = file_path
        self.__processed_restaurants = self.__input_processed_companies()

    def get_by_pnr(self, pnr: str) -> dict:
        return self.__processed_restaurants.get(pnr)

    def output_processed_companies(self, restaurants: list):
        with open(self.file_path, 'w+') as f:
            fieldnames = ['pnr', 'seneste_kontrol_dato']
            writer = csv.DictWriter(
                f, fieldnames=fieldnames, extrasaction='ignore')

            writer.writeheader()

            for restaurant in restaurants:
                writer.writerow(restaurant)

            for pnr, control_date in self.__processed_restaurants.items():
                writer.writerow(
                    {'pnr': pnr, 'seneste_kontrol_dato': control_date})

    def should_process_restaurant(self, pnr: str, control_date: str):
        prev_processed_restaurant = self.get_by_pnr(pnr)
        if prev_processed_restaurant:
            if self.__is_control_newer(control_date, prev_processed_restaurant):
                self.__delete(pnr)
                return True
            else:
                return False
        return True

    def __is_control_newer(self, new_date_str: str, previous_date_str: str) -> bool:
        date_format = '%d-%m-%Y %H:%M:%S'
        new_date = datetime.strptime(new_date_str, date_format)
        previous_date = datetime.strptime(previous_date_str, date_format)
        return new_date > previous_date

    def __delete(self, pnr: str):
        del self.__processed_restaurants[pnr]

    def __input_processed_companies(self) -> dict:
        try:
            with open(self.file_path, 'r') as f:
                reader = csv.DictReader(f)
                out = dict()
                for entry in reader:
                    out[entry['pnr']] = entry['seneste_kontrol_dato']
                return out
        except FileNotFoundError:
            return {}
