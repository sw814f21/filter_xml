from filter_xml.blacklist import Blacklist
from filter_xml.catalog import Restaurant
import unittest
import os

FILENAME = 'test/blacklist_test.csv'


class BlacklistTest(unittest.TestCase):

    @classmethod
    def tearDownClass(cls) -> None:
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

    def test_adding_entries_across_multiple_sessions_persists_both(self):
        restaurant1 = Restaurant()
        restaurant1.name_seq_nr = '1234'
        restaurant2 = Restaurant()
        restaurant2.name_seq_nr = '4321'

        Blacklist.add(restaurant1)
        self.reset_blacklist_state()
        Blacklist.add(restaurant2)

        self.assertTrue(Blacklist.contains('1234'))
        self.assertTrue(Blacklist.contains('4321'))


    def reset_blacklist_state(self):
        Blacklist._restaurants = []
        Blacklist._file_path = FILENAME
        Blacklist._file_writer = None
        Blacklist._file = None