import unittest
import datetime

from decision import *
from run import *

class RunTest(unittest.TestCase):
    def testRunInstant(self):
        aRunInstant = RunInstant(datetime.datetime.now(), Loc(lat=53.0, lon=-3.0), "../myRunConf.py")
        self.assertTrue(anInstant.score)

    def testRunAction(self):
        aRunInstant = RunInstant(datetime.datetime.now(), Loc(lat=53.0, lon=-3.0), "../myRunConf.py")
        possibility = [aRunInstant] * 5
        aRunAction = RunAction(possibility)

        self.assertTrue(aRunAction.score)