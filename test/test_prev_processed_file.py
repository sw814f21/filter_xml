from prev_processed_file import PrevProcessedFile
import unittest
import os

FILENAME = 'processed_pnrs_test.csv'


class PrevProcessedFileTest(unittest.TestCase):

    @classmethod
    def tearDownClass(cls) -> None:
        if os.path.exists(FILENAME):
            os.remove(FILENAME)

    def setUp(self) -> None:
        if os.path.exists(FILENAME):
            os.remove(FILENAME)

    def test_get_by_pnr_returns_correct_date(self):
        pnr = '123'
        date = '01-01-2001 00:00:00'
        self.create_file_with_data(pnr, date)

        processed_file = PrevProcessedFile(FILENAME)

        self.assertEqual(processed_file.get_by_pnr(pnr), date)

    def test_should_not_process_restaurant_with_no_changes(self):
        pnr = '123'
        date = '01-01-2001 00:00:00'
        self.create_file_with_data(pnr, date)

        processed_file = PrevProcessedFile(FILENAME)
        should_process = processed_file.should_process_restaurant(pnr, date)

        self.assertFalse(should_process)

    def test_should_process_new_restaurant(self):
        self.create_file_with_data()

        processed_file = PrevProcessedFile(FILENAME)
        should_process = processed_file.should_process_restaurant(
            '555', '01-01-2001 00:00:00')

        self.assertTrue(should_process)

    def test_should_process_restaurant_with_new_date(self):
        pnr = '123'
        self.create_file_with_data(pnr, '01-01-2001 00:00:00')

        processed_file = PrevProcessedFile(FILENAME)
        should_process = processed_file.should_process_restaurant(
            pnr, '01-02-2001 00:00:00')

        self.assertTrue(should_process)

    def test_date_in_file_gets_updated(self):
        pnr = '123'
        new_date = '01-02-2001 00:00:00'
        self.create_file_with_data(pnr, '01-01-2001 00:00:00')

        processed_file = PrevProcessedFile(FILENAME)
        processed_file.should_process_restaurant(
            pnr, new_date)
        processed_file.output_processed_companies([])
        processed_file = PrevProcessedFile(FILENAME)

        self.assertEqual(processed_file.get_by_pnr(pnr), new_date)

    def create_file_with_data(self, pnr='123', date='01-01-2001 00:00:00'):
        restaurant1 = {'pnr': '11111',
                       'seneste_kontrol_dato': '02-02-2002 00:00:00'}
        restaurant2 = {'pnr': pnr,
                       'seneste_kontrol_dato': date}
        restaurant3 = {'pnr': '22222',
                       'seneste_kontrol_dato': '03-03-2003 00:00:00'}

        processed_file = PrevProcessedFile(FILENAME)
        processed_file.output_processed_companies(
            [restaurant1, restaurant2, restaurant3])