# -*- coding: utf-8 -*-
import unittest
from core import utils


class UtilsTests(unittest.TestCase):
    def test_ping(self):
        self.assertIs(utils.ping('127.0.0.1', 9728), False, "ping() failed")

    def test_replace(self):
        self.assertEqual(utils.replace('ä'), 'ae')
        self.assertEqual(utils.replace('ö'), 'oe')
        self.assertEqual(utils.replace('ü'), 'ue')
        # ...

    def test_get_movie_extensions(self):
        extensions = utils.get_movie_extensions()
        self.assertIn('.mkv', extensions)
        self.assertIn('.avi', extensions)
        self.assertIn('.mpg', extensions)
        # ...

if __name__ == '__main__':
    unittest.main()
