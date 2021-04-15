import csv

from datetime import datetime


class PrevProcessedFile:
    """
    Handler for processed_companies.csv file.

    In this file every restaurant that has been previously processed is maintained. That is,
    every restaurant for which we have already collected external CVR data. The file is updated
    after every ended session.
    """

    def __init__(self, file_path) -> None:
        self.file_path = file_path
        self.__processed_restaurants = self.__input_processed_companies()

    def get_control_date_by_seq_nr(self, seq_nr: str) -> dict:
        """
        Retrieve the latest control date in the previous processed file, indexed by sequence number
        """
        return self.__processed_restaurants.get(seq_nr)

    def output_processed_companies(self, restaurants: list) -> None:
        """
        Write list of restaurant dicts to file processed_companies.csv
        """
        with open(self.file_path, 'w+') as f:
            fieldnames = ['navnelbnr', 'seneste_kontrol_dato']
            writer = csv.DictWriter(
                f, fieldnames=fieldnames, extrasaction='ignore')

            writer.writeheader()

            for restaurant in restaurants:
                writer.writerow(restaurant)

            for seq_nr, control_date in self.__processed_restaurants.items():
                writer.writerow(
                    {'navnelbnr': seq_nr, 'seneste_kontrol_dato': control_date})

    def should_process_restaurant(self, restaurant: dict) -> bool:
        """
        Check whether or not a restaurant should be processed.
        Returns True if:
            the restaurant does not exist in the file, or
            the restaurant has received a new check up since last time it was processed
        """
        seq_nr = restaurant['navnelbnr']
        control_date = restaurant['seneste_kontrol_dato']
        prev_processed_restaurant_date = self.get_control_date_by_seq_nr(
            seq_nr)
        if prev_processed_restaurant_date:
            if self.__is_control_newer(control_date,
                                       prev_processed_restaurant_date):
                self.__delete(seq_nr)
                return True
            else:
                return False
        return True

    @staticmethod
    def __is_control_newer(new_date_str: str, previous_date_str: str) -> bool:
        """
        Check if new_date is different from our stored date.
        """
        date_format = '%d-%m-%Y %H:%M:%S'
        new_date = datetime.strptime(new_date_str, date_format)
        previous_date = datetime.strptime(previous_date_str, date_format)
        return new_date > previous_date

    def __delete(self, seq_nr: str) -> None:
        """
        Delete a single restaurant, indexed by sequence number.
        """
        del self.__processed_restaurants[seq_nr]

    def __input_processed_companies(self) -> dict:
        """
        Retrieve all previously processed restaurants
        """
        try:
            with open(self.file_path, 'r') as f:
                reader = csv.DictReader(f)
                out = dict()
                for entry in reader:
                    out[entry['navnelbnr']] = entry['seneste_kontrol_dato']
                return out
        except FileNotFoundError:
            return {}
