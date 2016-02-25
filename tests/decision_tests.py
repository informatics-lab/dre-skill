import cPickle as pickle
import datetime
import os
import pytz
import unittest
import isodate

import dre.actions as actions
from dre.when_decision import *
from dre.what_decision import *
from dre.decision import *
from dre.forecast_cache import ForecastCache

from database import database

run = database.get_default_values_conf("tests")['default_values']["run"]
run.update(database.get_default_values_conf("tests")['general_config']["run"])
sunbathe = database.get_default_values_conf("tests")['default_values']["sunbathe"]
sunbathe.update(database.get_default_values_conf("tests")['general_config']["sunbathe"])
cinema = database.get_default_values_conf("tests")['default_values']["cinema"]
cinema.update(database.get_default_values_conf("tests")['general_config']["cinema"])


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

    def testWhatDecisionManual(self):
      mySunbathe = Activity([actions.GaussDistFromIdeal(self.timesteps[0].date, self.loc, run["conditions"], self.cache)])
      myRun = Activity([actions.GaussDistFromIdeal(self.timesteps[0].date, self.loc, run["conditions"], self.cache)])

      activities = [mySunbathe, myRun]
      activities.sort(key=lambda v: v.score.value, reverse=True)

    def testWhatDecision(self):
      thisSunbathe = WhatActivity('sunbathe', actions.GaussDistFromIdeal, sunbathe["conditions"], isodate.parse_duration(sunbathe["totalTime"]))
      thisRun = WhatActivity('run', actions.GaussDistFromIdeal, run["conditions"], isodate.parse_duration(run["totalTime"]))
      thisCinema = WhatActivity('cinema', actions.GaussDistFromIdeal, cinema["conditions"], isodate.parse_duration(cinema["totalTime"]))
      activities = [thisCinema, thisRun, thisSunbathe]
      startTime = self.timesteps[0].date
      timeslot = TimeSlot(startTime, startTime+datetime.timedelta(hours=3))

      aDecision = WhatDecision(activities, timeslot, self.loc, self.cache)
      aDecision.generatePossibleActivities(datetime.timedelta(seconds=15*60))
      self.assertEquals(aDecision.possibleActivities[0].name, 'cinema')
      self.assertEquals(aDecision.possibleActivities[0].score.value, 0.5826122793382577)


if __name__ == '__main__':
    unittest.main()