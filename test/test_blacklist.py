from filter_xml.blacklist import Blacklist
from filter_xml.catalog import Restaurant
import unittest
import os

FILENAME = 'test/blacklist_test.csv'


class BlacklistTest(unittest.TestCase):

    @classmethod
    def tearDownClass(cls) -> None:
        cls.reset_blacklist_state()
        if os.path.exists(FILENAME):
            os.remove(FILENAME)

    def setUp(self) -> None:
        self.reset_blacklist_state()
        if os.path.exists(FILENAME):
            os.remove(FILENAME)

    def test_contains_added_entry(self):
        restaurant = Restaurant()
        restaurant.name_seq_nr = '1234'

        Blacklist.add(restaurant)

        self.assertTrue(Blacklist.contains('1234'))

    def test_contains_previously_outputted_entry(self):
        restaurant = Restaurant()
        restaurant.name_seq_nr = '1234'
        Blacklist.add(restaurant)
        self.reset_blacklist_state()
       
        self.assertTrue(Blacklist.contains('1234'))

    @classmethod
    def reset_blacklist_state(cls):
        Blacklist._restaurants = []
        Blacklist._file_path = FILENAME
        Blacklist._file_writer = None
        Blacklist.close_file()
        Blacklist._file = None
