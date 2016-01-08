import cPickle as pickle
import datetime
import pytz
import unittest

from decision import *
from run import *
from forecastCache import ForecastCache


class WhenDecisionTest(unittest.TestCase):
    cache = ForecastCache()
    with open("./tests/testForecast.pkl", "rb") as f:
        timesteps = pickle.load(f)
    cache.cacheForecast(timesteps, Loc(lat=53.0, lon=-3.0))

    whats = [RunAction] * 5
    whatConfigFiles = ["myRunConf.py"] * 5
    wheres = [Loc(lat=53.0, lon=-3.0),
              Loc(lat=53.0, lon=-3.0),
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
        self.assertEquals(len(aDecision.possibleActivities), 24)
        self.assertEquals(aDecision.possibleActivities[0].score.value, 0.320456502460288)


if __name__ == '__main__':
    unittest.main()