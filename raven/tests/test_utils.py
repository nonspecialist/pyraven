import unittest
import datetime
import raven


class TestUtils(unittest.TestCase):
    def test_convert_timestamp(self):
        # should return a datetime object created from 1522109270
        should = datetime.datetime.fromtimestamp(1522109270)
        result = raven.raven.convert_timestamp(575464070)
        self.assertEqual(should, result)
