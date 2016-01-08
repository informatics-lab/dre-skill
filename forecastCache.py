class forecastCache(object):
    def __init__(self):
        self.forecasts = []
        self.timeThresh = 0

    def cacheForecast(self, forecast, loc):
        """
        Forecast must be an unpacked list of timesteps

        """
        self.forecasts.append([forecast, loc])

    def getForecast(self, time, loc):
        for forecast, forecastLoc in self.forecasts:
            nearestForecast = min(forecast, key=lambda v: abs(v.date-time))
            if abs(nearestForecast.date-time)<abs(forecast[0].date-forecast[1].date)\
                 and forecastLoc.lat == loc.lat\
                 and forecastLoc.lon == loc.lon:
                return nearestForecast