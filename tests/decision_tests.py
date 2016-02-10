import cPickle as pickle
import datetime
import os
import pytz
import unittest

import dre.actions as actions
from dre.when_decision import *
from dre.decision import *
from dre.forecast_cache import ForecastCache

from config import config
run = config.get_default_values_conf("tests")["run"]


class WhenDecisionTest(unittest.TestCase):
    cache = ForecastCache()

    base = os.path.split(__file__)[0]
    with open(os.path.join(base, 'data', 'testForecast.pkl'), "rb") as f:
        timesteps = pickle.load(f)
    cache.cache_forecast(timesteps, Loc(lat=53.0, lon=-3.0))

    whenActionBuilders = [WhenActionBuilder(actions.GaussDistFromIdeal,
                              run["conditions"],
                              Loc(lat=53.0, lon=-3.0),
                              i*datetime.timedelta(seconds=15*60),
                              cache=cache)
                      for i in range(5)]
    
    startTime = timesteps[0].date
    whenFilter = [TimeSlot(startTime, startTime+datetime.timedelta(days=1)),
                  TimeSlot(startTime+datetime.timedelta(days=2), startTime+datetime.timedelta(days=4))]

    def testWhenRunDecision(self):
        aDecision = WhenDecision(self.whenActionBuilders, self.whenFilter)
        aDecision.generatePossibleActivities(timeRes=datetime.timedelta(hours=3))
        self.assertEquals(len(aDecision.possibleActivities), 24)
        self.assertEquals(aDecision.possibleActivities[0].score.value, 0.491081617138855)


class WhatDecisionTest(unittest.TestCase):
    loc = Loc(lat=53.0, lon=-3.0)
    cache = ForecastCache()
    base = os.path.split(__file__)[0]
    with open(os.path.join(base, 'data', 'testForecast.pkl'), "rb") as f:
        timesteps = pickle.load(f)
    cache.cache_forecast(timesteps, loc)

    def testWhatDecision(self):
      mySunbathe = Activity([actions.GaussDistFromIdeal(self.timesteps[0].date, self.loc, run["conditions"], self.cache)])
      myRun = Activity([actions.GaussDistFromIdeal(self.timesteps[0].date, self.loc, run["conditions"], self.cache)])

      activities = [mySunbathe, myRun]
      activities.sort(key=lambda v: v.score.value, reverse=True)


if __name__ == '__main__':
    unittest.main()