from filter_xml.prev_processed_file import PrevProcessedFile
from filter_xml.catalog import Restaurant, SmileyReport
import unittest
import os

FILENAME = 'processed_companies_test.csv'


class PrevProcessedFileTest(unittest.TestCase):

    @classmethod
    def tearDownClass(cls) -> None:
        if os.path.exists(FILENAME):
            os.remove(FILENAME)

    def setUp(self) -> None:
        if os.path.exists(FILENAME):
            os.remove(FILENAME)

    def test_get_control_date_by_seq_nr_returns_correct_date(self):
        seq_nr = '123'
        date = '01-01-2001 00:00:00'
        self.create_file_with_data(seq_nr, date)

        processed_file = PrevProcessedFile(FILENAME)

        self.assertEqual(
            processed_file.get_control_date_by_seq_nr(seq_nr), '2001-01-01T00:00:00Z')

    def test_should_not_process_restaurant_with_no_changes(self):
        seq_nr = '123'
        date = '01-01-2001 00:00:00'
        self.create_file_with_data(seq_nr, date)
        res = Restaurant()
        res.name_seq_nr = '123'
        res.smiley_reports = [SmileyReport.from_xml('1', '01-01-2001 00:00:00')]

        processed_file = PrevProcessedFile(FILENAME)
        should_process = processed_file.should_process_restaurant(res)

        self.assertFalse(should_process)

    def test_should_process_new_restaurant(self):
        self.create_file_with_data()
        res = Restaurant()
        res.name_seq_nr = '555'
        res.smiley_reports = [SmileyReport.from_xml('1', '01-01-2001 00:00:00')]

        processed_file = PrevProcessedFile(FILENAME)
        should_process = processed_file.should_process_restaurant(res)

        self.assertTrue(should_process)

    def test_should_process_restaurant_with_new_date(self):
        seq_nr = '123'
        self.create_file_with_data(seq_nr, '01-01-2001 00:00:00')
        res = Restaurant()
        res.name_seq_nr = seq_nr
        res.smiley_reports = [SmileyReport.from_xml('1', '01-02-2001 00:00:00')]

        processed_file = PrevProcessedFile(FILENAME)
        should_process = processed_file.should_process_restaurant(res)

        self.assertTrue(should_process)

    def test_date_in_file_gets_updated(self):
        seq_nr = '123'
        self.create_file_with_data(seq_nr, '01-01-2001 00:00:00')
        new_res = Restaurant()
        new_res.name_seq_nr = seq_nr
        new_res.smiley_reports = [SmileyReport.from_xml('1', '01-02-2001 00:00:00')]

        processed_file = PrevProcessedFile(FILENAME)
        processed_file.should_process_restaurant(new_res)
        processed_file.add_list([new_res])
        processed_file.output_processed_companies()
        processed_file = PrevProcessedFile(FILENAME)

        self.assertEqual(
            processed_file.get_control_date_by_seq_nr(seq_nr), '2001-02-01T00:00:00Z')

    def test_old_entry_is_deleted_when_new_control_date(self):
        seq_nr = '123'
        self.create_file_with_data(seq_nr, '01-01-2001 00:00:00')
        new_res = Restaurant()
        new_res.name_seq_nr = seq_nr
        new_res.smiley_reports = [SmileyReport.from_xml('1', '01-02-2001 00:00:00')]

        processed_file = PrevProcessedFile(FILENAME)
        processed_file.should_process_restaurant(new_res)
        processed_file.output_processed_companies()
        processed_file = PrevProcessedFile(FILENAME)

        self.assertEqual(
            processed_file.get_control_date_by_seq_nr(seq_nr), None)

    def test_error_when_adding_restaurant_without_control_date(self):
        restaurant = Restaurant()
        restaurant.name_seq_nr = '1111'
        processed_file = PrevProcessedFile(FILENAME)

        with self.assertRaises(IndexError):
            processed_file.add_list([restaurant])

    def create_file_with_data(self, seq_nr='123', date='01-01-2001 00:00:00'):
        restaurant1 = Restaurant()
        restaurant1.name_seq_nr = '11111'
        restaurant1.smiley_reports = [SmileyReport.from_xml('1', '02-02-2002 00:00:00')]

        restaurant2 = Restaurant()
        restaurant2.name_seq_nr = seq_nr
        restaurant2.smiley_reports = [SmileyReport.from_xml('1', date)]

        restaurant3 = Restaurant()
        restaurant3.name_seq_nr = '22222'
        restaurant3.smiley_reports = [SmileyReport.from_xml('1', '03-03-2003 00:00:00')]

        processed_file = PrevProcessedFile(FILENAME)
        processed_file.add_list([restaurant1, restaurant2, restaurant3])
        processed_file.output_processed_companies()
