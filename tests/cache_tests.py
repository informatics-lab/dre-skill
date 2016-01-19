import cPickle as pickle
import datetime
import pytz
import unittest

import datapoint

from dre.forecastCache import ForecastCache, ForecastNotCachedException
from dre.decision import Loc

class TestChacheAndRetrieve(unittest.TestCase):
    cache = ForecastCache()
    loc = Loc(lat=53.0, lon=-3.0)
    with open("./tests/testForecast.pkl", "rb") as f:
        timesteps = pickle.load(f)
    cache.cacheForecast(timesteps, loc)

    def test_getVal(self):
        fc = self.cache.getForecast(self.timesteps[0].date, self.loc, "temperature")
        self.assertEquals(fc, 18.0)

class TestRetrieveEmpty(unittest.TestCase):
    cache = ForecastCache()
    loc = Loc(lat=53.0, lon=-3.0)
    
    def test_getVal(self):
        with self.assertRaises(ForecastNotCachedException):
            self.cache.getForecast(datetime.datetime.now(), self.loc, "temperature")


if __name__ == '__main__':
    unittest.main()
