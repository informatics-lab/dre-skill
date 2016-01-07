import math

import datapoint

from decision import *
from forecastCache import forecastCache
cache = forecastCache()

DATAPOINT_KEY = "41bf616e-7dbc-4066-826a-7270b8da4b93"
DP_FORECAST_FREQUENCY = "3hourly"

class RunInstant(Instant):
    def getScore(self):
        """ 
        Score for each variable is distance between idean an limit in gaussian space
        Multiplicitavely combines scores for different variables

        """

        def getForecast(condition):
            cachedForecast = cache.getForecast(self.time, self.loc)
            if cachedForecast:
                instantForecast = cachedForecast
            else:
                conn = datapoint.connection(api_key=DATAPOINT_KEY)
                site = conn.get_nearest_site(latitude=self.loc.lat, longitude=self.loc.lon)
                forecast = conn.get_forecast_for_site(site.id, frequency=DP_FORECAST_FREQUENCY)
                timesteps = [step for day in forecast.days for step in day.timesteps]

                cache.cacheForecast(timesteps, self.loc)

                instantForecast = min(timesteps, key=lambda v: abs(v.date-self.time))
            return instantForecast

        normalizeDistance = lambda val, min, max: (val-min) / (max-min)
        toGaussianSpace = lambda x: 1.0/math.sqrt(2.0*math.pi) * math.e**(-0.5 * x**2)
        
        scores = []        
        for condition in self.config.conditions:
            forecastCondition = getForecast(condition)
            thisMin = condition.ideal if forecastCondition > condition.ideal else condition.min
            thisMax = condition.max if forecastCondition > condition.ideal else condition.ideal
            guassianDistance = toGaussianSpace(normalizeDistance(condition.ideal, thisMin, thisMax))
            scores.append(guassianDistance)

        combinedScoreValue = sum(scores)/len(scores)
        return Score(combinedScoreValue, metadata={"log": "Score for each variable is distance between ideal an limit in gaussian space Multiplicitavely combines scores for different variables",
                                                   "conditions": self.config.conditions})