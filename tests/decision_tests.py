import unittest
import datetime

import sys
sys.path.append("..")

from decision import *
from run import *

class WhenDecisionTest(unittest.TestCase):
    whats = [RunInstant] * 5
    whatConfigFiles = ["myRunConf.py"] * 5
    wheres = [Loc(lat=53.0, lon=-2.9),
              Loc(lat=52.9, lon=-3.0),
              Loc(lat=53.0, lon=-3.0),
              Loc(lat=53.0, lon=-3.0),
              Loc(lat=53.0, lon=-3.0)]
    whenDeltas = [datetime.timedelta(seconds=15*60)] * 5
    now = datetime.datetime.now()
    whenFilter = [TimeSlot(now, now+datetime.timedelta(days=1)),
                  TimeSlot(now+datetime.timedelta(days=2), now+datetime.timedelta(days=4))]

    def testWhenRunDecision(self):
        aDecision = WhenDecision(self.whats, self.whatConfigFiles, self.wheres, self.whenDeltas, self.whenFilter)
        aDecision.generatePossibleActions(timeRes=datetime.timedelta(hours=3))

        assertTrue(len(aDecision.possibleActions) > 0)
        assertTrue(aDecision.possibleActions[0].score > aDecision.possibleActions[-1].score)


if __name__ == '__main__':
    unittest.main()