import unittest
import datetime
import pytz

import sys
sys.path.append("..")

from dre.decision import *
import dre.actions as actions

from config import config
run = config.get_activities_conf("tests", "run")

class RunTest(unittest.TestCase):
    def testRunAction(self):
        aRunAction = actions.GaussDistFromIdeal(datetime.datetime.now(tz=pytz.UTC),
                                                    Loc(lat=53.0, lon=-3.0),
                                                    run["conditions"])
        self.assertTrue(aRunAction.score)

    def testRunActivity(self):
        aRunAction = actions.GaussDistFromIdeal(datetime.datetime.now(tz=pytz.UTC),
                                                    Loc(lat=53.0, lon=-3.0),
                                                    run["conditions"])
        possibility = [aRunAction] * 5
        aRunActivity = Activity(possibility)

        self.assertTrue(aRunActivity.score)


if __name__ == '__main__':
    unittest.main()