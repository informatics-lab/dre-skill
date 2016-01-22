class ForecastNotCachedException(Exception):
    def __init__(self, goodTime, goodLat, goodLon, goodVariable, time, loc, variable):
        message = ""
        if not goodTime:
            message += "Time %s not found in any forecasts\n" % str(time)
        if not goodLat:
            message += "Latitude %d not found in any forecasts\n" % loc.lat
        if not goodLon:
            message += "Longitude %d not found in any forecasts\n" % loc.lon
        if not goodVariable:
            message += "Variable %s not in any forecast" % variable
        super(ForecastNotCachedException, self).__init__(message)


class ForecastCache(object):
    def __init__(self):
        self.forecasts = []

    def cacheForecast(self, forecast, loc):
        """
        Forecast must be an unpacked list of timesteps

        """
        self.forecasts.append([forecast, loc])

    def getForecast(self, time, loc, variable):
        goodForecasts = []
        goodTime = goodLat = goodLon = goodVariable = False
        for forecast, forecastLoc in self.forecasts:
            thisGoodTime = thisGoodLat = thisGoodLon = thisGoodVariable = False 

            nearestForecast = min(forecast, key=lambda v: abs(v.date-time))
            
            thisGoodTime = abs(nearestForecast.date-time) < abs(forecast[0].date-forecast[1].date)
            goodTime = True if thisGoodTime else goodTime
            
            thisGoodLat = forecastLoc.lat == loc.lat
            goodLat = True if thisGoodLat else goodLat
            
            thisGoodLon = forecastLoc.lon == loc.lon
            goodLat = True if thisGoodLat else goodLat
            
            thisGoodVariable = variable in nearestForecast.__dict__.keys()
            goodVariable = True if thisGoodVariable else goodVariable
            
            if thisGoodTime and thisGoodLat and thisGoodLon and thisGoodVariable:
                goodForecasts.append(nearestForecast)

        try:
            return min(goodForecasts, key=lambda v: abs(v.date-time)).__dict__[variable].value
        except ValueError:
            raise ForecastNotCachedException(goodTime, goodLat, goodLon, goodVariable, time, loc, variable)