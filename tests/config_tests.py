import unittest
import pytz

import sys
sys.path.append("..")

from config.load_config import *

class ConfigTest(unittest.TestCase):
    default = 'default'
    blanks = ['empty_str', 'none', 'empty_list']
    lookup = {'specified': 'value', 'empty_str': '', 'none': None, 'empty_list': []}

    def testTryLoading(self):
        self.assertEquals(try_loading(self.lookup, 'missing', self.default), self.default)
        for key in self.blanks:
            self.assertEquals(try_loading(self.lookup, key, self.default), self.default)
        self.assertEquals(try_loading(self.lookup, 'specified', self.default), 'value')


if __name__ == '__main__':
    unittest.main()