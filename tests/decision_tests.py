import unittest
import datetime
import pytz

import sys
sys.path.append("..")

from decision import *
from run import *

class WhenDecisionTest(unittest.TestCase):
    whats = [RunAction] * 5
    whatConfigFiles = ["myRunConf.py"] * 5
    wheres = [Loc(lat=53.0, lon=-2.9),
              Loc(lat=52.9, lon=-3.0),
              Loc(lat=53.0, lon=-3.0),
              Loc(lat=53.0, lon=-3.0),
              Loc(lat=53.0, lon=-3.0)]
    whenDeltas = [i*datetime.timedelta(seconds=15*60) for i in range(1,6)]
    now = datetime.datetime.now(tz=pytz.UTC)
    whenFilter = [TimeSlot(now, now+datetime.timedelta(days=1)),
                  TimeSlot(now+datetime.timedelta(days=2), now+datetime.timedelta(days=4))]

    def testWhenRunDecision(self):
        aDecision = WhenDecision(self.whats, self.whatConfigFiles, self.wheres, self.whenDeltas, self.whenFilter)
        aDecision.generatePossibleActivities(timeRes=datetime.timedelta(hours=3))

        self.assertTrue(len(aDecision.possibleActivities) > 0)
        self.assertTrue(aDecision.possibleActivities[0].score.value >= aDecision.possibleActivities[-1].score.value)


if __name__ == '__main__':
    unittest.main()