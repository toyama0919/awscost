import unittest
from awscost.util import Util
import datetime


class UtilTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_handler(self):
        time = datetime.datetime(2010, 1, 1, 0, 0, 10)
        self.assertEqual("2010-01-01T00:00:10", Util.datetime_handler(time))

        date = datetime.date(2010, 1, 1)
        self.assertEqual("2010-01-01", Util.datetime_handler(date))


if __name__ == "__main__":
    unittest.main()
