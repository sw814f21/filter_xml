from prev_processed_file import PrevProcessedFile
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
            processed_file.get_control_date_by_seq_nr(seq_nr), date)

    def test_should_not_process_restaurant_with_no_changes(self):
        seq_nr = '123'
        date = '01-01-2001 00:00:00'
        self.create_file_with_data(seq_nr, date)

        processed_file = PrevProcessedFile(FILENAME)
        should_process = processed_file.should_process_restaurant(
            {'navnelbnr': seq_nr, 'seneste_kontrol_dato': date})

        self.assertFalse(should_process)

    def test_should_process_new_restaurant(self):
        self.create_file_with_data()

        processed_file = PrevProcessedFile(FILENAME)
        should_process = processed_file.should_process_restaurant({
            'navnelbnr': '555', 'seneste_kontrol_dato': '01-01-2001 00:00:00'})

        self.assertTrue(should_process)

    def test_should_process_restaurant_with_new_date(self):
        seq_nr = '123'
        self.create_file_with_data(seq_nr, '01-01-2001 00:00:00')

        processed_file = PrevProcessedFile(FILENAME)
        should_process = processed_file.should_process_restaurant({
            'navnelbnr': seq_nr, 'seneste_kontrol_dato': '01-02-2001 00:00:00'})

        self.assertTrue(should_process)

    def test_date_in_file_gets_updated(self):
        seq_nr = '123'
        new_date = '01-02-2001 00:00:00'
        self.create_file_with_data(seq_nr, '01-01-2001 00:00:00')
        new_restaurant = {'navnelbnr': seq_nr,
                          'seneste_kontrol_dato': new_date}

        processed_file = PrevProcessedFile(FILENAME)
        processed_file.should_process_restaurant(new_restaurant)
        processed_file.output_processed_companies([new_restaurant])
        processed_file = PrevProcessedFile(FILENAME)

        self.assertEqual(
            processed_file.get_control_date_by_seq_nr(seq_nr), new_date)

    def test_old_entry_is_deleted_when_new_control_date(self):
        seq_nr = '123'
        new_date = '01-02-2001 00:00:00'
        self.create_file_with_data(seq_nr, '01-01-2001 00:00:00')
        new_restaurant = {'navnelbnr': seq_nr,
                          'seneste_kontrol_dato': new_date}

        processed_file = PrevProcessedFile(FILENAME)
        processed_file.should_process_restaurant(new_restaurant)
        processed_file.output_processed_companies([])
        processed_file = PrevProcessedFile(FILENAME)

        self.assertEqual(
            processed_file.get_control_date_by_seq_nr(seq_nr), None)

    def create_file_with_data(self, seq_nr='123', date='01-01-2001 00:00:00'):
        restaurant1 = {'navnelbnr': '11111',
                       'seneste_kontrol_dato': '02-02-2002 00:00:00'}
        restaurant2 = {'navnelbnr': seq_nr,
                       'seneste_kontrol_dato': date}
        restaurant3 = {'navnelbnr': '22222',
                       'seneste_kontrol_dato': '03-03-2003 00:00:00'}

        processed_file = PrevProcessedFile(FILENAME)
        processed_file.output_processed_companies(
            [restaurant1, restaurant2, restaurant3])
