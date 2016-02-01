import cPickle as pickle
import datetime
import os
import unittest

from dre.forecast_cache import ForecastCache, ForecastNotCachedException
from dre.decision import Loc


class TestChacheAndRetrieve(unittest.TestCase):
    cache = ForecastCache()
    loc = Loc(lat=53.0, lon=-3.0)
    base = os.path.split(__file__)[0]
    with open(os.path.join(base, 'data', 'testForecast.pkl'), "rb") as f:
        timesteps = pickle.load(f)
    cache.cache_forecast(timesteps, loc)

    def test_getVal(self):
        fc = self.cache.get_forecast(self.timesteps[0].date, self.loc, "temperature")
        self.assertEquals(fc, 18.0)

class TestRetrieveEmpty(unittest.TestCase):
    cache = ForecastCache()
    loc = Loc(lat=53.0, lon=-3.0)
    
    def test_getVal(self):
        with self.assertRaises(ForecastNotCachedException):
            self.cache.get_forecast(datetime.datetime.now(), self.loc, "temperature")


if __name__ == '__main__':
    unittest.main()
