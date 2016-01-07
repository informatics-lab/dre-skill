import unittest
import datetime
import pytz

import sys
sys.path.append("..")

from decision import *
from run import *

class RunTest(unittest.TestCase):
    def testRunInstant(self):
        aRunInstant = RunInstant(datetime.datetime.now(tz=pytz.UTC), Loc(lat=53.0, lon=-3.0), "myRunConf.py")
        self.assertTrue(aRunInstant.score)

    def testRunAction(self):
        aRunInstant = RunInstant(datetime.datetime.now(tz=pytz.UTC), Loc(lat=53.0, lon=-3.0), "myRunConf.py")
        possibility = [aRunInstant] * 5
        aRunAction = Action(possibility)

        self.assertTrue(aRunAction.score)


if __name__ == '__main__':
    unittest.main()