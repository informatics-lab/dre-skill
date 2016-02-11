"""
Defines a set of classes which inherit from `dre.decision.Action`
and define different `get_score` methods.

These are then uses to rank possible actions in different ways

"""

# future imports
from __future__ import division

# standard library
import math
import sys
sys.path.append("./lib")

# third party
import datapoint

# local
from decision import *
from forecast_cache import ForecastNotCachedException

# globals for data point
DATAPOINT_KEY = "41bf616e-7dbc-4066-826a-7270b8da4b93"
DP_FORECAST_FREQUENCY = "3hourly"


class GaussDistFromIdeal(Action):
    def get_score(self):
        """ 
        Score for each variable is distance between idean an limit in gaussian space
        Multiplicitavely combines scores for different variables

        """

        def get_forecast(condition):
            """
            Hits database API e.g. data point for forecast data

            Args:
                * condition (condition)

            """
            try:
                action_forecast = self.cache.get_forecast(self.time, self.loc, condition.variable)
            except ForecastNotCachedException:
                conn = datapoint.connection(api_key=DATAPOINT_KEY)
                site = conn.get_nearest_site(latitude=self.loc.lat, longitude=self.loc.lon)
                forecast = conn.get_forecast_for_site(site.id, frequency=DP_FORECAST_FREQUENCY)
                timesteps = [step for day in forecast.days for step in day.timesteps]

                self.cache.cache_forecast(timesteps, self.loc)
                action_forecast = self.cache.get_forecast(self.time, self.loc, condition.variable)
            return action_forecast

        def normalized_linear_score(val, minlim, maxlim):
            """
            Converts to fractional distance between limits

            Args:
                * val (float): value to convert
                * minlim (float): minmum value in range
                * maxlim (float): maxmum value in range

            """
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
        to_gaussian_space = lambda x: 1.0-2.5066*1.0/math.sqrt(2.0*math.pi) * math.e**(-0.5 * (x*3)**2)
        
        scores = []
        logs = []
        for condition in self.conditions:
            forecast_condition = get_forecast(condition)
            this_min = condition.ideal if forecast_condition > condition.ideal else condition.min
            this_max = condition.max if forecast_condition > condition.ideal else condition.ideal
            guassian_distance = to_gaussian_space(normalized_linear_score(forecast_condition, this_min, this_max))

            logs.append({"variable": condition.variable, 
                         "min": condition.min,
                         "max": condition.max,
                         "ideal": condition.ideal,
                         "forecast": forecast_condition,
                         "metric": "GaussDistFromIdeal"})

            scores.append(guassian_distance)

        combined_score_value = sum(scores)/len(scores)
        return Score(combined_score_value, metadata=logs)