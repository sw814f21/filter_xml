import csv


class PrevProcessedFile:
    FILE_NAME = "processed_pnrs.csv"

    def __init__(self) -> None:
        self.__processed_restaurants = self.__input_processed_companies()

    def get_by_pnr(self, pnr: str) -> dict:
        return self.__processed_restaurants.get(pnr)

    def delete(self, pnr: str):
        del self.__processed_restaurants[pnr]

    def __input_processed_companies(self) -> dict:
        try:
            with open(self.FILE_NAME, 'r') as f:
                reader = csv.DictReader(f)
                out = dict()
                for entry in reader:
                    out[entry['pnr']] = entry['seneste_kontrol_dato']
                return out
        except FileNotFoundError:
            return {}

    def output_processed_companies(self, restaurants: list):
        with open(self.FILE_NAME, 'w+') as f:
            fieldnames = ['pnr', 'seneste_kontrol_dato']
            writer = csv.DictWriter(
                f, fieldnames=fieldnames, extrasaction='ignore')

            writer.writeheader()

            for restaurant in restaurants:
                writer.writerow(restaurant)

            for pnr, control_date in self.__processed_restaurants.items():
                writer.writerow(
                    {'pnr': pnr, 'seneste_kontrol_dato': control_date})
