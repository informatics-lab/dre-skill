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

    whenActions = [WhenAction(RunAction,
                              "myRunConf.py",
                              Loc(lat=53.0, lon=-3.0),
                              i*datetime.timedelta(seconds=15*60))
                      for i in range(5)]
    
    startTime = timesteps[0].date
    whenFilter = [TimeSlot(startTime, startTime+datetime.timedelta(days=1)),
                  TimeSlot(startTime+datetime.timedelta(days=2), startTime+datetime.timedelta(days=4))]

    def testWhenRunDecision(self):
        aDecision = WhenDecision(self.whenActions, self.whenFilter)
        aDecision.generatePossibleActivities(timeRes=datetime.timedelta(hours=3))
        self.assertEquals(len(aDecision.possibleActivities), 24)
        self.assertEquals(aDecision.possibleActivities[0].score.value, 0.320456502460288)


if __name__ == '__main__':
    unittest.main()