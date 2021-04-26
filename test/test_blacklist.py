from filter_xml.blacklist import Blacklist
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
        restaurant = {'navnelbnr': '1234'}

        Blacklist.add(restaurant)

        self.assertTrue(Blacklist.contains('1234'))

    def test_contains_previously_outputted_entry(self):
        restaurant = {'navnelbnr': '1234'}
        Blacklist.add(restaurant)
        self.reset_blacklist_state()

        Blacklist.read_restaurants_file()
       
        self.assertTrue(Blacklist.contains('1234'))

    def test_adding_entries_across_multiple_sessions_persists_both(self):
        restaurant1 = {'navnelbnr': '1234'}
        restaurant2 = {'navnelbnr': '4321'}

        Blacklist.add(restaurant1)
        self.reset_blacklist_state()
        Blacklist.add(restaurant2)
        Blacklist.read_restaurants_file()

        self.assertTrue(Blacklist.contains('1234'))
        self.assertTrue(Blacklist.contains('4321'))


    def reset_blacklist_state(self):
        Blacklist._restaurants = []
        Blacklist._file_path = FILENAME
        Blacklist._file_writer = None
        Blacklist._file = None
