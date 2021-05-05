import unittest
import os

from datetime import datetime
from filter_xml.temp_file import TempFile
from filter_xml.catalog import Restaurant


class TempFileTest(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_file = None

    def tearDown(self) -> None:
        if os.path.exists(TempFile.FILE_NAME):
            os.remove(TempFile.FILE_NAME)

    def test_can_add_valid_date(self):
        self.temp_file = TempFile()
        data = Restaurant()
        data.name_seq_nr = '4321'
        data.start_date = datetime.now()

        self.temp_file.add_data(data)

    def test_get_all_correct_data(self):
        self.temp_file = TempFile()
        row1 = Restaurant()
        row1.name_seq_nr = '123'
        row1.start_date = datetime.now()
        row2 = Restaurant()
        row2.name_seq_nr = '456'
        row2.start_date = datetime.now()
        row3 = Restaurant()
        row3.name_seq_nr = '789'
        row3.start_date = datetime.now()
        self.temp_file.add_data(row1)
        self.temp_file.add_data(row2)
        self.temp_file.add_data(row3)

        data = self.temp_file.get_all()

        self.assertEqual(data.catalog[0], row1)
        self.assertEqual(data.catalog[1], row2)
        self.assertEqual(data.catalog[2], row3)

    def test_close_removes_file(self):
        self.temp_file = TempFile()
        row1 = Restaurant()
        row1.name_seq_nr = '123'
        row1.start_date = datetime.now()
        self.temp_file.add_data(row1)

        self.assertTrue(os.path.exists(TempFile.FILE_NAME))
        self.temp_file.close()
        self.assertFalse(os.path.exists(TempFile.FILE_NAME))

    def test_exception_when_no_seq_nr_in_data(self):
        row = Restaurant()
        row.name_seq_nr = None
        self.temp_file = TempFile()

        with self.assertRaises(ValueError):
            self.temp_file.add_data(row)

    def test_empty_field_returns_correct(self):
        row = Restaurant()
        row.name_seq_nr = '123'
        row.start_date = None
        self.temp_file = TempFile()
        self.temp_file.add_data(row)
        self.temp_file = TempFile() # construct new temp file to load the data

        data = self.temp_file.get_all()
        
        self.assertEqual(data.catalog[0].start_date, None)
