import unittest
import os

from filter_xml.temp_file import TempFile


class TempFileTest(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_file = None

    def tearDown(self) -> None:
        if self.temp_file and os.path.exists(TempFile.FILE_NAME):
            self.temp_file.close()

    def test_can_add_valid_date(self):
        self.temp_file = TempFile()

        self.temp_file.add_data(
            {'navnelbnr': '4321', 'smiley_reports': 'testValue'})

    def test_get_all_correct_data(self):
        self.temp_file = TempFile()
        row1 = {'navnelbnr': '123', 'smiley_reports': 'test1'}
        row2 = {'navnelbnr': '456', 'smiley_reports': 'test2'}
        row3 = {'navnelbnr': '789', 'smiley_reports': 'test3'}
        self.temp_file.add_data(row1)
        self.temp_file.add_data(row2)
        self.temp_file.add_data(row3)

        data = self.temp_file.get_all()

        self.assertEqual(data[0], row1)
        self.assertEqual(data[1], row2)
        self.assertEqual(data[2], row3)

    def test_close_removes_file(self):
        self.temp_file = TempFile()

        self.assertTrue(os.path.exists(TempFile.FILE_NAME))
        self.temp_file.close()
        self.assertFalse(os.path.exists(TempFile.FILE_NAME))

    def test_exception_when_no_seq_nr_in_data(self):
        row1 = {'id': '123', 'field1': '321'}
        self.temp_file = TempFile()

        with self.assertRaises(ValueError):
            self.temp_file.add_data(row1)
