import unittest
import datetime

from decision import *
from run import *

class WhenDecisionTest(unittest.TestCase):
    whats = [RunInstant] * 5
    wheres = [Loc(lat=53.0, lon=-2.9),
              Loc(lat=52.9.0, lon=-3.0),
              Loc(lat=53.0, lon=-3.0),
              Loc(lat=53.0, lon=-3.0),
              Loc(lat=53.0, lon=-3.0)]
    whenDeltas = [datetime.timedelta.seconds(15*60)] * 5
    now = datetime.datetime.now()
    whereFilter = [[_now, _now+datetime.timedelta.days(1)],
                   [_now+datetime.timedelta.days(2), _now+datetime.timedelta.days(4)]]

    def testWhenRunDecision(self):
        aDecision = WhenDecision(self.whats, self.wheres. self.whenDeltas, self.whenFilter)
        aDecision.generatePossibleActions(timeRes=datetime.timedelta.hours(3))

        assertTrue(len(aDecision.possibleActions) > 0)
        assertTrue(aDecision.possibleActions[0].score > aDecision.possibleActions[-1].score)