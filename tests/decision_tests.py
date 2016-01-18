import cPickle as pickle
import datetime
import pytz
import unittest

import dre.actions as actions
from dre.whenDecision import *
from dre.decision import *
from dre.forecastCache import ForecastCache


class WhenDecisionTest(unittest.TestCase):
    cache = ForecastCache()
    with open("./tests/testForecast.pkl", "rb") as f:
        timesteps = pickle.load(f)
    cache.cacheForecast(timesteps, Loc(lat=53.0, lon=-3.0))

    whenActionBuilders = [WhenActionBuilder(actions.GaussDistFromIdeal,
                              "gauss_config/run.py",
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
        self.assertEquals(aDecision.possibleActivities[0].score.value, 0.320456502460288)


class WhatDecisionTest(unittest.TestCase):
    loc = Loc(lat=53.0, lon=-3.0)
    cache = ForecastCache()
    with open("./tests/testForecast.pkl", "rb") as f:
        timesteps = pickle.load(f)
    cache.cacheForecast(timesteps, loc)

    def testWhatDecision(self):
      mySunbathe = Activity([actions.GaussDistFromIdeal(self.timesteps[0].date, self.loc, "gauss_config/sunbathe.py", self.cache)])
      myRun = Activity([actions.GaussDistFromIdeal(self.timesteps[0].date, self.loc, "gauss_config/run.py", self.cache)])

      activities = [mySunbathe, myRun]
      activities.sort(key=lambda v: v.score.value, reverse=True)

      self.assertEqual(activities[0].possibility[0].config.name, "Run")
      self.assertEqual(activities[1].possibility[0].config.name, "Sunbathe")


if __name__ == '__main__':
    unittest.main()