from __future__ import division

import math

from decision import *
from forecastCache import ForecastNotCachedException

import sys
sys.path.append("./lib")
import datapoint

DATAPOINT_KEY = "41bf616e-7dbc-4066-826a-7270b8da4b93"
DP_FORECAST_FREQUENCY = "3hourly"

class GaussDistFromIdeal(Action):
    def getScore(self):
        """ 
        Score for each variable is distance between idean an limit in gaussian space
        Multiplicitavely combines scores for different variables

        """

        def getForecast(condition):
            try:
                actionForecast = self.cache.getForecast(self.time, self.loc, condition.variable)
            except ForecastNotCachedException:
                conn = datapoint.connection(api_key=DATAPOINT_KEY)
                site = conn.get_nearest_site(latitude=self.loc.lat, longitude=self.loc.lon)
                forecast = conn.get_forecast_for_site(site.id, frequency=DP_FORECAST_FREQUENCY)
                timesteps = [step for day in forecast.days for step in day.timesteps]

                self.cache.cacheForecast(timesteps, self.loc)
                actionForecast = self.cache.getForecast(self.time, self.loc, condition.variable)
            return actionForecast

        def normalizedLinearScore(val, minlim, maxlim):
            if val == minlim == maxlim:
                dist = 1.0
            elif not minlim < val < maxlim:
                dist = 0.0
            else:
                dist = (val-minlim) / max((maxlim-minlim), 1e-8)
            return dist

        # magic numbers scale Guassian to unit amp and unit practial max/min,
        # flip upside down and move up one
        # i.e. an x of 1 gives a value of 0 and a x of 0 gives a value of 1.
        toGaussianSpace = lambda x: 1.0-2.5066*1.0/math.sqrt(2.0*math.pi) * math.e**(-0.5 * (x*3)**2)
        
        scores = []
        for condition in self.conditions:
            forecastCondition = getForecast(condition)
            thisMin = condition.ideal if forecastCondition > condition.ideal else condition.min
            thisMax = condition.max if forecastCondition > condition.ideal else condition.ideal
            guassianDistance = toGaussianSpace(normalizedLinearScore(forecastCondition, thisMin, thisMax))
            scores.append(guassianDistance)

        combinedScoreValue = sum(scores)/len(scores)
        return Score(combinedScoreValue, metadata={"log": "Score for each variable is distance between ideal an limit in gaussian space Multiplicitavely combines scores for different variables",
                                                   "conditions": self.conditions})