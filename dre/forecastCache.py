class ForecastNotCachedException(Exception):
    """
    This exception is thown when the user tries to access
    forecast data which is considered not to be stored
    in the cache.

    Exception messesage details why the forecast was considered
    not to be cached.

    """
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
    """
    An object for persisting forecast data for a whole session.

    """
    def __init__(self):
        self.forecasts = []

    def cacheForecast(self, forecast, loc):
        """
        Args:
            * forecast (list): Forecast is a list of dictionaries
                where each dictionary element represents a
                a forecast for a specific point in time and space.
                At a minimum it must have a `date` element consisting
                of a `datetime.datetime` object.
            * loc (Loc): A location obejct which specifies the
                requested (as opposed to returned) location.

        """
        self.forecasts.append([forecast, loc])

    def getForecast(self, time, loc, variable):
        """
        Gets the forecast data. First it attempts to retrieve
        suitable data from the cache, then from the data base
        e.g. data point, which is subsequently cached.

        Args:
            * time (datetime.datetime): time of desired forecast
            * loc (Loc): location of desired forecast
            * variable (string): name of desired forecast variable

        """
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