import unittest
import datetime
import pytz

import sys
sys.path.append("..")

from decision import *
from actions import SunbatheAction

class RunTest(unittest.TestCase):
    def testRunAction(self):
        aRunAction = RunAction(datetime.datetime.now(tz=pytz.UTC), Loc(lat=53.0, lon=-3.0), "myRunConf.py")
        self.assertTrue(aRunAction.score)

    def testRunActivity(self):
        aRunAction = RunAction(datetime.datetime.now(tz=pytz.UTC), Loc(lat=53.0, lon=-3.0), "myRunConf.py")
        possibility = [aRunAction] * 5
        aRunActivity = Activity(possibility)

        self.assertTrue(aRunActivity.score)


if __name__ == '__main__':
    unittest.main()