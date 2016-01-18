class ForecastCache(object):
    def __init__(self):
        self.forecasts = []

    def cacheForecast(self, forecast, loc):
        """
        Forecast must be an unpacked list of timesteps

        """
        self.forecasts.append([forecast, loc])

    def getForecast(self, time, loc, variable):
        for forecast, forecastLoc in self.forecasts:
            nearestForecast = min(forecast, key=lambda v: abs(v.date-time))
            if abs(nearestForecast.date-time) < abs(forecast[0].date-forecast[1].date)\
                 and forecastLoc.lat == loc.lat\
                 and forecastLoc.lon == loc.lon\
                 and variable in nearestForecast.__dict__.keys():
                return nearestForecast.__dict__[variable].value
            else:
                print loc.lat, loc.lon, time
                print forecastLoc.lat, forecastLoc.lon, nearestForecast.date
